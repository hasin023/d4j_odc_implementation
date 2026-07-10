# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j_work\prefix\Lang_28b`
- Generated: `2026-07-10T19:45:24+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is an algorithmic failure in how the unescaper iterates through and processes characters. It is not a missing guard (Checking) or a simple value assignment error; it is a procedural logic error in the character processing loop, making Algorithm/Method the correct classification.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
