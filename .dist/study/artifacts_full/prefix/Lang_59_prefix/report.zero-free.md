# Defects4J ODC Classification Report: Lang-59

- Version: `59b`
- Work directory: `C:\d4j_work\prefix\Lang_59b`
- Generated: `2026-07-10T19:30:15+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderAppendInsertTest::testLang299`: java.lang.StringIndexOutOfBoundsException: offset 0, count 3, length 1

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.appendFixedWidthPadRight` at `StrBuilder.java:884`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `incorrect parameter usage in string manipulation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The method appendFixedWidthPadRight attempts to copy characters from a string into a buffer. When the string length exceeds the specified width, the code incorrectly uses the full length of the string (strLen) as the end index for the getChars method, rather than the specified width. This causes an attempt to copy more characters than the buffer has been allocated for or than the logic intends to append, leading to a StringIndexOutOfBoundsException.
