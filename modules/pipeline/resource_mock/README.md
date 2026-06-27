# OpenRare pipeline mock resources

迷你 mock 数据库，用于接口联调、dry/smoke test 和流程连通性验证，不用于真实分析。

包含：

- `regulatory/hg38/encode_screen_v4_grch38_ccre.slim.mock.bed.gz`
- `ncrna/hg38/gencode.v49.ncrna_gene.slim.mock.bed.gz`
- `genos_evee/genos_evee.cpra.mock.tsv.gz`

调用示例（跳过 phasing，使用 mock 注释库）：

```bash
cd /path/to/OpenRare/modules/pipeline
pixi run mock-smoke-test
```

或手动：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf test/input/P001.genotyper10000.vcf \
  --out-dir /tmp/openrare_mock_smoke \
  --chromosomes 1 \
  --phasing no \
  --ccre-bed resource_mock/regulatory/hg38/encode_screen_v4_grch38_ccre.slim.mock.bed.gz \
  --ncrna-bed resource_mock/ncrna/hg38/gencode.v49.ncrna_gene.slim.mock.bed.gz \
  --GENOS-VarRisk-db resource_mock/genos_evee/genos_evee.cpra.mock.tsv.gz \
  --dry-run
```

注意：VEP cache、LoFTEE、CADD、SpliceAI 等大数据库仍使用 `.env` 中的正式路径；此处不提供可替代的 VEP mock cache。
