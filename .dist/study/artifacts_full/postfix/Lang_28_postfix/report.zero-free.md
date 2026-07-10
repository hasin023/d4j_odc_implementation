# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j_work\postfix\Lang_28b`
- Generated: `2026-07-10T19:28:41+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incorrect character encoding handling`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the NumericEntityUnescaper was treating all numeric entities as single 16-bit characters. When encountering supplementary characters (Unicode code points above 0xFFFF), which require two 16-bit characters (a surrogate pair) in Java, the original code failed to correctly convert the integer entity value into the appropriate surrogate pair. The fix introduces logic to check if the entity value exceeds 0xFFFF and, if so, uses Character.toChars() to correctly write the surrogate pair to the output stream.
