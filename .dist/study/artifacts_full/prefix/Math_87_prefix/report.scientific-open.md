# Defects4J ODC Classification Report: Math-87

- Version: `87b`
- Work directory: `C:\d4j_work\prefix\Math_87b`
- Generated: `2026-07-25T16:55:25+00:00`

## Failure Summary
- `org.apache.commons.math.optimization.linear.SimplexSolverTest::testSingleVariableAndConstraint`: junit.framework.AssertionFailedError: expected:<10.0> but was:<0.0>

## Suspicious Frames
- `org.apache.commons.math.optimization.linear.SimplexSolverTest.testSingleVariableAndConstraint` at `SimplexSolverTest.java:75`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic case of incorrect validation logic (Checking) where the condition for identifying a basic variable is too broad (non-zero instead of 1.0).

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
