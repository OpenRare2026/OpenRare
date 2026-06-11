"""Centralized configuration for RAG-HPO pipeline.

All values can be overridden via environment variables with prefix RAG_HPO_.
Example: RAG_HPO_MODEL_NAME=llama3-70b python rag_hpo.py

For the .env file, place it in the project root (parent of dev/).
"""
from typing import Optional, Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── File paths (relative to working directory = project root) ──
    prompts_file: str = "system_prompts.json"
    meta_path: str = "hpo_meta.json"
    vec_path: str = "hpo_embedded.npz"
    temp_dir: str = "tmp"
    hpo_terms_csv: str = "hpo_terms_full.csv"
    jobs_dir: str = "jobs"
    obo_url: str = "https://purl.obolibrary.org/obo/hp.obo"
    obo_path: str = "hp.obo"
    obo_refresh_days: int = 14

    # ── LLM ──
    api_key: Optional[str] = None
    base_url: str = "https://api.groq.com/openai/v1/chat/completions"
    model: str = "llama3-groq-70b-8192-tool-use-preview"
    max_tokens_per_day: int = 500000
    max_queries_per_minute: int = 30
    temperature: float = 0.7
    llm_connect_timeout: int = 10
    llm_read_timeout: int = 120
    llm_max_retries: int = 5

    # ── Embedding model ──
    embedding_model: str = "pritamdeka/SapBERT-mnli-snli-scinli-scitail-mednli-stsb"
    embedding_backend: Literal["auto", "sentence-transformers", "fastembed"] = "auto"
    faiss_metric: str = "cosine"

    # ── Retrieval ──
    retrieval_top_k: int = 500
    retrieval_similarity_threshold: float = 0.35
    retrieval_min_unique: int = 15
    retrieval_max_unique: int = 20

    # ── HPO matching ──
    fuzzy_match_threshold: int = 80
    hpo_id_pattern: str = r"(HP:\d{6,7})"
    hpo_json_keys: tuple = ("hpo_id", "HPO_ID", "hp_id", "id")

    # ── Pipeline control ──
    checkpoint_interval_notes: int = 5
    checkpoint_interval_hpo: int = 50
    hpo_embedding_precision: str = "float16"
    pipeline_max_workers: int = 20

    # ── OLS API ──
    ols_iri_template: str = "http://purl.obolibrary.org/obo/{id}"
    ols_api_url: str = "https://www.ebi.ac.uk/ols4/api/ontologies/hp/terms"
    ols_max_retries: int = 3
    ols_sleep_seconds: int = 1
    ols_timeout: int = 20

    # ── HTTP retry ──
    http_retry_total: int = 5
    http_retry_wait_cap: float = 30.0

    model_config = {
        "env_prefix": "RAG_HPO_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
