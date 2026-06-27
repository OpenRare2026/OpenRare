# V3 完整流程主程序说明

> 完整架构和数据资源下载说明见上一层 `../README.md`。本文件保留主程序/API 的详细调用说明。


本目录包含 FastAPI 服务（`full_pipeline_api.py`）与 API 任务目录，负责把 liftover（可选）、phasing、VCF 前处理、假基因注释、VEP runner、VCF INFO 回填、GENOS-VarRisk 注释、HLA 过滤串成一个完整流程。

主程序：

```bash
scripts/run_full_pipeline.sh
```

API 服务：

```bash
pixi run api
```

## Pixi 环境（推荐）

本模块提供 [`pixi.toml`](../pixi.toml)，通过 bioconda `ensembl-vep`（115.x）与 bcftools、openjdk 等统一管理运行环境。详见 [`README.md`](../README.md) 中的 Pixi 与环境变量说明。

```bash
cd /path/to/OpenRare/modules/pipeline
pixi install
pixi run bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/input.vcf \
  --out-dir /path/to/output_dir \
  --fork 4
```

## 流程顺序

1. `00_liftover`（可选）
   - 脚本：`modules/vcf_preprocessing/liftover_grch37/scripts/liftover_vcf.py`
   - 触发：`--input-assembly GRCh37` 或 `auto` 检测到 GRCh37
   - 输出：`00_liftover/output/output.grch38.norm.vcf.gz`

2. `01_phasing`（可 `--phasing no` 跳过）
   - 脚本：`modules/phasing_beagle_refsupport/scripts/run_beagle_refsupport_pipeline.sh`
   - 功能：Beagle + CHN reference panel phasing/ref-support。
   - 输出：`*.original_sites.beagle_phase_merged.refsupport.vcf.gz`

3. `02_vcf_preprocessing`（`--vaf` / `--regulatory-annotation` / `--ncrna-annotation` 可单独 `no`）
   - 脚本：`modules/vcf_preprocessing/run_vcf_preprocessing.sh`
   - 功能：VAF 写入 INFO、ENCODE SCREEN cCRE 注释、GENCODE ncRNA 注释。
   - 输出：`preprocessed.regulatory.vcf.gz`

4. `03_pseudogene_annotation`（可 `--pseudogene-annotation no` 跳过）
   - 脚本：`modules/pseudogene_annotation/scripts/annotate_pseudogene.py`
   - 功能：假基因注释，增加 `is_pseudogene`、`pseudogene_name`、`pseudogene_source` INFO 字段。

5. `04_vep`
   - 脚本：`modules/vep_runner/scripts/run_vep_to_csv.py`
   - 输出：`04_vep/vep_output.base.csv`

6. `05_vcf_info_to_csv`
   - 脚本：`modules/vcf_info_to_csv/scripts/add_vcf_info_to_vep_csv.py`
   - 输出：`05_vcf_info_to_csv/vep_output.with_info.csv`

7. `06_genos_evee_annotation`
   - 脚本：`modules/genos_evee_annotation/scripts/add_genos_evee_to_csv.py`
   - 输出：`06_genos_evee_annotation/vep_output.with_genos_evee.csv`

8. `07_hla_filter`（可 `--hla-filter no` 跳过）
   - 脚本：`modules/hla_filter/scripts/filter_hla_region_csv.py`
   - 功能：删除 GRCh38 HLA/MHC 区（`chr6:28477797-33448354`）行
   - 输出：`07_hla_filter/vep_output.no_hla.csv`（**默认最终 CSV**）

## 推荐最小调用

日常给大系统调用时，只需要传输入、输出和可选 fork/HPO。

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/input.vcf.gz \
  --out-dir /path/to/output_dir \
  --fork 4
```

有患者 HPO 时：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/input.vcf.gz \
  --out-dir /path/to/output_dir \
  --fork 4 \
  --hpo-id HP:0001250
```

