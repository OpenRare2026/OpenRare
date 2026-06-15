#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DATA_DIR="${RARE_PPI_DATA_DIR:-${PROJECT_DIR}/data}"
LOG_DIR="${SCRIPT_DIR}/logs"
GTEX_V11_SOURCE_DIR="${GTEX_V11_SOURCE_DIR:-${PROJECT_DIR}/data/GTEx/v11}"
GTEX_V11_GCT="GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.gct.gz"
PYTHON_BIN="${RARE_PPI_PYTHON:-${PROJECT_DIR}/ppi_env/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "[ERROR] Python environment not found: $PYTHON_BIN" >&2
  echo "[ERROR] Run ${SCRIPT_DIR}/setup_env.sh first, or set RARE_PPI_PYTHON." >&2
  exit 1
fi
export DATA_DIR
mkdir -p "$DATA_DIR" "$LOG_DIR"
cd "$DATA_DIR" || exit 1

log() {
  printf '[%s] %s\n' "$(date '+%F %T')" "$*"
}

download() {
  local url="$1"
  local out="$2"
  local remote_size
  local local_size
  if [[ -s "$out" ]]; then
    remote_size="$(curl -fLIs --connect-timeout 20 --max-time 60 "$url" \
      | awk 'BEGIN{IGNORECASE=1} /^content-length:/ {gsub(/\r/,"",$2); size=$2} END{print size}')"
    local_size="$(stat -c '%s' "$out")"
    if [[ -n "$remote_size" && "$local_size" -eq "$remote_size" ]]; then
      log "skip existing complete file: $out (${local_size} bytes)"
      return 0
    fi
  fi
  log "download: $out <- $url"
  curl -fL -C - \
    --retry 999 --retry-delay 20 --retry-connrefused \
    --connect-timeout 30 --speed-time 120 --speed-limit 1024 \
    -o "$out" "$url"
}

download_optional() {
  local url="$1"
  local out="$2"
  if ! download "$url" "$out"; then
    log "optional download failed or unavailable: $out"
    return 1
  fi
  return 0
}

unzip_file() {
  local zip="$1"
  if [[ -s "$zip" ]]; then
    log "unzip: $zip"
    unzip -o "$zip" -d "$DATA_DIR"
  fi
}

gunzip_copy() {
  local gz="$1"
  local out="$2"
  if [[ -s "$gz" ]]; then
    log "gunzip copy: $gz -> $out"
    gzip -dc "$gz" > "${out}.tmp" && mv "${out}.tmp" "$out"
  fi
}

download_biomart() {
  local out="ensembl_biomart_export.txt"
  local query="biomart_query.xml"
  cat > "$query" <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query virtualSchemaName="default" formatter="TSV" header="1" uniqueRows="1" count="" datasetConfigVersion="0.6">
  <Dataset name="hsapiens_gene_ensembl" interface="default">
    <Attribute name="ensembl_gene_id" />
    <Attribute name="ensembl_peptide_id" />
    <Attribute name="external_gene_name" />
    <Attribute name="hgnc_symbol" />
  </Dataset>
</Query>
XML
  log "download BioMart export: $out"
  curl -fL \
    --retry 20 --retry-delay 20 --retry-connrefused \
    --connect-timeout 30 --speed-time 120 --speed-limit 1024 \
    --data-urlencode "query@${query}" \
    -o "${out}.tmp" "https://www.ensembl.org/biomart/martservice" \
    && mv "${out}.tmp" "$out" \
    || { rm -f "${out}.tmp"; log "BioMart export failed"; return 1; }
}

get_omim_key() {
  if [[ -n "${OMIM_API_KEY:-}" ]]; then
    printf '%s\n' "$OMIM_API_KEY"
    return 0
  fi
  for key_file in "${SCRIPT_DIR}/omim_api_key.txt" "${SCRIPT_DIR}/api_key.txt"; do
    if [[ -s "$key_file" ]]; then
      awk -F'=' '
        /^[[:space:]]*#/ { next }
        NF {
          value=$NF
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
          if (value != "") { print value; exit }
        }
      ' "$key_file"
      return 0
    fi
  done
  return 1
}

