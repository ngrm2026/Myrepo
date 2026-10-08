/*
    Why is [WorkFlow].[uspGetProcessActivities_5_1445Server_mod1] slow for closed cases over 6 months?

    Measured so far (SSMS):
      1 month  (2025-09-15 .. 2025-10-15), @IsOpenActivity = NULL  -> ~10 s
      6 months, inactive cases                                     -> ~60 s
    Time grows with the date range, so the cost is per activity in the range
    (row-by-row work, or a read of every activity before the date filter), not a fixed overhead.

    SQLCMD mode is required (Query > SQLCMD Mode). Edit the :setvar values, then run each
    step separately (select the block, F5). Turn on "Include Actual Execution Plan" (Ctrl+M)
    for steps 2 and 3. Steps 1-3 call the procedure; steps 4-7 only read data and catalog views.

    What each step tells you:
      1  Server time vs SSMS rendering time, and which step inside the procedure is slow (#TimeLog)
      2  Logical reads per table (STATISTICS IO): the table with the huge read count is the problem
      3  WITH RECOMPILE: if this is much faster than step 2, it is parameter sniffing
      4  Data volume: activities in the date range, open vs closed
      5  Indexes on the two big tables: is there one that leads on IsActive / StartDate / ProcessInstanceID?
      6  Missing-index suggestions SQL Server has recorded for those tables
      7  Cached plan stats: average vs last elapsed time of the procedure
*/

-- ---- The captured application call (edit these) ---------------------------
--  Captured call: 1 month, IsOpenActivity = NULL (open and closed) -> ~10 s.
--  The slow use case: 6 months, inactive only. Set IsOpenActivity to 0 for that,
--  or NULL to reproduce exactly what the application sent.
:setvar ProcName        "[WorkFlow].[uspGetProcessActivities_5_1445Server_mod1]"
:setvar StartDate       "2025-04-15 00:00:00"
:setvar EndDate         "2025-10-15 23:59:59"
:setvar IsOpenActivity  0
:setvar ProcessTitle    2
:setvar UserID          431135
:setvar RoleID          287
:setvar TagRow          "6737,N'BSP',0,366713,NULL,28,366713,5031,1626,0,NULL,'0001-01-01 00:00:00'"
-- ----------------------------------------------------------------------------

SET NOCOUNT ON;
GO

-- ===========================================================================
-- Step 1. Server-side time and per-step timings
--   Before running: Query > Query Options > Results > Grid >
--   "Discard results after execution". If the call then drops far below 60 s,
--   the rest of the time is SSMS drawing the grids, not SQL Server.
--   EnableTimeLog writes to NF.ProcedureTimeLog, so the call is rolled back.
--   If the _mod1 procedure has no @IsDebug / @EnableTimeLog parameters (error 8145),
--   remove that line; TotalServerMs still works.
-- ===========================================================================
BEGIN TRAN;

DECLARE @p11 Tag.TagModelTVP;
INSERT INTO @p11 VALUES ($(TagRow));
DECLARE @p3  WorkFlow.ProcessActivityFilterValueTVP,
        @p4  WorkFlow.ProcessActivityFilterValueTVP,
        @p5  WorkFlow.ProcessActivityFilterValueTVP,
        @p14 WorkFlow.ProcessActivityFilterValueTVP;

DECLARE @t0 datetime2 = SYSDATETIME();

