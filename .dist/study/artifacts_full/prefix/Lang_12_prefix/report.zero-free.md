# Defects4J ODC Classification Report: Lang-12

- Version: `12b`
- Work directory: `C:\d4j_work\prefix\Lang_12b`
- Generated: `2026-07-10T19:27:56+00:00`

## Failure Summary
- `org.apache.commons.lang3.RandomStringUtilsTest::testExceptions`: java.lang.ArrayIndexOutOfBoundsException: Index 304389849 out of bounds for length 0
- `org.apache.commons.lang3.RandomStringUtilsTest::testLANG805`: java.lang.ArrayIndexOutOfBoundsException: Index 43525044 out of bounds for length 1

## Suspicious Frames
- `org.apache.commons.lang3.RandomStringUtils.random` at `RandomStringUtils.java:248`
- `org.apache.commons.lang3.RandomStringUtils.random` at `RandomStringUtils.java:321`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect Array Index Calculation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code in RandomStringUtils.random() calculates an index for the 'chars' array using 'random.nextInt(gap) + start'. This logic assumes that the range defined by 'start' and 'gap' (which is 'end - start') maps directly to valid indices within the provided 'chars' array. However, when 'chars' is provided, the method should select a random index within the bounds of the array itself, rather than using the 'start' and 'gap' parameters which are intended for character range generation. Consequently, the calculated index frequently exceeds the array's length, triggering an ArrayIndexOutOfBoundsException.
