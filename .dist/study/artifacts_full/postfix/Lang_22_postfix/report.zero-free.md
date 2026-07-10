# Defects4J ODC Classification Report: Lang-22

- Version: `22b`
- Work directory: `C:\d4j_work\postfix\Lang_22b`
- Generated: `2026-07-10T19:28:28+00:00`

## Failure Summary
- `org.apache.commons.lang3.math.FractionTest::testReducedFactory_int_int`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>
- `org.apache.commons.lang3.math.FractionTest::testReduce`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>

## Suspicious Frames
- `org.apache.commons.lang3.math.FractionTest.testReducedFactory_int_int` at `FractionTest.java:336`
- `org.apache.commons.lang3.math.FractionTest.testReduce` at `FractionTest.java:654`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Integer overflow in GCD calculation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the `greatestCommonDivisor` method fails to handle `Integer.MIN_VALUE` correctly. When `Integer.MIN_VALUE` is passed, `Math.abs(Integer.MIN_VALUE)` returns `Integer.MIN_VALUE` due to two's complement overflow, which causes the existing logic to incorrectly identify the GCD or fail to reduce the fraction. The fix introduces explicit handling for zero values and `Integer.MIN_VALUE` to prevent this overflow and ensure the GCD is calculated correctly.
