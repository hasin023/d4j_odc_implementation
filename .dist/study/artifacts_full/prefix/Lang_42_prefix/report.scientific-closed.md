# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j_work\prefix\Lang_42b`
- Generated: `2026-07-10T19:39:57+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report and test failure clearly indicate that the method treats surrogate pairs as individual characters. This is a procedural error in the string processing algorithm used by StringEscapeUtils.escapeHtml.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
