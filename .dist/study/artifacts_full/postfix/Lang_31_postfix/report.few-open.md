# Defects4J ODC Classification Report: Lang-31

- Version: `31b`
- Work directory: `C:\d4j_work\postfix\Lang_31b`
- Generated: `2026-07-10T19:24:12+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:696`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:680`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by a missing validation check for supplementary Unicode characters. The existing logic correctly identifies a match for characters in the Basic Multilingual Plane but fails to distinguish between a single character and the first half of a surrogate pair. The fix introduces a conditional guard to validate the full surrogate pair, which is a classic 'Checking' defect.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Capability`
