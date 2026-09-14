# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j-work\study-work\postfix\Lang_17b`
- Generated: `2026-09-13T17:56:48+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringEscapeUtilsTest::testLang720`: junit.framework.ComparisonFailure: expected:<𠮷[A]> but was:<𠮷[?]>

## Suspicious Frames
- `org.apache.commons.lang3.StringEscapeUtilsTest.testLang720` at `StringEscapeUtilsTest.java:431`
- `org.apache.commons.lang3.builder.Builder.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.concurrent.ConcurrentInitializer.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.exception.ExceptionContext.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.FormatFactory.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.translate.EntityArrays.` at `org/apache/commons/lang3/text/translate/EntityArrays.java:418`
- `org.apache.commons.lang3.text.translate.LookupTranslator.` at `org/apache/commons/lang3/text/translate/LookupTranslator.java:45`
- `org.apache.commons.lang3.text.translate.AggregateTranslator.` at `org/apache/commons/lang3/text/translate/AggregateTranslator.java:40`
- `org.apache.commons.lang3.StringEscapeUtils.` at `org/apache/commons/lang3/StringEscapeUtils.java:52`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by an incorrect iteration strategy in the translation loop. The original code used Character.codePointCount to determine the loop limit and incremented the position incorrectly, failing to account for the fact that some characters (surrogate pairs) occupy two char positions. The fix involves changing the loop limit to the string length and correctly incrementing the position based on the character count of the processed code points. This is a fundamental procedural logic error in the translation algorithm.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
