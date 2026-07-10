# Defects4J ODC Classification Report: Lang-31

- Version: `31b`
- Work directory: `C:\d4j_work\postfix\Lang_31b`
- Generated: `2026-07-10T19:28:51+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:696`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:680`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Unicode Supplementary Character Handling Error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the `StringUtils.containsAny` method treats Unicode supplementary characters (which are represented as surrogate pairs in Java) as individual 16-bit characters. When comparing strings, the algorithm incorrectly matches a high surrogate character in isolation, leading to false positives. The fix introduces logic to check if a matched character is a high surrogate and, if so, verifies that the subsequent low surrogate also matches, ensuring the entire supplementary character is treated as a single unit.
