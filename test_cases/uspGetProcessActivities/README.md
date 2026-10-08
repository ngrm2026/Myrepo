# Test Suite: `[WorkFlow].[uspGetProcessActivities]` (SQL Server)

The test cases come from two sources: the baseline use case below, which is the call the application actually makes, and the **procedure source** (`sp_helptext`). The expected results describe what the code actually does. Where that looks wrong, the case is marked as a suspected defect.

```sql
declare @p2 Tag.TagModelTVP
insert into @p2 values(6737,N'BSP',0,366713,NULL,28,366713,5031,410129,0,NULL,'0001-01-01 00:00:00')
declare @p9 WorkFlow.ProcessActivityFilterValueTVP    -- ProcessStatus     (empty)
declare @p10 WorkFlow.ProcessActivityFilterValueTVP   -- ProcessPriorities (empty)
declare @p13 WorkFlow.ProcessActivityFilterValueTVP   -- ProcessTypes      (empty)
declare @p14 WorkFlow.ProcessActivityFilterValueTVP   -- ProcessTriggers   (empty)

exec [WorkFlow].[uspGetProcessActivities] @EndDate=NULL,@FilterTags=@p2,@IsMobileEnabled=NULL,@IsOpenActivity=1
    ,@IsChildElementTasks=0,@ProcessTitle=1,@IsPersistentDataRequired=NULL,@ProcessDateFilterAppliesTo=1
    ,@ProcessStatus=@p9,@ProcessPriorities=@p10,@IsReferenceElementTasks=0,@StartDate=NULL,@ProcessTypes=@p13
    ,@ProcessTriggers=@p14,@UserID=285,@RoleID=346314,@ParentProcessInstanceID=0
```

The use case is **My Tasks** (`@ProcessTitle = 1`): user 285 lists open process activities on elements tagged BSP.

## How the procedure works (what the tests target)

```
@IsReferenceElementTasks = 1 AND a process-design tag (ElementTypeID 2008)  -> path A: activities on tagged elements, by process name
@IsReferenceElementTasks = 1                                                 -> path B: activities on tagged elements (no user check)
@IsChildElementTasks = 1 AND @ParentProcessInstanceID > 0                    -> path C: latest activity of each child process
otherwise, @ProcessTitle = 3                                                 -> path D: My Requests (TriggeredBy = @UserID)
otherwise (1 = My Tasks, 2 = All Requests, anything else)                    -> path E: tag search + user/role assignment
```

Every path keeps **only the latest activity per process** (`RANK() ... = 1`). After that, filters run for process name (process-design tags), trigger, type, priority and mobile. The procedure returns these result sets:

1. Process instances
2. Activity instances
3. One row, `ProcessInstanceID = NULL` (not implemented yet)
4. SLA
5. Persistent data (only when `@IsPersistentDataRequired = 1`)

## Files

| File | Purpose |
|------|---------|
| `TestCases.md` | Test case catalogue, with a table of suspected defects at the top |
| `TestCases.csv` | The same cases for Excel, with **Suspected Defect**, **Actual Result** and **Status** columns |
| `00_Discover_Metadata.sql` | Read-only queries for parameter types, table-type columns, result shape, source and dependent tables |
| `01_Run_TestCases.sql` | SQLCMD-mode harness. Every case runs inside a rolled-back transaction, and a summary follows at the end |
| `generate_test_cases.py` | Single source of truth. Edit the cases here, then run `python generate_test_cases.py` |

## Coverage (70 cases, 12 suspected defects)

| Area | Cases |
|------|-------|
| Baseline and repeatability | TC001–TC002 |
| `@ProcessTitle` 1 / 2 / 3 / undefined / NULL | TC005–TC008 |
| `@FilterTags`: empty, two tags, missing tag, duplicate, process-design tag | TC010–TC015 |
| `@IsOpenActivity` | TC020–TC021 |
| Reference-element path, including the error-512 defects and the missing security check | TC030–TC035 |
| Child-element path | TC040–TC045 |
| `@IsMobileEnabled`, `@IsPersistentDataRequired` | TC050–TC056 |
| Dates and `@ProcessDateFilterAppliesTo` | TC060–TC069 |
| `@ProcessStatus` (not used by the code), triggers, types (including tag-mapped types), priorities | TC070–TC090 |
| Security (`@UserID` / `@RoleID`) and required parameters | TC100–TC108 |
| `@IsDebug` / `@EnableTimeLog`; the time-log write is checked automatically | TC110–TC112 |
| Combinations and performance | TC120–TC132 |

## Suspected defects found by reading the code

