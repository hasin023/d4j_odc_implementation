# Defects4J ODC Classification Report: Lang-6

- Version: `6b`
- Work directory: `C:\d4j_work\prefix\Lang_6b`
- Generated: `2026-07-10T19:35:13+00:00`

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
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The logic at lines 94-96 is fundamentally incorrect for advancing the index 'pos'. It iterates 'consumed' times, and in each iteration, it adds the character count of the codepoint at the current 'pos'. This results in 'pos' being advanced by more than the number of characters actually consumed by the translator, leading to an index out of bounds error.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
