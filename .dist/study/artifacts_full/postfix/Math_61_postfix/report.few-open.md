# Defects4J ODC Classification Report: Math-61

- Version: `61b`
- Work directory: `C:\d4j_work\postfix\Math_61b`
- Generated: `2026-07-25T17:05:52+00:00`

## Failure Summary
- `org.apache.commons.math.distribution.PoissonDistributionTest::testMean`: org.apache.commons.math.MathRuntimeException$4: the Poisson mean must be positive (-1)

## Suspicious Frames
- `org.apache.commons.math.MathRuntimeException.createIllegalArgumentException` at `MathRuntimeException.java:387`
- `org.apache.commons.math.distribution.PoissonDistributionImpl.<init>` at `PoissonDistributionImpl.java:94`
- `org.apache.commons.math.distribution.PoissonDistributionImpl.<init>` at `PoissonDistributionImpl.java:80`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Interface/O-O Messages`
- Family: `Structural`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a mismatch between the exception type thrown by the constructor and the exception type expected by the test. This is a classic interface/contract issue where the caller (the test) expects a specific exception type (NotStrictlyPositiveException) and the callee (the constructor) provides a different one (IllegalArgumentException).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
