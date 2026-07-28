# Defects4J ODC Classification Report: Math-31

- Version: `31b`
- Work directory: `C:\d4j_work\prefix\Math_31b`
- Generated: `2026-07-25T16:45:08+00:00`

## Failure Summary
- `org.apache.commons.math3.distribution.BinomialDistributionTest::testMath718`: org.apache.commons.math3.exception.ConvergenceException: illegal state: Continued fraction diverged to NaN for value 0.5
- `org.apache.commons.math3.distribution.FDistributionTest::testMath785`: junit.framework.AssertionFailedError: Failing to calculate inverse cumulative probability

## Suspicious Frames
- `org.apache.commons.math3.util.ContinuedFraction.evaluate` at `ContinuedFraction.java:178`
- `org.apache.commons.math3.special.Beta.regularizedBeta` at `Beta.java:156`
- `org.apache.commons.math3.special.Beta.regularizedBeta` at `Beta.java:129`
- `org.apache.commons.math3.special.Beta.regularizedBeta` at `Beta.java:50`
- `org.apache.commons.math3.distribution.BinomialDistribution.cumulativeProbability` at `BinomialDistribution.java:101`
- `org.apache.commons.math3.distribution.AbstractIntegerDistribution.checkedCumulativeProbability` at `AbstractIntegerDistribution.java:201`
- `org.apache.commons.math3.distribution.AbstractIntegerDistribution.solveInverseCumulativeProbability` at `AbstractIntegerDistribution.java:143`
- `org.apache.commons.math3.distribution.AbstractIntegerDistribution.inverseCumulativeProbability` at `AbstractIntegerDistribution.java:116`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is an algorithmic limitation in how the continued fraction evaluation handles numerical instability. It is not a missing check (Checking) because the check exists and is causing the failure; it is not an initialization error (Assignment/Initialization) because the values are being computed correctly according to the current algorithm; it is not a design-level capability gap (Function/Class/Object) because the functionality exists but is numerically fragile.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
