# pipline_V3 cleanup manifest

V3 已整理为一个总入口和三个底层模块，避免根目录散落 `bin/`、`config/`、多个旧 API。

## 保留结构

- `complete_pipeline/`
  - 唯一 API 和总流程入口。
- `modules/phasing_beagle_refsupport/`
  - Beagle phasing/ref-support 核心脚本。
- `modules/vcf_preprocessing/`
  - VAF、CRE/cCRE、GENCODE ncRNA 注释脚本与资源。
- `modules/pseudogene_annotation/`
  - 假基因注释模块。
- `modules/vep_runner/`
  - VEP runner 主脚本和配置。

## 已删除/收敛

- 根目录旧 `api/`、`bin/`、`config/`。
- 旧 8000 API 副本和 `serve_api.sh`。
- phasing 自带旧 API/Docker 包装。
- standalone preprocessing/regulatory API。
- 当前总流程不直接调用的旧文档副本、缓存、日志、测试输出。

## 当前唯一 API

```bash
FULL_PIPELINE_API_PORT=18080 /mnt/workspace/wangzilu1/pipline_V3/complete_pipeline/start_full_pipeline_api.sh
```

## 最新收敛

- 已删除 `complete_pipeline/scripts/run_pseudogene_annotation.sh`。
- 假基因注释调用、bgzip 压缩和 tabix/bcftools 建索引逻辑已并入 `complete_pipeline/run_full_pipeline.sh`。
