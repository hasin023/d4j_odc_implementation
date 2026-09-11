# Defects4J ODC Classification Report: Lang-6

- Version: `6b`
- Work directory: `C:\d4j_work\postfix\Lang_6b`
- Generated: `2026-08-04T17:36:32+00:00`

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
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by an incorrect implementation of the loop advancement logic. In the buggy code, the `pos` variable was being incremented using `Character.codePointAt(input, pos)` inside a loop that was intended to skip over consumed characters. However, the loop variable `pt` was ignored, and the logic incorrectly used the absolute position `pos` to calculate the character count, leading to an out-of-bounds access. The fix corrects the algorithm by using the loop index `pt` to correctly advance the position, which is a procedural correction within the method.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Reliability`
