# Defects4J ODC Classification Report: Lang-6

- Version: `6b`
- Work directory: `C:\d4j_work\prefix\Lang_6b`
- Generated: `2026-07-10T19:22:07+00:00`

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

The defect is in the procedural logic of the translation loop. The algorithm for advancing the 'pos' pointer is flawed because it attempts to re-calculate the character count of the code point at the current position instead of using the 'consumed' value returned by the translator. This is a classic algorithmic error in handling iteration state, fitting the Algorithm/Method ODC type.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Reliability`