download_omim() {
  download "https://omim.org/static/omim/data/mim2gene.txt" "mim2gene.txt"

  local key
  key="$(get_omim_key || true)"
  if [[ -n "$key" ]]; then
    if download_optional "https://data.omim.org/downloads/${key}/genemap2.txt" "genemap2.txt"; then
      return 0
    fi
  fi

  log "OMIM genemap2.txt was not downloaded. It usually requires an OMIM download key; set OMIM_API_KEY or put it in ${SCRIPT_DIR}/omim_api_key.txt."
}

download_panelapp() {
  log "download PanelApp panel TSV cache -> panelapp_panels.json"
  "$PYTHON_BIN" - <<'PY'
import csv
import io
import json
import os
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

out = os.path.join(os.environ["DATA_DIR"], "panelapp_panels.json")
headers = {"User-Agent": "rare-ppi-local-cache/1.0 (luqi)"}
max_workers = int(os.environ.get("PANELAPP_MAX_WORKERS", "2"))

def fetch_json(url, retries=3):
    last_exc = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_exc = exc
            time.sleep(1 + attempt)
    raise last_exc

def fetch_text(url, retries=2):
    last_exc = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8-sig", errors="replace")
        except Exception as exc:
            last_exc = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                time.sleep(10 * (attempt + 1))
            else:
                time.sleep(1 + attempt)
    raise last_exc

def fetch_panel_list():
    url = "https://panelapp.genomicsengland.co.uk/api/v1/panels/?format=json"
    panels = []
    seen = set()
    while url and url not in seen:
        seen.add(url)
        payload = fetch_json(url)
        if isinstance(payload, dict):
            panels.extend(payload.get("results", []))
            url = payload.get("next")
        elif isinstance(payload, list):
            panels.extend(payload)
            url = None
        else:
            url = None
        time.sleep(0.2)
    return panels

def load_existing():
    if not os.path.exists(out):
        return []
    with open(out, encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        return payload.get("results", [])
    return payload if isinstance(payload, list) else []

existing = load_existing()
panels = existing or fetch_panel_list()
existing_by_id = {panel.get("id"): panel for panel in existing if isinstance(panel, dict) and panel.get("id")}

def needs_download(panel):
    cached = existing_by_id.get(panel.get("id")) if isinstance(panel, dict) else None
    return not (cached and cached.get("genes") and not cached.get("download_error"))

def fetch_panel_tsv(panel):
    panel_id = panel.get("id") if isinstance(panel, dict) else None
    if not panel_id:
        return None
    detail = {k: panel.get(k) for k in [
        "id", "hash_id", "name", "disease_group", "disease_sub_group", "status",
        "version", "version_created", "relevant_disorders", "stats", "types"
    ]}
    detail["download_url"] = f"https://panelapp.genomicsengland.co.uk/panels/{panel_id}/download/01234/"
    detail["genes"] = []
    try:
        text = fetch_text(detail["download_url"])
        reader = csv.DictReader(io.StringIO(text), delimiter="\t")
        for row in reader:
            gene = (row.get("Gene Symbol") or row.get("Entity Name") or "").strip()
            if not gene:
                continue
            detail["genes"].append({
                "gene_symbol": gene,
                "entity_name": (row.get("Entity Name") or "").strip(),
                "entity_type": (row.get("Entity type") or "").strip(),
                "confidence_level": "4" if row.get("Level4") else ("3" if row.get("Level3") else ("2" if row.get("Level2") else "")),
                "phenotypes": (row.get("Phenotypes") or "").strip(),
                "hpo": (row.get("HPO") or "").strip(),
                "omim": (row.get("Omim") or "").strip(),
                "orphanet": (row.get("Orphanet") or "").strip(),
            })
    except Exception as exc:
        detail["download_error"] = str(exc)
    return detail

details_by_id = {}
for panel_id, panel in existing_by_id.items():
    if panel.get("genes") and not panel.get("download_error"):
        details_by_id[panel_id] = panel

targets = [panel for panel in panels if isinstance(panel, dict) and panel.get("id") and needs_download(panel)]
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(fetch_panel_tsv, panel): panel for panel in targets}
    for index, future in enumerate(as_completed(futures), start=1):
        detail = future.result()
        if isinstance(detail, dict) and detail.get("id"):
            details_by_id[detail["id"]] = detail
        if index % 50 == 0:
            print(f"PanelApp TSV panels: {index}/{len(targets)}")

details = [details_by_id[p["id"]] for p in panels if isinstance(p, dict) and p.get("id") in details_by_id]
tmp = out + ".tmp"
with open(tmp, "w", encoding="utf-8") as handle:
    json.dump(details, handle, ensure_ascii=False)
os.replace(tmp, out)
with_genes = sum(1 for panel in details if panel.get("genes"))
gene_links = sum(len(panel.get("genes") or []) for panel in details)
failed = sum(1 for panel in details if panel.get("download_error"))
print(f"PanelApp panel cache: {len(details)} panels, {with_genes} with genes, {gene_links} gene links, {failed} failed")
PY
}

