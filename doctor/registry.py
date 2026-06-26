"""Explicit module registry — no dynamic discovery.

Each entry maps a short label to (module_path, check_file_path).
The check_file_path is relative to the repo root and loaded via importlib.util
so hyphens in directory names are not a problem.
"""

MODULES = {
    "pipeline":             "modules/pipeline/check.py",
    "ppi_score":            "modules/pixi_ppi_score/check.py",
    "phenotype_score":      "modules/pixi_phenotype_score/check.py",
    "RAG-HPO":              "modules/pixi_RAG-HPO/check.py",
    "rare_sort":            "modules/pixi_rare_sort_fastapi/check.py",
    "report":               "modules/pixi_report/check.py",
    "RareSystem":           "modules/RareSystem/check.py",
}
