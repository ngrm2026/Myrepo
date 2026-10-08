"""Generate test case artifacts for [WorkFlow].[uspGetProcessActivities].

Single source of truth for the test cases. Running this script regenerates:
  - TestCases.md          human-readable test case catalogue
  - TestCases.csv         same catalogue, for Excel / test management tools
  - 01_Run_TestCases.sql  SQLCMD-mode T-SQL harness that executes every case

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

# Order in which parameters appear in the original call.
PARAM_ORDER = [
    "EndDate", "FilterTags", "IsMobileEnabled", "IsOpenActivity",
    "IsChildElementTasks", "ProcessTitle", "IsPersistentDataRequired",
    "ProcessDateFilterAppliesTo", "ProcessStatus", "ProcessPriorities",
    "IsReferenceElementTasks", "StartDate", "ProcessTypes", "ProcessTriggers",
    "UserID", "RoleID", "ParentProcessInstanceID",
]

# TVP parameter -> (variable, type)
TVPS = {
    "FilterTags": ("@p2", "Tag.TagModelTVP"),
    "ProcessStatus": ("@p9", "WorkFlow.ProcessActivityFilterValueTVP"),
    "ProcessPriorities": ("@p10", "WorkFlow.ProcessActivityFilterValueTVP"),
    "ProcessTypes": ("@p13", "WorkFlow.ProcessActivityFilterValueTVP"),
    "ProcessTriggers": ("@p14", "WorkFlow.ProcessActivityFilterValueTVP"),
}

ALT_TAG_ROW = BASELINE_TAG_ROW.replace("6737,", "$(AltTagID),", 1)
MISSING_TAG_ROW = BASELINE_TAG_ROW.replace("6737,", "-1,", 1)

# Expectation codes used by the harness:
#   SUCCESS - procedure must execute without error
#   ERROR   - procedure must raise an error
#   ANY     - either outcome is acceptable; verify behaviour manually
CASES = []


def case(tc_id, category, title, kind, priority, expected, expect="SUCCESS",
         params=None, tvps=None, omit=(), max_ms=None, preconditions="Baseline data exists (see README)."):
    CASES.append(dict(
        id=tc_id, category=category, title=title, kind=kind, priority=priority,
        expected=expected, expect=expect, params=params or {}, tvps=tvps or {},
        omit=tuple(omit), max_ms=max_ms, preconditions=preconditions,
    ))


# ---------------------------------------------------------------- Baseline
case("TC001", "Baseline", "Execute baseline call exactly as captured", "Positive", "High",
     "Executes without error. Returns open (IsOpenActivity=1) activities tagged with tag 6737 (BSP) "
     "that user 285 / role 346314 can see, excluding child and reference element tasks. "
     "Record the row count; later cases compare against it.")
case("TC002", "Baseline", "Re-execute baseline call (repeatability)", "Positive", "Medium",
     "Same rows, same column set, and same order as TC001. Proves the result is deterministic.")

# ---------------------------------------------------------------- Filter tags
case("TC010", "FilterTags", "Empty @FilterTags TVP", "Boundary", "High",
     "No error. Either no tag filter is applied (rows >= TC001) or zero rows are returned; "
     "confirm which behaviour is intended against the procedure definition.",
     tvps={"FilterTags": []})
case("TC011", "FilterTags", "Two tags in @FilterTags", "Positive", "High",
     "Rows for tag 6737 OR tag $(AltTagID). Row count >= TC001. No duplicate activity rows.",
     tvps={"FilterTags": [BASELINE_TAG_ROW, ALT_TAG_ROW]})
case("TC012", "FilterTags", "Non-existent tag ID (-1)", "Negative", "High",
     "No error, zero rows.", tvps={"FilterTags": [MISSING_TAG_ROW]})
case("TC013", "FilterTags", "Same tag supplied twice", "Boundary", "Medium", expect="ANY", expected=
     "Identical to TC001. Activities are not duplicated by the repeated tag. "
     "(If the TVP has a primary key, the duplicate INSERT fails; that is also acceptable.)",
     tvps={"FilterTags": [BASELINE_TAG_ROW, BASELINE_TAG_ROW]})

# ---------------------------------------------------------------- Open activity
case("TC020", "IsOpenActivity", "IsOpenActivity = 0", "Positive", "High",
     "Returns closed/completed activities only (or all activities, per the definition). "
     "No activity is in both the TC001 and TC020 results if 0 means closed.",
     params={"IsOpenActivity": "0"})
case("TC021", "IsOpenActivity", "IsOpenActivity = NULL", "Boundary", "Medium",
     "No error. Expected: open and closed activities (row count >= TC001).",
     params={"IsOpenActivity": "NULL"})

# ---------------------------------------------------------------- Child / reference tasks
case("TC030", "ElementTasks", "IsChildElementTasks = 1", "Positive", "High",
     "Child element tasks are included. Row count >= TC001.",
     params={"IsChildElementTasks": "1"})
case("TC031", "ElementTasks", "IsReferenceElementTasks = 1", "Positive", "High",
     "Reference element tasks are included. Row count >= TC001.",
     params={"IsReferenceElementTasks": "1"})
case("TC032", "ElementTasks", "IsChildElementTasks = 1 and IsReferenceElementTasks = 1", "Positive", "Medium",
     "Child and reference tasks are both included. Rows >= max(TC030, TC031). No duplicates.",
     params={"IsChildElementTasks": "1", "IsReferenceElementTasks": "1"})
case("TC033", "ElementTasks", "IsChildElementTasks = NULL and IsReferenceElementTasks = NULL", "Boundary", "Low",
     "No error. Behaves the same as 0, or as the defaults documented in the procedure.",
     params={"IsChildElementTasks": "NULL", "IsReferenceElementTasks": "NULL"})

# ---------------------------------------------------------------- Mobile
case("TC040", "IsMobileEnabled", "IsMobileEnabled = 1", "Positive", "Medium",
     "Only activities whose process is mobile-enabled. Subset of TC001.",
     params={"IsMobileEnabled": "1"})
case("TC041", "IsMobileEnabled", "IsMobileEnabled = 0", "Positive", "Medium",
     "Only activities that are not mobile-enabled (or no filter). TC040 + TC041 should equal TC001.",
     params={"IsMobileEnabled": "0"})

# ---------------------------------------------------------------- Persistent data
case("TC045", "IsPersistentDataRequired", "IsPersistentDataRequired = 1", "Positive", "Medium",
     "Persistent data columns or result set are returned and populated. Activity rows match TC001.",
     params={"IsPersistentDataRequired": "1"})
case("TC046", "IsPersistentDataRequired", "IsPersistentDataRequired = 0", "Positive", "Low",
     "Same as TC001 (NULL and 0 behave the same).",
     params={"IsPersistentDataRequired": "0"})

# ---------------------------------------------------------------- Process title
case("TC050", "ProcessTitle", "ProcessTitle = 0", "Positive", "Medium",
     "No error. Process title column or result set is omitted or changed per the definition. "
     "Activity rows match TC001.",
     params={"ProcessTitle": "0"})
case("TC051", "ProcessTitle", "ProcessTitle = NULL", "Boundary", "Low",
     "No error. Behaves the same as 0 or as the default.",
     params={"ProcessTitle": "NULL"})

# ---------------------------------------------------------------- Dates
case("TC060", "DateRange", "StartDate only", "Positive", "High",
     "Only activities whose date (per ProcessDateFilterAppliesTo=1) is on or after $(StartDate).",
     params={"StartDate": "'$(StartDate)'"})
case("TC061", "DateRange", "EndDate only", "Positive", "High",
     "Only activities whose date is on or before $(EndDate).",
     params={"EndDate": "'$(EndDate)'"})
case("TC062", "DateRange", "StartDate and EndDate (valid range)", "Positive", "High",
     "Only activities within [$(StartDate), $(EndDate)]. This is the intersection of TC060 and TC061.",
     params={"StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"})
case("TC063", "DateRange", "StartDate later than EndDate", "Negative", "High",
     "No error, zero rows (or a meaningful validation error if the procedure validates the range).",
     expect="ANY", params={"StartDate": "'$(EndDate)'", "EndDate": "'$(StartDate)'"})
case("TC064", "DateRange", "StartDate = EndDate (single day)", "Boundary", "High",
     "Includes activities at any time on that day. Watch for a time-portion bug where EndDate "
     "midnight excludes the rest of the day.",
     params={"StartDate": "'$(StartDate)'", "EndDate": "'$(StartDate)'"})
case("TC065", "DateRange", "Widest range (1900-01-01 to 9999-12-31)", "Boundary", "Medium",
     "No overflow error. Same rows as TC001.",
     params={"StartDate": "'1900-01-01'", "EndDate": "'9999-12-31'"})
case("TC066", "DateRange", "ProcessDateFilterAppliesTo = 2 with date range", "Positive", "Medium",
     "The date range is applied to the alternative date column (e.g. due date instead of start date).",
     params={"ProcessDateFilterAppliesTo": "2", "StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"})
case("TC067", "DateRange", "ProcessDateFilterAppliesTo = 0 with date range", "Boundary", "Low",
     "No error. Either the date filter is ignored or a defined default applies.",
     params={"ProcessDateFilterAppliesTo": "0", "StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"})
case("TC068", "DateRange", "ProcessDateFilterAppliesTo = NULL with date range", "Boundary", "Low",
     "No error. Either the date filter is ignored or a defined default applies.",
     params={"ProcessDateFilterAppliesTo": "NULL", "StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"})
case("TC069", "DateRange", "ProcessDateFilterAppliesTo = 99 (invalid)", "Negative", "Medium",
     "Either a handled validation error or zero rows / no date filter. Must not be an unhandled crash.",
     expect="ANY", params={"ProcessDateFilterAppliesTo": "99", "StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'"})

# ---------------------------------------------------------------- Filter-value TVPs
for base, (name, valid, label) in enumerate([
        ("ProcessStatus", "$(StatusValue)", "status"),
        ("ProcessPriorities", "$(PriorityValue)", "priority"),
        ("ProcessTypes", "$(TypeValue)", "type"),
        ("ProcessTriggers", "$(TriggerValue)", "trigger")]):
    n = 70 + base * 5
    case(f"TC{n:03d}", name, f"@{name} with one valid value", "Positive", "High",
         f"Only activities whose process {label} = {valid}. Subset of TC001.",
         tvps={name: [valid]})
    case(f"TC{n + 1:03d}", name, f"@{name} with two values", "Positive", "Medium",
         f"Activities with {label} {valid} OR $(Alt{label.capitalize()}Value). Rows >= TC{n:03d}.",
         tvps={name: [valid, f"$(Alt{label.capitalize()}Value)"]})
    case(f"TC{n + 2:03d}", name, f"@{name} with non-existent value (-1)", "Negative", "High",
         "No error, zero rows.", tvps={name: ["-1"]})

case("TC090", "FilterValues", "Omit all four filter-value TVP parameters", "Positive", "Medium",
     "Omitted TVPs default to empty, so the result equals TC001.",
     omit=("ProcessStatus", "ProcessPriorities", "ProcessTypes", "ProcessTriggers"))

# ---------------------------------------------------------------- User / role security
case("TC100", "Security", "Non-existent UserID (999999999)", "Negative", "High",
     "No error, zero rows. Must not leak other users' activities.",
     params={"UserID": "999999999"})
case("TC101", "Security", "UserID = NULL", "Negative", "High",
     "Zero rows or a handled validation error. Must never return every user's activities.",
     expect="ANY", params={"UserID": "NULL"})
case("TC102", "Security", "UserID = 0", "Negative", "Medium",
     "No error, zero rows.", params={"UserID": "0"})
case("TC103", "Security", "Non-existent RoleID (-1)", "Negative", "High",
     "No error. Zero rows, or only activities assigned directly to the user rather than a role.",
     params={"RoleID": "-1"})
case("TC104", "Security", "RoleID = NULL", "Negative", "Medium",
     "Zero rows or user-only activities, or a handled validation error.",
     expect="ANY", params={"RoleID": "NULL"})
case("TC105", "Security", "Valid role the user is NOT a member of", "Negative", "High",
     "Must not return the role's activities to user 285 (authorisation check).",
     params={"RoleID": "$(OtherRoleID)"})
case("TC106", "Security", "Omit @UserID", "Negative", "Medium",
     "Error 201 ('expects parameter @UserID') if the parameter has no default; otherwise the documented default.",
     expect="ANY", omit=("UserID",))

# ---------------------------------------------------------------- Parent process instance
case("TC110", "ParentProcess", "Valid ParentProcessInstanceID", "Positive", "High",
     "Only activities of child processes of instance $(ParentProcessInstanceID).",
     params={"ParentProcessInstanceID": "$(ParentProcessInstanceID)"})
case("TC111", "ParentProcess", "Non-existent ParentProcessInstanceID (-1)", "Negative", "Medium",
     "No error, zero rows.", params={"ParentProcessInstanceID": "-1"})
case("TC112", "ParentProcess", "ParentProcessInstanceID = NULL", "Boundary", "Medium",
     "No error. Same as 0 (no parent filter).",
     params={"ParentProcessInstanceID": "NULL"})

# ---------------------------------------------------------------- Combinations
case("TC120", "Combination", "All filters applied together", "Positive", "High",
     "Rows satisfy every filter at once. This is a subset of each single-filter case "
     "(TC060-TC062, TC070, TC075, TC080, TC085).",
     params={"StartDate": "'$(StartDate)'", "EndDate": "'$(EndDate)'", "IsMobileEnabled": "1",
             "IsPersistentDataRequired": "1"},
     tvps={"ProcessStatus": ["$(StatusValue)"], "ProcessPriorities": ["$(PriorityValue)"],
           "ProcessTypes": ["$(TypeValue)"], "ProcessTriggers": ["$(TriggerValue)"]})
case("TC121", "Combination", "All optional bit flags = 1", "Positive", "Medium",
     "No error. Includes child and reference tasks, mobile-enabled only, with persistent data.",
     params={"IsMobileEnabled": "1", "IsChildElementTasks": "1", "IsReferenceElementTasks": "1",
             "IsPersistentDataRequired": "1", "ProcessTitle": "1"})
case("TC122", "Combination", "All nullable parameters NULL", "Boundary", "Medium",
     "Zero rows or a handled validation error. No unhandled error and no unfiltered data leak.",
     expect="ANY",
     params={k: "NULL" for k in BASELINE_PARAMS})

# ---------------------------------------------------------------- Performance
case("TC130", "Performance", "Baseline call within time budget", "Performance", "High",
     "Completes within $(MaxDurationMs) ms on a warm cache.", max_ms="$(MaxDurationMs)")
case("TC131", "Performance", "@FilterTags with 500 rows", "Performance", "Medium",
     "No error. Completes within $(MaxDurationMs) ms. No tempdb spill or plan regression.",
     tvps={"FilterTags": "LOOP500"}, max_ms="$(MaxDurationMs)")
case("TC132", "Performance", "Widest date range with child + reference tasks", "Performance", "Medium",
     "Completes within $(MaxDurationMs) ms with the largest realistic result set.",
     params={"StartDate": "'1900-01-01'", "EndDate": "'9999-12-31'", "IsOpenActivity": "NULL",
             "IsChildElementTasks": "1", "IsReferenceElementTasks": "1"},
     max_ms="$(MaxDurationMs)")


# ======================================================================== render
def describe_inputs(c):
    parts = [f"@{k}={v}" for k, v in c["params"].items()]
    for k, v in c["tvps"].items():
        if v == "LOOP500":
            parts.append(f"@{k}=500 generated rows")
        elif not v:
            parts.append(f"@{k}=<empty>")
        elif k == "FilterTags":
            parts.append(f"@{k}=" + " + ".join(r.split(",", 1)[0] for r in v))
        else:
            parts.append(f"@{k}=[{', '.join(v)}]")
    for k in c["omit"]:
        parts.append(f"@{k} omitted")
    return "; ".join(parts) or "Baseline values"


def sql_case(c):
    q = lambda s: s.replace("'", "''")
    lines = [
        f"-- {'=' * 74}",
        f"-- {c['id']} | {c['category']} | {c['title']}",
        f"-- Expected: {c['expected']}",
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
        rows = c["tvps"].get(name, [BASELINE_TAG_ROW] if name == "FilterTags" else [])
        if rows == "LOOP500":
            rest = BASELINE_TAG_ROW.split(",", 1)[1]
            lines += [
                "    DECLARE @i int = 0;",
                "    WHILE @i < 500",
                "    BEGIN",
                f"        INSERT INTO {var} VALUES (6737 + @i,{rest});",
                "        SET @i += 1;",
                "    END",
            ]
        else:
            for r in rows:
                lines.append(f"    INSERT INTO {var} VALUES ({r});")
    lines += ["    SET @t0 = SYSDATETIME();", "    BEGIN TRAN;"]
    values = {**BASELINE_PARAMS, **c["params"]}
    args = []
    for p in PARAM_ORDER:
        if p in c["omit"]:
            continue
        args.append(f"@{p}={TVPS[p][0] if p in TVPS else values[p]}")
    lines.append("    EXEC [WorkFlow].[uspGetProcessActivities]")
    lines.append("         " + "\n        ,".join(args) + ";")
    lines += [
        "    IF @@TRANCOUNT > 0 ROLLBACK TRAN;",
        f"    INSERT INTO #TestResults (TestCase, Title, Expectation, Outcome, DurationMs, MaxDurationMs, ErrorNumber, ErrorMessage)",
        f"    VALUES ('{c['id']}', '{q(c['title'])}', '{c['expect']}', 'SUCCESS', DATEDIFF(ms, @t0, SYSDATETIME()), "
        f"{c['max_ms'] or 'NULL'}, NULL, NULL);",
        "END TRY",
        "BEGIN CATCH",
        "    IF @@TRANCOUNT > 0 ROLLBACK TRAN;",
        f"    INSERT INTO #TestResults (TestCase, Title, Expectation, Outcome, DurationMs, MaxDurationMs, ErrorNumber, ErrorMessage)",
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
      2. Set the :setvar values below to real IDs from your test database.
         Run 00_Discover_Metadata.sql first to find them.
      3. Execute. Every call runs inside BEGIN TRAN / ROLLBACK, so no data is changed.
      4. The final result set is the PASS/FAIL summary. The result grids above it
         hold each case's output; compare them against the "Expected" text in
         TestCases.md (PASS* = executed as expected, data still needs a manual check).
*/

-- ---- Environment-specific test data (edit these) -------------------------
:setvar AltTagID                 6738
:setvar StatusValue              1
:setvar AltStatusValue           2
:setvar PriorityValue            1
:setvar AltPriorityValue         2
:setvar TypeValue                1
:setvar AltTypeValue             2
:setvar TriggerValue             1
:setvar AltTriggerValue          2
:setvar OtherRoleID              346315
:setvar ParentProcessInstanceID  1
:setvar StartDate                2026-01-01
:setvar EndDate                  2026-12-31
:setvar MaxDurationMs            2000
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

SQL_FOOTER = """-- ==========================================================================
-- Summary
-- ==========================================================================
SELECT  TestCase,
        Title,
        Expectation,
        Outcome,
        DurationMs,
        MaxDurationMs,
        CASE
            WHEN MaxDurationMs IS NOT NULL AND DurationMs > MaxDurationMs THEN 'FAIL (slow)'
            WHEN Expectation = 'SUCCESS' AND Outcome = 'SUCCESS'          THEN 'PASS*'
            WHEN Expectation = 'ERROR'   AND Outcome = 'ERROR'            THEN 'PASS'
            WHEN Expectation = 'ANY'                                      THEN 'REVIEW'
            ELSE 'FAIL'
        END AS Verdict,
        ErrorNumber,
        ErrorMessage
