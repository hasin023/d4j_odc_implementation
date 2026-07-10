# Defects4J ODC Classification Report: Lang-22

- Version: `22b`
- Work directory: `C:\d4j_work\postfix\Lang_22b`
- Generated: `2026-07-10T19:15:35+00:00`

## Failure Summary
- `org.apache.commons.lang3.math.FractionTest::testReducedFactory_int_int`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>
- `org.apache.commons.lang3.math.FractionTest::testReduce`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>

## Suspicious Frames
- `org.apache.commons.lang3.math.FractionTest.testReducedFactory_int_int` at `FractionTest.java:336`
- `org.apache.commons.lang3.math.FractionTest.testReduce` at `FractionTest.java:654`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is an algorithmic error in the greatestCommonDivisor method. The method uses Math.abs() which overflows for Integer.MIN_VALUE, causing incorrect behavior in the GCD calculation. This is a classic algorithmic flaw in handling edge cases for integer arithmetic.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
