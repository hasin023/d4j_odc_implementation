# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j_work\postfix\Lang_28b`
- Generated: `2026-08-04T17:38:37+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The fix involves changing the logic for writing the unescaped character to the output stream. Specifically, it adds a conditional check to handle supplementary characters (code points > 0xFFFF) by converting them into a pair of UTF-16 surrogate characters using Character.toChars(), rather than attempting to write the raw integer value directly. This is a procedural correction to the unescaping algorithm to correctly handle multi-char UTF-16 representations.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
