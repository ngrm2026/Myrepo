# SQL AI Query Advisor (POC)

Finds the most expensive queries in SQL Server (Query Store, or the plan cache as a fallback), gathers the evidence a tuning expert would look at, and asks an LLM to explain the bottleneck and recommend fixes.

**It is read-only.** It never runs DDL or DML on your server. A human decides what to apply.

```
Query Store / DMVs ──► plan summary + table & index definitions ──► mask literals ──► LLM ──► diagnosis (UI + reports/*.md)
```

## What it does

| Feature | Where |
|---|---|
| Top N queries by total CPU for the last X hours | `db.py` (Query Store; plan-cache fallback) |
| Plan summary: costliest operators, warnings (spills, implicit conversions), missing indexes, sniffed parameters | `plan_parser.py` |
| Context: columns, indexes and row counts of every table in the plan | `db.table_context` |
| Masks string literals and parameter values before anything leaves the machine | `masking.py` |
| LLM diagnosis in a fixed format: Bottleneck, Evidence, Recommendations, How to verify, Confidence | `advisor.py` |
| Wait-stats explanation | `advisor.explain_waits` |
| Works with Azure OpenAI, OpenAI or Anthropic Claude | `llm.py` |
| Web UI and a nightly batch report | `app.py`, `nightly_report.py` |

## Prerequisites (Windows laptop)

1. **Python 3.10+**: `python --version`
2. **ODBC Driver 18 for SQL Server** (install it from Microsoft if `SQL_DRIVER` errors).
3. A **SQL Server** instance you can reach: local Developer/Express edition, LocalDB, or a dev server.
4. An **LLM key**: Azure OpenAI (recommended for work data, since it stays in your tenant), OpenAI or Anthropic.

## Setup

```bat
cd sql-ai-advisor
setup.bat
```

Then edit `.env`. At minimum, set `SQL_SERVER`, `SQL_DATABASE`, `LLM_PROVIDER`, `LLM_MODEL` and the key for that provider.

### Optional: demo database

Run `demo\demo_setup.sql` in SSMS on your **local** instance. It creates `AdvisorDemo` with 500k orders, turns on Query Store, and runs two deliberately slow procedures:

- `GetCustomerOrders`: a missing index, so it does a clustered index scan.
- `GetRegionSales`: `YEAR(OrderDate)` is non-SARGable, and an nvarchar parameter is compared to a varchar column.

## Run

```bat
run.bat
```

This opens http://localhost:8501.

1. Click **Load top queries**.
2. Pick a query.
3. Click **Diagnose with AI**.

The answer is also saved to `reports\`. Expand **Evidence sent to the LLM** to see exactly what left your machine.

### Batch report

```bat
.venv\Scripts\python nightly_report.py --database AdvisorDemo --hours 24 --top 10
```

### Run it nightly (Windows Task Scheduler)

```bat
schtasks /create /tn "SQL AI Advisor" /sc daily /st 06:00 ^
  /tr "\"%CD%\.venv\Scripts\python.exe\" \"%CD%\nightly_report.py\""
```

## Permissions

On a shared server, use `demo\readonly_login.sql`. It grants only `VIEW SERVER STATE`, `VIEW DATABASE STATE` and `VIEW DEFINITION`, with no access to table data.

## Guardrails

- Read-only connection (`ApplicationIntent=ReadOnly`) and a least-privilege login.
- `MASK_LITERALS=true` replaces `'values'` and sniffed parameter values before the LLM call.
- The prompt forbids invented object names and requires evidence for every claim.
- Test every recommendation on a non-production copy first, and compare in Query Store.

## Next steps (roadmap)

1. Detect plan regressions (`sys.query_store_plan` with more than one plan per query) and compare the old and new plans.
2. RAG over past RCAs and fixes, using SQL Server 2025 / Azure SQL `VECTOR` columns.
3. Store diagnoses in a table and show them on the monitoring dashboard.
4. Add a CI step: send the DACPAC schema diff to the LLM to get a deployment risk score.
