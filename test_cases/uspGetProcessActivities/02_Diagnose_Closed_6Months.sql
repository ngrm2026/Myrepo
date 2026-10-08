/*
    Why does the "closed cases, last 6 months" call of [WorkFlow].[uspGetProcessActivities] take ~1 minute?

    Run each step separately in SSMS (select the block, F5) and note the numbers.
    Steps 1-3 call the procedure; steps 4-7 only read data and catalog views.
    Turn on "Include Actual Execution Plan" (Ctrl+M) for steps 2 and 3.

    What each step tells you:
      1  Server time vs SSMS rendering time, and which step inside the procedure is slow (#TimeLog)
      2  Logical reads per table (STATISTICS IO): the table with the huge read count is the problem
      3  WITH RECOMPILE: if this is much faster than step 2, it is parameter sniffing
      4  Data volume: closed vs open rows, and closed rows inside the 6-month window
      5  Indexes on the two big tables: is there one that leads on IsActive / StartDate / ProcessInstanceID?
      6  Missing-index suggestions SQL Server has recorded for those tables
      7  Cached plan stats: average vs last elapsed time of the procedure
*/
SET NOCOUNT ON;
GO

-- ===========================================================================
-- Step 1. Server-side time and per-step timings
--   Before running: Query > Query Options > Results > Grid >
--   "Discard results after execution". If the call then drops from ~60 s to a few
--   seconds, the time is SSMS drawing the grids, not SQL Server.
--   EnableTimeLog writes to NF.ProcedureTimeLog, so the call is rolled back.
-- ===========================================================================
BEGIN TRAN;

DECLARE @p2 Tag.TagModelTVP;
INSERT INTO @p2 VALUES (6737,N'BSP',0,366713,NULL,28,366713,5031,410129,0,NULL,'0001-01-01 00:00:00');
DECLARE @p9  WorkFlow.ProcessActivityFilterValueTVP,
        @p10 WorkFlow.ProcessActivityFilterValueTVP,
        @p13 WorkFlow.ProcessActivityFilterValueTVP,
        @p14 WorkFlow.ProcessActivityFilterValueTVP;

-- Full timestamps: a date-only @EndDate drops the last day (BETWEEN with a midnight end, see TC064),
-- and @EndDate is ignored when @StartDate is NULL (TC061).
DECLARE @Start datetime2 = DATEADD(MONTH, -6, CAST(SYSDATETIME() AS date)),
        @End   datetime2 = SYSDATETIME();

DECLARE @t0 datetime2 = SYSDATETIME();

EXEC [WorkFlow].[uspGetProcessActivities]
     @EndDate = @End, @FilterTags = @p2, @IsMobileEnabled = NULL, @IsOpenActivity = 0
    ,@IsChildElementTasks = 0, @ProcessTitle = 1, @IsPersistentDataRequired = NULL, @ProcessDateFilterAppliesTo = 1
    ,@ProcessStatus = @p9, @ProcessPriorities = @p10, @IsReferenceElementTasks = 0, @StartDate = @Start
    ,@ProcessTypes = @p13, @ProcessTriggers = @p14, @UserID = 285, @RoleID = 346314, @ParentProcessInstanceID = 0
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
--   spills (yellow warning), and estimated vs actual rows that differ 100x or more.
-- ===========================================================================
SET STATISTICS IO, TIME ON;

DECLARE @p2 Tag.TagModelTVP;
INSERT INTO @p2 VALUES (6737,N'BSP',0,366713,NULL,28,366713,5031,410129,0,NULL,'0001-01-01 00:00:00');
DECLARE @p9  WorkFlow.ProcessActivityFilterValueTVP,
        @p10 WorkFlow.ProcessActivityFilterValueTVP,
        @p13 WorkFlow.ProcessActivityFilterValueTVP,
        @p14 WorkFlow.ProcessActivityFilterValueTVP;
DECLARE @Start datetime2 = DATEADD(MONTH, -6, CAST(SYSDATETIME() AS date)),
        @End   datetime2 = SYSDATETIME();

