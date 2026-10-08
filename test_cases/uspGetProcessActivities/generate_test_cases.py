"""Generate test case artifacts for [WorkFlow].[uspGetProcessActivities].

Single source of truth for the test cases. Running this script regenerates:
  - TestCases.md          human-readable test case catalogue
  - TestCases.csv         same catalogue, for Excel / test management tools
  - 01_Run_TestCases.sql  SQLCMD-mode T-SQL harness that executes every case

Expected results are derived from the procedure source (sp_helptext) and the
baseline call captured from the application.

Usage:  python generate_test_cases.py
"""

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Baseline call captured from the application (SQL Profiler trace).
BASELINE_TAG_ROW = "6737,N'BSP',0,366713,NULL,28,366713,5031,410129,0,NULL,'0001-01-01 00:00:00'"

# Scalar parameters of the baseline call. Values are T-SQL literals.
BASELINE_PARAMS = {
    "EndDate": "NULL",
    "IsMobileEnabled": "NULL",
    "IsOpenActivity": "1",
    "IsChildElementTasks": "0",
    "ProcessTitle": "1",
    "IsPersistentDataRequired": "NULL",
    "ProcessDateFilterAppliesTo": "1",
    "IsReferenceElementTasks": "0",
    "StartDate": "NULL",
    "UserID": "285",
    "RoleID": "346314",
    "ParentProcessInstanceID": "0",
}

# Order in which parameters appear in the original call. Optional parameters
# that the application does not pass are appended only when a case sets them.
PARAM_ORDER = [
    "EndDate", "FilterTags", "IsMobileEnabled", "IsOpenActivity",
    "IsChildElementTasks", "ProcessTitle", "IsPersistentDataRequired",
    "ProcessDateFilterAppliesTo", "ProcessStatus", "ProcessPriorities",
    "IsReferenceElementTasks", "StartDate", "ProcessTypes", "ProcessTriggers",
    "UserID", "RoleID", "ParentProcessInstanceID", "IsDebug", "EnableTimeLog",
]

# TVP parameter -> (variable, type)
TVPS = {
    "FilterTags": ("@p2", "Tag.TagModelTVP"),
    "ProcessStatus": ("@p9", "WorkFlow.ProcessActivityFilterValueTVP"),
    "ProcessPriorities": ("@p10", "WorkFlow.ProcessActivityFilterValueTVP"),
    "ProcessTypes": ("@p13", "WorkFlow.ProcessActivityFilterValueTVP"),
    "ProcessTriggers": ("@p14", "WorkFlow.ProcessActivityFilterValueTVP"),
}

# Tag rows are written as overrides of the baseline row, by column name, so the
# harness does not depend on the TVP's column order. {} = baseline row as is.
BASE_TAG = {}
ALT_TAG = {"TagName": "N'$(AltTagName)'", "ObjectID": "$(AltTagObjectID)"}
MISSING_TAG = {"TagName": "N'__NO_SUCH_TAG__'", "ObjectID": "-1"}
PROCESS_TAG = {"TagName": "N'$(ProcessName)'", "ElementTypeID": "2008"}
ALT_PROCESS_TAG = {"TagName": "N'$(AltProcessName)'", "ElementTypeID": "2008"}

# Expectation codes used by the harness:
#   SUCCESS - procedure must execute without error
#   ERROR   - procedure must raise an error
#   DEFECT  - procedure currently raises an error that is a defect
#   ANY     - either outcome is acceptable; verify behaviour manually
CASES = []


def case(tc_id, category, title, kind, priority, expected, expect="SUCCESS",
         params=None, tvps=None, tags=None, omit=(), max_ms=None, defect=None,
         pre_sql=None, post_sql=None, preconditions="Baseline data exists (see README)."):
    CASES.append(dict(
        id=tc_id, category=category, title=title, kind=kind, priority=priority,
        expected=expected, expect=expect, params=params or {}, tvps=tvps or {},
        tags=tags, omit=tuple(omit), max_ms=max_ms, defect=defect,
        pre_sql=pre_sql, post_sql=post_sql, preconditions=preconditions,
    ))


SAME_AS_BASELINE = "Identical result sets to TC001"

# ---------------------------------------------------------------- Baseline
case("TC001", "Baseline", "Execute baseline call exactly as captured", "Positive", "High",
     "No error. User/Role path, ProcessTitle=1 (My Tasks). Returns 4 result sets: "
     "(1) process instances; (2) activity instances, one row per process, the latest by StartDate "
     "(RANK=1), where both process and activity are open (IsActive=1) and the activity is on an "
     "element tagged BSP on which user 285 holds the activity's ExecutorRoleID, or is executed by user 285; "
     "(3) one row, ProcessInstanceID = NULL; (4) SLA rows for the returned processes. "
     "Processes missing a ProcessType, ProcessPriority or SupportedClient attribute are never returned. "
     "Record the row count of each set; later cases compare against them.")
