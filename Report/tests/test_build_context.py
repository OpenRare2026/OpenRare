"""Integration tests for the deterministic report builder."""
import json
from pathlib import Path
import pytest
from scripts.build_context import build, read_hpo

FIXTURES = Path(__file__).parent / "fixtures"


class TestReadHPO:
    def test_reads_valid_hpo_file(self):
        hpo = read_hpo(FIXTURES / "hpo.txt")
        assert len(hpo) == 8
        assert "HP:0002201" in hpo

    def test_nonexistent_file_returns_empty(self):
        assert read_hpo(FIXTURES / "nonexistent.txt") == []

    def test_none_path_returns_empty(self):
        assert read_hpo(None) == []


class TestBuildPipeline:
    @pytest.fixture(scope="class")
    def result(self):
        md, slots, stats = build(
            wide_csv=str(FIXTURES / "wide.csv"),
            pheno_csv=str(FIXTURES / "phenotype.csv"),
            ppi_csv=str(FIXTURES / "ppi.csv"),
            top_n=5, k=3,
            case_id="TEST-001",
            hpo_file=str(FIXTURES / "hpo.txt"),
            symptom_text="患儿男，3岁，反复呼吸道感染。",
        )
        return md, slots, stats

    def test_genes_selected(self, result):
        md, slots, stats = result
        assert stats["genes"] == ["CFTR", "DMD", "USH2A", "PAH", "CDKL5"]
        assert len(stats["genes"]) == 5
        assert stats["pheno_coverage"] == 5
        assert stats["ppi_coverage"] == 5

    def test_report_has_header(self, result):
        md, slots, stats = result
        assert "# 罕见病候选基因分析报告" in md
        assert "TEST-001" in md

    def test_report_has_overview_table(self, result):
        md, slots, stats = result
        assert "## 候选基因排序总览" in md
        for g in ["CFTR", "DMD", "USH2A", "PAH", "CDKL5"]:
            assert g in md

    def test_report_has_narrative_slots(self, result):
        md, slots, stats = result
        assert "{{narrative:phenotype_overview}}" in md
        for g in ["CFTR", "DMD", "USH2A", "PAH", "CDKL5"]:
            assert f"{{{{narrative:gene:{g}}}}}" in md

    def test_slots_have_required_keys(self, result):
        md, slots, stats = result
        for name, slot in slots.items():
            assert "instruction" in slot
            assert "ground_text" in slot
            assert "context" in slot

    def test_phenotype_overview_slot(self, result):
        md, slots, stats = result
        slot = slots["phenotype_overview"]
        assert len(slot["context"]["hpo_list"]) == 8
        assert "患儿男" in slot["context"]["symptom_text"]

    def test_gene_slots_have_context(self, result):
        md, slots, stats = result
        for g in ["CFTR", "DMD", "USH2A", "PAH", "CDKL5"]:
            s = slots[f"gene:{g}"]
            assert s["context"]["gene"] == g
            assert isinstance(s["context"]["variants"], list)
            assert s["context"]["phenotype"]["present"] is True
            assert s["context"]["ppi"]["present"] is True

    def test_supplementary_missing_handled(self):
        """Build with only wide table (no pheno/ppi) should still work."""
        md, slots, stats = build(
            wide_csv=str(FIXTURES / "wide.csv"),
            top_n=3, k=2, case_id="MINIMAL",
        )
        assert "_本模块无该基因数据。_" in md
        for slot in slots.values():
            if slot["context"].get("phenotype"):
                assert slot["context"]["phenotype"]["present"] is False

    def test_gene_list_overrides_top_n(self):
        md, slots, stats = build(
            wide_csv=str(FIXTURES / "wide.csv"),
            top_n=10, genes=["CFTR", "PAH"], k=2,
        )
        assert stats["genes"] == ["CFTR", "PAH"]

    def test_methods_section_present(self, result):
        md, slots, stats = result
        assert "## 方法与局限" in md
        assert "不作为临床诊断依据" in md

    def test_narrative_context_is_valid_json(self, result):
        md, slots, stats = result
        dumped = json.dumps(slots, ensure_ascii=False)
        reloaded = json.loads(dumped)
        assert len(reloaded) == len(slots)
