"""Central configuration, read from the .env file next to this script."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "y")


# ---- SQL Server -----------------------------------------------------------
SQL_SERVER = os.getenv("SQL_SERVER", "localhost")
SQL_DATABASE = os.getenv("SQL_DATABASE", "master")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
SQL_TRUSTED = _bool("SQL_TRUSTED_CONNECTION", True)   # Windows authentication
SQL_USER = os.getenv("SQL_USER", "")
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")
SQL_TRUST_CERT = _bool("SQL_TRUST_SERVER_CERTIFICATE", True)

# ---- LLM ------------------------------------------------------------------
# azure | openai | anthropic | ollama (free, local)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "azure").strip().lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")  # Azure: deployment name
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1500"))

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# ---- Behaviour ------------------------------------------------------------
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "24"))
TOP_N = int(os.getenv("TOP_N", "10"))
MAX_PLAN_CHARS = int(os.getenv("MAX_PLAN_CHARS", "30000"))
MASK_LITERALS = _bool("MASK_LITERALS", True)
REPORT_DIR = BASE_DIR / "reports"
