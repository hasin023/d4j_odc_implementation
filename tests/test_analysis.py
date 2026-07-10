"""Tests for the analysis module (RQ1.1, RQ1.2, RQ2.1, RQ2.2, RQ2.3, RQ3.1)."""

import unittest

from d4j_odc_pipeline.analysis import (
    compute_type_distribution,
    compute_project_type_correlation,
    analyze_impact_vs_type,
    compute_impact_distribution,
    compute_impact_stability,
    compute_per_type_metrics,
    compare_baseline_vs_scientific,
    compute_semantic_gap_metrics,
    map_naive_to_odc,
    analyze_naive_labels,
    compute_taxonomy_grounding_metrics,
)


def _make_cls(project: str, bug: int, odc_type: str, **kwargs) -> dict:
    return {
        "project_id": project,
        "bug_id": bug,
        "odc_type": odc_type,
        "confidence": kwargs.get("confidence", 0.85),
        "family": kwargs.get("family", ""),
        "alternative_types": kwargs.get("alternative_types", []),
        "impact": kwargs.get("impact"),
        # Legacy field — still accepted as a fallback by analysis._extract_impact
        # for pre-2026-07-10 artifacts.
        "inferred_impact": kwargs.get("inferred_impact", []),
        "evidence_mode": kwargs.get("evidence_mode", "pre-fix"),
    }


class TestTypeDistribution(unittest.TestCase):
    def test_basic_distribution(self) -> None:
        data = [
            _make_cls("Lang", 1, "Checking"),
            _make_cls("Lang", 2, "Checking"),
            _make_cls("Math", 3, "Algorithm/Method"),
        ]
        result = compute_type_distribution(data)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["type_counts"]["Checking"], 2)
        self.assertEqual(result["type_counts"]["Algorithm/Method"], 1)
        self.assertIn("Lang", result["per_project"])
        self.assertIn("Math", result["per_project"])

    def test_empty_input(self) -> None:
        result = compute_type_distribution([])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["type_counts"], {})

    def test_invalid_types_excluded(self) -> None:
        data = [
            _make_cls("Lang", 1, "Checking"),
            _make_cls("Lang", 2, "InvalidType"),
        ]
        result = compute_type_distribution(data)
        self.assertEqual(result["total"], 1)


class TestProjectTypeCorrelation(unittest.TestCase):
    def test_chi_squared_requires_two_projects(self) -> None:
        data = [_make_cls("Lang", i, "Checking") for i in range(5)]
        result = compute_project_type_correlation(data)
        self.assertIsNone(result["chi2"])

    def test_chi_squared_with_multiple_projects(self) -> None:
        data = (
            [_make_cls("Lang", i, "Checking") for i in range(5)] +
            [_make_cls("Math", i, "Algorithm/Method") for i in range(5)]
        )
        result = compute_project_type_correlation(data)
        self.assertIn("observed", result)
        self.assertEqual(len(result["observed"]), 2)


class TestImpactVsType(unittest.TestCase):
    """Impact×Type cross-tab — the empirical orthogonality check
    (docs/odc_alignment_audit.md §6.2). No naive symptom→type map anymore:
    that mapping was invented with no literature basis and was removed."""

    def test_basic_impact_tracking(self) -> None:
        data = [
            _make_cls("Lang", 1, "Checking", impact="Reliability"),
            _make_cls("Lang", 2, "Algorithm/Method", impact="Performance"),
        ]
        result = analyze_impact_vs_type(data)
        self.assertEqual(result["total_with_impact"], 2)
        self.assertTrue(len(result["impact_type_pairs"]) > 0)

    def test_cross_tab_pairs_are_counted(self) -> None:
        data = [
            _make_cls("Lang", 1, "Checking", impact="Reliability"),
            _make_cls("Lang", 2, "Checking", impact="Reliability"),
            _make_cls("Lang", 3, "Algorithm/Method", impact="Performance"),
        ]
        result = analyze_impact_vs_type(data)
        pair = next(p for p in result["impact_type_pairs"] if p["impact"] == "Reliability")
        self.assertEqual(pair["odc_type"], "Checking")
        self.assertEqual(pair["count"], 2)

    def test_falls_back_to_legacy_inferred_impact_list(self) -> None:
        """Pre-2026-07-10 artifacts carry inferred_impact (a list); the first
        entry is used when the new single-select `impact` field is absent."""
        data = [_make_cls("Lang", 1, "Checking", inferred_impact=["Reliability", "Usability"])]
        result = analyze_impact_vs_type(data)
        self.assertEqual(result["total_with_impact"], 1)
        self.assertEqual(result["impact_type_pairs"][0]["impact"], "Reliability")

    def test_no_impact_returns_empty(self) -> None:
        data = [_make_cls("Lang", 1, "Checking")]
        result = analyze_impact_vs_type(data)
        self.assertEqual(result["total_with_impact"], 0)
        self.assertEqual(result["impact_type_pairs"], [])


