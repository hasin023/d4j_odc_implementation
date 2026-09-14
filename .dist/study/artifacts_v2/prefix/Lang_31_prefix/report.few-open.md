# Defects4J ODC Classification Report: Lang-31

- Version: `31b`
- Work directory: `C:\d4j-work\study-work\prefix\Lang_31b`
- Generated: `2026-09-13T17:57:46+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:696`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:680`
- `org.apache.commons.lang3.exception.ExceptionContext.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.FormatFactory.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.ArrayUtils.` at `org/apache/commons/lang3/ArrayUtils.java:3279`
- `org.apache.commons.lang3.StringUtils.` at `org/apache/commons/lang3/StringUtils.java:194`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a failure in the computational logic of the containsAny method. It fails to correctly handle surrogate pairs, which are the standard way Java represents supplementary characters. This is an algorithmic error in how the method iterates through or compares characters, rather than a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
