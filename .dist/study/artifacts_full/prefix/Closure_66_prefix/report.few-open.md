# Defects4J ODC Classification Report: Closure-66

- Version: `66b`
- Work directory: `C:\d4j_work\prefix\Closure_66b`
- Generated: `2026-07-26T07:01:43+00:00`

## Failure Summary
- `com.google.javascript.jscomp.TypeCheckTest::testGetTypedPercent5`: junit.framework.AssertionFailedError: expected:<100.0> but was:<62.5>
- `com.google.javascript.jscomp.TypeCheckTest::testGetTypedPercent6`: junit.framework.AssertionFailedError: expected:<100.0> but was:<66.66666666666667>

## Suspicious Frames
- `com.google.javascript.jscomp.TypeCheckTest.testGetTypedPercent5` at `TypeCheckTest.java:7784`
- `com.google.javascript.jscomp.TypeCheckTest.testGetTypedPercent6` at `TypeCheckTest.java:7789`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The issue is a miscalculation of a metric (typed percentage) based on the structure of the AST. This is a procedural logic error in how the compiler traverses and evaluates the type information of enum nodes, which fits the Algorithm/Method category as it involves correcting the computational strategy for determining type coverage.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
