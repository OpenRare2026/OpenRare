"""Core HPO extraction pipeline — reusable by CLI and HTTP server."""

from __future__ import annotations

import os
import sys
import time
import traceback
from typing import Optional

import numpy as np
import pandas as pd

try:
    from config import settings
    from http_utils import build_retry_session, request_with_retry
except ImportError:
    from dev.config import settings
    from dev.http_utils import build_retry_session, request_with_retry

# ── Reuse core functions from rag_hpo ──
# These are imported at module level; they need llm_client passed explicitly
# where the original used a module-level global.


class Pipeline:
    """HPO extraction pipeline.

    Load models once at startup, then call ``run()`` for each batch of notes.
    """

    def __init__(self):
        self.llm_client = None
        self.emb_model = None
        self.docs = None
        self.index = None
        self.cluster_index = None
        self._prompts = None

    # ── Initialization ──────────────────────────────────────────────

    def initialize(self, llm_client):
        """Load all models and indices.  Call once at startup."""
        # Import here to keep module-level import cost low
        try:
            from rag_hpo import (
                initialize_embeddings_model,
                load_vector_db,
                create_faiss_index,
                build_cluster_index,
                load_prompts,
            )
        except ImportError:
            from dev.rag_hpo import (
                initialize_embeddings_model,
                load_vector_db,
                create_faiss_index,
                build_cluster_index,
                load_prompts,
            )

        self.llm_client = llm_client
        self._prompts = load_prompts()

        self.emb_model = initialize_embeddings_model()
        self.docs, emb_matrix = load_vector_db()
        self.index = create_faiss_index(emb_matrix)
        self.cluster_index = build_cluster_index(self.docs)

    @property
    def is_ready(self) -> bool:
        return self.llm_client is not None and self.emb_model is not None

    # ── Pipeline entry point ────────────────────────────────────────

    def run(self, notes: list[dict]) -> list[dict]:
        """Run the full pipeline on a list of clinical notes.

        Parameters
        ----------
        notes : list[dict]
            Each dict must have ``patient_id`` (str) and ``clinical_note`` (str).

        Returns
        -------
        list[dict]
            Each dict: ``{patient_id, phrase, category, hpo_id}``.
        """
        if not self.is_ready:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")

        try:
            from rag_hpo import (
                validate_input,
                process_row,
                extract_hpo_term,
                split_exact_nonexact,
                generate_hpo_terms,
            )
        except ImportError:
            from dev.rag_hpo import (
                validate_input,
                process_row,
                extract_hpo_term,
                split_exact_nonexact,
                generate_hpo_terms,
            )

        system_I = self._prompts.get("system_message_I", "")
        system_II = self._prompts.get("system_message_II", "")

        t0 = time.time()

        # 1) Ingest
        df_input = pd.DataFrame(notes)
        df_input = validate_input(df_input)

        # 2) Stage I — LLM phenotype extraction
        combined = pd.DataFrame()
        pids = sorted(df_input["patient_id"].unique())
        for pid in pids:
            note = df_input.loc[df_input["patient_id"] == pid, "clinical_note"].iloc[0]
            res = process_row(
                note, system_I, self.emb_model, self.index, self.docs,
                llm_client=self.llm_client,
            )
            if not res.empty:
                res["patient_id"] = pid
                combined = pd.concat([combined, res], ignore_index=True)

        if combined.empty:
            return []

        # 3) Split exact vs non-exact based on local HPO matching
        if "HPO_Term" not in combined.columns:
            combined["HPO_Term"] = np.nan
        combined["HPO_Term"] = (
            combined.apply(
                lambda r: extract_hpo_term(r["phrase"], r["unique_metadata"], self.cluster_index)
                if pd.isna(r.get("HPO_Term"))
                else r["HPO_Term"],
                axis=1,
            )
            .astype(object)
            .where(lambda x: pd.notna(x), np.nan)
        )
        exact_df, non_exact_df = split_exact_nonexact(combined, hpo_term_col="HPO_Term")

        # 4) Stage II — LLM HPO mapping for non-exact entries
        non_ex = non_exact_df.copy()
        idxs = non_ex[
            (non_ex["category"] == "Abnormal")
            & (non_ex["HPO_Term"].isna())
        ].index

        for idx in idxs:
            row_df = non_ex.loc[[idx]]
            out_df = generate_hpo_terms(
                row_df, system_II, llm_client=self.llm_client,
            )
            hp = out_df.at[0, "HPO_Terms"][0]["HPO_Term"] if not out_df.empty else None
            non_ex.at[idx, "HPO_Term"] = hp or "No Candidate Fit"

        # 5) Compile final
        merged = pd.concat([exact_df, non_ex], ignore_index=True)
        merged = merged.dropna(subset=["HPO_Term"])

        results = []
        for _, r in merged.iterrows():
            pid = r.get("patient_id")
            hp = r.get("HPO_Term") or ""
            if isinstance(hp, str):
                hp = hp.replace("HP:HP:", "HP:")
            results.append({
                "patient_id": str(pid),
                "phrase": r.get("phrase", ""),
                "category": r.get("category", ""),
                "hpo_id": hp if hp else None,
            })

        elapsed = time.time() - t0
        print(f"Pipeline completed: {len(results)} results from {len(notes)} notes in {elapsed:.1f}s")
        return results
