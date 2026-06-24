#!/usr/bin/env python3
"""
Script to clean duplicate variants from database.

Usage:
    python scripts/clean_duplicate_variants.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.session import DATABASE_URL

def clean_duplicates():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Finding duplicate variants...")
    
    result = session.execute(text("""
        SELECT chromosome, position, ref, alt, vcf_file_id, COUNT(*) as cnt
        FROM variants
        GROUP BY chromosome, position, ref, alt, vcf_file_id
        HAVING cnt > 1
    """))
    
    duplicates = result.fetchall()
    
    if not duplicates:
        print("No duplicates found.")
        return
    
    print(f"Found {len(duplicates)} groups of duplicates")
    
    deleted_count = 0
    
    for dup in duplicates:
        chrom, pos, ref, alt, vcf_id, cnt = dup
        
        keep_result = session.execute(text("""
            SELECT id FROM variants
            WHERE chromosome = :chrom AND position = :pos 
              AND ref = :ref AND alt = :alt AND vcf_file_id = :vcf_id
            ORDER BY id ASC
            LIMIT 1
        """), {"chrom": chrom, "pos": pos, "ref": ref, "alt": alt, "vcf_id": vcf_id})
        
        keep_row = keep_result.fetchone()
        if not keep_row:
            continue
        keep_id = keep_row[0]
        
        delete_result = session.execute(text("""
            DELETE FROM variants
            WHERE chromosome = :chrom AND position = :pos 
              AND ref = :ref AND alt = :alt AND vcf_file_id = :vcf_id
              AND id != :keep_id
        """), {"chrom": chrom, "pos": pos, "ref": ref, "alt": alt, "vcf_id": vcf_id, "keep_id": keep_id})
        
        deleted_count += delete_result.rowcount
    
    session.commit()
    print(f"Deleted {deleted_count} duplicate variants")
    
    session.close()
    engine.dispose()

def recreate_table_with_constraint():
    engine = create_engine(DATABASE_URL)
    
    print("Recreating variants table with unique constraint...")
    
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS variants_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chromosome VARCHAR(10) NOT NULL,
                position INTEGER NOT NULL,
                ref VARCHAR(512) NOT NULL,
                alt VARCHAR(512) NOT NULL,
                variant_type VARCHAR(50) NOT NULL,
                quality FLOAT,
                filter_status VARCHAR(50),
                info_field TEXT,
                gene VARCHAR(100),
                vcf_file_id INTEGER NOT NULL,
                hgvs_c VARCHAR(255),
                hgvs_p VARCHAR(255),
                consequence VARCHAR(200),
                impact VARCHAR(50),
                transcript VARCHAR(50),
                all_genes VARCHAR(500),
                cdna_position VARCHAR(50),
                cds_position VARCHAR(50),
                protein_position VARCHAR(50),
                amino_acids VARCHAR(100),
                codons VARCHAR(100),
                exon VARCHAR(50),
                intron VARCHAR(50),
                strand VARCHAR(10),
                protein_domains VARCHAR(500),
                revel_score FLOAT,
                cadd FLOAT,
                spliceai_ds_max FLOAT,
                spliceai_type VARCHAR(50),
                loftee_lof_flag VARCHAR(50),
                loftee_lof_filter VARCHAR(200),
                clinvar_significance VARCHAR(100),
                clinvar_review_status VARCHAR(200),
                clinvar_star_rating INTEGER,
                sift VARCHAR(100),
                polyphen VARCHAR(100),
                gnomad_popmax_af FLOAT,
                gnomad_eas_af FLOAT,
                gnomad_nhomalt INTEGER,
                pathogenic_rank VARCHAR(50),
                evidence_summary TEXT,
                vep_annotated INTEGER DEFAULT 0,
                CONSTRAINT uix_variant_unique UNIQUE (chromosome, position, ref, alt, vcf_file_id)
            )
        """))
        
        conn.execute(text("""
            INSERT INTO variants_new SELECT * FROM variants
        """))
        
        conn.execute(text("DROP TABLE variants"))
        
        conn.execute(text("ALTER TABLE variants_new RENAME TO variants"))
        
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_variants_chromosome ON variants(chromosome)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_variants_position ON variants(position)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_variants_variant_type ON variants(variant_type)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_variants_gene ON variants(gene)"))
        
        conn.commit()
    
    print("Table recreated with unique constraint.")
    engine.dispose()

if __name__ == "__main__":
    clean_duplicates()
    recreate_table_with_constraint()
    print("Done!")
