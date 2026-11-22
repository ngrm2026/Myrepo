"""Turn a SQL Server showplan XML into a compact summary an LLM can read.

Plans are often 100 KB+. Sending the whole thing is slow and expensive, so we
extract what a tuning expert looks at first, and attach a truncated raw plan.
"""
import re
import xml.etree.ElementTree as ET

NS = {"sp": "http://schemas.microsoft.com/sqlserver/2004/07/showplan"}
_TAG = "{http://schemas.microsoft.com/sqlserver/2004/07/showplan}"


def _strip(name: str | None) -> str:
    return (name or "").replace("[", "").replace("]", "")


def referenced_tables(plan_xml: str) -> list[str]:
    """Distinct schema.table names referenced by the plan (temp tables skipped)."""
    found = []
    for m in re.finditer(r'<Object\b[^>]*?Schema="([^"]+)"[^>]*?Table="([^"]+)"', plan_xml or ""):
        schema, table = _strip(m.group(1)), _strip(m.group(2))
        if table.startswith("#"):
            continue
        name = f"{schema}.{table}"
        if name not in found:
            found.append(name)
    return found


def summarize_plan(plan_xml: str, top_ops: int = 8) -> str:
    if not plan_xml:
        return "No execution plan available."
    try:
        root = ET.fromstring(plan_xml)
    except ET.ParseError as exc:
        return f"Plan XML could not be parsed ({exc})."

    lines: list[str] = []

    stmt = root.find(".//sp:StmtSimple", NS)
    if stmt is not None:
        lines.append(
            "Statement: est. cost={}, est. rows={}, optimization level={}, CE version={}".format(
                stmt.get("StatementSubTreeCost"), stmt.get("StatementEstRows"),
                stmt.get("StatementOptmLevel"), stmt.get("CardinalityEstimationModelVersion"),
            )
        )
        if stmt.get("StatementOptmEarlyAbortReason"):
            lines.append(f"Optimizer early abort: {stmt.get('StatementOptmEarlyAbortReason')}")

    qp = root.find(".//sp:QueryPlan", NS)
    if qp is not None:
        extras = {k: qp.get(k) for k in ("DegreeOfParallelism", "MemoryGrant", "CachedPlanSize",
                                         "NonParallelPlanReason") if qp.get(k)}
        if extras:
            lines.append("Plan attributes: " + ", ".join(f"{k}={v}" for k, v in extras.items()))
        mg = qp.find("sp:MemoryGrantInfo", NS)
        if mg is not None:
            lines.append("Memory grant: " + ", ".join(f"{k}={v}" for k, v in mg.attrib.items()))

    # Warnings anywhere in the plan
    warnings = set()
    for w in root.iter(f"{_TAG}Warnings"):
        for k, v in w.attrib.items():
            warnings.add(f"{k}={v}")
        for child in w:
            tag = child.tag.replace(_TAG, "")
            detail = child.get("Expression") or " ".join(f"{k}={v}" for k, v in child.attrib.items())
            warnings.add(f"{tag} {detail}".strip())
    if warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {w}" for w in sorted(warnings))

    # Most expensive operators (by estimated subtree cost)
    ops = []
    for op in root.iter(f"{_TAG}RelOp"):
        # The operator's own <Object> sits directly under its physical-op element
        # (e.g. <IndexScan>); searching deeper would pick up child operators' tables.
        obj = next((c.find("sp:Object", NS) for c in op if c.find("sp:Object", NS) is not None), None)
        target = ""
        if obj is not None:
            target = ".".join(filter(None, [_strip(obj.get("Schema")), _strip(obj.get("Table"))]))
            if obj.get("Index"):
                target += f" ({_strip(obj.get('Index'))})"
        ops.append((
            float(op.get("EstimatedTotalSubtreeCost", 0) or 0),
            op.get("PhysicalOp"), op.get("LogicalOp"), target,
            op.get("EstimateRows"), op.get("EstimatedRowsRead"),
        ))
    if ops:
        lines.append(f"Top {min(top_ops, len(ops))} operators by estimated subtree cost:")
        for cost, phys, logical, target, rows, rows_read in sorted(ops, reverse=True)[:top_ops]:
            extra = f", est. rows read={rows_read}" if rows_read else ""
            lines.append(f"  - {phys}/{logical} {target} cost={cost:.4f}, est. rows={rows}{extra}")

    # Missing index suggestions embedded in the plan
    for grp in root.iter(f"{_TAG}MissingIndexGroup"):
        mi = grp.find("sp:MissingIndex", NS)
        if mi is None:
            continue
        cols = {"EQUALITY": [], "INEQUALITY": [], "INCLUDE": []}
        for cg in mi.findall("sp:ColumnGroup", NS):
            cols.setdefault(cg.get("Usage"), []).extend(_strip(c.get("Name")) for c in cg.findall("sp:Column", NS))
        lines.append(
            "Missing index (impact {}%): {}.{} eq=[{}] ineq=[{}] include=[{}]".format(
                grp.get("Impact"), _strip(mi.get("Schema")), _strip(mi.get("Table")),
                ", ".join(cols["EQUALITY"]), ", ".join(cols["INEQUALITY"]), ", ".join(cols["INCLUDE"]),
            )
        )

    # Parameters: compiled values reveal parameter sniffing
    params = [
        f"{p.get('Column')} compiled={p.get('ParameterCompiledValue')}"
        + (f" runtime={p.get('ParameterRuntimeValue')}" if p.get("ParameterRuntimeValue") else "")
        for p in root.iter(f"{_TAG}ColumnReference")
        if p.get("ParameterCompiledValue") is not None
    ]
    if params:
        lines.append("Parameters: " + "; ".join(params))

    return "\n".join(lines) if lines else "Plan parsed, but no notable details were found."


def truncate_plan(plan_xml: str, max_chars: int) -> str:
    if not plan_xml or len(plan_xml) <= max_chars:
        return plan_xml or ""
    return plan_xml[:max_chars] + f"\n<!-- truncated: plan was {len(plan_xml)} chars -->"
