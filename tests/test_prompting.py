import unittest

from d4j_odc_pipeline.models import BugContext, Failure, StackFrame
from d4j_odc_pipeline.prompting import build_messages


class PromptingTests(unittest.TestCase):
    def test_prompt_excludes_hidden_oracle(self) -> None:
        context = BugContext(
            project_id="Lang",
            bug_id=1,
            version_id="1b",
            work_dir="C:/tmp/Lang_1b",
            created_at="2026-04-13T00:00:00+00:00",
            defects4j_command=["defects4j"],
            metadata={"classes.modified": "org.example.Hidden", "tests.trigger": "FooTest::testOne"},
            failures=[
                Failure(
                    test_name="org.example.FooTest::testOne",
                    test_class="org.example.FooTest",
                    test_method="testOne",
                    headline="java.lang.AssertionError",
                    stack_trace=[],
                    frames=[StackFrame("org.example.Foo", "fail", "Foo.java", 42, "raw")],
                )
            ],
        )
        messages = build_messages(context, "scientific")
        combined = "\n".join(message["content"] for message in messages)
        self.assertIn("tests.trigger", combined)
        self.assertNotIn("org.example.Hidden", combined)
        self.assertIn('"odc_opener_hints"', combined)
        self.assertIn('"odc_closer_hints"', combined)


if __name__ == "__main__":
    unittest.main()