EXEC $(ProcName)
     @ProcessDateFilterAppliesTo = 1, @StartDate = '$(StartDate)', @EndDate = '$(EndDate)'
    ,@ProcessTypes = @p3, @ProcessTriggers = @p4, @ProcessPriorities = @p5, @ProcessStatus = @p14
    ,@UserID = $(UserID), @RoleID = $(RoleID), @IsOpenActivity = $(IsOpenActivity)
    ,@IsPersistentDataRequired = NULL, @FilterTags = @p11, @ProcessTitle = $(ProcessTitle)
    ,@IsReferenceElementTasks = 0, @IsMobileEnabled = NULL, @IsChildElementTasks = 0, @ParentProcessInstanceID = 0
    ,@IsDebug = 1, @EnableTimeLog = 1;   -- last result set (#TimeLog) = time spent in each step

SELECT DATEDIFF(MILLISECOND, @t0, SYSDATETIME()) AS TotalServerMs;

ROLLBACK;
GO

-- ===========================================================================
-- Step 2. Same call (no debug output) with I/O and CPU statistics
--   Messages tab: look for the table with the largest "logical reads" and the
--   statement with the largest "elapsed time".
--   Execution plan: look for scans of ActivityInstanceDetail / ProcessInstanceDetail /
--   nf.Attribute, Sort or Window Aggregate (RANK) operators over millions of rows,
--   spills (yellow warning), scalar functions or nested loops executed once per row,
--   and estimated vs actual rows that differ 100x or more.
-- ===========================================================================
SET STATISTICS IO, TIME ON;

DECLARE @p11 Tag.TagModelTVP;
INSERT INTO @p11 VALUES ($(TagRow));
DECLARE @p3  WorkFlow.ProcessActivityFilterValueTVP,
        @p4  WorkFlow.ProcessActivityFilterValueTVP,
        @p5  WorkFlow.ProcessActivityFilterValueTVP,
        @p14 WorkFlow.ProcessActivityFilterValueTVP;

EXEC $(ProcName)
     @ProcessDateFilterAppliesTo = 1, @StartDate = '$(StartDate)', @EndDate = '$(EndDate)'
    ,@ProcessTypes = @p3, @ProcessTriggers = @p4, @ProcessPriorities = @p5, @ProcessStatus = @p14
    ,@UserID = $(UserID), @RoleID = $(RoleID), @IsOpenActivity = $(IsOpenActivity)
    ,@IsPersistentDataRequired = NULL, @FilterTags = @p11, @ProcessTitle = $(ProcessTitle)
    ,@IsReferenceElementTasks = 0, @IsMobileEnabled = NULL, @IsChildElementTasks = 0, @ParentProcessInstanceID = 0;

SET STATISTICS IO, TIME OFF;
GO

-- ===========================================================================
-- Step 3. Same call WITH RECOMPILE (this execution only; the cached plan is not changed)
--   Much faster than step 2  -> parameter sniffing: the cached plan was built for a
--   small call (open cases, one month) and is reused for a large one.
--   Fix: OPTION (RECOMPILE) on the statements that filter on IsActive / StartDate.
--   About the same as step 2 -> the plan is bad for every value; use steps 4-6.
-- ===========================================================================
SET STATISTICS IO, TIME ON;

DECLARE @p11 Tag.TagModelTVP;
INSERT INTO @p11 VALUES ($(TagRow));
DECLARE @p3  WorkFlow.ProcessActivityFilterValueTVP,
        @p4  WorkFlow.ProcessActivityFilterValueTVP,
        @p5  WorkFlow.ProcessActivityFilterValueTVP,
        @p14 WorkFlow.ProcessActivityFilterValueTVP;

EXEC $(ProcName)
     @ProcessDateFilterAppliesTo = 1, @StartDate = '$(StartDate)', @EndDate = '$(EndDate)'
    ,@ProcessTypes = @p3, @ProcessTriggers = @p4, @ProcessPriorities = @p5, @ProcessStatus = @p14
    ,@UserID = $(UserID), @RoleID = $(RoleID), @IsOpenActivity = $(IsOpenActivity)
    ,@IsPersistentDataRequired = NULL, @FilterTags = @p11, @ProcessTitle = $(ProcessTitle)
    ,@IsReferenceElementTasks = 0, @IsMobileEnabled = NULL, @IsChildElementTasks = 0, @ParentProcessInstanceID = 0
WITH RECOMPILE;

SET STATISTICS IO, TIME OFF;
GO

-- ===========================================================================
-- Step 4. Data volume
--   Compare ActivitiesInRange with the run time: ~10 s for 1 month and ~60 s for
--   6 months means a fixed cost per activity. If ClosedActivities (all time) is
--   far larger than ClosedInRange, check whether the procedure reads every closed
--   activity before applying the date filter (e.g. RANK() before the StartDate filter).
-- ===========================================================================
SELECT  COUNT(*)                                                                         AS AllActivities,
        SUM(CASE WHEN IsActive = 0 THEN 1 ELSE 0 END)                                    AS ClosedActivities,
        SUM(CASE WHEN StartDate BETWEEN '$(StartDate)' AND '$(EndDate)' THEN 1 ELSE 0 END) AS ActivitiesInRange,
        SUM(CASE WHEN StartDate BETWEEN '$(StartDate)' AND '$(EndDate)' AND IsActive = 0
                 THEN 1 ELSE 0 END)                                                      AS ClosedInRange,
        COUNT(DISTINCT CASE WHEN StartDate BETWEEN '$(StartDate)' AND '$(EndDate)'
                            THEN ProcessInstanceID END)                                  AS ProcessesInRange
FROM    WorkFlow.ActivityInstanceDetail WITH (NOLOCK);
GO

-- ===========================================================================
-- Step 5. Existing indexes on the two big tables
--   Closed cases + date range + "latest activity per process" is served well by:
--     ActivityInstanceDetail (IsActive, StartDate) INCLUDE (ProcessInstanceID, Executor, ExecutorRoleID, ...)
--     ActivityInstanceDetail (ProcessInstanceID, StartDate DESC)      -- for the RANK() / latest-per-process
--   If neither exists, that is the likely cause.
-- ===========================================================================
SELECT  OBJECT_SCHEMA_NAME(i.object_id) + '.' + OBJECT_NAME(i.object_id) AS TableName,
        i.name       AS IndexName,
        i.type_desc,
        STUFF((SELECT ', ' + c.name + CASE WHEN ic.is_descending_key = 1 THEN ' DESC' ELSE '' END
               FROM sys.index_columns ic JOIN sys.columns c
                 ON c.object_id = ic.object_id AND c.column_id = ic.column_id
               WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id AND ic.is_included_column = 0
               ORDER BY ic.key_ordinal FOR XML PATH('')), 1, 2, '') AS KeyColumns,
        STUFF((SELECT ', ' + c.name
               FROM sys.index_columns ic JOIN sys.columns c
                 ON c.object_id = ic.object_id AND c.column_id = ic.column_id
               WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id AND ic.is_included_column = 1
               FOR XML PATH('')), 1, 2, '') AS IncludedColumns,
        i.filter_definition
FROM    sys.indexes i
WHERE   i.object_id IN (OBJECT_ID(N'WorkFlow.ActivityInstanceDetail'), OBJECT_ID(N'WorkFlow.ProcessInstanceDetail'))
  AND   i.type > 0
ORDER BY TableName, i.index_id;
GO

-- ===========================================================================
-- Step 6. Missing-index suggestions for the tables the procedure reads
--   Treat these as hints, not a to-do list: check them against step 2's plan.
-- ===========================================================================
SELECT  d.statement            AS TableName,
        d.equality_columns,
        d.inequality_columns,
        d.included_columns,
        s.user_seeks + s.user_scans AS TimesWanted,
        CAST(s.avg_total_user_cost * s.avg_user_impact * (s.user_seeks + s.user_scans) AS bigint) AS Benefit
FROM    sys.dm_db_missing_index_details d
JOIN    sys.dm_db_missing_index_groups g        ON g.index_handle = d.index_handle
JOIN    sys.dm_db_missing_index_group_stats s   ON s.group_handle = g.index_group_handle
WHERE   d.database_id = DB_ID()
  AND  (d.statement LIKE N'%ActivityInstanceDetail%' OR d.statement LIKE N'%ProcessInstanceDetail%'
        OR d.statement LIKE N'%Attribute%' OR d.statement LIKE N'%TagMap%')
ORDER BY Benefit DESC;
GO

-- ===========================================================================
-- Step 7. Cached plan statistics for the procedure
--   last_elapsed much higher than avg_elapsed for the same plan = the plan suits
--   some parameter values (open cases) and not others (closed, 6 months).
-- ===========================================================================
SELECT  ps.execution_count,
        ps.total_elapsed_time / NULLIF(ps.execution_count, 0) / 1000 AS avg_elapsed_ms,
        ps.last_elapsed_time / 1000                                  AS last_elapsed_ms,
        ps.max_elapsed_time / 1000                                   AS max_elapsed_ms,
        ps.total_logical_reads / NULLIF(ps.execution_count, 0)       AS avg_logical_reads,
        ps.last_logical_reads,
        ps.cached_time
FROM    sys.dm_exec_procedure_stats ps
WHERE   ps.database_id = DB_ID()
  AND   ps.object_id = OBJECT_ID(N'$(ProcName)');
GO
