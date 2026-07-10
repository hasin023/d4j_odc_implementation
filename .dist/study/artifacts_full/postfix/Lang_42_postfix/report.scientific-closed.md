# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j_work\postfix\Lang_42b`
- Generated: `2026-07-10T19:40:03+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic case of incorrect iteration over a string containing surrogate pairs. The code treats the string as a sequence of 16-bit chars rather than a sequence of Unicode codepoints. This is a procedural/algorithmic error in the implementation of the escape method.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
