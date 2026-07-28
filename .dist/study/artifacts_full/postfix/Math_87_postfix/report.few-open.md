# Defects4J ODC Classification Report: Math-87

- Version: `87b`
- Work directory: `C:\d4j_work\postfix\Math_87b`
- Generated: `2026-07-25T17:08:39+00:00`

## Failure Summary
- `org.apache.commons.math.optimization.linear.SimplexSolverTest::testSingleVariableAndConstraint`: junit.framework.AssertionFailedError: expected:<10.0> but was:<0.0>

## Suspicious Frames
- `org.apache.commons.math.optimization.linear.SimplexSolverTest.testSingleVariableAndConstraint` at `SimplexSolverTest.java:75`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is in the procedural logic of the `getBasicRow` method, which incorrectly implemented the search criteria for a basic variable in the Simplex tableau. This is a classic algorithmic error where the implementation of the search strategy was flawed, not a missing guard (Checking) or a simple initialization error (Assignment/Initialization).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
