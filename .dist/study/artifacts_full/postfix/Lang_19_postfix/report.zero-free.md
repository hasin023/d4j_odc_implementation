# Defects4J ODC Classification Report: Lang-19

- Version: `19b`
- Work directory: `C:\d4j_work\postfix\Lang_19b`
- Generated: `2026-07-10T19:28:18+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testUnfinishedEntity`: java.lang.StringIndexOutOfBoundsException: String index out of range: 19
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testOutOfBounds`: java.lang.StringIndexOutOfBoundsException: String index out of range: 7

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:54`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:86`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:44`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `IndexOutOfBoundsException due to improper boundary checking`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code attempted to access characters in a CharSequence using index-based lookups without verifying if the index was within the bounds of the string. Specifically, the loop condition 'input.charAt(end) != ';'' assumed that a semicolon would always be present before the end of the string, leading to an out-of-bounds access when the input string ended prematurely (e.g., '&#03'). The fix introduced explicit boundary checks (end < seqEnd) and replaced the unsafe character lookup with a validation loop that checks for valid numeric/hexadecimal characters, preventing the code from reading past the end of the input.
