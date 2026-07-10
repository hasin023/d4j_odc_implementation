# Defects4J ODC Classification Report: Lang-12

- Version: `12b`
- Work directory: `C:\d4j_work\prefix\Lang_12b`
- Generated: `2026-07-10T19:14:13+00:00`

## Failure Summary
- `org.apache.commons.lang3.RandomStringUtilsTest::testExceptions`: java.lang.ArrayIndexOutOfBoundsException: Index 304389849 out of bounds for length 0
- `org.apache.commons.lang3.RandomStringUtilsTest::testLANG805`: java.lang.ArrayIndexOutOfBoundsException: Index 43525044 out of bounds for length 1

## Suspicious Frames
- `org.apache.commons.lang3.RandomStringUtils.random` at `RandomStringUtils.java:248`
- `org.apache.commons.lang3.RandomStringUtils.random` at `RandomStringUtils.java:321`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a missing validation check (guard) for the input parameter 'chars'. The code assumes 'chars' has elements, but when it is empty, the logic for selecting a random index fails. This is a classic 'Checking' defect.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
