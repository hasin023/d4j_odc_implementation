# Defects4J ODC Classification Report: Lang-6

- Version: `6b`
- Work directory: `C:\d4j_work\prefix\Lang_6b`
- Generated: `2026-08-04T17:36:29+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsTest::testEscapeSurrogatePairs`: java.lang.StringIndexOutOfBoundsException: index 2,length 2

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:95`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.StringEscapeUtils.escapeCsv` at `StringEscapeUtils.java:556`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect lies in the loop logic within CharSequenceTranslator.java. When a translator successfully consumes a character sequence (consumed > 0), the code increments the position 'pos' by the number of characters in the code point. However, the logic inside the loop (line 95) uses 'Character.codePointAt(input, pos)' to determine the increment, which is redundant and potentially incorrect if the translator has already consumed a surrogate pair, leading to an index out of bounds error. This is a procedural logic error in the translation algorithm, not a missing guard or a simple assignment error.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Reliability`
