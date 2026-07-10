# Defects4J ODC Classification Report: Lang-19

- Version: `19b`
- Work directory: `C:\d4j_work\prefix\Lang_19b`
- Generated: `2026-07-10T19:28:16+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testUnfinishedEntity`: java.lang.StringIndexOutOfBoundsException: String index out of range: 19
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testOutOfBounds`: java.lang.StringIndexOutOfBoundsException: String index out of range: 7

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:54`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:86`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:44`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `IndexOutOfBoundsException due to missing bounds check`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The NumericEntityUnescaper class attempts to parse numeric entities from a string. When it encounters an entity that does not end with a semicolon, the while loop at line 54 continues to increment the 'end' index until it reaches the end of the string or finds a semicolon. Because there is no check to ensure 'end' remains within the bounds of the input string, the code attempts to access characters beyond the string's length, resulting in a StringIndexOutOfBoundsException. This occurs both when accessing the character at 'start' (line 44) and when iterating through the string to find the end of the entity (line 54).
