#!/usr/bin/env python3
"""
convert_gtex_simple.py - GTEx v11 TPM 转 Parquet（PyArrow 流式版）

数据说明见同目录 README.md。

在服务器上运行:
  cd modules/pipeline/resource_mock/gtex_preprocess
  python convert_gtex_simple.py
"""

import os
import pandas as pd
import numpy as np
import gzip
import time
import pyarrow as pa
import pyarrow.csv as pv

# ========== 配置路径 ==========
TPM_FILE = "/path/to/GTEx_Analysis_2025-08-22_v11_RSEMv1.3.3_transcripts_tpm.txt.gz"
ANNOTATION_FILE = "/path/to/GTEx_Analysis_v11_Annotations_SampleAttributesDS.txt"
OUTPUT_FILE = "/path/to/gtex_v11_transcript_tpm.parquet"

# PyArrow 每个内存块大小（50MB ≈ 300~600 行 × 2 万列）
BLOCK_SIZE = 50 * 1024 * 1024
# =============================

def main():
    print("=" * 60)
    print("GTEx 数据转换为 Parquet (PyArrow高速版)")
    print("=" * 60)
    total_start = time.time()

    # Step 1: 读取样本注释文件
    print("\n[1/3] 读取样本注释文件...")
    start = time.time()

    if ANNOTATION_FILE.endswith('.gz'):
        annot_df = pd.read_csv(ANNOTATION_FILE, sep='\t', compression='gzip', low_memory=False)
    else:
        annot_df = pd.read_csv(ANNOTATION_FILE, sep='\t', low_memory=False)

    sample_to_tissue = dict(zip(annot_df['SAMPID'], annot_df['SMTSD']))

    tissue_samples = {}
    for sample, tissue in sample_to_tissue.items():
        tissue_samples.setdefault(tissue, []).append(sample)

    print(f"  样本总数: {len(sample_to_tissue)}")
    print(f"  组织类型数: {len(tissue_samples)}")
    print(f"  耗时: {time.time() - start:.1f}s")

    print("\n  组织分布 (Top 10):")
    for tissue, samples in sorted(tissue_samples.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"    {tissue}: {len(samples)} samples")

    # Step 2: 读取TPM表头并建立列名映射
    print("\n[2/3] 读取TPM数据并计算组织中位数...")
    print(f"  PyArrow block_size: {BLOCK_SIZE // 1024 // 1024}MB")
    start = time.time()

    with gzip.open(TPM_FILE, 'rt') as f:
        header_line = f.readline().strip()

    columns = header_line.split('\t')
    print(f"  总列数: {len(columns)}")
    print(f"  第1列: {columns[0]}")
    print(f"  第2列: {columns[1]}")
    print(f"  第3列示例: {columns[2]}")

    all_samples = columns[2:]
    print(f"  样本列数: {len(all_samples)}")
    print(f"  前5个样本ID示例:")
    for s in all_samples[:5]:
        print(f"    {s}")

    # O(1) 存在性判断，为每个组织收集实际存在的样本列名
    all_samples_set = set(all_samples)
    tissue_col_names = {}
    matched_samples = 0
    for tissue, samples in tissue_samples.items():
        present = [s for s in samples if s in all_samples_set]
        tissue_col_names[tissue] = present
        matched_samples += len(present)

    print(f"\n  匹配到注释的样本数: {matched_samples}")

    if matched_samples == 0:
        print("\n  ⚠️ 警告: 没有匹配的样本!")
        print(f"  注释文件样本: {list(sample_to_tissue.keys())[0]}")
        print(f"  TPM文件样本: {all_samples[0]}")
        return

    # 为 PyArrow 指定列类型：前两列 string，其余全部 float64（避免后续 to_numeric）
    column_types = {columns[0]: pa.string(), columns[1]: pa.string()}
    for s in all_samples:
        column_types[s] = pa.float64()

    # Step 3: PyArrow 流式读取 + 向量化计算
    print(f"\n  开始流式处理...")
    chunk_start = time.time()

    input_stream = pa.input_stream(TPM_FILE)  # 自动识别 .gz 并解压

    read_options = pv.ReadOptions(
        skip_rows=1,               # 跳过第1行表头（我们已手动读取并提供列名）
        column_names=columns,      # 使用解析好的列名
        use_threads=True,
        block_size=BLOCK_SIZE,
    )
    parse_options = pv.ParseOptions(delimiter='\t')
    convert_options = pv.ConvertOptions(
        column_types=column_types,
        check_utf8=False,
        null_values=['NA', 'N/A', 'null', 'NULL', ''],
        auto_dict_encode=False,
    )

    reader = pv.open_csv(input_stream, read_options=read_options,
                         parse_options=parse_options, convert_options=convert_options)

    batch_results = []
    batch_count = 0
    total_rows = 0

    for batch in reader:
        df = batch.to_pandas()
        batch_count += 1
        n_rows = len(df)
        total_rows += n_rows

        # 重命名前两列方便引用
        df.rename(columns={df.columns[0]: 'transcript_id', df.columns[1]: 'gene_id'}, inplace=True)

        # 向量化计算：每个组织一次性 median(axis=1)
        result_dict = {'transcript_id': df['transcript_id'].values}
        for tissue, col_names in tissue_col_names.items():
            if col_names:
                sub_df = df[col_names]
                # 保留原逻辑：只取 >0 的值，其余视为缺失；全缺失则填 0
                masked = sub_df.where(sub_df > 0)
                result_dict[tissue] = masked.median(axis=1, skipna=True).fillna(0).values
            else:
                result_dict[tissue] = np.zeros(n_rows, dtype=np.float32)

        batch_results.append(pd.DataFrame(result_dict))

        if batch_count % 10 == 0:
            elapsed = time.time() - chunk_start
            print(f"    已处理 {batch_count} batches, 累计 {total_rows} transcripts, 耗时 {elapsed:.1f}s")

    print(f"  共处理 {batch_count} batches, {total_rows} transcripts")
    print(f"  计算耗时: {time.time() - chunk_start:.1f}s")

    # Step 4: 合并并保存
    print("\n[3/3] 合并结果并保存Parquet...")
    start = time.time()

    result_df = pd.concat(batch_results, ignore_index=True)
    result_df.set_index('transcript_id', inplace=True)

    # 统一转 float32 节省空间
    for col in result_df.columns:
        if result_df[col].dtype != np.float32:
            result_df[col] = result_df[col].astype(np.float32)

    result_df.to_parquet(OUTPUT_FILE, engine='pyarrow', compression='zstd')

    file_size = os.path.getsize(OUTPUT_FILE) / (1024**3)
    print(f"  输出文件: {OUTPUT_FILE}")
    print(f"  文件大小: {file_size:.2f} GB")
    print(f"  耗时: {time.time() - start:.1f}s")

    # 验证
    print("\n[验证] 读取Parquet文件验证...")
    check_df = pd.read_parquet(OUTPUT_FILE)
    print(f"  行数: {len(check_df)}")
    print(f"  列数: {len(check_df.columns)}")
    print(f"  示例数据 (前3行, 前3列):")
    print(check_df.iloc[:3, :3])

    total_elapsed = time.time() - total_start
    print(f"\n{'=' * 60}")
    print(f"全部完成! 总耗时: {total_elapsed:.1f}s ({total_elapsed/60:.1f} 分钟)")
    print(f"{'=' * 60}")
    print(f"\n输出文件: {OUTPUT_FILE}")
    print(f"\n下一步: 将 parquet 部署到流水线数据目录:")
    print(f'  ${{OPENRARE_DATA_ROOT}}/vep_data/GTEx/v11/expression/gtex_v11_transcript_tpm.parquet')
    print(f"  当前输出: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()