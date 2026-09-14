# Defects4J ODC Classification Report: Lang-19

- Version: `19b`
- Work directory: `C:\d4j-work\study-work\prefix\Lang_19b`
- Generated: `2026-09-13T17:56:50+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testUnfinishedEntity`: java.lang.StringIndexOutOfBoundsException: String index out of range: 19
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testOutOfBounds`: java.lang.StringIndexOutOfBoundsException: String index out of range: 7

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:54`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:86`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:44`
- `org.apache.commons.lang3.builder.Builder.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.concurrent.ConcurrentInitializer.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.exception.ExceptionContext.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.FormatFactory.` at `coverage: line_rate=1.00`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code at line 54 uses a while loop `while(input.charAt(end) != ';')` to find the end of an entity. If the input string ends before a semicolon is found, `end` increments until it exceeds the string length, causing an IndexOutOfBoundsException. This is a classic missing boundary check (guard) for the end of the string within the loop condition.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
