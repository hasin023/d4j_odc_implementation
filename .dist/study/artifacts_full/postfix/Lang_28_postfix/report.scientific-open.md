# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j_work\postfix\Lang_28b`
- Generated: `2026-07-10T19:16:14+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic case of an incorrect algorithm for handling character encoding. The code assumes all characters fit into a single char (16-bit), which is false for supplementary characters. The fix involves implementing the correct conversion logic (Character.toChars), which is a local algorithmic change.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
