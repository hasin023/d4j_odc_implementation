# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j_work\prefix\Lang_42b`
- Generated: `2026-07-10T19:29:26+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Unicode surrogate pair handling error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The code fails to correctly handle Unicode characters outside the Basic Multilingual Plane (BMP). In Java, characters with codepoints above U+FFFF are represented as surrogate pairs (two 16-bit char values). The StringEscapeUtils.escapeHtml method treats these surrogate pairs as two separate characters rather than a single Unicode codepoint, resulting in two separate HTML entities (e.g., &#55348;&#57186;) instead of the single correct entity (&#119650;).
