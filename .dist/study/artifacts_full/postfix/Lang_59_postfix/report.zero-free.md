# Defects4J ODC Classification Report: Lang-59

- Version: `59b`
- Work directory: `C:\d4j_work\postfix\Lang_59b`
- Generated: `2026-07-10T19:30:17+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderAppendInsertTest::testLang299`: java.lang.StringIndexOutOfBoundsException: offset 0, count 3, length 1

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.appendFixedWidthPadRight` at `StrBuilder.java:884`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incorrect parameter usage in array copy operation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code intended to copy a fixed-width portion of a string into a buffer. When the string length exceeded the specified width, the code incorrectly used the full string length as the end index for the 'getChars' method instead of the specified width. This caused an attempt to copy more characters than the allocated buffer space allowed, leading to an ArrayIndexOutOfBoundsException.
