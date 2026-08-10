import json
import unittest

from d4j_odc_pipeline.web_fetch import (
    _fetch_generic_page,
    _flatten_json_for_display,
    _format_tracker_comments,
    _format_tracker_json,
)


class _FakeResponse:
    """Minimal requests.Response stand-in: only what _fetch_generic_page reads."""

    def __init__(self, *, content_type: str, body: object):
        self.headers = {"Content-Type": content_type}
        self.text = body if isinstance(body, str) else json.dumps(body)

    def json(self):
        return json.loads(self.text)


class FormatTrackerJsonTests(unittest.TestCase):
    """Regression fixture: Closure-150's bug tracker (Google Code archive
    JSON) used to end up verbatim in bug_report_content — literal
    \\u003c-escaped HTML, opaque commenterId ints, epoch timestamps, empty
    attachments arrays. See example_latext_contexts/Closure_150_prefix_context.json."""

    _PAYLOAD = {
        "id": 61,
        "status": "Fixed",
        "summary": "Type checker misses annotations on functions defined within functions",
        "labels": ["Type-Defect", "Priority-Medium"],
        "stars": 7,
        "commentCount": 7,
        "comments": [
            {
                "id": 0,
                "commenterId": -2383702226191207389,
                "content": "<b>What steps will reproduce the problem?</b>\nCompile the code.",
                "timestamp": 1259166883,
                "attachments": [],
            },
            {
                "id": 1,
                "commenterId": -7699928860083865744,
                "content": "thanks for the report.",
                "timestamp": 1259811145,
                "attachments": [],
            },
        ],
    }

    def test_decodes_html_entities_in_comment_content(self) -> None:
        text = _format_tracker_json(self._PAYLOAD)
        self.assertIn("What steps will reproduce the problem?", text)
        self.assertNotIn("&lt;b&gt;", text)
        self.assertNotIn("<b>", text)

    def test_drops_commenter_id_and_attachments(self) -> None:
        text = _format_tracker_json(self._PAYLOAD)
        self.assertNotIn("commenterId", text)
        self.assertNotIn("-2383702226191207389", text)
        self.assertNotIn("attachments", text)

    def test_keeps_every_comment_text(self) -> None:
        text = _format_tracker_json(self._PAYLOAD)
        self.assertIn("What steps will reproduce the problem", text)
        self.assertIn("thanks for the report.", text)

    def test_converts_epoch_timestamp_to_date(self) -> None:
        text = _format_tracker_json(self._PAYLOAD)
        self.assertIn("2009-11-25", text)  # 1259166883 -> 2009-11-25 UTC

    def test_keeps_summary_and_status(self) -> None:
        text = _format_tracker_json(self._PAYLOAD)
        self.assertIn("Type checker misses annotations", text)
        self.assertIn("Fixed", text)

    def test_non_tracker_json_falls_back_to_flatten(self) -> None:
        data = {"title": "Some issue", "body": "Plain description"}
        text = _format_tracker_json(data)
        self.assertIn("title: Some issue", text)
        self.assertIn("body: Plain description", text)


class FlattenJsonForDisplayTests(unittest.TestCase):
    def test_decodes_entities_in_generic_flatten(self) -> None:
        text = _flatten_json_for_display({"description": "a &lt;b&gt;bold&lt;/b&gt; bug"})
        self.assertIn("a <b>bold</b> bug", text)

    def test_drops_noise_keys(self) -> None:
        text = _flatten_json_for_display({"commenterId": -123, "userId": 5, "title": "Foo"})
        self.assertNotIn("commenterId", text)
        self.assertNotIn("userId", text)
        self.assertIn("title: Foo", text)


class FormatTrackerCommentsTests(unittest.TestCase):
    def test_skips_empty_content(self) -> None:
        lines = _format_tracker_comments([{"content": "", "timestamp": 1259166883}])
        self.assertEqual(lines, [])

    def test_skips_non_dict_items(self) -> None:
        lines = _format_tracker_comments(["not a dict"])
        self.assertEqual(lines, [])

    def test_labels_comments_in_order(self) -> None:
        lines = _format_tracker_comments(
            [{"content": "first"}, {"content": "second"}]
        )
        self.assertTrue(lines[0].startswith("Comment 0"))
        self.assertTrue(lines[1].startswith("Comment 1"))


class FetchGenericPageContentTypeTests(unittest.TestCase):
    """Regression: Google Cloud Storage (and similar static-file hosts) serve
    valid JSON under a generic content-type like application/octet-stream —
    gating JSON parsing on "json" in content_type silently skipped
    _format_tracker_json's cleanup for exactly this case (found via a live
    Closure-150 collect: bug_report_content still had raw \\u003c escapes and
    commenterId noise post-fix)."""

    def test_octet_stream_valid_json_still_gets_tracker_formatting(self) -> None:
        payload = {
            "id": 61,
            "status": "Fixed",
            "summary": "Type checker misses annotations",
            "comments": [{"id": 0, "commenterId": -123, "content": "<b>Repro steps</b>", "timestamp": 1259166883, "attachments": []}],
        }
        response = _FakeResponse(content_type="application/octet-stream", body=payload)
        text = _fetch_generic_page(response)
        self.assertIn("Repro steps", text)
        self.assertNotIn("<b>", text)
        self.assertNotIn("commenterId", text)

    def test_plain_text_body_falls_back_to_entity_decoding(self) -> None:
        response = _FakeResponse(content_type="text/plain", body="a &lt;b&gt;bold&lt;/b&gt; bug, not JSON")
        text = _fetch_generic_page(response)
        self.assertIn("a <b>bold</b> bug, not JSON", text)

    def test_html_content_type_uses_html_to_text_not_json(self) -> None:
        response = _FakeResponse(content_type="text/html; charset=utf-8", body="<p>hello</p>")
        text = _fetch_generic_page(response)
        self.assertEqual(text.strip(), "hello")


if __name__ == "__main__":
    unittest.main()
