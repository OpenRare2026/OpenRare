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

    return {
        "open_targets": {
            "transport": "http",
            "url": os.getenv(
                "OPEN_TARGETS_MCP_URL", "http://localhost:8010/mcp"
            ),
        },
        "paper_search": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "paper_search_mcp.server"],
            "env": paper_search_env,
        },
    }