case("TC002", "Baseline", "Re-execute baseline call (repeatability)", "Positive", "Medium",
     "Same rows as TC001, compared as sets: there is no ORDER BY, so row order can differ. "
     "Reads use NOLOCK, so counts can drift if data changes between runs.")

# ---------------------------------------------------------------- Process title
case("TC005", "ProcessTitle", "ProcessTitle = 2 (All Requests)", "Positive", "High",
     "Reads the SupportedElementTypes attribute of RoleID 346314. If it is set: activities executed by user 285 "
     "plus every activity on tagged elements of those element types (no role-membership check). "
     "If it is not set: activities executed by user 285 plus unassigned activities whose ExecutorRoleID is one of "
     "the user's groups. Set (2) has IsUserTaskExecutor = 1 only where Executor = 285.",
     params={"ProcessTitle": "2"})
case("TC006", "ProcessTitle", "ProcessTitle = 3 (My Requests)", "Positive", "High",
     "Only processes with TriggeredBy = 285 (the latest activity of each). Element tags and RoleID are ignored; "
     "only process-design tags (ElementTypeID 2008) still filter by name.",
     params={"ProcessTitle": "3"})
case("TC007", "ProcessTitle", "ProcessTitle = 0 (undefined value)", "Negative", "Medium",
     "No error and no validation. Takes the 'All Tasks' branch without SupportedElementTypes: activities executed by "
     "user 285 plus unassigned activities of the user's groups.",
     params={"ProcessTitle": "0"}, defect="No validation of @ProcessTitle; undefined values silently run the 'All Tasks' path.")
case("TC008", "ProcessTitle", "ProcessTitle = NULL", "Negative", "Low",
     "No error. Behaves like TC007 (every comparison with NULL is false).",
     params={"ProcessTitle": "NULL"})

# ---------------------------------------------------------------- Filter tags
case("TC010", "FilterTags", "Empty @FilterTags", "Boundary", "High",
     "No error. NF.uspGetElementsByTags_OPT receives no tags, so no tag-based activities. "
     "Activities executed directly by user 285 (Executor = 285) are still returned.",
     tags=[])
case("TC011", "FilterTags", "Two element tags (BSP + $(AltTagName))", "Positive", "High",
     "Rows for either tag. Row count >= TC001. No duplicate processes (one activity per process).",
     tags=[BASE_TAG, ALT_TAG])
case("TC012", "FilterTags", "Non-existent tag", "Negative", "High",
     "No error. Not necessarily zero rows: tag-based activities disappear, but activities executed directly "
     "by user 285 are still returned (same as TC010).",
     tags=[MISSING_TAG])
case("TC013", "FilterTags", "Same tag supplied twice", "Boundary", "Medium",
     SAME_AS_BASELINE + " (reference elements are DISTINCT). If the TVP has a primary key, the duplicate INSERT fails; "
     "that is also acceptable.",
     expect="ANY", tags=[BASE_TAG, BASE_TAG])
case("TC014", "FilterTags", "BSP tag + process-design tag (ElementTypeID 2008)", "Positive", "High",
     "Subset of TC001: only processes with ProcessName = '$(ProcessName)', plus processes whose ProcessName is NULL.",
     tags=[BASE_TAG, PROCESS_TAG])
case("TC015", "FilterTags", "Process-design tag only", "Positive", "Medium",
     "No element tags, so like TC010 (only activities executed by user 285), then filtered to ProcessName = '$(ProcessName)'.",
     tags=[PROCESS_TAG])

# ---------------------------------------------------------------- Open activity
case("TC020", "IsOpenActivity", "IsOpenActivity = 0", "Positive", "High",
     "Only closed processes (PID.IsActive = 0) with their latest closed activity. No overlap with TC001's processes.",
     params={"IsOpenActivity": "0"})
case("TC021", "IsOpenActivity", "IsOpenActivity = NULL", "Boundary", "High",
     "Open and closed processes. Process count >= TC001 and >= TC020.",
     params={"IsOpenActivity": "NULL"})

# ---------------------------------------------------------------- Reference element tasks
case("TC030", "ReferenceElementTasks", "IsReferenceElementTasks = 1 (element tag only)", "Positive", "High",
     "Reference-element path: the latest activity of each process whose activity RefElementVersionID = ObjectID of the BSP tag. "
     "Respects IsOpenActivity and the date filter. Does not check the user or role (see TC034).",
     params={"IsReferenceElementTasks": "1"})
case("TC031", "ReferenceElementTasks", "IsReferenceElementTasks = 1 + one process-design tag + one element tag", "Positive", "High",
     "Activities of processes named '$(ProcessName)' on elements tagged against the BSP tag's ObjectID (via Tag.TagMap).",
     params={"IsReferenceElementTasks": "1"}, tags=[BASE_TAG, PROCESS_TAG],
     preconditions="$(ProcessName) is a real process name that has open activities on the BSP-tagged element (and $(AltTagObjectID) a real element).")
