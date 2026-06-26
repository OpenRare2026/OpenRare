#!/usr/bin/env python3
"""
Post-processing utilities for RAG-HPO results.

Commands:
    replace-obsolete  Replace obsolete HPO terms using OLS API
    enrich            Merge alt_ids, SNOMED CT, UMLS info into results
"""

import csv
import time
import argparse
import re

import requests
import pandas as pd
from tqdm import tqdm

try:
    from http_utils import build_retry_session, request_with_retry
    from config import settings
except ImportError:
    from dev.http_utils import build_retry_session, request_with_retry
    from dev.config import settings


_HTTP_SESSION = build_retry_session()


# =========================== Batch HPO Term Replacement ===========================

def get_ols_term_status(hpo_id, max_retries=None, sleep_seconds=None):
    """Check OLS for HPO term status and replacement."""
    if max_retries is None:
        max_retries = settings.ols_max_retries
    if sleep_seconds is None:
        sleep_seconds = settings.ols_sleep_seconds
    if not hpo_id.startswith("HP:"):
        print(f"[SKIP] Invalid HPO ID format: {hpo_id}")
        return False, None, "invalid_format"
    iri = settings.ols_iri_template.format(id=hpo_id.replace(":", "_"))
    url = f"{settings.ols_api_url}?iri={requests.utils.quote(iri)}"
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            r = request_with_retry(
                _HTTP_SESSION,
                "GET",
                url,
                timeout=(5, settings.ols_timeout),
                max_retries=1,
            )
            r.raise_for_status()
            data = r.json()
            term = data.get("_embedded", {}).get("terms", [{}])[0]
            is_obsolete = term.get("is_obsolete", False)
            replacement_id = term.get("term_replaced_by")
            return is_obsolete, replacement_id, None
        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"[WARN] {hpo_id} failed (attempt {attempt}): {e}")
            if attempt < max_retries:
                time.sleep(sleep_seconds * attempt)
    return False, None, str(last_error) if last_error else "unknown_error"


def process_and_replace_all(infile, outfile):
    """Read CSV, replace obsolete HPO terms, write updated CSV."""
    failures = []
    replaced_count = 0
    skipped_count = 0
    with open(infile, newline="") as rf:
        reader = list(csv.DictReader(rf))
        fieldnames = list(reader[0].keys()) + ["was_replaced", "original_term"]
        with open(outfile, "w", newline="") as wf:
            writer = csv.DictWriter(wf, fieldnames=fieldnames)
            writer.writeheader()
            for row in tqdm(reader, desc="Processing HPO terms", unit="row"):
                hpo_field = row.get("hpo_term", "").strip()
                if not hpo_field or hpo_field.lower() == "none":
                    row["original_term"] = hpo_field
                    row["was_replaced"] = "False"
                    skipped_count += 1
                    writer.writerow(row)
                    continue
                hpo_ids = [h.strip() for h in hpo_field.split(",") if h.strip().startswith("HP:")]
                replaced_ids = []
                was_any_replaced = False
                for hpo_id in hpo_ids:
                    is_obs, replacement, error = get_ols_term_status(hpo_id)
                    if error:
                        failures.append({"hpo_id": hpo_id, "error": error, "row": row})
                        replaced_ids.append(hpo_id)
                        continue
                    if is_obs and replacement:
                        replaced_ids.append(replacement)
                        was_any_replaced = True
                        replaced_count += 1
                        print(f"[REPLACED] {hpo_id} -> {replacement}")
                    elif is_obs and not replacement:
                        print(f"[OBSOLETE w/o replacement] {hpo_id}")
                        replaced_ids.append(hpo_id)
                    else:
                        replaced_ids.append(hpo_id)
                row["original_term"] = hpo_field
                row["hpo_term"] = ", ".join(replaced_ids)
                row["was_replaced"] = str(was_any_replaced)
                writer.writerow(row)

    print(f"\nBatch complete. Updated file saved to:\n{outfile}")
    print(f"Terms replaced: {replaced_count}")
    print(f"Skipped (empty or 'none'): {skipped_count}")
    print(f"Failed API lookups: {len(failures)}")
    if failures:
        failfile = outfile.replace(".csv", "_failures.csv")
        with open(failfile, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["hpo_id", "error", "row"])
            writer.writeheader()
            writer.writerows(failures)
        print(f"Failures saved to: {failfile}")


# =========================== Enrich Results with HPO Info ===========================

def enrich_results_with_hpo_info(results_csv: str, hpo_full_csv: str, output_csv: str):
    """
    Replace alt_ids in 'hpo_term' with canonical hp_id, then merge in
    alt_ids, snomedct, umls by matching hpo_term -> hp_id.
    """
    results_df = pd.read_csv(results_csv, dtype=str).fillna("")
    hpo_full_df = pd.read_csv(hpo_full_csv, dtype=str).fillna("")
    hpo_info_df = (
        hpo_full_df.loc[:, ["hp_id", "alt_ids", "snomedct", "umls"]]
        .drop_duplicates(subset=["hp_id"])
    )

    # Build alt_id -> canonical hp_id mapping
    alt_map = {}
    for hp_id, alt_ids in zip(hpo_info_df["hp_id"], hpo_info_df["alt_ids"]):
        if not alt_ids:
            continue
        for alt in re.split(r"[;,]\s*", alt_ids):
            alt = alt.strip()
            if alt:
                alt_map[alt] = hp_id

    # Replace alt_ids
    original_terms = results_df["hpo_term"].copy()
    results_df["hpo_term"] = results_df["hpo_term"].apply(lambda x: alt_map.get(x, x))
    num_replaced = (results_df["hpo_term"] != original_terms).sum()
    print(f"[INFO] Replaced {num_replaced} alt_id entries with canonical hp_id")

    # Merge in HPO info
    enriched_df = results_df.merge(
        hpo_info_df, how="left", left_on="hpo_term", right_on="hp_id"
    )
    enriched_df.drop(columns=["hp_id"], inplace=True)
    enriched_df.to_csv(output_csv, index=False)
    print(f"Saved enriched results to {output_csv}")


# =========================== CLI ===========================

def main():
    parser = argparse.ArgumentParser(description="RAG-HPO post-processing utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    # replace-obsolete
    p1 = sub.add_parser("replace-obsolete", help="Replace obsolete HPO terms via OLS API")
    p1.add_argument("input", help="Input CSV with hpo_term column")
    p1.add_argument("--output", "-o", required=True, help="Output CSV path")

    # enrich
    p2 = sub.add_parser("enrich", help="Merge alt_ids, SNOMED CT, UMLS into results")
    p2.add_argument("results", help="Pipeline results CSV (with hpo_term column)")
    p2.add_argument("hpo_full", help="Full HPO terms CSV (hpo_terms_full.csv)")
    p2.add_argument("--output", "-o", required=True, help="Output enriched CSV path")

    args = parser.parse_args()

    if args.command == "replace-obsolete":
        process_and_replace_all(args.input, args.output)
    elif args.command == "enrich":
        enrich_results_with_hpo_info(args.results, args.hpo_full, args.output)


if __name__ == "__main__":
    main()
