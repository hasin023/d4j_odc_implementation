# Defects4J ODC Classification Report: Lang-12

- Version: `12b`
- Work directory: `C:\d4j_work\postfix\Lang_12b`
- Generated: `2026-07-10T19:44:13+00:00`

## Failure Summary
- `org.apache.commons.lang3.RandomStringUtilsTest::testExceptions`: java.lang.ArrayIndexOutOfBoundsException: Index 1490277398 out of bounds for length 0
- `org.apache.commons.lang3.RandomStringUtilsTest::testLANG805`: java.lang.ArrayIndexOutOfBoundsException: Index 1154780297 out of bounds for length 1

## Suspicious Frames
- `org.apache.commons.lang3.RandomStringUtils.random` at `RandomStringUtils.java:248`
- `org.apache.commons.lang3.RandomStringUtils.random` at `RandomStringUtils.java:321`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic missing validation check. The code fails to verify the state of the input (the character array and the range parameters) before using them in an array access operation. Adding these checks prevents the ArrayIndexOutOfBoundsException, which is the hallmark of a 'Checking' ODC type.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Reliability`
