"""Remove literal values before anything leaves your machine."""
import re

_STRING_LITERAL = re.compile(r"N?'(?:[^']|'')*'")
_COMPILED_VALUE = re.compile(r'(Parameter(?:Compiled|Runtime)Value)="[^"]*"')


def mask_sql(text: str) -> str:
    """Replace string literals such as 'john@x.com' with '?'."""
    return _STRING_LITERAL.sub("'?'", text or "")


def mask_plan(plan_xml: str) -> str:
    """Hide sniffed parameter values and string literals inside the plan XML.

    String literals inside XML attributes appear as &apos;...&apos; or '...'.
    """
    out = _COMPILED_VALUE.sub(r'\1="(masked)"', plan_xml or "")
    out = re.sub(r"N?&apos;.*?&apos;", "&apos;?&apos;", out)
    return out
