# Defects4J ODC Classification Report: Lang-6

- Version: `6b`
- Work directory: `C:\d4j_work\postfix\Lang_6b`
- Generated: `2026-07-10T19:27:35+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsTest::testEscapeSurrogatePairs`: java.lang.StringIndexOutOfBoundsException: index 2,length 2

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:95`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.StringEscapeUtils.escapeCsv` at `StringEscapeUtils.java:556`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Off-by-one index calculation error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code iterates through a CharSequence to translate characters. When a translator does not consume a character (returns 0), the loop attempts to advance the position pointer. The original code used 'pos' as the index for 'Character.codePointAt(input, pos)' inside a loop that was intended to iterate based on the number of consumed characters. However, the logic was flawed because it was using the global 'pos' variable instead of the local loop index 'pt' to determine the character count, leading to an incorrect index calculation that eventually exceeded the string length, causing a StringIndexOutOfBoundsException.
