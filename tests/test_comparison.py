import unittest

from d4j_odc_pipeline.comparison import compare_classifications


class ComparisonTests(unittest.TestCase):
    def test_legacy_family_fallback_from_coarse_group(self) -> None:
        prefix = {
            "project_id": "Lang",
            "bug_id": 1,
            "version_id": "1b",
            "odc_type": "Checking",
            "coarse_group": "Control and Data Flow",
            "confidence": 0.9,
            "alternative_types": [],
            "reasoning_summary": "pre",
        }
        postfix = {
            "project_id": "Lang",
            "bug_id": 1,
            "version_id": "1b",
            "odc_type": "Algorithm/Method",
            "coarse_group": "Control and Data Flow",
            "confidence": 0.8,
            "alternative_types": [],
            "reasoning_summary": "post",
        }

        result = compare_classifications(prefix, postfix)
        self.assertTrue(result.family_match)
        self.assertEqual("Control and Data Flow", result.prefix_family)
        self.assertEqual("Control and Data Flow", result.postfix_family)

    def test_optional_closer_fields_are_preserved(self) -> None:
        prefix = {
            "project_id": "Lang",
            "bug_id": 1,
            "version_id": "1b",
            "odc_type": "Checking",
            "family": "Control and Data Flow",
            "target": "Design/Code",
            "qualifier": "Incorrect",
            "age": "Base",
            "source": "Developed In-House",
            "confidence": 0.9,
            "alternative_types": [],
            "reasoning_summary": "pre",
        }
        postfix = {
            "project_id": "Lang",
            "bug_id": 1,
            "version_id": "1b",
            "odc_type": "Checking",
            "family": "Control and Data Flow",
            "target": "Design/Code",
            "qualifier": "Incorrect",
            "age": "Base",
            "source": "Developed In-House",
            "confidence": 0.9,
            "alternative_types": [],
            "reasoning_summary": "post",
        }

        result = compare_classifications(prefix, postfix)
        self.assertEqual("Design/Code", result.prefix_target)
        self.assertEqual("Incorrect", result.prefix_qualifier)
        self.assertEqual("Base", result.prefix_age)
        self.assertEqual("Developed In-House", result.prefix_source)


if __name__ == "__main__":
    unittest.main()