`--fork` 可不传，默认 `1`。`--hpo-id` 可不传；传入后用于 phenotype-aware transcript selection。

## 命令行参数总表

| 参数 | 是否常用 | 默认值 | 说明 |
|---|---:|---|---|
| `--input-vcf FILE` | 是，必填 | 无 | 输入患者 VCF。支持 `.vcf` 和 `.vcf.gz`；未压缩 `.vcf` 会自动 bgzip 压缩并建索引。 |
| `--out-dir DIR` | 是，必填 | 无 | 输出目录。主程序会在其中创建 `00_input` 到 `07_hla_filter` 等子目录。 |
| `--fork N` | 是，可选 | `1` | VEP fork 数。大样本可适当调高，例如 `4`、`8`、`16`。 |
| `--hpo-id ID` | 是，可选 | 空 | 患者 HPO ID，例如 `HP:0001250`。支持逗号分隔多个 ID。 |
| `--phasing yes\|no` | 是，可选 | `yes` | 是否运行 Beagle phasing。 |
| `--vaf yes\|no` | 是，可选 | `yes` | 是否计算 VAF/REF_DP/ALT_DP。 |
| `--regulatory-annotation yes\|no` | 是，可选 | `yes` | 是否运行 cCRE 调控区注释。 |
| `--ncrna-annotation yes\|no` | 是，可选 | `yes` | 是否运行 ncRNA 注释。 |
| `--pseudogene-annotation yes\|no` | 是，可选 | `yes` | 是否运行假基因注释。 |
| `--hla-filter yes\|no` | 是，可选 | `yes` | 是否从最终宽表删除 HLA/MHC 区行。 |
| `--input-assembly SPEC` | 高级覆盖 | `auto` | `auto` / `GRCh37` / `GRCh38`；GRCh37 时在 phasing 前 liftover。 |
| `--sample-id ID` | 高级覆盖 | `auto` | 样本名。默认由 phasing 模块自动识别；特殊情况下可手动指定。 |
| `--chromosomes SPEC` | 高级覆盖 | `1-22` | 要运行的染色体。示例：`22`、`1`、`1-22`、`1,3,5`。测试小 VCF 时常用 `1` 或 `22`。 |
| `--ref-dir DIR` | 高级覆盖 | `$FULL_PIPELINE_REF_DIR`（默认见主 README） | Beagle CHN reference panel 目录。 |
| `--beagle-jar FILE` | 高级覆盖 | `$FULL_PIPELINE_BEAGLE_JAR`（默认见主 README） | Beagle jar 路径。 |
| `--ccre-bed FILE` | 高级覆盖 | V3 内置 cCRE BED | ENCODE SCREEN cCRE slim BED.GZ。 |
| `--ncrna-bed FILE` | 高级覆盖 | V3 内置 ncRNA BED | GENCODE ncRNA slim BED.GZ。 |
| `--chr-jobs N` | 高级覆盖 | `1` | phasing 阶段染色体并发数。 |
| `--beagle-threads N` | 高级覆盖 | `4` | 每个 Beagle 进程线程数。 |
| `--java-heap-gb N` | 高级覆盖 | `12` | 每个 Beagle 进程 Java heap，单位 GB。 |
| `--java-bin PATH` | 高级覆盖 | `$JAVA_BIN`（默认 `java`，pixi 提供 openjdk） | Beagle 使用的 Java 可执行文件。 |
| `--top-k-transcripts N` | 高级覆盖 | `5` | 每个 variant-gene 保留的转录本数量。 |
| `--clinical-tissue NAME` | 高级覆盖 | 空 | 手动传入 GTEx tissue，用于转录本表达加权；通常优先使用 `--hpo-id`。 |
| `--keep-raw-vep yes|no` | 高级覆盖 | `yes` | 是否保留 VEP 原始 TSV：`04_vep/raw_vep.tsv`。 |
| `--dry-run` | 调试 | 关闭 | 只打印将要执行的命令，不实际运行。 |

