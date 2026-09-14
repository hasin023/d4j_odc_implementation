# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j-work\study-work\postfix\Lang_28b`
- Generated: `2026-09-13T17:57:32+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`
- `org.apache.commons.lang3.builder.Builder.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.concurrent.ConcurrentInitializer.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.exception.ExceptionContext.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.FormatFactory.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.` at `org/apache/commons/lang3/text/translate/NumericEntityUnescaper.java:48`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.` at `org/apache/commons/lang3/text/translate/CharSequenceTranslator.java:93`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The fix involves changing the internal logic of the unescaping procedure to correctly handle supplementary characters by converting the entity value into a surrogate pair (two chars) when the value exceeds 0xFFFF. This is a procedural correction to the unescaping algorithm, not a missing guard (Checking) or a simple value assignment (Assignment/Initialization).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
