# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j_work\prefix\Lang_42b`
- Generated: `2026-07-10T19:18:25+00:00`

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

The bug report and test failure confirm that the method incorrectly splits surrogate pairs. This is a classic case of an algorithm that assumes all characters are 16-bit (char), which is incorrect for modern Unicode support in Java.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
