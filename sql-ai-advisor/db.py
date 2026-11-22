"""Read-only data collection from SQL Server (Query Store, DMVs, metadata)."""
import pandas as pd
import pyodbc

import config

# Top queries from Query Store for the look-back window, ranked by total CPU.
# Runtime stats are aggregated per plan in a CTE first, because nvarchar(max)
# columns (query text, plan) cannot appear in a GROUP BY.
QUERY_STORE_TOP_SQL = """
WITH agg AS (
    SELECT rs.plan_id,
           SUM(rs.count_executions)                          AS executions,
           SUM(rs.avg_duration * rs.count_executions)        AS tot_duration_us,
           SUM(rs.avg_cpu_time * rs.count_executions)        AS tot_cpu_us,
           SUM(rs.avg_logical_io_reads * rs.count_executions) AS tot_reads
    FROM sys.query_store_runtime_stats rs
    JOIN sys.query_store_runtime_stats_interval i
         ON i.runtime_stats_interval_id = rs.runtime_stats_interval_id
    WHERE i.end_time >= DATEADD(HOUR, -?, SYSDATETIMEOFFSET())
    GROUP BY rs.plan_id
)
SELECT TOP (?)
       q.query_id,
       p.plan_id,
       OBJECT_NAME(q.object_id)                               AS object_name,
       qt.query_sql_text,
       a.executions,
       a.tot_duration_us / NULLIF(a.executions, 0) / 1000.0   AS avg_duration_ms,
       a.tot_cpu_us      / NULLIF(a.executions, 0) / 1000.0   AS avg_cpu_ms,
       a.tot_reads       / NULLIF(a.executions, 0)            AS avg_logical_reads,
       a.tot_cpu_us / 1000.0                                  AS total_cpu_ms,
       p.query_plan
FROM agg a
JOIN sys.query_store_plan       p  ON p.plan_id = a.plan_id
JOIN sys.query_store_query      q  ON q.query_id = p.query_id
JOIN sys.query_store_query_text qt ON qt.query_text_id = q.query_text_id
ORDER BY total_cpu_ms DESC;
"""

# Fallback when Query Store is off: the plan cache (lost on restart).
PLAN_CACHE_TOP_SQL = """
SELECT TOP (?)
       NULL AS query_id,
       NULL AS plan_id,
       OBJECT_NAME(st.objectid, st.dbid) AS object_name,
       SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1,
                 ((CASE qs.statement_end_offset WHEN -1 THEN DATALENGTH(st.text)
                   ELSE qs.statement_end_offset END - qs.statement_start_offset) / 2) + 1) AS query_sql_text,
       qs.execution_count AS executions,
       qs.total_elapsed_time / qs.execution_count / 1000.0 AS avg_duration_ms,
       qs.total_worker_time  / qs.execution_count / 1000.0 AS avg_cpu_ms,
       qs.total_logical_reads / qs.execution_count         AS avg_logical_reads,
       qs.total_worker_time / 1000.0                       AS total_cpu_ms,
       CAST(qp.query_plan AS nvarchar(max))                AS query_plan
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
OUTER APPLY sys.dm_exec_query_plan(qs.plan_handle) qp
ORDER BY qs.total_worker_time DESC;
"""

WAIT_STATS_SQL = """
SELECT TOP (15)
       wait_type,
       waiting_tasks_count,
       wait_time_ms,
       signal_wait_time_ms,
       CAST(100.0 * wait_time_ms / SUM(wait_time_ms) OVER () AS decimal(5, 2)) AS pct
FROM sys.dm_os_wait_stats
WHERE waiting_tasks_count > 0
  AND wait_type NOT IN (
      'BROKER_EVENTHANDLER','BROKER_RECEIVE_WAITFOR','BROKER_TASK_STOP','BROKER_TO_FLUSH',
      'BROKER_TRANSMITTER','CHECKPOINT_QUEUE','CLR_AUTO_EVENT','CLR_MANUAL_EVENT',
      'DIRTY_PAGE_POLL','DISPATCHER_QUEUE_SEMAPHORE','FT_IFTS_SCHEDULER_IDLE_WAIT',
      'HADR_FILESTREAM_IOMGR_IOCOMPLETION','HADR_WORK_QUEUE','LAZYWRITER_SLEEP',
      'LOGMGR_QUEUE','ONDEMAND_TASK_QUEUE','REQUEST_FOR_DEADLOCK_SEARCH',
      'RESOURCE_QUEUE','SERVER_IDLE_CHECK','SLEEP_DBSTARTUP','SLEEP_DCOMSTARTUP',
      'SLEEP_MASTERDBREADY','SLEEP_MASTERMDREADY','SLEEP_MASTERUPGRADED','SLEEP_MSDBSTARTUP',
      'SLEEP_SYSTEMTASK','SLEEP_TASK','SLEEP_TEMPDBSTARTUP','SNI_HTTP_ACCEPT',
      'SP_SERVER_DIAGNOSTICS_SLEEP','SQLTRACE_BUFFER_FLUSH','SQLTRACE_INCREMENTAL_FLUSH_SLEEP',
      'WAITFOR','XE_DISPATCHER_JOIN','XE_DISPATCHER_WAIT','XE_TIMER_EVENT',
      'QDS_PERSIST_TASK_MAIN_LOOP_SLEEP','QDS_ASYNC_QUEUE','QDS_CLEANUP_STALE_QUERIES_TASK_MAIN_LOOP_SLEEP',
      'PREEMPTIVE_XE_DISPATCHER','PWAIT_ALL_COMPONENTS_INITIALIZED','PWAIT_EXTENSIBILITY_CLEANUP_TASK',
      'SOS_WORK_DISPATCHER','XE_LIVE_TARGET_TVF','CXCONSUMER','PARALLEL_REDO_DRAIN_WORKER',
      'PARALLEL_REDO_LOG_CACHE','PARALLEL_REDO_TRAN_LIST','PARALLEL_REDO_WORKER_SYNC',
      'PARALLEL_REDO_WORKER_WAIT_WORK','HADR_CLUSAPI_CALL','HADR_TIMER_TASK',
      'HADR_NOTIFICATION_DEQUEUE','HADR_LOGCAPTURE_WAIT','STARTUP_DEPENDENCY_MANAGER')
ORDER BY wait_time_ms DESC;
"""

