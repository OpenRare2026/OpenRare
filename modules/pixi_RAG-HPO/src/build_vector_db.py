"""Build HPO vector database: hpo_meta.json + hpo_embedded.npz"""
import time
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pronto
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

try:
    from http_utils import build_retry_session, request_with_retry
    from config import settings
except ImportError:
    from dev.http_utils import build_retry_session, request_with_retry
    from dev.config import settings

ROOT_ID = 'HP:0000001'
PHENO_ID = 'HP:0000118'
_HTTP_SESSION = build_retry_session()

# ── Ontology download ──
def init_ontology(obo_url=None, obo_path=None, refresh_days=None):
    if obo_url is None:
        obo_url = settings.obo_url
    if obo_path is None:
        obo_path = settings.obo_path
    if refresh_days is None:
        refresh_days = settings.obo_refresh_days
    obo_file = Path(obo_path)
    if not obo_file.exists() or ((time.time() - obo_file.stat().st_mtime) / 86400) > refresh_days:
        print(f"Downloading HPO ontology from {obo_url} ...")
        resp = request_with_retry(_HTTP_SESSION, "GET", obo_url, timeout=(5, 30), max_retries=5)
        resp.raise_for_status()
        obo_file.write_text(resp.text, encoding="utf-8")
    with open(obo_file, 'rb') as f:
        ont = pronto.Ontology(f)
    print(f"Loaded ontology with {len(list(ont.terms()))} terms")
    return ont

ont = init_ontology()

parent_map = {term.id: [p.id for p in term.superclasses(distance=1)] for term in ont.terms()}
label_map = {term.id: term.name for term in ont.terms()}

_lineage_memo = {}

def _build_lineage_paths(hp_id, seen=None):
    if seen is None:
        seen = set()
    if hp_id in seen:
        return []
    seen = seen | {hp_id}
    if hp_id in _lineage_memo:
        return _lineage_memo[hp_id]
    if hp_id == ROOT_ID:
        paths = [[ROOT_ID]]
    else:
        parents = parent_map.get(hp_id, [])
        if not parents:
            paths = [[ROOT_ID, hp_id]]
        else:
            paths = []
            for p in parents:
                for ppath in _build_lineage_paths(p, seen):
                    paths.append(ppath + [hp_id])
    _lineage_memo[hp_id] = paths
    return paths

CLEAN_ABNORMALITY = re.compile(r'(?i)^Abnormality of(?: the)?\s*')

def _sort_by_numeric(entries):
    def key_fn(e):
        digs = ''.join(filter(str.isdigit, e))
        return int(digs) if digs else float('inf')
    return sorted(entries, key=key_fn)

def build_hpo_dataframe(limit=None):
    terms = list(ont.terms())[:limit] if limit else list(ont.terms())
    records = []
    for term in tqdm(terms, desc="Building HPO DataFrame", unit="term"):
        hp_id = term.id
        label = term.name
        definition = term.definition or ""
        synonyms = [syn.description for syn in term.synonyms]
        alt_ids = _sort_by_numeric(list(term.alternate_ids))
        snomedct, umls = [], []
        for xr in term.xrefs:
            txt = str(xr)
            m = re.search(r"'(.+?:.+?)'", txt)
            ent = m.group(1) if m else txt
            pre, _, _ = ent.partition(':')
            if pre.upper() == 'UMLS':
                umls.append(ent)
            elif pre.upper().startswith('SNOMED'):
                snomedct.append(ent)
        snomedct = _sort_by_numeric(snomedct)
        umls = _sort_by_numeric(umls)
        paths = _build_lineage_paths(hp_id) or [[ROOT_ID, hp_id]]
        for path_ids in paths:
            lineage_str = " -> ".join(f"{label_map[i]} ({i})" for i in path_ids)
            if PHENO_ID in path_ids:
                idx = path_ids.index(PHENO_ID)
                organ = label_map.get(path_ids[idx + 1], "Other") if idx + 1 < len(path_ids) else "Other"
            else:
                organ = "Other"
            organ_system = CLEAN_ABNORMALITY.sub("", organ).title()
            for phrase in [label] + synonyms:
                if not phrase:
                    continue
                clean_phrase = phrase.title()
                records.append({
                    "hp_id": hp_id,
                    "phrase": clean_phrase,
                    "organ_system": organ_system,
                    "lineage": lineage_str,
                    "definition": definition,
                    "alt_ids": ";".join(alt_ids),
                    "snomedct": ";".join(snomedct),
                    "umls": ";".join(umls),
                })
    return pd.DataFrame(records, columns=[
        "hp_id", "phrase", "organ_system", "lineage",
        "definition", "alt_ids", "snomedct", "umls"
    ])

PAT = re.compile(r'\s*\([^)]*\)\s*')

def clean_text(txt):
    txt = PAT.sub(' ', txt)
    txt = re.sub(r'\s+', ' ', txt).strip().lower()
    txt = re.sub(r'[^\w\s]+$', '', txt)
    return txt

def vectorize_dataframe(df, meta_out, vec_out):
    print(f"Loading model: {settings.embedding_model}")
    model = SentenceTransformer(settings.embedding_model)
    precision = np.float16 if settings.hpo_embedding_precision == "float16" else np.float32

    NEG_PATTERN = re.compile(r'\b(?:decreas(?:e|ed|ing)?|loss(?:es)?|hypo[-]?\w+)\b', re.IGNORECASE)
    POS_PATTERN = re.compile(r'\b(?:increas(?:e|ed|ing)?|gain(?:s|ed)?|hyper[-]?\w+)\b', re.IGNORECASE)

    constants = {}
    entries = []
    embs = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Embedding rows", unit="row"):
        info = clean_text(row.phrase)
        direction = 0
        if NEG_PATTERN.search(info):
            direction = -1
        elif POS_PATTERN.search(info):
            direction = 1
        vec = model.encode(info, convert_to_numpy=True)
        entries.append({'hp_id': row.hp_id, 'info': info, 'direction': direction})
        if row.hp_id not in constants:
            constants[row.hp_id] = {
                'organ_system': row.organ_system,
                'lineage': row.lineage,
                'definition': row.definition,
                'alt_ids': row.alt_ids,
                'snomedct': row.snomedct,
                'umls': row.umls
            }
        embs.append(vec.astype(precision))

    emb_matrix = np.vstack(embs)
    combined = {'constants': constants, 'entries': entries}
    with open(meta_out, 'w') as f:
        json.dump(combined, f, separators=(',', ':'))
    np.savez_compressed(vec_out, emb=emb_matrix)
    print(f"Saved {len(entries)} embeddings -> {meta_out}, {vec_out}")

if __name__ == '__main__':
    df = build_hpo_dataframe()
    df.to_csv(settings.hpo_terms_csv, index=False)
    print(f"Built DataFrame with {len(df)} rows -> {settings.hpo_terms_csv}")
    vectorize_dataframe(df, meta_out=settings.meta_path, vec_out=settings.vec_path)
