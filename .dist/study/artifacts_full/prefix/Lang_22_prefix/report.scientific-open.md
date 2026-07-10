# Defects4J ODC Classification Report: Lang-22

- Version: `22b`
- Work directory: `C:\d4j_work\prefix\Lang_22b`
- Generated: `2026-07-10T19:15:31+00:00`

## Failure Summary
- `org.apache.commons.lang3.math.FractionTest::testReducedFactory_int_int`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>
- `org.apache.commons.lang3.math.FractionTest::testReduce`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>

## Suspicious Frames
- `org.apache.commons.lang3.math.FractionTest.testReducedFactory_int_int` at `FractionTest.java:336`
- `org.apache.commons.lang3.math.FractionTest.testReduce` at `FractionTest.java:654`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The failure to reduce (Integer.MIN_VALUE / 2) to (-1073741824 / 1) confirms that the GCD calculation is returning 1 instead of 2. This is caused by the inability of the standard GCD algorithm to handle the edge case of Integer.MIN_VALUE due to overflow during absolute value calculation.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
