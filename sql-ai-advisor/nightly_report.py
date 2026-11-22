"""Batch mode: diagnose the top N queries and write one Markdown report.

Run manually:            python nightly_report.py
Schedule (Windows):      see README -> "Run it nightly"
"""
import argparse
from datetime import datetime

import advisor
import config
import db


def main() -> None:
    ap = argparse.ArgumentParser(description="AI diagnosis of the top expensive queries")
    ap.add_argument("--database", default=config.SQL_DATABASE)
    ap.add_argument("--hours", type=int, default=config.LOOKBACK_HOURS)
    ap.add_argument("--top", type=int, default=config.TOP_N)
    args = ap.parse_args()

    conn = db.connect(args.database)
    df, source = db.top_queries(conn, args.hours, args.top)
    stamp = datetime.now()
    parts = [
        f"# Top {len(df)} expensive queries — {config.SQL_SERVER}/{args.database}",
        f"Generated {stamp:%Y-%m-%d %H:%M}, source: {source}, window: last {args.hours} h, ranked by total CPU.",
        "",
    ]

    for i, row in df.iterrows():
        print(f"[{i + 1}/{len(df)}] diagnosing query_id={row['query_id']} ...", flush=True)
        try:
            _, answer = advisor.diagnose(conn, row)
        except Exception as exc:
            answer = f"_Diagnosis failed: {exc}_"
        snippet = (row["query_sql_text"] or "").strip().replace("\n", " ")[:200]
        parts += [
            f"## {i + 1}. query_id {row['query_id']} — {row.get('object_name') or 'ad hoc'}",
            f"`{snippet}`",
            "",
            answer,
            "",
            "---",
            "",
        ]

    config.REPORT_DIR.mkdir(exist_ok=True)
    out = config.REPORT_DIR / f"report_{args.database}_{stamp:%Y%m%d_%H%M}.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Report written: {out}")


if __name__ == "__main__":
    main()
