# Defects4J ODC Classification Report: Lang-43

- Version: `43b`
- Work directory: `C:\d4j_work\prefix\Lang_43b`
- Generated: `2026-07-08T16:59:12+00:00`

## Failure Summary
- `org.apache.commons.lang.text.ExtendedMessageFormatTest::testEscapedQuote_LANG_477`: java.lang.OutOfMemoryError: Java heap space

## Suspicious Frames
- `org.apache.commons.lang.text.ExtendedMessageFormat.appendQuotedString` at `ExtendedMessageFormat.java:422`
- `org.apache.commons.lang.text.ExtendedMessageFormat.applyPattern` at `ExtendedMessageFormat.java:158`
- `org.apache.commons.lang.text.ExtendedMessageFormat.<init>` at `ExtendedMessageFormat.java:127`
- `org.apache.commons.lang.text.ExtendedMessageFormat.<init>` at `ExtendedMessageFormat.java:112`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code at line 421-422 in ExtendedMessageFormat.java returns without calling next(pos) or updating the index. Since the caller (applyPattern) relies on the ParsePosition to advance through the string, failing to advance it causes the loop to process the same character repeatedly, leading to infinite recursion/looping and memory exhaustion.
