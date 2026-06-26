#!/usr/bin/env python3
"""Inspect a random HPO term from the ontology."""

import time
import random
from pathlib import Path

import pronto

from http_utils import build_retry_session, request_with_retry


_hpo_ontology = None
_HTTP_SESSION = build_retry_session()


def initialize_hpo_resources(
    obo_url: str = "https://purl.obolibrary.org/obo/hp.obo",
    obo_path: str = "hp.obo",
    refresh_days: int = 14,
) -> pronto.Ontology:
    """Download / refresh HPO OBO file, load via pronto."""
    global _hpo_ontology
    if _hpo_ontology is None:
        obo_file = Path(obo_path)
        if (
            not obo_file.exists()
            or ((time.time() - obo_file.stat().st_mtime) / 86400) > refresh_days
        ):
            print(f"Downloading HPO ontology from {obo_url} ...")
            resp = request_with_retry(_HTTP_SESSION, "GET", obo_url, timeout=(5, 30), max_retries=5)
            resp.raise_for_status()
            obo_file.write_text(resp.text, encoding="utf-8")
        with open(obo_file, "rb") as f:
            _hpo_ontology = pronto.Ontology(f)
        print(f"Loaded ontology with {len(list(_hpo_ontology.terms()))} terms")
    return _hpo_ontology


def print_random_term():
    ont = initialize_hpo_resources()
    term = random.choice(list(ont.terms()))

    print("\n=== Random HPO Term ===")
    print(f"ID         : {term.id}")
    print(f"Name       : {term.name}")
    print(f"Definition : {term.definition!r}")

    syns = [syn.description for syn in term.synonyms]
    print(f"Synonyms   : {syns}")

    xrs = [str(x) for x in term.xrefs]
    print(f"Xrefs      : {xrs}")

    for attr in ("other_ids", "alt_ids", "ids", "synonyms", "xrefs"):
        if hasattr(term, attr):
            val = getattr(term, attr)
            print(f"{attr!r:12}: {val!r}")

    known = {"id", "name", "definition", "synonyms", "xrefs", "other_ids", "alt_ids", "ids"}
    present = set(dir(term))
    if not any(a in present for a in ("other_ids", "alt_ids", "ids")):
        print("\n-- No alt_ids-like attribute found; available attributes: --")
        print(sorted(present))
    print("========================\n")


if __name__ == "__main__":
    print_random_term()