FROM    #TestResults
ORDER BY TestCase;

SELECT  Verdict = v.Verdict, Cases = COUNT(*)
FROM    #TestResults r
CROSS APPLY (SELECT CASE
            WHEN r.MaxDurationMs IS NOT NULL AND r.DurationMs > r.MaxDurationMs THEN 'FAIL (slow)'
            WHEN r.Expectation = 'SUCCESS' AND r.Outcome = 'SUCCESS'            THEN 'PASS*'
            WHEN r.Expectation = 'ERROR'   AND r.Outcome = 'ERROR'              THEN 'PASS'
            WHEN r.Expectation = 'ANY'                                          THEN 'REVIEW'
            ELSE 'FAIL' END) v(Verdict)
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
               "Input (changes from baseline)", "Expected Result", "Harness Expectation",
               "Actual Result", "Status"]
    rows = [[c["id"], c["category"], c["title"], c["kind"], c["priority"], c["preconditions"],
             describe_inputs(c), c["expected"], c["expect"], "", ""] for c in CASES]

    with open(os.path.join(HERE, "TestCases.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)

    md = ["# Test Cases: `[WorkFlow].[uspGetProcessActivities]`", "",
          "_Generated by `generate_test_cases.py`. Edit the generator, then re-run it._", "",
          f"Total cases: **{len(CASES)}**", "",
          "Inputs list only the parameters that differ from the baseline call (TC001). "
          "`$(Name)` values are SQLCMD variables set at the top of `01_Run_TestCases.sql`.", ""]
    category = None
    for c, r in zip(CASES, rows):
        if c["category"] != category:
            category = c["category"]
            md += ["", f"## {category}", "",
                   "| ID | Title | Type | Priority | Input | Expected Result |",
                   "|----|-------|------|----------|-------|-----------------|"]
        cell = lambda s: s.replace("|", "\\|")
        md.append(f"| {c['id']} | {cell(c['title'])} | {c['kind']} | {c['priority']} | "
                  f"`{cell(r[6])}` | {cell(c['expected'])} |")
    with open(os.path.join(HERE, "TestCases.md"), "w", newline="\n") as f:
        f.write("\n".join(md) + "\n")

    print(f"Generated {len(CASES)} test cases.")


if __name__ == "__main__":
    main()
