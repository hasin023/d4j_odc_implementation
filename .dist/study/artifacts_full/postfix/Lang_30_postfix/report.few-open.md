# Defects4J ODC Classification Report: Lang-30

- Version: `30b`
- Work directory: `C:\d4j_work\postfix\Lang_30b`
- Generated: `2026-08-04T17:38:49+00:00`

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
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The fix involves rewriting the core iteration logic within several StringUtils methods to correctly identify and handle surrogate pairs. The original implementation only checked individual characters, whereas the fixed version adds logic to detect high surrogates and verify the subsequent low surrogate before confirming a match. This is a procedural correction to the search algorithm, not a simple guard or initialization issue.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
