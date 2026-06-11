# CRE and ncRNA VCF Annotation API

FastAPI service for hg38/GRCh38 VCF annotation with:

- ENCODE SCREEN cCRE regulatory-region overlaps (`REG_*` INFO fields)
- GENCODE v49 non-coding RNA gene overlaps (`NCRNA_*` INFO fields)

The API accepts server-side VCF paths and writes bgzipped/indexed VCF output plus summary TSV files.

## Layout

```text
regulatory_annotation/
├── regulatory_annotation_api.py
├── start_regulatory_api.sh
├── scripts/
├── resources/
└── results/
```

Large annotation resources and generated result files are intentionally ignored by git.

## Prepare Resources

Expected resource files:

```text
resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz
resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz.tbi
resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz
resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz.tbi
```

cCRE resource source:

```text
https://www.encodeproject.org/files/ENCFF420VPZ/@@download/ENCFF420VPZ.bed.gz
```

GENCODE v49 GRCh38 GTF source:

```text
https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_49/gencode.v49.annotation.gtf.gz
```

Prepare cCRE BED:

```bash
python3 scripts/prepare_encode_ccre_bed.py ENCFF420VPZ.bed.gz resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed
sort -k1,1 -k2,2n resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed > /tmp/ccre.slim.bed
mv /tmp/ccre.slim.bed resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed
bgzip -f resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed
tabix -f -p bed resources/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.bed.gz
```

Prepare ncRNA BED:

```bash
python3 scripts/prepare_gencode_ncrna_bed.py gencode.v49.annotation.gtf.gz resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed
sort -k1,1 -k2,2n resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed > /tmp/ncrna.slim.bed
mv /tmp/ncrna.slim.bed resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed
bgzip -f resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed
tabix -f -p bed resources/ncrna/hg38/gencode.v49.ncrna_gene.slim.bed.gz
```

## Start API

```bash
pip install -r requirements.txt
./start_regulatory_api.sh
```

Default service port is `10086`.

## Submit a Job

`input_vcf`, `output_prefix`, `ccre_bed`, and `ncrna_bed` support absolute paths or paths relative to `REG_API_BASE_WORKDIR`.

```bash
curl -X POST http://127.0.0.1:10086/annotate \
  -H 'Content-Type: application/json' \
  -d '{
    "input_vcf": "/mnt/workspace/wangzilu1/test1.vcf",
    "output_prefix": "/mnt/workspace/wangzilu1/regulatory_annotation/results/regulatory/api/test1"
  }'
```

Check status:

```bash
curl http://127.0.0.1:10086/jobs/<job_id>
```

## Output

Output VCF:

```text
<output_prefix>.regulatory.vcf.gz
<output_prefix>.regulatory.vcf.gz.tbi
```

Summary files:

```text
<output_prefix>.regulatory.summary.tsv
<output_prefix>.ncrna.summary.tsv
```

Added INFO fields:

```text
REG_CCRE_ID
REG_CCRE_CLASS
REG_CCRE_COUNT
REG_CCRE_SOURCE
NCRNA_GENE_ID
NCRNA_GENE_NAME
NCRNA_GENE_TYPE
NCRNA_GENE_COUNT
NCRNA_SOURCE
```
