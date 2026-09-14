# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j-work\study-work\prefix\Lang_28b`
- Generated: `2026-09-13T17:57:30+00:00`

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
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect lies in the procedural logic of the unescaper, which treats characters as single 16-bit units rather than correctly handling surrogate pairs (code points). The fix requires updating the algorithmic steps for parsing and translating these characters, which is a classic Algorithm/Method defect.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
