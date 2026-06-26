# Agent 数据准备 Prompt

把下面这段 prompt 给其他 Agent 后，它应该能在一台 Linux 机器上把 PPI 模块外部数据库准备好。

```text
你要为 OpenRare 的 PPI 评分模块准备外部数据库。请按下面步骤执行，不要把下载的数据提交到 Git。

1. 进入仓库中的 modules/pixi_ppi_score。
2. 安装 Pixi 环境：pixi install。
3. 确认数据目录。默认使用 ../../../data；如果要放到其他位置，先设置环境变量：
   export RARE_PPI_DATA_DIR=/absolute/path/to/data
4. 如有 OMIM 下载权限，设置 OMIM_API_KEY。没有 key 时脚本仍会继续，但 genemap2.txt 可能缺失，后续 check-data 会提示。
5. 如已有 GTEx v11 原始文件，把它们放到 $RARE_PPI_DATA_DIR/GTEx/v11：
   - expression/GTEx_Analysis_2025-08-22_v11_RSEMv1.3.3_transcripts_tpm.txt.gz
   - metadata/GTEx_Analysis_v11_Annotations_SampleAttributesDS.txt
   没有这些文件时，脚本会尝试下载官方 GTEx v9/v10/v8 fallback 文件。
6. 运行：pixi run download-data。
7. 运行：pixi run check-data。若仍缺文件，按输出补齐；重点关注 genemap2.txt、GTEx_Analysis_v11_RSEMv1.3.3_gene_median_tpm.gct.gz、CRISPRGeneEffect.csv、Model.csv。
8. 最后运行：pixi run health；要求 missing_file_count 为 0。

请把执行命令、数据目录、缺失文件列表和最终 health JSON 返回给用户。
```

## 注意事项

- 数据下载可能持续较久，`download_data.sh` 使用断点续传和重试，重复运行不会覆盖已经完整下载的文件。
- OMIM 的 `genemap2.txt` 需要合法 API key；没有 key 时需要使用者自行补齐。
- GTEx v11 基因中位 TPM 文件由 `app/prepare_gtex_v11.py` 从本地 GTEx v11 transcript TPM 和 metadata 生成；如果没有这些原始文件，脚本会尽量下载旧版公开 fallback 文件。
- `../../../data`、`output/`、`uploads/` 和 `tests/outputs/` 都是运行数据目录，不应提交到 Git。
