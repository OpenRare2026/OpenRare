from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

GENERIC_PATHWAY_NAMES = frozenset(
    {
        "Signal Transduction",
        "Developmental Biology",
        "Gene expression (Transcription)",
        "Metabolism",
        "Metabolism of proteins",
        "Programmed Cell Death",
        "Immune System",
        "Disease",
    }
)

PATHWAY_QUERY = """
MATCH (re:ReferenceEntity)
WHERE $gene IN re.geneName
MATCH (pe)-[:referenceEntity]->(re)
MATCH (r:ReactionLikeEvent)-[:catalystActivity|input|output|hasComponent*1..3]->(pe)
MATCH (p:Pathway)-[:hasEvent*1..6]->(r)
RETURN DISTINCT p.displayName AS pathway
ORDER BY pathway
LIMIT $limit
"""


def reactome_enabled() -> bool:
    return os.getenv("REACTOME_ENABLED", "1").lower() in ("1", "true", "yes")


def get_reactome_settings() -> dict[str, str]:
    return {
        "uri": os.getenv("REACTOME_NEO4J_URI", "bolt://localhost:7687"),
        "user": os.getenv("REACTOME_NEO4J_USER", "neo4j"),
        "password": os.getenv("REACTOME_NEO4J_PASSWORD", "neo4j"),
        "database": os.getenv("REACTOME_NEO4J_DATABASE", "graph.db"),
    }


def pick_main_pathway(gene_symbol: str, pathways: list[str]) -> str:
    if not pathways:
        return "-"

    gene_upper = gene_symbol.upper()
    signaling_prefix = f"signaling by {gene_upper}".lower()
    for pathway in pathways:
        if pathway.lower().startswith(signaling_prefix):
            return pathway

    for pathway in pathways:
        if gene_upper in pathway.upper():
            return pathway

    specific = [pathway for pathway in pathways if pathway not in GENERIC_PATHWAY_NAMES]
    if specific:
        return specific[0]
    return pathways[0]


@lru_cache(maxsize=1)
def _get_driver():
    from neo4j import GraphDatabase

    settings = get_reactome_settings()
    return GraphDatabase.driver(
        settings["uri"],
        auth=(settings["user"], settings["password"]),
    )


def lookup_gene_pathways(gene_symbol: str, *, limit: int = 20) -> list[str]:
    if not reactome_enabled():
        return []

    settings = get_reactome_settings()
    driver = _get_driver()
    with driver.session(database=settings["database"]) as session:
        result = session.run(
            PATHWAY_QUERY,
            gene=gene_symbol.strip().upper(),
            limit=limit,
        )
        return [record["pathway"] for record in result if record.get("pathway")]


def lookup_main_pathway(gene_symbol: str) -> str:
    try:
        pathways = lookup_gene_pathways(gene_symbol)
        return pick_main_pathway(gene_symbol, pathways)
    except Exception:
        return "-"
