# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j_work\prefix\Lang_42b`
- Generated: `2026-08-04T17:40:04+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The issue is that the current implementation of the escape logic iterates over the string using standard char-based processing, which splits high-unicode characters (represented as surrogate pairs in Java) into two separate entities. This is a procedural logic error in how the string is traversed and encoded, requiring a change to the algorithm to correctly handle supplementary characters as single codepoints.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
