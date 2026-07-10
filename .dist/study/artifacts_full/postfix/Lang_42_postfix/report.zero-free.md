# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j_work\postfix\Lang_42b`
- Generated: `2026-07-10T19:29:28+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Unicode surrogate pair handling error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code was iterating through a string using charAt(i), which treats characters as 16-bit units. For Unicode characters outside the Basic Multilingual Plane (BMP), Java represents them as surrogate pairs (two 16-bit chars). The original code processed each surrogate individually, resulting in two separate HTML entities (e.g., &#55348;&#57186;) instead of a single entity representing the full code point (e.g., &#119650;). The fix uses Character.codePointAt to correctly identify the full 32-bit code point and skips the second surrogate unit during iteration.
