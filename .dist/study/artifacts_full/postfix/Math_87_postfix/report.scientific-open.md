# Defects4J ODC Classification Report: Math-87

- Version: `87b`
- Work directory: `C:\d4j_work\postfix\Math_87b`
- Generated: `2026-07-25T16:55:29+00:00`

## Failure Summary
- `org.apache.commons.math.optimization.linear.SimplexSolverTest::testSingleVariableAndConstraint`: junit.framework.AssertionFailedError: expected:<10.0> but was:<0.0>

## Suspicious Frames
- `org.apache.commons.math.optimization.linear.SimplexSolverTest.testSingleVariableAndConstraint` at `SimplexSolverTest.java:75`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic 'Checking' error where the predicate logic for identifying a basic variable in the Simplex tableau is too broad (non-zero) instead of specific (equal to 1.0).

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
