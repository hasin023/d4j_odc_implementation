# Defects4J ODC Classification Report: Lang-31

- Version: `31b`
- Work directory: `C:\d4j_work\prefix\Lang_31b`
- Generated: `2026-07-10T19:28:49+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:696`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:680`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Unicode supplementary character handling error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The StringUtils.containsAny method fails to correctly handle Unicode supplementary characters (characters outside the Basic Multilingual Plane, represented as surrogate pairs in Java). The evidence shows that while standard JRE methods like String.indexOf correctly identify that two different supplementary characters do not match, the custom implementation of containsAny incorrectly returns true. This indicates that the logic within containsAny likely iterates over or compares characters as individual 16-bit char units rather than treating surrogate pairs as single code points, leading to false positive matches when partial surrogate components overlap.