download_depmap() {
  log "download DepMap file index"
  if download "https://depmap.org/portal/api/download/files" "depmap_files.csv"; then
    "$PYTHON_BIN" - <<'PY'
import csv
import os
import subprocess

data_dir = os.environ["DATA_DIR"]
index_path = os.path.join(data_dir, "depmap_files.csv")
targets = ["CRISPRGeneEffect.csv", "Model.csv"]

def row_text(row):
    return " ".join(str(v) for v in row.values())

def row_url(row):
    for value in row.values():
        value = str(value)
        if value.startswith("http://") or value.startswith("https://"):
            return value
    return None

with open(index_path, newline="", encoding="utf-8", errors="ignore") as handle:
    rows = list(csv.DictReader(handle))

for target in targets:
    matches = [r for r in rows if target in row_text(r)]
    if not matches:
        print(f"[DepMap] no match for {target}")
        continue
    matches.sort(key=lambda r: (r.get("release_date", ""), r.get("release", "")), reverse=True)
    url = row_url(matches[0])
    if not url:
        print(f"[DepMap] no URL for {target}")
        continue
    out = os.path.join(data_dir, target)
    print(f"[DepMap] download {target} <- {url}")
    subprocess.run([
        "curl", "-fL", "-C", "-",
        "--retry", "999", "--retry-delay", "20", "--retry-connrefused",
        "--connect-timeout", "30", "--speed-time", "120", "--speed-limit", "1024",
        "-o", out, url
    ], check=False)
PY
  fi
}

download_gtex() {
  if [[ -s "$GTEX_V11_GCT" ]]; then
    log "skip existing GTEx v11 GCT: $GTEX_V11_GCT"
    return 0
  fi

  if [[ -s "${SCRIPT_DIR}/prepare_gtex_v11.py" \
        && -s "${GTEX_V11_SOURCE_DIR}/expression/GTEx_Analysis_2025-08-22_v11_RSEMv1.3.3_transcripts_tpm.txt.gz" \
        && -s "${GTEX_V11_SOURCE_DIR}/metadata/GTEx_Analysis_v11_Annotations_SampleAttributesDS.txt" ]]; then
    log "prepare GTEx v11 gene median GCT from ${GTEX_V11_SOURCE_DIR}"
    if "$PYTHON_BIN" "${SCRIPT_DIR}/prepare_gtex_v11.py" --source-dir "$GTEX_V11_SOURCE_DIR" --data-dir "$DATA_DIR"; then
      [[ -s "$GTEX_V11_GCT" ]] && return 0
    fi
    log "GTEx v11 preparation failed; falling back to official v9/v10/v8 downloads."
  fi

  local v9_url="https://storage.googleapis.com/adult-gtex/bulk-gex/v9/rna-seq/GTEx_Analysis_v9_RNAseq_RNASeQCv1.1.9_gene_median_tpm.gct.gz"
  local v9_out="GTEx_Analysis_v9_RNAseq_RNASeQCv1.1.9_gene_median_tpm.gct.gz"
  if download_optional "$v9_url" "$v9_out"; then
    gunzip_copy "$v9_out" "${v9_out%.gz}"
    return 0
  fi

  log "GTEx v9 exact file was not available at the checked official GCS URL; downloading official v10 and v8 fallback files."
  download "https://storage.googleapis.com/adult-gtex/bulk-gex/v10/rna-seq/GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz" "GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz"
  gunzip_copy "GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz" "GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct"
  download_optional "https://storage.googleapis.com/adult-gtex/bulk-gex/v8/rna-seq/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz" "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz" \
    && gunzip_copy "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz" "GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct"
}

