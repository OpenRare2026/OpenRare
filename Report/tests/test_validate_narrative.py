"""Unit tests for the anti-hallucination validation guard."""
import pytest
from scripts.validate_narrative import find_violations, is_grounded

GROUND_MULTI = (
    "| 1 | p.Val600Glu | missense_variant | HIGH | 0.9 | 32 | 1.93e-04 | "
    "Likely pathogenic |\nOMIM:265000 / MONDO:0009926  gene_score 0.634138"
)


class TestFindViolations:
    def test_grounded_narrative_passes(self):
        narrative = (
            "该基因顶层变异 p.Val600Glu 为 missense，CADD 32，"
            "gnomAD popmax 1.93e-04；表型分 0.634 中等。"
        )
        assert find_violations(narrative, GROUND_MULTI) == []

    def test_hallucinated_omim_id_caught(self):
        narrative = "对应 OMIM:999999，该变异可能致病。"
        v = find_violations(narrative, GROUND_MULTI)
        assert "OMIM:999999" in v

    def test_hallucinated_decimal_caught(self):
        narrative = "频率 0.012，为常见多态。"
        v = find_violations(narrative, GROUND_MULTI)
        assert "0.012" in v

    def test_hallucinated_revel_score_caught(self):
        narrative = "REVEL 0.88，预测有害。"
        v = find_violations(narrative, GROUND_MULTI)
        assert "0.88" in v

    def test_small_integers_ignored(self):
        narrative = "共检测到 3 个变异，排名第 2 位。"
        assert find_violations(narrative, GROUND_MULTI) == []

    def test_values_in_ground_not_flagged(self):
        narrative = "基因分 0.634138，CADD 32。"
        assert find_violations(narrative, GROUND_MULTI) == []

    def test_rounded_value_within_tolerance_ok(self):
        narrative = "表型分约 0.634。"
        assert find_violations(narrative, GROUND_MULTI) == []

    def test_hgvs_id_in_ground_not_flagged(self):
        narrative = "顶层变异 p.Val600Glu 为已知致病位点。"
        assert find_violations(narrative, GROUND_MULTI) == []

    def test_empty_narrative_always_grounded(self):
        assert find_violations("", "任意文本") == []

    def test_empty_ground_flags_everything(self):
        narrative = "OMIM:123456 频率 0.5"
        v = find_violations(narrative, "")
        assert "OMIM:123456" in v
        assert "0.5" in v

    def test_is_grounded_convenience(self):
        assert is_grounded("CADD 32", GROUND_MULTI) is True
        assert is_grounded("OMIM:999999", GROUND_MULTI) is False


class TestIDPatterns:
    @pytest.mark.parametrize("id_str", [
        "OMIM:265000", "OMIM: 265000", "MONDO:0009926",
        "ORPHA:2990", "HP:0001324", "HGNC:1884",
    ])
    def test_known_ids_not_flagged(self, id_str):
        ground = f"文本中包含 {id_str} 作为参考。"
        assert find_violations(id_str, ground) == []

    @pytest.mark.parametrize("bad_id", [
        "OMIM:999999", "MONDO:8888888", "ORPHA:7777",
    ])
    def test_unknown_ids_flagged(self, bad_id):
        assert bad_id in find_violations(f"关联 {bad_id}", "没有这个ID")


class TestScientificNotation:
    def test_scientific_matches_decimal(self):
        ground = "频率 1.93e-04"
        assert is_grounded("频率约 0.000193", ground)
        assert is_grounded("频率 1.93e-04", ground)

    def test_different_scientific_values_caught(self):
        ground = "频率 1.93e-04"
        v = find_violations("频率 5.0e-03", ground)
        assert "5.0e-03" in v
