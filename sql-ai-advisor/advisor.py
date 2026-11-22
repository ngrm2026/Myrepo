"""Builds the evidence for one query and asks the LLM for a diagnosis."""
import config
import llm
from masking import mask_plan, mask_sql
from plan_parser import referenced_tables, summarize_plan, truncate_plan

SYSTEM_PROMPT = """You are a senior SQL Server performance tuning expert.
You receive one query, its runtime statistics, a summary of its execution plan,
the definitions of the tables it touches, and a (possibly truncated) plan XML.

Rules:
- Base every statement on the evidence given. If something is not in the evidence, say "not visible in the evidence".
- Never invent table, column or index names.
- Do not recommend running anything on production without testing.
- Consider write overhead before recommending new indexes; prefer modifying an existing index when it is close.

Answer in Markdown with exactly these sections:
## Bottleneck
One or two sentences: the main reason this query is expensive.
## Evidence
Bullets quoting the specific plan operators, warnings, statistics or row counts that prove it.
## Recommendations
Numbered, most impactful first. For each: the change (with T-SQL), why it helps, and the risk or trade-off.
## How to verify
How to measure the improvement (e.g. SET STATISTICS IO/TIME, Query Store comparison).
## Confidence
High / Medium / Low, with one line explaining why.
"""


def _num(value, fmt: str) -> str:
    try:
        return format(float(value), fmt)
    except (TypeError, ValueError):
        return "n/a"


def build_evidence(conn, row) -> str:
    from db import table_context  # local import keeps the module testable without pyodbc

    sql_text = row["query_sql_text"] or ""
    plan = row["query_plan"] or ""
    if config.MASK_LITERALS:
        sql_text, plan = mask_sql(sql_text), mask_plan(plan)

    tables = referenced_tables(plan)
    table_text = "\n\n".join(table_context(conn, t) for t in tables[:8]) or "No tables identified in the plan."

    return f"""### Runtime statistics
- Object: {row.get('object_name') or '(ad hoc)'}
- Executions: {_num(row.get('executions'), ',.0f')}
- Avg duration: {_num(row.get('avg_duration_ms'), ',.1f')} ms
- Avg CPU: {_num(row.get('avg_cpu_ms'), ',.1f')} ms
- Avg logical reads: {_num(row.get('avg_logical_reads'), ',.0f')}
- Total CPU in window: {_num(row.get('total_cpu_ms'), ',.0f')} ms

### Query text
```sql
{sql_text.strip()}
```

### Execution plan summary
{summarize_plan(plan)}

### Tables involved
{table_text}

### Plan XML (may be truncated)
```xml
{truncate_plan(plan, config.MAX_PLAN_CHARS)}
```
"""


def diagnose(conn, row) -> tuple[str, str]:
    """Return (evidence_sent, llm_answer)."""
    evidence = build_evidence(conn, row)
    answer = llm.ask(SYSTEM_PROMPT, evidence)
    return evidence, answer


WAITS_PROMPT = """You are a senior SQL Server DBA. Given the top wait statistics since the
last restart (or clear), explain in Markdown: what the top 3-5 waits mean, what they
suggest about this server's bottleneck, and what to check next (specific DMVs or settings).
Do not overreact to waits that are normally benign. Be concise."""


def explain_waits(waits_df) -> str:
    return llm.ask(WAITS_PROMPT, waits_df.to_markdown(index=False))