case("TC032", "ReferenceElementTasks", "IsReferenceElementTasks = 1 + process-design tag + TWO element tags", "Negative", "High",
     "Fails with error 512 'Subquery returned more than 1 value' from "
     "T.SourceObjectID = (SELECT RefElementVersionID FROM @ReferenceElementFilter). It should return activities for both elements.",
     expect="DEFECT", params={"IsReferenceElementTasks": "1"}, tags=[BASE_TAG, ALT_TAG, PROCESS_TAG],
     defect="Scalar subquery '= (SELECT ... FROM @ReferenceElementFilter)' fails with error 512 when more than one element tag is passed. Use IN or a JOIN.",
     preconditions="$(ProcessName) is a real process name that has open activities on the BSP-tagged element (and $(AltTagObjectID) a real element).")
case("TC033", "ReferenceElementTasks", "IsReferenceElementTasks = 1 + TWO process-design tags + element tag", "Negative", "High",
     "Fails with error 512 from PID.ProcessName = (SELECT ProcessName FROM @ProcessNameFilter). "
     "It should return activities for both process names.",
     expect="DEFECT", params={"IsReferenceElementTasks": "1"}, tags=[BASE_TAG, PROCESS_TAG, ALT_PROCESS_TAG],
     defect="Scalar subquery '= (SELECT ProcessName FROM @ProcessNameFilter)' fails with error 512 when more than one process-design tag is passed.",
     preconditions="$(ProcessName) is a real process name that has open activities on the BSP-tagged element (and $(AltTagObjectID) a real element).")
case("TC034", "ReferenceElementTasks", "IsReferenceElementTasks = 1 with a non-existent UserID", "Security", "High",
     "Same rows as TC030: the reference-element path has no user or role check. "
     "Confirm this is intended; otherwise it is an authorisation gap.",
     params={"IsReferenceElementTasks": "1", "UserID": "999999999"},
     defect="Reference-element path returns the same activities for any @UserID / @RoleID (no security filter).")
case("TC035", "ReferenceElementTasks", "IsReferenceElementTasks = 1 and IsChildElementTasks = 1 with a parent", "Boundary", "Low",
     "Same as TC030: the reference-element branch takes priority, and the child-task flags are ignored.",
     params={"IsReferenceElementTasks": "1", "IsChildElementTasks": "1",
             "ParentProcessInstanceID": "$(ParentProcessInstanceID)"})

# ---------------------------------------------------------------- Child element tasks
case("TC040", "ChildElementTasks", "IsChildElementTasks = 1, ParentProcessInstanceID = 0", "Boundary", "High",
     SAME_AS_BASELINE + ". The child branch needs ParentProcessInstanceID > 0, so the user/role path runs.",
     params={"IsChildElementTasks": "1"})
case("TC041", "ChildElementTasks", "IsChildElementTasks = 1, valid ParentProcessInstanceID", "Positive", "High",
     "The latest activity of every child process of $(ParentProcessInstanceID). User, role, tags (except process-design), "
     "IsOpenActivity and the dates are not applied.",
     params={"IsChildElementTasks": "1", "ParentProcessInstanceID": "$(ParentProcessInstanceID)"})
case("TC042", "ChildElementTasks", "IsChildElementTasks = 1 + parent + IsOpenActivity = 0 + date range", "Boundary", "Medium",
     "Same rows as TC041: the child branch ignores IsOpenActivity, StartDate and EndDate. "
     "Confirm with the business whether these filters should apply.",
     params={"IsChildElementTasks": "1", "ParentProcessInstanceID": "$(ParentProcessInstanceID)",
             "IsOpenActivity": "0", "StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"},
     defect="Child-task branch ignores @IsOpenActivity, @StartDate and @EndDate.")
case("TC043", "ChildElementTasks", "IsChildElementTasks = 1, ParentProcessInstanceID = -1", "Negative", "Medium",
     SAME_AS_BASELINE + " (-1 is not > 0, so the user/role path runs).",
     params={"IsChildElementTasks": "1", "ParentProcessInstanceID": "-1"})
case("TC044", "ChildElementTasks", "IsChildElementTasks = 1, non-existent parent", "Negative", "Medium",
     "No error. Sets (1), (2) and (4) are empty.",
     params={"IsChildElementTasks": "1", "ParentProcessInstanceID": "999999999999"})
case("TC045", "ChildElementTasks", "Valid parent but IsChildElementTasks = 0", "Boundary", "Medium",
     SAME_AS_BASELINE + ". ParentProcessInstanceID is ignored without the flag.",
     params={"ParentProcessInstanceID": "$(ParentProcessInstanceID)"})

# ---------------------------------------------------------------- Mobile
case("TC050", "IsMobileEnabled", "IsMobileEnabled = 1", "Positive", "Medium",
     "Subset of TC001: only processes whose SupportedClient attribute = 2.",
     params={"IsMobileEnabled": "1"})