EXEC [WorkFlow].[uspGetProcessActivities]
     @EndDate = @End, @FilterTags = @p2, @IsMobileEnabled = NULL, @IsOpenActivity = 0
    ,@IsChildElementTasks = 0, @ProcessTitle = 1, @IsPersistentDataRequired = NULL, @ProcessDateFilterAppliesTo = 1
    ,@ProcessStatus = @p9, @ProcessPriorities = @p10, @IsReferenceElementTasks = 0, @StartDate = @Start
    ,@ProcessTypes = @p13, @ProcessTriggers = @p14, @UserID = 285, @RoleID = 346314, @ParentProcessInstanceID = 0;

SET STATISTICS IO, TIME OFF;
GO

-- ===========================================================================
-- Step 3. Same call WITH RECOMPILE (this execution only; the cached plan is not changed)
--   Much faster than step 2  -> parameter sniffing: the cached plan was built for
--   @IsOpenActivity = 1 (few rows) and is reused for closed cases (many rows).
--   Fix: OPTION (RECOMPILE) on the statements that filter on IsActive / StartDate.
--   About the same as step 2 -> the plan is bad for every value; use steps 4-6.
-- ===========================================================================
SET STATISTICS IO, TIME ON;

DECLARE @p2 Tag.TagModelTVP;
INSERT INTO @p2 VALUES (6737,N'BSP',0,366713,NULL,28,366713,5031,410129,0,NULL,'0001-01-01 00:00:00');
DECLARE @p9  WorkFlow.ProcessActivityFilterValueTVP,
        @p10 WorkFlow.ProcessActivityFilterValueTVP,
        @p13 WorkFlow.ProcessActivityFilterValueTVP,
        @p14 WorkFlow.ProcessActivityFilterValueTVP;
DECLARE @Start datetime2 = DATEADD(MONTH, -6, CAST(SYSDATETIME() AS date)),
        @End   datetime2 = SYSDATETIME();

EXEC [WorkFlow].[uspGetProcessActivities]
     @EndDate = @End, @FilterTags = @p2, @IsMobileEnabled = NULL, @IsOpenActivity = 0
    ,@IsChildElementTasks = 0, @ProcessTitle = 1, @IsPersistentDataRequired = NULL, @ProcessDateFilterAppliesTo = 1
    ,@ProcessStatus = @p9, @ProcessPriorities = @p10, @IsReferenceElementTasks = 0, @StartDate = @Start
    ,@ProcessTypes = @p13, @ProcessTriggers = @p14, @UserID = 285, @RoleID = 346314, @ParentProcessInstanceID = 0
WITH RECOMPILE;

SET STATISTICS IO, TIME OFF;
GO

-- ===========================================================================
-- Step 4. Data volume
--   If ClosedActivities is in the millions but ClosedActivitiesLast6Months is small,
--   the procedure is reading the whole closed history and filtering by date late
--   (for example, RANK() over every closed activity before the StartDate filter).
-- ===========================================================================
DECLARE @Start datetime2 = DATEADD(MONTH, -6, CAST(SYSDATETIME() AS date));

SELECT  'ProcessInstanceDetail' AS TableName,
        SUM(CASE WHEN IsActive = 1 THEN 1 ELSE 0 END) AS OpenRows,
        SUM(CASE WHEN IsActive = 0 THEN 1 ELSE 0 END) AS ClosedRows,
        NULL                                          AS ClosedRowsLast6Months
FROM    WorkFlow.ProcessInstanceDetail WITH (NOLOCK)
UNION ALL
SELECT  'ActivityInstanceDetail',
        SUM(CASE WHEN IsActive = 1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN IsActive = 0 THEN 1 ELSE 0 END),
        SUM(CASE WHEN IsActive = 0 AND StartDate >= @Start THEN 1 ELSE 0 END)
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
  AND   ps.object_id = OBJECT_ID(N'WorkFlow.uspGetProcessActivities');
GO