## 高级覆盖规则

主程序已经写入一套默认参数，普通调用不需要传高级参数。只有当 API 或命令行显式传入高级参数时，才会覆盖默认值。

示例：默认跑 `1-22`：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/input.vcf.gz \
  --out-dir /path/to/output_dir
```

只跑 chr1：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/input.vcf.gz \
  --out-dir /path/to/output_dir \
  --chromosomes 1
```

只跑 chr22：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/input.vcf.gz \
  --out-dir /path/to/output_dir \
  --chromosomes 22
```

多个染色体：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf /path/to/input.vcf.gz \
  --out-dir /path/to/output_dir \
  --chromosomes 1,3,5
```

## API 启动

默认端口是 `18081`：

```bash
pixi run api
```

指定端口：

```bash
FULL_PIPELINE_API_PORT=18081 \
  pixi run api
```

指定 API job 目录，适合在 V3 外部干净目录测试或被大系统收录：

```bash
FULL_PIPELINE_API_JOBS_DIR=/path/to/api_jobs \
FULL_PIPELINE_API_PORT=18081 \
  pixi run api
```

## API 接口

| 方法 | 路径 | 功能 |
|---|---|---|
| `GET` | `/health` | 查看服务状态、默认资源路径、主程序路径。 |
| `POST` | `/run` | JSON 方式提交全流程任务，`input_vcf` 是服务器上的文件路径。后台异步执行，立即返回 `job_id`。 |
| `POST` | `/run-upload` | multipart/form-data 上传 VCF 文件并提交全流程任务，适合大系统用 `curl -F` 直接传文件。 |
| `GET` | `/jobs/{job_id}` | 查询任务状态、命令、输出目录、summary。 |
| `GET` | `/jobs/{job_id}/log` | 查看该任务的运行日志。 |

## API 最小请求

如果在工作站本机调用，用 `127.0.0.1`；如果需要从外部机器访问，并且网络/防火墙允许，也可以把 URL 改成 `http://172.27.206.113:18081/run`。

```bash
curl -X POST http://127.0.0.1:18081/run \
  -H 'Content-Type: application/json' \
  -d '{
    "input_vcf": "/path/to/input.vcf.gz",
    "output_dir": "/path/to/output_dir",
    "fork": 4
  }'
```

带患者 HPO：

```bash
curl -X POST http://127.0.0.1:18081/run \
  -H 'Content-Type: application/json' \
  -d '{
    "input_vcf": "/path/to/input.vcf.gz",
    "output_dir": "/path/to/output_dir",
    "fork": 4,
    "hpo_id": "HP:0001250"
  }'
```

上传文件调用，使用 `curl -F`：

```bash
curl -X POST http://127.0.0.1:18081/run-upload \
  -F 'input_vcf=@/path/to/input.vcf.gz' \
  -F 'output_dir=/path/to/output_dir' \
  -F 'fork=4' \
  -F 'hpo_id=HP:0001250'
```

HPO 也可以用 TXT 文件上传，txt 支持一行一个 HPO，或用逗号、空格、分号分隔：

```bash
curl -X POST http://127.0.0.1:18081/run-upload \
  -F 'input_vcf=@/path/to/input.vcf.gz' \
  -F 'output_dir=/path/to/output_dir' \
  -F 'fork=4' \
  -F 'hpo_file=@/path/to/hpo.txt'
```

也可以同时传 `hpo_id` 和 `hpo_file`，服务会自动合并为逗号分隔的 HPO ID 列表。

公网调用时，如果网络/防火墙允许，可以改成：

```bash
curl -X POST http://172.27.206.113:18081/run-upload \
  -F 'input_vcf=@/path/to/input.vcf.gz' \
  -F 'output_dir=/path/to/output_dir' \
  -F 'fork=4'
```