case("TC051", "IsMobileEnabled", "IsMobileEnabled = 0", "Positive", "Medium",
     "Subset of TC001: SupportedClient <> 2. TC050 + TC051 processes = TC001 processes.",
     params={"IsMobileEnabled": "0"})

# ---------------------------------------------------------------- Persistent data
case("TC055", "IsPersistentDataRequired", "IsPersistentDataRequired = 1", "Positive", "High",
     "A 5th result set (persistent data) is returned and should hold the activities' app data. "
     "Currently it is always empty: AssociatedAppID is inserted as NULL into #ActivitiesTVP, so #ElementRootMap is empty.",
     params={"IsPersistentDataRequired": "1"},
     defect="Output 5 (persistent data) is always empty: #FilteredActivitiesTVP.AssociatedAppID is always NULL.")
case("TC056", "IsPersistentDataRequired", "IsPersistentDataRequired = 0", "Positive", "Low",
     SAME_AS_BASELINE + " (4 result sets).",
     params={"IsPersistentDataRequired": "0"})

# ---------------------------------------------------------------- Dates
case("TC060", "DateRange", "StartDate only", "Positive", "High",
     "Subset of TC001: activity StartDate BETWEEN $(StartDate) AND GETDATE().",
     params={"StartDate": "'$(StartDate)'"})
case("TC061", "DateRange", "EndDate only", "Negative", "High",
     SAME_AS_BASELINE + ": EndDate is only used when StartDate is set. "
     "A user filtering 'up to a date' gets no filtering.",
     params={"EndDate": "'$(EndDate)'"},
     defect="@EndDate is ignored when @StartDate is NULL.")
case("TC062", "DateRange", "StartDate and EndDate", "Positive", "High",
     "Activity StartDate BETWEEN $(StartDate) AND $(EndDate). Subset of TC060.",
     params={"StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"})
case("TC063", "DateRange", "StartDate later than EndDate", "Negative", "High",
     "No error. Sets (1), (2) and (4) are empty (BETWEEN with an inverted range matches nothing).",
     params={"StartDate": "'$(EndDate)'", "EndDate": "'$(StartDate)'"})
case("TC064", "DateRange", "StartDate = EndDate (date only, single day)", "Boundary", "High",
     "Should return activities started on that day. Actually returns only activities starting exactly at 00:00:00, "
     "because the DATETIME2 BETWEEN uses midnight as the end. If the application sends date-only values, "
     "same-day searches miss data.",
     params={"StartDate": "'$(StartDate)'", "EndDate": "'$(StartDate)'"},
     defect="Date-only @EndDate excludes the rest of that day (BETWEEN on DATETIME2 with a midnight upper bound).")
case("TC065", "DateRange", "StartDate in the future, EndDate NULL", "Boundary", "Medium",
     "No error. Empty: BETWEEN '2099-01-01' AND GETDATE() is an inverted range.",
     params={"StartDate": "'2099-01-01'"})
case("TC066", "DateRange", "Widest range (1900-01-01 to 9999-12-31)", "Boundary", "Medium",
     SAME_AS_BASELINE + ". No overflow.",
     params={"StartDate": "'1900-01-01'", "EndDate": "'9999-12-31'"})
case("TC067", "DateRange", "ProcessDateFilterAppliesTo = 2 with range", "Positive", "Medium",
     "Same rows as TC062: the parameter is not used ('TODO' in the code). Activity StartDate is always the filtered column.",
     params={"ProcessDateFilterAppliesTo": "2", "StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"},
     defect="@ProcessDateFilterAppliesTo is not implemented; every value filters on activity StartDate.")
case("TC068", "DateRange", "ProcessDateFilterAppliesTo = 99 (invalid) with range", "Negative", "Low",
     "Same rows as TC062. No validation.",
     params={"ProcessDateFilterAppliesTo": "99", "StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"})
case("TC069", "DateRange", "ProcessDateFilterAppliesTo = NULL with range", "Boundary", "Low",
     "Same rows as TC062.",
     params={"ProcessDateFilterAppliesTo": "NULL", "StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"})

# ---------------------------------------------------------------- Status (not implemented)
case("TC070", "ProcessStatus", "@ProcessStatus with one value", "Positive", "Medium",
     SAME_AS_BASELINE + ": @ProcessStatus is not used (the code says the SLA check is done in C#).",
     tvps={"ProcessStatus": ["$(StatusValue)"]},
     defect="@ProcessStatus is accepted but ignored.")
case("TC071", "ProcessStatus", "@ProcessStatus with non-existent value (-1)", "Negative", "Low",
     SAME_AS_BASELINE + " (parameter ignored).", tvps={"ProcessStatus": ["-1"]})

