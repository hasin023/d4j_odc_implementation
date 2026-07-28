# Defects4J ODC Classification Report: Math-73

- Version: `73b`
- Work directory: `C:\d4j_work\prefix\Math_73b`
- Generated: `2026-07-25T16:52:47+00:00`

## Failure Summary
- `org.apache.commons.math.analysis.solvers.BrentSolverTest::testBadEndpoints`: junit.framework.AssertionFailedError: Expecting IllegalArgumentException - non-bracketing

## Suspicious Frames
- `org.apache.commons.math.analysis.solvers.BrentSolverTest.testBadEndpoints` at `BrentSolverTest.java:334`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report explicitly states that the check for the sign of the function values at the three points is missing. This is a classic 'Checking' defect where a required validation predicate is absent.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
