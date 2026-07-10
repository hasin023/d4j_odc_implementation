# Defects4J ODC Classification Report: Lang-30

- Version: `30b`
- Work directory: `C:\d4j_work\postfix\Lang_30b`
- Generated: `2026-07-10T19:28:48+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_CharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<true> but was:<false>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_StringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<true> but was:<false>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAny_StringCharArrayWithBadSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testIndexOfAnyBut_StringStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<2> but was:<3>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAny_StringWithBadSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testIndexOfAny_StringCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<2> but was:<0>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testIndexOfAnyBut_StringCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<2> but was:<3>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_StringWithBadSupplementaryChars`: junit.framework.AssertionFailedError: expected:<true> but was:<false>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testIndexOfAny_StringStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<2> but was:<0>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_CharArrayWithBadSupplementaryChars`: junit.framework.AssertionFailedError: expected:<true> but was:<false>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsNone_CharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:327`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsNone_StringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:381`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAny_StringCharArrayWithBadSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:138`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testIndexOfAnyBut_StringStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:616`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAny_StringWithBadSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:186`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testIndexOfAny_StringCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:528`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Unicode Supplementary Character Handling Error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code failed to correctly process Unicode supplementary characters (which are represented as surrogate pairs in Java). The original implementation treated each 16-bit char in a surrogate pair as an independent character, leading to incorrect matching logic when searching for or excluding these characters. The fix introduces checks using Character.isHighSurrogate(ch) to ensure that when a high surrogate is encountered, the subsequent low surrogate is also considered as part of the same character unit, preventing partial or incorrect matches.