class TestImpactDistribution(unittest.TestCase):
    def test_counts_and_rates(self) -> None:
        data = [
            _make_cls("Lang", 1, "Checking", impact="Reliability"),
            _make_cls("Lang", 2, "Checking", impact="Reliability"),
            _make_cls("Math", 3, "Algorithm/Method", impact="Capability"),
        ]
        result = compute_impact_distribution(data)
        self.assertEqual(result["with_impact"], 3)
        self.assertEqual(result["without_impact"], 0)
        self.assertEqual(result["impact_counts"]["Reliability"], 2)
        self.assertAlmostEqual(result["impact_rates"]["Reliability"], 2 / 3, places=3)

    def test_missing_impact_counted_separately(self) -> None:
        data = [
            _make_cls("Lang", 1, "Checking", impact="Reliability"),
            _make_cls("Lang", 2, "Checking"),
        ]
        result = compute_impact_distribution(data)
        self.assertEqual(result["with_impact"], 1)
        self.assertEqual(result["without_impact"], 1)
        self.assertEqual(result["total"], 2)

    def test_empty_input(self) -> None:
        result = compute_impact_distribution([])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["impact_counts"], {})


class TestImpactStability(unittest.TestCase):
    """The prefix/postfix drift negative control: impact is fix-independent
    per v5.2 §3.3, so its disagreement measures pure instrument noise."""

    def test_perfect_agreement(self) -> None:
        pairs = [
            (
                _make_cls("Lang", 1, "Checking", impact="Reliability"),
                _make_cls("Lang", 1, "Assignment/Initialization", impact="Reliability"),
            ),
            (
                _make_cls("Lang", 2, "Checking", impact="Capability"),
                _make_cls("Lang", 2, "Checking", impact="Capability"),
            ),
        ]
        result = compute_impact_stability(pairs)
        self.assertEqual(result["pairs_with_impact"], 2)
        self.assertEqual(result["agreement_count"], 2)
        self.assertEqual(result["agreement_rate"], 1.0)

    def test_disagreement_lowers_agreement_rate(self) -> None:
        pairs = [
            (
                _make_cls("Lang", 1, "Checking", impact="Reliability"),
                _make_cls("Lang", 1, "Checking", impact="Capability"),
            ),
        ]
        result = compute_impact_stability(pairs)
        self.assertEqual(result["agreement_count"], 0)
        self.assertEqual(result["agreement_rate"], 0.0)

    def test_pairs_missing_impact_are_excluded(self) -> None:
        pairs = [
            (_make_cls("Lang", 1, "Checking"), _make_cls("Lang", 1, "Checking", impact="Reliability")),
        ]
        result = compute_impact_stability(pairs)
        self.assertEqual(result["pairs_with_impact"], 0)
        self.assertIsNone(result["agreement_rate"])

    def test_degenerate_distribution_notes_caveat(self) -> None:
        """Fewer than 3 distinct labels across all pairs → kappa is unreliable;
        the raw agreement rate is the number to read."""
        pairs = [
            (
                _make_cls("Lang", 1, "Checking", impact="Reliability"),
                _make_cls("Lang", 1, "Checking", impact="Reliability"),
            ),
        ]
        result = compute_impact_stability(pairs)
        self.assertIsNotNone(result["note"])