# ---------------------------------------------------------------- Triggers / types / priorities
case("TC075", "ProcessTriggers", "@ProcessTriggers with one value", "Positive", "High",
     "Subset of TC001: processes with TriggerSource = $(TriggerValue), plus processes whose TriggerSource is NULL.",
     tvps={"ProcessTriggers": ["$(TriggerValue)"]})
case("TC076", "ProcessTriggers", "@ProcessTriggers with two values", "Positive", "Medium",
     "TriggerSource IN ($(TriggerValue), $(AltTriggerValue)) or NULL. Rows >= TC075.",
     tvps={"ProcessTriggers": ["$(TriggerValue)", "$(AltTriggerValue)"]})
case("TC077", "ProcessTriggers", "@ProcessTriggers with non-existent value (-1)", "Negative", "High",
     "Not zero rows: processes with a NULL TriggerSource always pass the filter. Confirm that NULL should be included.",
     tvps={"ProcessTriggers": ["-1"]},
     defect="Rows with NULL TriggerSource / ProcessType / ProcessPriority always pass those filters.")
case("TC080", "ProcessTypes", "@ProcessTypes with one value", "Positive", "High",
     "Subset of TC001: ProcessType = $(TypeValue) (from ProcessActionParameters, else the process attribute), "
     "or ProcessType NULL, or the tag-mapped type (see TC083).",
     tvps={"ProcessTypes": ["$(TypeValue)"]})
case("TC081", "ProcessTypes", "@ProcessTypes with two values", "Positive", "Medium",
     "ProcessType IN ($(TypeValue), $(AltTypeValue)) or NULL. Rows >= TC080.",
     tvps={"ProcessTypes": ["$(TypeValue)", "$(AltTypeValue)"]})
case("TC082", "ProcessTypes", "@ProcessTypes with non-existent value (-1)", "Negative", "High",
     "Only processes whose ProcessType is NULL (often zero rows, because ProcessType comes from a mandatory attribute).",
     tvps={"ProcessTypes": ["-1"]})
case("TC083", "ProcessTypes", "@ProcessTypes = 5244 (FixRequest tag mapping)", "Positive", "Medium",
     "Includes processes with ProcessType > 20 whose process element carries tag 'FixRequest' (ElementTypeID 6263). "
     "Repeat with 5239, 5238, 5243 and 5242 for InvestigationRequest, OSW, IntegratedAssurance and IAPowerStation.",
     tvps={"ProcessTypes": ["5244"]})
case("TC085", "ProcessPriorities", "@ProcessPriorities with one value", "Positive", "High",
     "Subset of TC001: ProcessPriority = $(PriorityValue), or NULL.",
     tvps={"ProcessPriorities": ["$(PriorityValue)"]})
case("TC086", "ProcessPriorities", "@ProcessPriorities with two values", "Positive", "Medium",
     "ProcessPriority IN ($(PriorityValue), $(AltPriorityValue)) or NULL. Rows >= TC085.",
     tvps={"ProcessPriorities": ["$(PriorityValue)", "$(AltPriorityValue)"]})
case("TC087", "ProcessPriorities", "@ProcessPriorities with non-existent value (-1)", "Negative", "Medium",
     "Only processes whose ProcessPriority is NULL (often zero rows).",
     tvps={"ProcessPriorities": ["-1"]})
case("TC090", "FilterValues", "Omit all four filter-value TVP parameters", "Positive", "Medium",
     SAME_AS_BASELINE + " (omitted TVPs default to empty).",
     omit=("ProcessStatus", "ProcessPriorities", "ProcessTypes", "ProcessTriggers"))

# ---------------------------------------------------------------- User / role security
case("TC100", "Security", "Non-existent UserID (999999999)", "Security", "High",
     "No error. Sets (1), (2) and (4) are empty: no role assignments and no activities executed by that user.",
     params={"UserID": "999999999"})
case("TC101", "Security", "UserID = NULL", "Security", "High",
     "No error. Sets (1), (2) and (4) are empty.",
     params={"UserID": "NULL"})
case("TC102", "Security", "UserID = 0", "Security", "Medium",
     "No error. Sets (1), (2) and (4) are empty.",
     params={"UserID": "0"})
case("TC103", "Security", "Non-existent RoleID with ProcessTitle = 1", "Security", "High",
     SAME_AS_BASELINE + ": with ProcessTitle = 1 the procedure uses every role the user holds and ignores @RoleID "
     "(it is used only for SupportedElementTypes when ProcessTitle > 1, and for the time log). "
     "Confirm that 'My Tasks' should not be scoped to the selected role.",
     params={"RoleID": "-1"},
     defect="@RoleID is ignored for ProcessTitle = 1; tasks are not scoped to the selected role.")
case("TC104", "Security", "RoleID = NULL with ProcessTitle = 1", "Security", "Medium",
     SAME_AS_BASELINE + ".", params={"RoleID": "NULL"})
