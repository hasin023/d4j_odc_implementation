# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j_work\prefix\Lang_28b`
- Generated: `2026-07-10T19:37:58+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic case of failing to account for the full range of Unicode characters in a string processing algorithm. The fix requires changing the translation logic to use Character.toChars(int) instead of (char) casting.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