class TestPerTypeMetrics(unittest.TestCase):
    def test_perfect_agreement(self) -> None:
        pairs = [
            (_make_cls("Lang", 1, "Checking"), _make_cls("Lang", 1, "Checking")),
            (_make_cls("Lang", 2, "Checking"), _make_cls("Lang", 2, "Checking")),
        ]
        result = compute_per_type_metrics(pairs)
        self.assertEqual(result["Checking"]["precision"], 1.0)
        self.assertEqual(result["Checking"]["recall"], 1.0)
        self.assertEqual(result["Checking"]["f1"], 1.0)

    def test_mixed_agreement(self) -> None:
        pairs = [
            (_make_cls("Lang", 1, "Checking"), _make_cls("Lang", 1, "Algorithm/Method")),
        ]
        result = compute_per_type_metrics(pairs)
        # Checking: fp=1, tp=0 → precision=0
        self.assertEqual(result["Checking"]["precision"], 0.0)
        # Algorithm/Method: fn=1, tp=0 → recall=0
        self.assertEqual(result["Algorithm/Method"]["recall"], 0.0)


class TestBaselineComparison(unittest.TestCase):
    def test_improvement_deltas(self) -> None:
        postfix = [_make_cls("Lang", 1, "Checking")]
        scientific = [_make_cls("Lang", 1, "Checking", confidence=0.90)]
        baseline = [_make_cls("Lang", 1, "Algorithm/Method", confidence=0.70)]
        result = compare_baseline_vs_scientific(
            scientific_classifications=scientific,
            baseline_classifications=baseline,
            postfix_classifications=postfix,
        )
        self.assertEqual(result["scientific"]["strict_match_rate"], 1.0)
        self.assertEqual(result["baseline"]["strict_match_rate"], 0.0)
        self.assertGreater(result["improvement_deltas"]["strict_match_rate"], 0)


class TestSemanticGapMetrics(unittest.TestCase):
    def test_exact_match_distance_zero(self) -> None:
        pairs = [
            (_make_cls("Lang", 1, "Checking"), _make_cls("Lang", 1, "Checking")),
        ]
        result = compute_semantic_gap_metrics(pairs)
        self.assertEqual(result["mean_semantic_distance"], 0.0)
        self.assertEqual(result["divergence_patterns"].get("exact-match"), 1)

    def test_different_types_nonzero_distance(self) -> None:
        pairs = [
            (_make_cls("Lang", 1, "Checking"), _make_cls("Lang", 1, "Function/Class/Object")),
        ]
        result = compute_semantic_gap_metrics(pairs)
        self.assertGreater(result["mean_semantic_distance"], 0.0)
        self.assertNotIn("exact-match", result["divergence_patterns"])

    def test_per_project_breakdown(self) -> None:
        pairs = [
            (_make_cls("Lang", 1, "Checking"), _make_cls("Lang", 1, "Algorithm/Method")),
            (_make_cls("Math", 2, "Checking"), _make_cls("Math", 2, "Checking")),
        ]
        result = compute_semantic_gap_metrics(pairs)
        self.assertIn("Lang", result["per_project"])
        self.assertIn("Math", result["per_project"])
        self.assertEqual(result["per_project"]["Math"]["mean_distance"], 0.0)
        self.assertGreater(result["per_project"]["Lang"]["mean_distance"], 0.0)


class TestMapNaiveToOdc(unittest.TestCase):
    """RQ2.3: Keyword heuristic mapper tests."""

    def test_null_check_maps_to_checking(self) -> None:
        odc_type, conf = map_naive_to_odc("missing null check")
        self.assertEqual(odc_type, "Checking")
        self.assertGreater(conf, 0.0)

    def test_wrong_algorithm_maps_correctly(self) -> None:
        odc_type, _ = map_naive_to_odc("incorrect algorithm logic")
        self.assertEqual(odc_type, "Algorithm/Method")

    def test_initialization_error_maps_correctly(self) -> None:
        odc_type, _ = map_naive_to_odc("wrong initialization value")
        self.assertEqual(odc_type, "Assignment/Initialization")

    def test_api_mismatch_maps_to_interface(self) -> None:
        odc_type, _ = map_naive_to_odc("api parameter type mismatch")
        self.assertEqual(odc_type, "Interface/O-O Messages")

    def test_race_condition_maps_to_timing(self) -> None:
        odc_type, _ = map_naive_to_odc("race condition in thread")
        self.assertEqual(odc_type, "Timing/Serialization")

    def test_unknown_label_returns_unknown(self) -> None:
        odc_type, conf = map_naive_to_odc("completely unrelated xyz")
        self.assertEqual(odc_type, "Unknown")
        self.assertEqual(conf, 0.0)

    def test_empty_label_returns_unknown(self) -> None:
        odc_type, conf = map_naive_to_odc("")
        self.assertEqual(odc_type, "Unknown")
        self.assertEqual(conf, 0.0)