case("TC105", "Security", "Different (non-admin) user and role", "Security", "High",
     "Only $(OtherUserID)'s tasks. No activity from TC001 that belongs only to 285 appears. "
     "Note: 285 is hard-coded as 'Nibras Admin' in CreatedUserName and ExecutorName.",
     params={"UserID": "$(OtherUserID)", "RoleID": "$(OtherUserRoleID)"})
case("TC106", "Security", "RoleID = -1 with ProcessTitle = 2", "Security", "Medium",
     "No error. No SupportedElementTypes are found, so it falls back to the user's group roles. Same as TC005 when "
     "role 346314 has no SupportedElementTypes attribute.",
     params={"RoleID": "-1", "ProcessTitle": "2"})
case("TC107", "Mandatory", "Omit @UserID", "Negative", "Medium",
     "Error 201: 'expects parameter @UserID, which was not supplied' (no default).",
     expect="ERROR", omit=("UserID",))
case("TC108", "Mandatory", "Omit @ProcessTitle", "Negative", "Medium",
     "Error 201: 'expects parameter @ProcessTitle' (no default).",
     expect="ERROR", omit=("ProcessTitle",))

# ---------------------------------------------------------------- Debug / time log
case("TC110", "Diagnostics", "IsDebug = 1", "Positive", "Low",
     "Business result sets match TC001. Extra debug result sets (labelled '----------#...----------') appear in between.",
     params={"IsDebug": "1"})
case("TC111", "Diagnostics", "EnableTimeLog = 1 writes NF.ProcedureTimeLog", "Positive", "Medium",
     "Result sets match TC001, and rows are inserted into NF.ProcedureTimeLog (the harness checks this, then rolls back).",
     params={"EnableTimeLog": "1"},
     pre_sql="DECLARE @logBefore int = (SELECT COUNT(*) FROM NF.ProcedureTimeLog);",
     post_sql="IF (SELECT COUNT(*) FROM NF.ProcedureTimeLog) <= @logBefore\n"
              "        THROW 50001, 'No rows were written to NF.ProcedureTimeLog', 1;")
case("TC112", "Diagnostics", "IsDebug = 1 and EnableTimeLog = 1", "Positive", "Low",
     "Like TC110, plus a final #TimeLog result set listing the step timings.",
     params={"IsDebug": "1", "EnableTimeLog": "1"})

# ---------------------------------------------------------------- Combinations
case("TC120", "Combination", "All filters applied together", "Positive", "High",
     "Rows satisfy every filter. A subset of TC062, TC050, TC075, TC080 and TC085.",
     params={"StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'", "IsMobileEnabled": "1"},
     tvps={"ProcessPriorities": ["$(PriorityValue)"], "ProcessTypes": ["$(TypeValue)"],
           "ProcessTriggers": ["$(TriggerValue)"]})
case("TC121", "Combination", "All nullable scalar parameters NULL", "Boundary", "Medium",
     "No error. Sets (1), (2) and (4) are empty (UserID NULL).",
     params={k: "NULL" for k in BASELINE_PARAMS})

# ---------------------------------------------------------------- Performance
case("TC130", "Performance", "Baseline call within time budget", "Performance", "High",
     "Completes within $(MaxDurationMs) ms on a warm cache.", max_ms="$(MaxDurationMs)")
case("TC131", "Performance", "@FilterTags with 500 rows", "Performance", "Medium",
     "No error. Completes within $(MaxDurationMs) ms.",
     tags="LOOP500", max_ms="$(MaxDurationMs)")
case("TC132", "Performance", "Largest result: ProcessTitle 2, open and closed", "Performance", "Medium",
     "Completes within $(MaxDurationMs) ms with the largest realistic result set.",
     params={"ProcessTitle": "2", "IsOpenActivity": "NULL"}, max_ms="$(MaxDurationMs)")


# ======================================================================== render
def describe_tag(t):
    if not t:
        return "BSP"
    return "BSP{" + ", ".join(f"{k}={v}" for k, v in t.items()) + "}"


def describe_inputs(c):
    parts = [f"@{k}={v}" for k, v in c["params"].items()]
    if c["tags"] == "LOOP500":
        parts.append("@FilterTags=500 generated rows")
    elif c["tags"] is not None:
        parts.append("@FilterTags=" + (" + ".join(describe_tag(t) for t in c["tags"]) or "<empty>"))
    for k, v in c["tvps"].items():
        parts.append(f"@{k}=[{', '.join(v)}]")
    for k in c["omit"]:
        parts.append(f"@{k} omitted")
    return "; ".join(parts) or "Baseline values"


