# Defects4J ODC Classification Report: Lang-31

- Version: `31b`
- Work directory: `C:\d4j_work\prefix\Lang_31b`
- Generated: `2026-07-10T19:45:41+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:696`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:680`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is in the procedural logic of the containsAny method. It fails to correctly handle Unicode supplementary characters because it likely treats them as individual 16-bit chars rather than single code points. This is a classic algorithmic error in string processing where the iteration strategy is insufficient for the data type (Unicode supplementary characters).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
