# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j_work\postfix\Lang_42b`
- Generated: `2026-08-04T17:40:08+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The fix involves changing the iteration logic from processing individual 16-bit 'char' units to using 'Character.codePointAt' to correctly identify full Unicode codepoints. It also adds a specific conditional branch to handle these high-codepoint characters (>= 0x010000) by incrementing the loop index to skip the second half of the surrogate pair. This is a procedural change to the algorithm used for string traversal and escaping, not a simple guard or initialization error.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
