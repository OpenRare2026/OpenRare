# 外部数据库配置说明

`external_data/` 是运行时数据库目录，整体由 `.gitignore` 排除，不上传 GitHub。程序只读取配置声明的路径，不在源码中写死服务器目录。

## 目录结构

```text
external_data/
├── hpo/
│   ├── hp.obo
│   ├── phenotype.hpoa
│   └── genes_to_disease.txt
├── hgnc/
│   └── hgnc_complete_set.txt
├── mondo/
│   └── mondo-rare.obo
├── omim/
│   └── omim_20250411.sqlite3
├── orphanet/
│   └── Orphapackets/
└── indexes/
    └── orpha_gene_profiles.pkl
```

路径由 `config/paths.toml` 配置。首次部署可执行：

```bash
cp config/paths.example.toml config/paths.toml
pixi run check-paths
```

## 数据清单

| 数据源 | 当前版本 | 当前大小 | 必需 | 数据链接 | 官方来源 |
|---|---:|---:|---|---|---|
| HPO ontology | 2026-02-16 | 10.2 MB | 是 | `https://purl.obolibrary.org/obo/hp.obo` | [HPO official releases](https://github.com/obophenotype/human-phenotype-ontology/releases) |
| HPO disease annotations | 2026-02-16 | 33.6 MB | 是 | `http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa` | [HPO official releases](https://github.com/obophenotype/human-phenotype-ontology/releases) |
| HPO gene-disease associations | 2026-02-16 | 1.4 MB | 是 | `http://purl.obolibrary.org/obo/hp/hpoa/genes_to_disease.txt` | [HPO GitHub releases](https://github.com/obophenotype/human-phenotype-ontology/releases) |
| HGNC complete set | 2026-05-27 | 16.0 MB | 是 | `https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt` | [HGNC downloads](https://www.genenames.org/download/custom/) |
| MONDO rare subset | 2026-05-05 | 31.8 MB | 是 | `http://purl.obolibrary.org/obo/mondo/subsets/mondo-rare.obo` | [MONDO downloads](https://mondo.monarchinitiative.org/pages/download/) |
| OMIM SQLite | 2025-04-11 | 311.6 MB | 是 | `需OMIM注册获取` | [OMIM downloads](https://www.omim.org/downloads/) |
| Orphapackets | 2026-05-29 | 60 MB | 是 | `https://github.com/Orphanet/orphapacket/tree/master/yaml` | [Orphadata](https://www.orphadata.com/) |
| Orphanet gene profile index | 由 Orphapackets 派生 | 9.0 MB | 推荐 | `首次运行模块脚本时自动生成` | 本项目生成 |

OMIM 数据受许可条款约束，必须由有权限的用户从官方渠道获取，不能随 GitHub 仓库分发。

## Orphanet 索引生成

`external_data/indexes/orpha_gene_profiles.pkl` 不是官方下载文件，而是由本项目根据 Orphapackets YAML 和 HGNC 基因命名数据生成的派生索引。评分时若该文件存在，程序直接读取索引，避免每次遍历全部 YAML。

### 生成内容

索引使用 Python pickle 保存以下内容：

| 键 | 内容 |
|---|---|
| `version` | 索引结构版本，当前为 `1` |
| `source_dir` | 生成时使用的 Orphapacket YAML 逻辑路径 |
| `gene_profiles` | 按 HGNC 归一化基因组织的 Orphanet disease-HPO profile |
| `orpha_to_omim_gene_refs` | Orphanet 疾病到 OMIM 基因引用的映射 |

pickle 文件只能从可信来源加载。不要使用第三方提供、来源不明的 `.pkl` 文件。

### 前置条件

1. 完成 `pixi install`。
2. 复制并检查相对路径配置：

   ```bash
   cp config/paths.example.toml config/paths.toml
   pixi run check-paths
   ```

   如果正式索引尚未生成，`orphanet_index` 显示 `MISSING` 属于预期情况；其余数据项必须为 `OK`。

3. Orphapacket YAML 应位于：

   ```text
   external_data/orphanet/Orphapackets/orphapacket/yaml/ORPHApacket_*.yaml
   ```

4. HGNC 文件应位于 `external_data/hgnc/hgnc_complete_set.txt`，用于统一正式基因符号、旧符号和别名。
5. `external_data/indexes/` 必须可写。完整索引生成时不要设置 `--max-orpha-files`；该参数非零时只用于调试，不会生成完整索引。

### 安全生成新索引

先写入新的临时索引文件，不直接覆盖生产索引：

```bash
mkdir -p external_data/indexes

pixi run python src/phenotype_hpo_score.py \
  --config config/paths.toml \
  --input-csv examples/test.P002.csv \
  --hpo-file examples/hpo_test.txt \
  --outdir runtime/index-build-validation \
  --orpha-index external_data/indexes/orpha_gene_profiles.new.pkl \
  --rebuild-orpha-index
```

该命令会：

1. 读取所有 `ORPHApacket_*.yaml`。
2. 使用 HGNC 数据归一化基因符号。
3. 汇总 Orphanet disease-gene-HPO profile 和 OMIM 引用。
4. 先写入 `orpha_gene_profiles.new.pkl.tmp`，完成后原子替换为 `orpha_gene_profiles.new.pkl`。
5. 使用新索引继续运行示例评分，将验证结果写入 `runtime/index-build-validation/`。

### 校验索引

检查文件大小和校验值：

```bash
ls -lh external_data/indexes/orpha_gene_profiles.new.pkl
sha256sum external_data/indexes/orpha_gene_profiles.new.pkl
```

pickle 内含项目的 `DiseaseProfile` 对象，不建议用通用 Python 单行命令直接反序列化。使用不带 `--rebuild-orpha-index` 的第二次评分确认新文件可以重新加载：

```bash
pixi run python src/phenotype_hpo_score.py \
  --config config/paths.toml \
  --input-csv examples/test.P002.csv \
  --hpo-file examples/hpo_test.txt \
  --outdir runtime/index-read-validation \
  --orpha-index external_data/indexes/orpha_gene_profiles.new.pkl
```

确认两次示例评分结果存在：

```bash
test -s runtime/index-build-validation/gene_phenotype_score.csv
test -s runtime/index-build-validation/variant_phenotype_score.csv
test -s runtime/index-read-validation/gene_phenotype_score.csv
test -s runtime/index-read-validation/variant_phenotype_score.csv
```

### 发布索引

确认 API 当前没有运行或排队任务后，再替换正式索引：

```bash
curl -s http://127.0.0.1:7773/queue
mv external_data/indexes/orpha_gene_profiles.new.pkl \
  external_data/indexes/orpha_gene_profiles.pkl
pixi run check-paths
```

当前服务器的正式索引可能是指向共享文件的相对软链接。上述 `mv` 会替换新项目中的软链接本身，不会修改软链接原目标；发布前仍应确认这是预期行为。

生成完成后清理评分验证结果和异常残留的临时文件：

```bash
rm -rf runtime/index-build-validation runtime/index-read-validation
rm -f external_data/indexes/orpha_gene_profiles.new.pkl.tmp
```

建议记录 Orphapackets 数据版本、HGNC 文件日期、索引 SHA-256 和生成日期。数据库升级后应重新生成并复测索引。索引和原始数据库均由 `.gitignore` 排除，不上传 GitHub。


## 配置项

| 配置键 | 用途 |
|---|---|
| `runtime_root` | API 任务、命令行结果及运行时文件根目录 |
| `default_input_csv` | 默认测试变异文件 |
| `default_hpo_file` | 默认测试 HPO 文件 |
| `hpo_ontology` | HPO 层级图谱 |
| `hpo_annotations` | disease-HPO 注释及 IC 计算输入 |
| `gene_disease_associations` | gene-disease 关联 |
| `hgnc_symbols` | 基因符号、别名及历史符号归一化 |
| `mondo_ontology` | OMIM/Orphanet 疾病等价映射 |
| `omim_database` | OMIM 本地 SQLite 数据库 |
| `orphanet_packets` | Orphanet YAML 原始数据 |
| `orphanet_index` | Orphanet 预计算基因表型索引 |