download_ogee() {
  log "OGEE.csv has no verified public direct-download URL in the current official site state; leave ${DATA_DIR}/OGEE.csv in place if you obtain it manually."
}

log "start data download into ${DATA_DIR}"

# Gene ID normalization
download "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt" "hgnc_complete_set.txt"
download_biomart || true
download "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping_selected.tab.gz" "idmapping_selected.tab.gz"
gunzip_copy "idmapping_selected.tab.gz" "idmapping_selected.tab"

# Disease axis D
download_omim || true
download "https://purl.obolibrary.org/obo/hp.obo" "hp.obo"
download "https://purl.obolibrary.org/obo/hp/hpoa/genes_to_phenotype.txt" "genes_to_phenotype.txt"
download "https://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa" "phenotype.hpoa"
download_optional "https://purl.obolibrary.org/obo/hp/hpoa/phenotype_to_anatomy.txt" "phenotype_to_anatomy.txt" || true
download "https://www.orphadata.com/data/xml/en_product6.xml" "en_product6.xml"
download "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz" "variant_summary.txt.gz"
gunzip_copy "variant_summary.txt.gz" "variant_summary.txt"
download_panelapp || log "PanelApp download failed"

# Tissue axis T
download "https://purl.obolibrary.org/obo/uberon.obo" "uberon.obo"
download_gtex
download "https://www.proteinatlas.org/download/tsv/rna_tissue_consensus.tsv.zip" "rna_tissue_consensus.tsv.zip"
unzip_file "rna_tissue_consensus.tsv.zip"
download "https://www.proteinatlas.org/download/tsv/normal_ihc_data.tsv.zip" "normal_ihc_data.tsv.zip"
unzip_file "normal_ihc_data.tsv.zip"
if [[ -s normal_ihc_data.tsv && ! -e normal_tissue.tsv ]]; then
  ln -s normal_ihc_data.tsv normal_tissue.tsv
fi
download_ogee
download_depmap
download "https://reactome.org/download/current/Ensembl2Reactome.txt" "Ensembl2Reactome.txt"
download "https://reactome.org/download/current/ReactomePathwaysRelation.txt" "ReactomePathwaysRelation.txt"

# PPI network required by Network.py
download "https://stringdb-downloads.org/download/protein.info.v12.0/9606.protein.info.v12.0.txt.gz" "9606.protein.info.v12.0.txt.gz"
gunzip_copy "9606.protein.info.v12.0.txt.gz" "9606.protein.info.v12.0.txt"
download "https://stringdb-downloads.org/download/protein.links.detailed.v12.0/9606.protein.links.detailed.v12.0.txt.gz" "9606.protein.links.detailed.v12.0.txt.gz"
gunzip_copy "9606.protein.links.detailed.v12.0.txt.gz" "9606.protein.links.detailed.v12.0.txt"

log "data download script finished"
find "$DATA_DIR" -maxdepth 1 -type f -printf '%f\t%s bytes\n' | sort
