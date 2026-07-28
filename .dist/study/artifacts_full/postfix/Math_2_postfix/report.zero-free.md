# Defects4J ODC Classification Report: Math-2

- Version: `2b`
- Work directory: `C:\d4j_work\postfix\Math_2b`
- Generated: `2026-07-25T17:11:01+00:00`

## Failure Summary
- `org.apache.commons.math3.distribution.HypergeometricDistributionTest::testMath1021`: junit.framework.AssertionFailedError: sample=-50

## Suspicious Frames
- `org.apache.commons.math3.distribution.HypergeometricDistributionTest.testMath1021` at `HypergeometricDistributionTest.java:297`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `integer overflow`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the calculation of the numerical mean in the HypergeometricDistribution class performs multiplication of two large integers before casting to a double. This causes an integer overflow when the product exceeds the maximum value of a 32-bit signed integer. The fix changes the order of operations to perform division first (by casting one operand to double), which ensures the intermediate calculation is performed in floating-point arithmetic, thus avoiding the overflow.
