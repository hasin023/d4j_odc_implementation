# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j_work\postfix\Lang_42b`
- Generated: `2026-07-10T19:18:30+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The defect is a procedural error in how the string is traversed and encoded. It is not a missing check (Checking) because the logic itself is fundamentally flawed for the data structure (UTF-16 strings). It is not an assignment error. It is a clear case of an incorrect algorithmic strategy for handling multi-byte/surrogate characters.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
