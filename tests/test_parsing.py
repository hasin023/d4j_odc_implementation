import unittest

from d4j_odc_pipeline.parsing import extract_json_object, parse_failing_tests


class ParsingTests(unittest.TestCase):
    def test_parse_failing_tests_groups_stack_traces(self) -> None:
        sample = """--- org.example.FooTest::testOne
java.lang.AssertionError: boom
    at org.example.Foo.fail(Foo.java:42)
    at org.example.FooTest.testOne(FooTest.java:11)
--- org.example.BarTest::testTwo
java.lang.NullPointerException
    at org.example.Bar.work(Bar.java:7)
"""
        failures = parse_failing_tests(sample)
        self.assertEqual(2, len(failures))
        self.assertEqual("org.example.FooTest::testOne", failures[0].test_name)
        self.assertEqual("org.example.Foo", failures[0].frames[0].class_name)
        self.assertEqual(42, failures[0].frames[0].line_number)

    def test_extract_json_object_from_code_fence(self) -> None:
        sample = """Here is the result:
```json
{"odc_type":"Checking","confidence":0.7}
```"""
        payload = extract_json_object(sample)
        self.assertEqual("Checking", payload["odc_type"])


if __name__ == "__main__":
    unittest.main()