| # | Finding | Case |
|---|---------|------|
| 1 | `T.SourceObjectID = (SELECT ... FROM @ReferenceElementFilter)` fails with **error 512** when more than one element tag is passed on the reference-element path | TC032 |
| 2 | `PID.ProcessName = (SELECT ProcessName FROM @ProcessNameFilter)` fails with **error 512** when more than one process-design tag is passed | TC033 |
| 3 | The reference-element path has **no user or role check**: any `@UserID` gets the same rows | TC034 |
| 4 | `@RoleID` is **ignored for My Tasks**: results aren't scoped to the selected role | TC103 |
| 5 | `@EndDate` is ignored when `@StartDate` is NULL | TC061 |
| 6 | A date-only `@EndDate` cuts off the rest of that day (`BETWEEN` with a midnight upper bound) | TC064 |
| 7 | `@ProcessDateFilterAppliesTo` is not implemented | TC067 |
| 8 | `@ProcessStatus` is accepted but ignored | TC070 |
| 9 | Persistent data (result set 5) is **always empty**, because `AssociatedAppID` is always NULL in `#ActivitiesTVP` | TC055 |
| 10 | Processes with a NULL trigger, type or priority always pass those filters | TC077 |
| 11 | The child path ignores `@IsOpenActivity` and the dates | TC042 |
| 12 | `@ProcessTitle` isn't validated | TC007 |

The code also has these issues; there are no separate cases for them:
- User **285 is hard-coded** as "Nibras Admin".
- Processes missing a `ProcessType`, `ProcessPriority` or `SupportedClient` attribute are always dropped, because of the INNER JOINs.
- `@AssetTag` is never filled.
- The debug block has `RefElementVersionID = 76703` hard-coded.
- The result sets have no `ORDER BY`.

## How to run

1. In `01_Run_TestCases.sql`, set the `:setvar` values (see the next section).
2. In SSMS, turn on **Query > SQLCMD Mode** and press F5. You can also run `sqlcmd -S <server> -d <db> -E -i 01_Run_TestCases.sql -o results.txt`.
3. Read the last two grids:
   - **PASS\***: ran without error. Still compare its result grids with the expected result in `TestCases.md`.
   - **PASS**: the expected error was raised (error 201 for a missing required parameter).
   - **DEFECT REPRODUCED**: the known bug happened. **DEFECT FIXED?**: it didn't; recheck the case.
   - **REVIEW**: either outcome is acceptable; check by hand.
   - **FAIL** / **FAIL (slow)**: an unexpected error, or the case ran past `MaxDurationMs`.
4. To show the summary again without re-running, run this in the same window:
   `SELECT * FROM #TestResults ORDER BY TestCase;`

Every call runs inside `BEGIN TRAN … ROLLBACK`, so `@EnableTimeLog = 1`, which writes to `NF.ProcedureTimeLog`, leaves nothing behind.

## Finding test values for `:setvar`

Run each query against the test database and pick a value from the results.

```sql
-- Map the baseline tag row to TVP column names (to see which value is TagName / ObjectID / ElementTypeID)
DECLARE @t Tag.TagModelTVP;
INSERT INTO @t VALUES (6737,N'BSP',0,366713,NULL,28,366713,5031,410129,0,NULL,'0001-01-01 00:00:00');
SELECT * FROM @t;

-- ProcessName / AltProcessName: process names with open activities
SELECT TOP 20 ProcessName, COUNT(*) AS OpenProcesses
FROM WorkFlow.ProcessInstanceDetail WHERE IsActive = 1
GROUP BY ProcessName ORDER BY 2 DESC;

-- TriggerValue / AltTriggerValue
SELECT TriggerSource, COUNT(*) FROM WorkFlow.ProcessInstanceDetail GROUP BY TriggerSource;

-- TypeValue / AltTypeValue and PriorityValue / AltPriorityValue
SELECT AttributeTemplateName, ValueInt, COUNT(*) FROM nf.Attribute
WHERE AttributeTemplateName IN ('ProcessType', 'ProcessPriority')
GROUP BY AttributeTemplateName, ValueInt ORDER BY 1, 3 DESC;

-- ParentProcessInstanceID: parents that have child processes
SELECT TOP 10 ParentProcessInstanceID, COUNT(*) AS Children
FROM WorkFlow.ProcessInstanceDetail WHERE ParentProcessInstanceID > 0
GROUP BY ParentProcessInstanceID ORDER BY 2 DESC;

-- OtherUserID / OtherUserRoleID: another (non-admin) user with open activities
SELECT TOP 10 Executor, ExecutorRoleID, COUNT(*) AS OpenActivities
FROM WorkFlow.ActivityInstanceDetail
WHERE IsActive = 1 AND Executor IS NOT NULL AND Executor <> 285
GROUP BY Executor, ExecutorRoleID ORDER BY 3 DESC;
```

For `AltTagName` / `AltTagObjectID`, the simplest way is to select a different tag in the application, capture the call in SQL Profiler, and copy those two values from its `insert into @p2` row.
