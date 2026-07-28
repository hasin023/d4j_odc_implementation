# Defects4J ODC Classification Report: Math-74

- Version: `74b`
- Work directory: `C:\d4j_work\prefix\Math_74b`
- Generated: `2026-07-25T17:15:30+00:00`

## Failure Summary
- `org.apache.commons.math.ode.nonstiff.AdamsMoultonIntegratorTest::polynomial`: junit.framework.AssertionFailedError

## Suspicious Frames
- `org.apache.commons.math.ode.nonstiff.AdamsMoultonIntegratorTest.polynomial` at `AdamsMoultonIntegratorTest.java:150`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect algorithm implementation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug report identifies that the EmbeddedRungeKuttaIntegrator (and related classes) incorrectly calculates the scaling factor used for the initial step size estimation. According to the theory (Hairer), the scaling should account for both absolute and relative tolerances based on the initial state values (sci = Atol_i + |y0_i| * Rtol_i). The current implementation only uses the absolute tolerance, leading to an incorrect initial step size that can cause integration failures or performance issues, as evidenced by the failing test case which expects a specific number of evaluations.