COLUMNS_SQL = """
SELECT c.name AS column_name,
       t.name AS data_type,
       CASE WHEN t.name IN ('varchar','char','varbinary','binary')
                 THEN CASE c.max_length WHEN -1 THEN 'max' ELSE CAST(c.max_length AS varchar(10)) END
            WHEN t.name IN ('nvarchar','nchar')
                 THEN CASE c.max_length WHEN -1 THEN 'max' ELSE CAST(c.max_length / 2 AS varchar(10)) END
            ELSE '' END AS length,
       c.is_nullable
FROM sys.columns c
JOIN sys.types t ON t.user_type_id = c.user_type_id
WHERE c.object_id = OBJECT_ID(?)
ORDER BY c.column_id;
"""

INDEXES_SQL = """
SELECT i.name AS index_name,
       i.type_desc,
       i.is_unique,
       i.is_primary_key,
       STUFF((SELECT ', ' + c.name + CASE WHEN ic.is_descending_key = 1 THEN ' DESC' ELSE '' END
              FROM sys.index_columns ic
              JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
              WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id AND ic.is_included_column = 0
              ORDER BY ic.key_ordinal
              FOR XML PATH('')), 1, 2, '') AS key_columns,
       STUFF((SELECT ', ' + c.name
              FROM sys.index_columns ic
              JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
              WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id AND ic.is_included_column = 1
              FOR XML PATH('')), 1, 2, '') AS included_columns,
       i.filter_definition
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID(?) AND i.type > 0
ORDER BY i.index_id;
"""

ROWCOUNT_SQL = """
SELECT SUM(p.rows) FROM sys.partitions p
WHERE p.object_id = OBJECT_ID(?) AND p.index_id IN (0, 1);
"""


def connection_string(database: str | None = None) -> str:
    parts = [
        f"DRIVER={{{config.SQL_DRIVER}}}",
        f"SERVER={config.SQL_SERVER}",
        f"DATABASE={database or config.SQL_DATABASE}",
        "ApplicationIntent=ReadOnly",
        "APP=sql-ai-advisor",
    ]
    if config.SQL_TRUSTED:
        parts.append("Trusted_Connection=yes")
    else:
        parts += [f"UID={config.SQL_USER}", f"PWD={config.SQL_PASSWORD}"]
    if config.SQL_TRUST_CERT:
        parts.append("TrustServerCertificate=yes")
    return ";".join(parts) + ";"


def connect(database: str | None = None) -> pyodbc.Connection:
    conn = pyodbc.connect(connection_string(database), timeout=15)
    conn.timeout = 120  # query timeout in seconds
    return conn


def _df(conn, sql: str, params=()) -> pd.DataFrame:
    cur = conn.cursor()
    cur.execute(sql, params)
    cols = [c[0] for c in cur.description]
    return pd.DataFrame.from_records(cur.fetchall(), columns=cols)


def query_store_enabled(conn) -> bool:
    row = conn.cursor().execute(
        "SELECT actual_state_desc FROM sys.database_query_store_options"
    ).fetchone()
    return bool(row) and row[0] in ("READ_ONLY", "READ_WRITE")


def top_queries(conn, hours: int = config.LOOKBACK_HOURS, top_n: int = config.TOP_N) -> tuple[pd.DataFrame, str]:
    """Return (dataframe, source) where source is 'Query Store' or 'Plan cache'."""
    if query_store_enabled(conn):
        return _df(conn, QUERY_STORE_TOP_SQL, (hours, top_n)), "Query Store"
    return _df(conn, PLAN_CACHE_TOP_SQL, (top_n,)), "Plan cache"


def wait_stats(conn) -> pd.DataFrame:
    return _df(conn, WAIT_STATS_SQL)


def table_context(conn, table: str) -> str:
    """Columns, indexes and row count for one schema.table, as plain text."""
    cols = _df(conn, COLUMNS_SQL, (table,))
    if cols.empty:
        return f"Table {table}: not found in this database."
    idx = _df(conn, INDEXES_SQL, (table,))
    rows = conn.cursor().execute(ROWCOUNT_SQL, (table,)).fetchone()[0]

    col_text = ", ".join(
        f"{r.column_name} {r.data_type}{f'({r.length})' if r.length else ''}{'' if r.is_nullable else ' NOT NULL'}"
        for r in cols.itertuples()
    )
    lines = [f"Table {table} (~{rows:,} rows)" if rows is not None else f"Table {table}",
             f"  Columns: {col_text}"]
    for r in idx.itertuples():
        flags = " ".join(f for f, on in (("PK", r.is_primary_key), ("UNIQUE", r.is_unique)) if on)
        line = f"  Index {r.index_name} [{r.type_desc}{' ' + flags if flags else ''}] keys=({r.key_columns or ''})"
        if r.included_columns:
            line += f" include=({r.included_columns})"
        if r.filter_definition:
            line += f" where {r.filter_definition}"
        lines.append(line)
    return "\n".join(lines)
