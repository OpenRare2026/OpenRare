# Clean-case 测试说明

以下路径均相对 `pixi_ppi_score/`。测试依赖仓库外部的大输入文件，因此在新机器上运行前需要先准备相同目录或修改请求 JSON。

## Case5

运行：

```bash
pixi run case5-clean
```

输入：

| 用途 | 路径 |
| --- | --- |
| phenotype-gene CSV | `../../input/Case5_gene_phenotype_score.csv` |
| VEP CSV | `../../../pangjiangshuan/vep_runner/tmux_runs/26D01487024_580d86_fork16_hpo_20260612_110118/26D01487024_580d86.vep.csv` |
| HPO | `tests/inputs/case5_hpo.txt` |

输出：

| 用途 | 路径 |
| --- | --- |
| final CSV | `tests/outputs/clean_cases/case5/case5_final_score.csv` |
| PPI CSV | `tests/outputs/clean_cases/case5/case5_ppi_score.csv` |

最近一次验证：

```text
status=completion
count=47319
hpo_count=6
ranked_gene_count=5109
mapped_tissues=["brain","uterus"]
mapped_tissue_counts={"brain":5,"uterus":1}
```

## Case6

运行：

```bash
pixi run case6-clean
```

输入：

| 用途 | 路径 |
| --- | --- |
| phenotype-gene CSV | `../../input/Case6_gene_phenotype_score.csv` |
| clean-case 使用的 VEP CSV | `../../../pangjiangshuan/vep_runner/tmux_runs/25B06715455_89a308_fork16_hpo_20260613_142102/25B06715455_89a308.vep.csv` |
| 原始 liftover VCF 记录 | `../../../changan/grch37_to_grch38_liftover/api_service/runs/25B06715455_89a308/output/output.grch38.vcf.gz` |
| HPO | `tests/inputs/case6_hpo.txt` |

输出：

| 用途 | 路径 |
| --- | --- |
| final CSV | `tests/outputs/clean_cases/case6/case6_final_score.csv` |
| PPI CSV | `tests/outputs/clean_cases/case6/case6_ppi_score.csv` |

最近一次验证：

```text
status=completion
count=47078
hpo_count=2
ranked_gene_count=5106
mapped_tissues=["brain"]
mapped_tissue_counts={"brain":2}
```

说明：clean-case 接口读取 VEP CSV，不直接读取 VCF。Case6 用户提供的 VCF 已记录在上表，实际测试使用同病例对应的 VEP CSV。
