# Defects4J ODC Classification Report: Lang-31

- Version: `31b`
- Work directory: `C:\d4j_work\postfix\Lang_31b`
- Generated: `2026-07-10T19:45:44+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:696`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:680`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is an algorithmic flaw in how the method iterates and compares characters. It fails to correctly handle Unicode supplementary characters (represented as surrogate pairs in Java). The fix modifies the internal loop logic to correctly identify and validate these pairs, which is a procedural correction rather than a simple missing guard or a wrong constant assignment.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
