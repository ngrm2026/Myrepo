# Test Suite: `[WorkFlow].[uspGetProcessActivities]` (SQL Server)

These test cases are derived from the baseline use case below, which is the call the application actually makes:

```sql
declare @p2 Tag.TagModelTVP
insert into @p2 values(6737,N'BSP',0,366713,NULL,28,366713,5031,410129,0,NULL,'0001-01-01 00:00:00')
declare @p9  WorkFlow.ProcessActivityFilterValueTVP   -- ProcessStatus     (empty)
declare @p10 WorkFlow.ProcessActivityFilterValueTVP   -- ProcessPriorities (empty)
declare @p13 WorkFlow.ProcessActivityFilterValueTVP   -- ProcessTypes      (empty)
declare @p14 WorkFlow.ProcessActivityFilterValueTVP   -- ProcessTriggers   (empty)

exec [WorkFlow].[uspGetProcessActivities] @EndDate=NULL,@FilterTags=@p2,@IsMobileEnabled=NULL,@IsOpenActivity=1
    ,@IsChildElementTasks=0,@ProcessTitle=1,@IsPersistentDataRequired=NULL,@ProcessDateFilterAppliesTo=1
    ,@ProcessStatus=@p9,@ProcessPriorities=@p10,@IsReferenceElementTasks=0,@StartDate=NULL,@ProcessTypes=@p13
    ,@ProcessTriggers=@p14,@UserID=285,@RoleID=346314,@ParentProcessInstanceID=0
```

Use case: user **285**, acting in role **346314**, lists **open** process activities tagged **BSP (6737)**. Child and reference element tasks are excluded, and there is no date, status, priority, type, trigger or parent filter.

## Files

| File | Purpose |
|------|---------|
| `TestCases.md` | Test case catalogue: ID, title, type, priority, inputs, expected result |
| `TestCases.csv` | The same catalogue for Excel or a test management tool, with blank **Actual Result** and **Status** columns |
| `00_Discover_Metadata.sql` | Read-only queries for parameter types, TVP columns, result shape, procedure source and dependent tables |
| `01_Run_TestCases.sql` | SQLCMD-mode harness that runs every case inside a rolled-back transaction and prints a PASS/FAIL summary |
| `generate_test_cases.py` | Single source of truth. Edit the cases here, then run `python generate_test_cases.py` to regenerate the three files above |

## Coverage (57 cases)

| Area | Cases |
|------|-------|
| Baseline and repeatability | TC001–TC002 |
| `@FilterTags` (empty, multiple, missing, duplicate) | TC010–TC013 |
| `@IsOpenActivity` (0 / NULL) | TC020–TC021 |
| `@IsChildElementTasks` / `@IsReferenceElementTasks` | TC030–TC033 |
| `@IsMobileEnabled`, `@IsPersistentDataRequired`, `@ProcessTitle` | TC040–TC051 |
| `@StartDate` / `@EndDate` / `@ProcessDateFilterAppliesTo` (ranges, inverted, single day, extremes, invalid mode) | TC060–TC069 |
| `@ProcessStatus`, `@ProcessPriorities`, `@ProcessTypes`, `@ProcessTriggers` (single, multiple, missing value) and omitted TVPs | TC070–TC090 |
| Security: `@UserID` / `@RoleID` (missing, NULL, 0, role not assigned to user, parameter omitted) | TC100–TC106 |
| `@ParentProcessInstanceID` | TC110–TC112 |
| Combinations | TC120–TC122 |
| Performance (time budget, 500-tag TVP, widest result set) | TC130–TC132 |

## How to run

1. Run `00_Discover_Metadata.sql` against the test database.
2. In `01_Run_TestCases.sql`, set the `:setvar` values (`AltTagID`, `StatusValue`, `OtherRoleID`, `ParentProcessInstanceID`, dates, `MaxDurationMs`, and so on) to real IDs from that database.
3. In SSMS, turn on **Query > SQLCMD Mode** and execute the script. You can also run it with `sqlcmd -S <server> -d <db> -E -i 01_Run_TestCases.sql`.
4. Read the summary at the end:
   - **PASS\***: the case ran as expected. Still compare its result grid with the *Expected Result* in `TestCases.md`, because the harness can't check row content.
   - **REVIEW**: either outcome is acceptable. Check the behaviour by hand.
   - **FAIL** / **FAIL (slow)**: an unexpected error, or the case ran past `MaxDurationMs`.
5. Fill in **Actual Result** and **Status** in `TestCases.csv`.

Every call is wrapped in `BEGIN TRAN … ROLLBACK`, so the suite is safe even if the procedure writes to a table (for example an audit log).

## Assumptions to confirm

I didn't have the procedure source, so the expected results come from the parameter names and the baseline call. Before you sign off, check them against the output of `00_Discover_Metadata.sql`:

- **`Tag.TagModelTVP`** has 12 columns in the order of the baseline insert, and the first column is the tag ID. The multi-tag, missing-tag and 500-tag cases change only that first column.
- **`WorkFlow.ProcessActivityFilterValueTVP`** has a single value column, so the harness inserts `VALUES (<value>)`. If the type has more columns, update the filter-value inserts in `generate_test_cases.py` and regenerate.
- `@ProcessDateFilterAppliesTo` uses `1` and `2` as valid modes. `@ProcessTitle` behaves like a flag.
- Empty TVPs mean "no filter" for status, priority, type and trigger. The behaviour for an empty `@FilterTags` is unclear, so TC010 asks you to confirm it.
- If a TVP insert doesn't match the type's columns, SQL Server raises a compile error (for example 213). `TRY/CATCH` can't catch that, so the case gets no row in the summary. A case missing from the summary means you should fix the TVP layout first.