def tag_inserts(tags):
    if tags == "LOOP500":
        return [
            "    DECLARE @tag Tag.TagModelTVP, @i int = 0;",
            f"    INSERT INTO @tag VALUES ({BASELINE_TAG_ROW});",
            "    WHILE @i < 500",
            "    BEGIN",
            "        UPDATE @tag SET ObjectID = 366713 + @i, TagName = CONCAT(N'PERF_', @i);",
            "        INSERT INTO @p2 SELECT * FROM @tag;",
            "        SET @i += 1;",
            "    END",
        ]
    lines = []
    if any(tags):
        lines.append("    DECLARE @tag Tag.TagModelTVP;")
    for t in tags:
        if not t:
            lines.append(f"    INSERT INTO @p2 VALUES ({BASELINE_TAG_ROW});")
        else:
            sets = ", ".join(f"{k} = {v}" for k, v in t.items())
            lines += [
                "    DELETE FROM @tag;",
                f"    INSERT INTO @tag VALUES ({BASELINE_TAG_ROW});",
                f"    UPDATE @tag SET {sets};",
                "    INSERT INTO @p2 SELECT * FROM @tag;",
            ]
    return lines


def sql_case(c):
    q = lambda s: s.replace("'", "''")
    lines = [
        f"-- {'=' * 74}",
        f"-- {c['id']} | {c['category']} | {c['title']}",
        f"-- Expected: {c['expected']}",
    ]
    if c["defect"]:
        lines.append(f"-- Suspected defect: {c['defect']}")
    lines += [
        f"-- {'=' * 74}",
        f"PRINT '>> {c['id']} - {q(c['title'])}';",
        f"SELECT '{c['id']}' AS TestCase, '{q(c['title'])}' AS Title;",
        "DECLARE @t0 datetime2 = SYSDATETIME();",
        "BEGIN TRY",
    ]
    for name, (var, typ) in TVPS.items():
        if name in c["omit"]:
            continue
        lines.append(f"    DECLARE {var} {typ};")
        if name == "FilterTags":
            lines += tag_inserts([BASE_TAG] if c["tags"] is None else c["tags"])
        else:
            for v in c["tvps"].get(name, []):
                lines.append(f"    INSERT INTO {var} (Value) VALUES ({v});")
    lines.append("    BEGIN TRAN;")
    if c["pre_sql"]:
        lines.append("    " + c["pre_sql"])
    lines.append("    SET @t0 = SYSDATETIME();")
    values = {**BASELINE_PARAMS, **c["params"]}
    args = []
    for p in PARAM_ORDER:
        if p in c["omit"] or (p not in values and p not in TVPS):
            continue
        args.append(f"@{p}={TVPS[p][0] if p in TVPS else values[p]}")
    lines.append("    EXEC [WorkFlow].[uspGetProcessActivities]")
    lines.append("         " + "\n        ,".join(args) + ";")
    lines.append("    DECLARE @ms int = DATEDIFF(ms, @t0, SYSDATETIME());")
    if c["post_sql"]:
        lines.append("    " + c["post_sql"])
    insert = ("    INSERT INTO #TestResults (TestCase, Title, Expectation, Outcome, DurationMs, MaxDurationMs, "
              "ErrorNumber, ErrorMessage)")
    lines += [
        "    IF @@TRANCOUNT > 0 ROLLBACK TRAN;",
        insert,
        f"    VALUES ('{c['id']}', '{q(c['title'])}', '{c['expect']}', 'SUCCESS', @ms, {c['max_ms'] or 'NULL'}, NULL, NULL);",
        "END TRY",
        "BEGIN CATCH",
        "    IF @@TRANCOUNT > 0 ROLLBACK TRAN;",
        insert,
        f"    VALUES ('{c['id']}', '{q(c['title'])}', '{c['expect']}', 'ERROR', DATEDIFF(ms, @t0, SYSDATETIME()), "
        f"{c['max_ms'] or 'NULL'}, ERROR_NUMBER(), ERROR_MESSAGE());",
        "END CATCH",
        "GO",
        "",
    ]
    return "\n".join(lines)


SQL_HEADER = """/*
    Test harness for [WorkFlow].[uspGetProcessActivities]
    GENERATED by generate_test_cases.py. Edit the generator, not this file.

    HOW TO RUN
      1. Open in SSMS and enable Query > SQLCMD Mode (or run with sqlcmd -i).
      2. Set the :setvar values below to real values from your test database
         (see "Finding test values" in README.md).
      3. Execute. Every call runs inside BEGIN TRAN / ROLLBACK, so no data is changed.
      4. The last two result sets are the summary. Each case's output follows its
         "TestCase | Title" grid; compare it with the Expected text in TestCases.md.
*/

-- ---- Environment-specific test data (edit these) -------------------------
:setvar AltTagName               "BSP2"
:setvar AltTagObjectID           366714
:setvar ProcessName              "Process A"
:setvar AltProcessName           "Process B"
:setvar StatusValue              1
:setvar PriorityValue            1
:setvar AltPriorityValue         2
:setvar TypeValue                1
:setvar AltTypeValue             2
:setvar TriggerValue             1
:setvar AltTriggerValue          2
:setvar OtherUserID              286
:setvar OtherUserRoleID          346315
:setvar ParentProcessInstanceID  1
:setvar StartDate                2026-01-01
:setvar EndDate                  2026-12-31
:setvar MaxDurationMs            5000
-- -------------------------------------------------------------------------

SET NOCOUNT ON;
SET XACT_ABORT OFF;
GO

IF OBJECT_ID('tempdb..#TestResults') IS NOT NULL DROP TABLE #TestResults;
CREATE TABLE #TestResults (
    TestCase      varchar(10)    NOT NULL,
    Title         nvarchar(200)  NOT NULL,
    Expectation   varchar(10)    NOT NULL,
    Outcome       varchar(10)    NOT NULL,
    DurationMs    int            NULL,
    MaxDurationMs int            NULL,
    ErrorNumber   int            NULL,
    ErrorMessage  nvarchar(4000) NULL
);
GO

"""