class TestAnalyzeNaiveLabels(unittest.TestCase):
    """RQ2.3: Naive label analysis tests."""

    def test_counts_unique_labels(self) -> None:
        data = [
            {"odc_type": "missing null check"},
            {"odc_type": "missing null check"},
            {"odc_type": "wrong algorithm"},
        ]
        result = analyze_naive_labels(data)
        self.assertEqual(result["unique_labels"], 2)
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["label_counts"]["missing null check"], 2)

    def test_entropy_single_label_is_zero(self) -> None:
        data = [{"odc_type": "same label"}] * 5
        result = analyze_naive_labels(data)
        self.assertEqual(result["label_entropy"], 0.0)

    def test_entropy_multiple_labels_positive(self) -> None:
        data = [
            {"odc_type": "label A"},
            {"odc_type": "label B"},
        ]
        result = analyze_naive_labels(data)
        self.assertGreater(result["label_entropy"], 0.0)

    def test_odc_coverage_counts_mapped_types(self) -> None:
        data = [
            {"odc_type": "missing null check"},
            {"odc_type": "wrong algorithm logic"},
            {"odc_type": "initialization error"},
        ]
        result = analyze_naive_labels(data)
        self.assertGreaterEqual(result["odc_coverage"], 2)

    def test_empty_input(self) -> None:
        result = analyze_naive_labels([])
        self.assertEqual(result["unique_labels"], 0)
        self.assertEqual(result["total"], 0)


class TestTaxonomyGroundingMetrics(unittest.TestCase):
    """RQ4: generic N-tier ablation-ladder comparison tests."""

    def test_vocabulary_comparison(self) -> None:
        zero_free = [
            {"odc_type": "missing null check"},
            {"odc_type": "wrong algorithm"},
            {"odc_type": "init error"},
            {"odc_type": "bad logic"},
            {"odc_type": "type mismatch"},
            {"odc_type": "thread race"},
            {"odc_type": "design flaw"},
            {"odc_type": "coupling issue"},
            {"odc_type": "bounds overflow"},
            {"odc_type": "wrong formula"},
        ]
        few_open = [_make_cls("L", i, "Checking") for i in range(5)] + [
            _make_cls("L", i, "Algorithm/Method") for i in range(5, 10)
        ]
        scientific_open = few_open[:]
        result = compute_taxonomy_grounding_metrics(
            tiers=[
                ("zero-free", zero_free),
                ("few-open", few_open),
                ("scientific-open", scientific_open),
            ],
        )
        self.assertEqual(["zero-free", "few-open", "scientific-open"], result["tier_order"])
        self.assertGreater(
            result["tiers"]["zero-free"]["unique_labels"],
            result["tiers"]["few-open"]["unique_labels"],
        )
        self.assertTrue(result["taxonomy_constrains_labels"])
        self.assertEqual(2, len(result["tier_deltas"]))
        self.assertEqual("zero-free", result["tier_deltas"][0]["from"])
        self.assertEqual("few-open", result["tier_deltas"][0]["to"])

    def test_empty_tier(self) -> None:
        result = compute_taxonomy_grounding_metrics(
            tiers=[("zero-free", []), ("few-open", [])],
        )
        self.assertEqual(result["tiers"]["zero-free"]["unique_labels"], 0)

    def test_generic_over_arbitrary_tier_count(self) -> None:
        """Not hardcoded to exactly 3 tiers — 2 and 4 should both work."""
        two_tier = compute_taxonomy_grounding_metrics(
            tiers=[("a", [{"odc_type": "x"}]), ("b", [{"odc_type": "y"}])],
        )
        self.assertEqual(["a", "b"], two_tier["tier_order"])

        four_tier = compute_taxonomy_grounding_metrics(
            tiers=[
                ("a", [{"odc_type": "x"}]),
                ("b", [{"odc_type": "y"}]),
                ("c", [{"odc_type": "z"}]),
                ("d", [{"odc_type": "w"}]),
            ],
        )
        self.assertEqual(["a", "b", "c", "d"], four_tier["tier_order"])
        self.assertEqual(3, len(four_tier["tier_deltas"]))


if __name__ == "__main__":
    unittest.main()