`/run-upload` 支持和 `/run` 相同的常规字段与高级覆盖字段；区别是 `input_vcf` 在上传接口中是文件字段，不是路径字符串。上传后的文件会保存到 API job 目录下的 `input/` 子目录，并作为主流程输入。

API 会返回：

```json
{
  "job_id": "...",
  "status": "queued",
  "status_url": "/jobs/<job_id>",
  "output_dir": "/path/to/output_dir"
}
```

查询状态：

```bash
curl http://127.0.0.1:18081/jobs/<job_id>
```

查看日志：

```bash
curl http://127.0.0.1:18081/jobs/<job_id>/log
```

## API 高级覆盖字段

API 的字段和主程序参数一一对应。常规字段和高级覆盖字段可以在 JSON `/run` 里传，也可以在上传接口 `/run-upload` 里用 `-F` 传。

| API 字段 | 对应命令行参数 | 是否常用 | 说明 |
|---|---|---:|---|
| `input_vcf` | `--input-vcf` | 是，必填 | 输入 VCF/VCF.GZ。 |
| `output_dir` | `--out-dir` | 是，可选 | 输出目录；不传则使用 API job 默认输出目录。 |
| `fork` | `--fork` | 是，可选 | VEP fork 数，默认 1。 |
| `hpo_id` | `--hpo-id` | 是，可选 | 患者 HPO ID，支持逗号分隔多个 ID。 |
| `phasing` | `--phasing` | 是，可选 | 是否运行 Beagle phasing，默认 `yes`。 |
| `vaf` | `--vaf` | 是，可选 | 是否计算 VAF，默认 `yes`。 |
| `regulatory_annotation` | `--regulatory-annotation` | 是，可选 | 是否运行 cCRE 注释，默认 `yes`。 |
| `ncrna_annotation` | `--ncrna-annotation` | 是，可选 | 是否运行 ncRNA 注释，默认 `yes`。 |
| `pseudogene_annotation` | `--pseudogene-annotation` | 是，可选 | 是否运行假基因注释，默认 `yes`。 |
| `hla_filter` | `--hla-filter` | 是，可选 | 是否删除 HLA/MHC 区行，默认 `yes`。 |
| `input_assembly` | `--input-assembly` | 高级覆盖 | `auto` / `GRCh37` / `GRCh38`。 |
| `hpo_file` | `--hpo-id` | 是，可选 | 仅 `/run-upload` 支持，上传 TXT 后自动解析并合并到 `hpo_id`。 |
| `sample_id` | `--sample-id` | 高级覆盖 | 样本名，默认 `auto`。 |
| `chromosomes` | `--chromosomes` | 高级覆盖 | 覆盖默认 `1-22`。例如测试 VCF 只有 chr1 时传 `"1"`。 |
| `ref_dir` | `--ref-dir` | 高级覆盖 | CHN reference panel 目录。 |
| `beagle_jar` | `--beagle-jar` | 高级覆盖 | Beagle jar 路径。 |
| `ccre_bed` | `--ccre-bed` | 高级覆盖 | cCRE BED.GZ。 |
| `ncrna_bed` | `--ncrna-bed` | 高级覆盖 | ncRNA BED.GZ。 |
| `chr_jobs` | `--chr-jobs` | 高级覆盖 | phasing 染色体并发数。 |
| `beagle_threads` | `--beagle-threads` | 高级覆盖 | 每个 Beagle 进程线程数。 |
| `java_heap_gb` | `--java-heap-gb` | 高级覆盖 | Beagle Java heap，单位 GB。 |
| `java_bin` | `--java-bin` | 高级覆盖 | Java 可执行文件。 |
| `top_k_transcripts` | `--top-k-transcripts` | 高级覆盖 | 每个 variant-gene 保留的转录本数量。 |
| `clinical_tissue` | `--clinical-tissue` | 高级覆盖 | 手动传 GTEx tissue。 |
| `keep_raw_vep` | `--keep-raw-vep` | 高级覆盖 | `true` 对应 `yes`，`false` 对应 `no`。 |
| `genos_evee_db` | `--GENOS-VarRisk-db` | 高级覆盖 | GENOS-VarRisk CPRA 数据库路径。 |
| `dry_run` | `--dry-run` | 调试 | 只打印命令，不实际运行。 |

