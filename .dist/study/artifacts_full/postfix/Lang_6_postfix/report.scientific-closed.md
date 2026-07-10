# Defects4J ODC Classification Report: Lang-6

- Version: `6b`
- Work directory: `C:\d4j_work\postfix\Lang_6b`
- Generated: `2026-07-10T19:35:16+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsTest::testEscapeSurrogatePairs`: java.lang.StringIndexOutOfBoundsException: index 2,length 2

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:95`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.StringEscapeUtils.escapeCsv` at `StringEscapeUtils.java:556`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic off-by-one/index-misuse error within a loop. The code attempts to advance the 'pos' pointer by the number of characters consumed by a translator. However, it uses the absolute 'pos' as the index for 'codePointAt' inside a loop that iterates 'consumed' times, instead of using the relative index 'pt'. This is a procedural logic error in the translation algorithm.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
