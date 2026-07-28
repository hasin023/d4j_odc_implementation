# Defects4J ODC Classification Report: Math-82

- Version: `82b`
- Work directory: `C:\d4j_work\postfix\Math_82b`
- Generated: `2026-07-25T17:08:07+00:00`

## Failure Summary
- `org.apache.commons.math.optimization.linear.SimplexSolverTest::testMath288`: junit.framework.AssertionFailedError: expected:<10.0> but was:<11.5>

## Suspicious Frames
- `org.apache.commons.math.optimization.linear.SimplexSolverTest.testMath288` at `SimplexSolverTest.java:73`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by an incorrect conditional check (>= 0 instead of > 0) in the SimplexSolver's ratio test. This is a classic 'Checking' defect because the logic for selecting a pivot row was flawed due to an overly permissive guard condition, which allowed invalid entries (zero) to be processed in a division operation.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
