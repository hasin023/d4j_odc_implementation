# Defects4J ODC Classification Report: Math-27

- Version: `27b`
- Work directory: `C:\d4j_work\prefix\Math_27b`
- Generated: `2026-07-25T17:12:36+00:00`

## Failure Summary
- `org.apache.commons.math3.fraction.FractionTest::testMath835`: junit.framework.AssertionFailedError: expected:<2.1691754E9> but was:<-2.125791896E9>

## Suspicious Frames
- `org.apache.commons.math3.fraction.FractionTest.testMath835` at `FractionTest.java:253`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Integer Overflow`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report and test failure indicate that the percentageValue() method performs arithmetic operations (specifically multiplication by 100) on integer values before converting to a double. This causes an integer overflow when the numerator is large, resulting in a negative value instead of the expected positive percentage. The evidence confirms that the calculation order is the root cause, as multiplying by 100 before the conversion to double exceeds the capacity of a 32-bit signed integer.