VERDICT = """CASE
            WHEN {p}MaxDurationMs IS NOT NULL AND {p}DurationMs > {p}MaxDurationMs THEN 'FAIL (slow)'
            WHEN {p}Expectation = 'SUCCESS' AND {p}Outcome = 'SUCCESS'            THEN 'PASS*'
            WHEN {p}Expectation = 'ERROR'   AND {p}Outcome = 'ERROR'              THEN 'PASS'
            WHEN {p}Expectation = 'DEFECT'  AND {p}Outcome = 'ERROR'              THEN 'DEFECT REPRODUCED'
            WHEN {p}Expectation = 'DEFECT'  AND {p}Outcome = 'SUCCESS'            THEN 'DEFECT FIXED?'
            WHEN {p}Expectation = 'ANY'                                           THEN 'REVIEW'
            ELSE 'FAIL'
        END"""

SQL_FOOTER = f"""-- ==========================================================================
-- Summary
-- ==========================================================================
SELECT  TestCase,
        Title,
        Expectation,
        Outcome,
        DurationMs,
        MaxDurationMs,
        {VERDICT.format(p='')} AS Verdict,
        ErrorNumber,
        ErrorMessage
FROM    #TestResults
ORDER BY TestCase;

SELECT  Verdict = v.Verdict, Cases = COUNT(*)
FROM    #TestResults r
CROSS APPLY (SELECT {VERDICT.format(p='r.')}) v(Verdict)
GROUP BY v.Verdict;
GO
"""


def main():
    with open(os.path.join(HERE, "01_Run_TestCases.sql"), "w", newline="\n") as f:
        f.write(SQL_HEADER)
        for c in CASES:
            f.write(sql_case(c))
        f.write(SQL_FOOTER)

    headers = ["Test Case ID", "Category", "Title", "Type", "Priority", "Preconditions",
               "Input (changes from baseline)", "Expected Result", "Suspected Defect",
               "Harness Expectation", "Actual Result", "Status"]
    rows = [[c["id"], c["category"], c["title"], c["kind"], c["priority"], c["preconditions"],
             describe_inputs(c), c["expected"], c["defect"] or "", c["expect"], "", ""] for c in CASES]

    with open(os.path.join(HERE, "TestCases.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)

    cell = lambda s: s.replace("|", "\\|")
    defects = [c for c in CASES if c["defect"]]
    md = ["# Test Cases: `[WorkFlow].[uspGetProcessActivities]`", "",
          "_Generated by `generate_test_cases.py`. Edit the generator, then re-run it._", "",
          f"Total cases: **{len(CASES)}**. Suspected defects or behaviours to confirm: **{len(defects)}**.", "",
          "Inputs list only the parameters that differ from the baseline call (TC001). "
          "`$(Name)` values are SQLCMD variables set at the top of `01_Run_TestCases.sql`. "
          "Result sets: (1) process instances, (2) activity instances, (3) a single NULL row, "
          "(4) SLA, (5) persistent data (only when IsPersistentDataRequired = 1).", "",
          "## Suspected defects / behaviours to confirm", "",
          "| Case | Finding |", "|------|---------|"]
    md += [f"| {c['id']} | {cell(c['defect'])} |" for c in defects]
    category = None
    for c, r in zip(CASES, rows):
        if c["category"] != category:
            category = c["category"]
            md += ["", f"## {category}", "",
                   "| ID | Title | Type | Priority | Input | Expected Result |",
                   "|----|-------|------|----------|-------|-----------------|"]
        flag = " ⚠" if c["defect"] else ""
        md.append(f"| {c['id']}{flag} | {cell(c['title'])} | {c['kind']} | {c['priority']} | "
                  f"`{cell(r[6])}` | {cell(c['expected'])} |")
    with open(os.path.join(HERE, "TestCases.md"), "w", newline="\n") as f:
        f.write("\n".join(md) + "\n")

    print(f"Generated {len(CASES)} test cases ({len(defects)} with suspected defects).")


if __name__ == "__main__":
    main()
