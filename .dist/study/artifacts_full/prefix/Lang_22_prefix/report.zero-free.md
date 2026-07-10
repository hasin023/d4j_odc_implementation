# Defects4J ODC Classification Report: Lang-22

- Version: `22b`
- Work directory: `C:\d4j_work\prefix\Lang_22b`
- Generated: `2026-07-10T19:28:27+00:00`

## Failure Summary
- `org.apache.commons.lang3.math.FractionTest::testReducedFactory_int_int`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>
- `org.apache.commons.lang3.math.FractionTest::testReduce`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>

## Suspicious Frames
- `org.apache.commons.lang3.math.FractionTest.testReducedFactory_int_int` at `FractionTest.java:336`
- `org.apache.commons.lang3.math.FractionTest.testReduce` at `FractionTest.java:654`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `integer overflow handling error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs because the greatestCommonDivisor (GCD) calculation fails to correctly handle Integer.MIN_VALUE when it is used as a numerator. In Java, Math.abs(Integer.MIN_VALUE) returns Integer.MIN_VALUE due to two's complement overflow, which causes the GCD algorithm to produce incorrect results or fail to reduce the fraction properly. The failing tests demonstrate that when the numerator is Integer.MIN_VALUE and the denominator is 2, the fraction is not reduced as expected, leading to an assertion failure where the numerator remains Integer.MIN_VALUE instead of being divided by the GCD.
