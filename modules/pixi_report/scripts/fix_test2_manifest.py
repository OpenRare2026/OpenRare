#!/usr/bin/env python3
"""Normalize test2.csv HPO fields for the report manifest parser."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST2_PATH = PROJECT_ROOT / "test_data/test_case/test2.csv"
HPO_RE = re.compile(r"HP:\d+")
TEST_CASE_DIR = "test_data/test_case"


def _format_raghpo(results: list[dict], job_id: str = "") -> str:
    lines: list[str] = []
    if job_id:
        lines.append(f"job_id: {job_id}")
    for item in results:
        hpo_id = (item.get("hpo_id") or "").strip()
        if not hpo_id.startswith("HP:"):
            continue
        phrase = (item.get("phrase") or "").strip()
        if phrase:
            lines.append(f"{hpo_id} {phrase}；")
        else:
            lines.append(f"{hpo_id}；")
    return "\n".join(lines)


def _hp_results(hp_ids: list[str]) -> list[dict]:
    return [
        {"patient_id": "1", "phrase": "", "category": "Abnormal", "hpo_id": hp_id}
        for hp_id in hp_ids
    ]


def build_rows() -> list[dict[str, str]]:
    job0 = "86d41396-7560-4aec-99c1-5fec0287e3af"
    results0 = [
        {
            "patient_id": "1",
            "phrase": "Growth and developmental delay",
            "category": "Abnormal",
            "hpo_id": "No Candidate Fit",
        },
        {"patient_id": "1", "phrase": "Cannot sit", "category": "Abnormal", "hpo_id": "HP:0000711"},
        {
            "patient_id": "1",
            "phrase": "Cannot roll over",
            "category": "Abnormal",
            "hpo_id": "HP:0032989",
        },
        {
            "patient_id": "1",
            "phrase": "Scattered hypopigmented macules on skin",
            "category": "Abnormal",
            "hpo_id": "HP:0020073",
        },
        {
            "patient_id": "1",
            "phrase": "Poor muscle tone in limbs",
            "category": "Abnormal",
            "hpo_id": "HP:0001252",
        },
        {
            "patient_id": "1",
            "phrase": "Multiple patchy and nodular shadows in deep white matter and subcortical white matter of bilateral cerebral hemispheres",
            "category": "Abnormal",
            "hpo_id": "HP:0007052",
        },
        {
            "patient_id": "1",
            "phrase": "Multiple punctate and nodular shadows along bilateral lateral ventricle margins and beside right foramen of Monro",
            "category": "Abnormal",
            "hpo_id": "HP:0030081",
        },
    ]

    job1 = "41d559a0-50fe-495e-afa8-7f4de2bc512b"
    hp_ids1 = [
        "HP:0004322",
        "HP:0002515",
        "HP:0000316",
        "HP:0000954",
        "HP:0004209",
        "HP:0000750",
        "HP:0002474",
        "HP:0001350",
        "HP:0009381",
        "HP:0035028",
    ]
    results1 = _hp_results(hp_ids1)

    return [
        {
            "家系类型": "单人",
            "家系关系": "先证者",
            "样本编号": "26B03420134",
            "临床信息": (
                "生长发育落后8月，父母身体健康，有一姐姐身体健康，目前患儿不会坐，不会翻身，"
                "体重:9.8Kg，身高:65.2cm。全身皮肤可见散在色素脱失斑，四肢肌张力欠佳。"
                "垂体+颅脑MRI:1.双侧大脑半球深部白质、灰质下白质散在多发片状、团片状影;"
                "2.双侧侧脑室边缘、右侧孟氏孔旁见多发斑点状、结节状影。上述征象，考虑结节性硬化症。"
            ),
            "raghpo": _format_raghpo(results0, job0),
            "raghpo-returns": json.dumps(
                {"job_id": job0, "status": "completed", "results": results0},
                ensure_ascii=False,
            ),
            "37 to 38": "",
            "gz to vcf": f"{TEST_CASE_DIR}/26B03420134_aa2bae.vcf",
            "宽表": f"{TEST_CASE_DIR}/case3_26B03420134_10000.csv",
            "基因与疾病": "",
            "ppi": "",
            "报告": "",
        },
        {
            "家系类型": "单人",
            "家系关系": "先证者",
            "样本编号": "25B07456346",
            "临床信息": (
                "因语言发育迟缓，身材矮小就诊，20个月开口叫爸爸，妈妈，现仅念2-3个字的短句，"
                "问诊口齿不清，走路似摇摆步。身高低于同龄人＜P3，眼距宽，断掌掌纹，"
                "手指短粗，小手指弯曲，有3羟基异戊酸肉碱增高"
            ),
            "raghpo": _format_raghpo(results1, job1),
            "raghpo-returns": json.dumps(
                {"job_id": job1, "status": "completed", "results": results1},
                ensure_ascii=False,
            ),
            "37 to 38": f"{TEST_CASE_DIR}/25B07456346_liftover/output.grch38.vcf.gz",
            "gz to vcf": f"{TEST_CASE_DIR}/25B07456346_2b4a35.vcf",
            "宽表": f"{TEST_CASE_DIR}/case4_25B07456346_10000.csv",
            "基因与疾病": "",
            "ppi": "",
            "报告": "",
        },
    ]


def main() -> None:
    rows = build_rows()
    fieldnames = [
        "家系类型",
        "家系关系",
        "样本编号",
        "临床信息",
        "raghpo",
        "raghpo-returns",
        "37 to 38",
        "gz to vcf",
        "宽表",
        "基因与疾病",
        "ppi",
        "报告",
    ]

    with TEST2_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    from report.manifest import load_manifest

    for index, row in enumerate(rows):
        meta = load_manifest(TEST2_PATH, row_index=index)
        print(
            f"{meta.sample_id}: hpo_terms={meta.hpo_terms} "
            f"returns={len((meta.raghpo_returns or {}).get('results', []))}"
        )


if __name__ == "__main__":
    main()
