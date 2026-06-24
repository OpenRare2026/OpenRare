# Beagle phasing / reference support 依赖梳理

来源目录：`/mnt/workspace/changan/1kgp/beagle_pipeline_param`

## 主流程脚本

- `scripts/run_beagle_refsupport_pipeline.sh`
  - 总调度脚本。
  - 输入 patient VCF，按染色体拆分，调用每染色体 worker，并最终合并结果。
- `scripts/process_one_chromosome.sh`
  - 单染色体 worker。
  - 提取 patient 染色体 VCF、抽取参考 panel 相同位点、运行 Beagle no-impute phasing，再合并参考支持信息。
- `scripts/merge_beagle_with_ref_support.py`
  - 将 Beagle phased GT 写回原始 patient 位点。
  - 增加参考 panel 支持相关 INFO 字段，例如是否在参考中、多态/单态、phasing confidence 等。
- `scripts/package_chn_ref.sh`
  - 打包/校验 1000G CHN reference panel 的工具脚本。

## API / Docker 包装

- `api_service/app.py`
  - FastAPI 服务，上传 VCF 后调用 `run_beagle_refsupport_pipeline.sh`。
- `api_service/run_api_docker.sh`
  - Docker 方式启动 API。
- `api_service/test_api_curl.sh`
  - curl 测试脚本。
- `docker/Dockerfile`
  - 命令行 pipeline 镜像。
- `api_service/Dockerfile.api`
  - API 镜像。

## 关键数据依赖

大数据未复制进 V3，只记录路径：

- CHN reference panel：`/mnt/workspace/changan/1kgp/beagle_pipeline_param/packages/CHN_ref/`
  - 命名：`1000G.CHN.chrN.phased.vcf.gz`
  - 索引：`.tbi`
  - 染色体：chr1-chr22
  - 样本数：359
  - 版本说明：1000 Genomes 30x GRCh38 phased panel, CHB + CHS + CDX subset
- 打包文件：`/mnt/workspace/changan/1kgp/beagle_pipeline_param/packages/CHN_ref_1000G_CHN_359_GRCh38_phased.tar.gz`
- Beagle jar 默认位置：`/mnt/workspace/changan/1kgp/beagle.27Feb25.75f.jar`

## 软件依赖

- `bash`
- `python3`
- `java`
- `bcftools`
- `tabix`
- `bgzip`
- Beagle：`beagle.27Feb25.75f.jar`
- FastAPI API 依赖见 `api_service/requirements.txt`

## 输出逻辑

典型最终输出：

- `*.original_sites.beagle_phase_merged.refsupport.vcf.gz`
- `*.original_sites.beagle_phase_merged.refsupport.vcf.gz.tbi`
- `logs/*summary*`
- `logs/*annotation_stats.tsv`
- `beagle_noimpute/*.beagle_phased.noimpute.vcf.gz`
- `reference_subset/*.patient_positions.vcf.gz`

## V3 当前策略

本目录只复制脚本、配置和说明文件，不复制 reference VCF、测试输出和 API 历史运行结果。后续如果要把 phasing 放进主前置流程，建议将 CHN_ref 与 Beagle jar 做成统一 `resources/` 配置项，而不是硬编码到脚本里。
