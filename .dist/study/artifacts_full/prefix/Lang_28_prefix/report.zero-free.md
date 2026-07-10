# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j_work\prefix\Lang_28b`
- Generated: `2026-07-10T19:28:40+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Unicode supplementary character handling error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The failing test demonstrates that the NumericEntityUnescaper fails to correctly process a numeric entity representing a supplementary character (code point > 0xFFFF). The error message shows that the unescaper produced a single character (U+0C22) instead of the expected surrogate pair (U+D803 U+DC22). This indicates that the unescaper logic is likely treating the numeric entity as a standard 16-bit character rather than correctly converting the code point into a surrogate pair, which is required for characters outside the Basic Multilingual Plane in Java.