示例：API 只跑 chr1：

```bash
curl -X POST http://127.0.0.1:18081/run \
  -H 'Content-Type: application/json' \
  -d '{
    "input_vcf": "/path/to/input.vcf.gz",
    "output_dir": "/path/to/output_dir",
    "fork": 1,
    "chromosomes": "1"
  }'
```

示例：API dry-run 检查命令：

```bash
curl -X POST http://127.0.0.1:18081/run \
  -H 'Content-Type: application/json' \
  -d '{
    "input_vcf": "/path/to/input.vcf.gz",
    "output_dir": "/path/to/output_dir",
    "fork": 1,
    "chromosomes": "1",
    "dry_run": true
  }'
```

## 输出文件说明

主输出文件：

```text
<out-dir>/07_hla_filter/vep_output.no_hla.csv
```

关键输出：

| 路径 | 说明 |
|---|---|
| `<out-dir>/00_input/*.vcf.gz` | 如果输入是未压缩 `.vcf`，这里保存自动压缩后的 VCF。 |
| `<out-dir>/01_phasing/*.vcf.gz` | phasing/ref-support 后的 VCF。 |
| `<out-dir>/02_vcf_preprocessing/preprocessed.regulatory.vcf.gz` | VAF + CRE/cCRE + ncRNA 注释后的 VCF。 |
| `<out-dir>/03_pseudogene_annotation/preprocessed.pseudogene_annotated.vcf.gz` | 假基因注释后的 VCF。 |
| `<out-dir>/04_vep/vep_output.base.csv` | 04 VEP runner 基础 CSV，不含 VCF INFO 展开列。 |
| `<out-dir>/04_vep/raw_vep.tsv` | VEP 原始 TSV，默认保留。 |
| `<out-dir>/05_vcf_info_to_csv/vep_output.with_info.csv` | 追加 VCF INFO 字段后的 CSV。 |
| `<out-dir>/07_hla_filter/vep_output.no_hla.csv` | 最终宽表（默认 `hla_filter=yes`）。 |
| `<out-dir>/full_pipeline.outputs.tsv` | 汇总每一步关键产物路径。 |
| `<out-dir>/logs/full_pipeline.log` | 全流程日志。 |

## HPO 说明

当前流程不做“文字描述转 HPO”。也就是说，不支持直接输入 `癫痫、发育迟缓` 这类自由文本。

当前支持的是标准 HPO ID：

```text
HP:0001250
```

传入 HPO 后，VEP runner 会执行：

```text
HPO ID -> tissue/organ 映射 -> GTEx 表达组织加权 -> 影响转录本选择排序
```

不传 HPO 时，转录本选择仍然会执行，但不会有 HPO 指导的组织表达加权。

## 输入压缩规则

- `--input-vcf` / API `input_vcf` 支持 `.vcf` 和 `.vcf.gz`。
- 未压缩 `.vcf` 会自动压缩到 `<out-dir>/00_input/*.vcf.gz` 并建立索引。
- 后续 phasing、VCF preprocessing、假基因注释、VEP runner 都使用 `.vcf.gz` 链路执行。

## 自检建议

查看帮助：

```bash
bash scripts/run_full_pipeline.sh --help
```

不实际运行，只检查命令展开：

```bash
bash scripts/run_full_pipeline.sh \
  --input-vcf test/input/P001.genotyper10000.vcf \
  --out-dir /tmp/openrare_v3_dryrun \
  --fork 1 \
  --chromosomes 1 \
  --dry-run
```

API 健康检查：

```bash
curl http://127.0.0.1:18081/health
```
