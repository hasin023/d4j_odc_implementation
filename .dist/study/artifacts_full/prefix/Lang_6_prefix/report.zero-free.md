# Defects4J ODC Classification Report: Lang-6

- Version: `6b`
- Work directory: `C:\d4j_work\prefix\Lang_6b`
- Generated: `2026-07-10T19:27:34+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsTest::testEscapeSurrogatePairs`: java.lang.StringIndexOutOfBoundsException: index 2,length 2

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:95`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.StringEscapeUtils.escapeCsv` at `StringEscapeUtils.java:556`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Off-by-one error in surrogate pair handling`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code in CharSequenceTranslator.java attempts to iterate through a CharSequence by manually advancing the position index. When a surrogate pair is encountered, the code correctly identifies the codepoint but then incorrectly increments the position index by the length of the character count of the codepoint. Because the loop logic already handles the character advancement for the surrogate pair via the 'consumed' variable or the default character writing logic, the additional increment at line 95 causes the index to skip past the end of the string, resulting in a StringIndexOutOfBoundsException when the loop condition is checked again.
