# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j_work\postfix\Lang_28b`
- Generated: `2026-07-10T19:45:27+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is an algorithmic failure in the unescaping procedure. The original code lacked the logic to handle supplementary characters (which require two chars in Java/UTF-16). The fix introduces a conditional branch to correctly process these values, which is a procedural/algorithmic correction rather than a simple guard (Checking) or a wrong constant (Assignment).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
