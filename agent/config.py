import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


def _resolve_pharmgkb_dir() -> Path:
    raw = os.getenv("PHARMGKB_DATA_DIR", "data/pharmGKB")
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


PHARMGKB_DATA_DIR = _resolve_pharmgkb_dir()

MONDO_DATA_PATH = PROJECT_ROOT / "data" / "MONDO" / "mondo-rare.json"

# paper-search-mcp tools that work without API keys
PAPER_SEARCH_TOOLS_NO_KEY = frozenset(
    {"search_arxiv", "search_pubmed", "search_biorxiv", "search_medrxiv"}
)

# Temporary switch: set OPEN_TARGETS_ONLY=1 to disable ClinPGx and paper search
OPEN_TARGETS_ONLY = os.getenv("OPEN_TARGETS_ONLY", "1").lower() in (
    "1",
    "true",
    "yes",
)


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.environ["LLM_MODEL"],
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.environ["LLM_BASE_URL"],
    )


def get_mcp_config() -> dict:
    paper_search_env = {
        key: value
        for key, value in os.environ.items()
        if key.startswith("PAPER_SEARCH_MCP_")
    }

    openfda_env = {}
    if os.getenv("OPENFDA_API_KEY"):
        openfda_env["OPENFDA_API_KEY"] = os.environ["OPENFDA_API_KEY"]

    openfda_transport = os.getenv("OPENFDA_MCP_TRANSPORT", "http").lower()
    if openfda_transport == "stdio":
        openfda_config = {
            "transport": "stdio",
            "command": os.getenv("OPENFDA_MCP_COMMAND", "npx"),
            "args": os.getenv(
                "OPENFDA_MCP_ARGS",
                "-y @cyanheads/openfda-mcp-server@latest",
            ).split(),
            "env": {
                **openfda_env,
                "MCP_TRANSPORT_TYPE": "stdio",
            },
        }
    else:
        openfda_config = {
            "transport": "http",
            "url": os.getenv(
                "OPENFDA_MCP_URL",
                "https://openfda.caseyjhand.com/mcp",
            ),
        }

    return {
        "open_targets": {
            "transport": "http",
            "url": os.getenv(
                "OPEN_TARGETS_MCP_URL", "http://localhost:8010/mcp"
            ),
        },
        "openfda": openfda_config,
        "paper_search": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "paper_search_mcp.server"],
            "env": paper_search_env,
        },
    }
