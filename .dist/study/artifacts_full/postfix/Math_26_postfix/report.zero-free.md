# Defects4J ODC Classification Report: Math-26

- Version: `26b`
- Work directory: `C:\d4j_work\postfix\Math_26b`
- Generated: `2026-07-25T17:12:34+00:00`

## Failure Summary
- `org.apache.commons.math3.fraction.FractionTest::testIntegerOverflow`: junit.framework.AssertionFailedError: an exception should have been thrown

## Suspicious Frames
- `org.apache.commons.math3.fraction.FractionTest.checkIntegerOverflow` at `FractionTest.java:145`
- `org.apache.commons.math3.fraction.FractionTest.testIntegerOverflow` at `FractionTest.java:138`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Integer overflow check logic error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug was caused by an incomplete check for integer overflow during the construction of a Fraction from a double. The original code only checked if the numerator or denominator exceeded Integer.MAX_VALUE using a direct comparison (e.g., 'a0 > overflow'), which failed to account for negative values that could underflow below Integer.MIN_VALUE. By using 'FastMath.abs()' in the comparison, the code correctly identifies when the absolute value of the calculated numerator or denominator exceeds the capacity of a 32-bit signed integer, regardless of its sign.
