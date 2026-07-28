# Defects4J ODC Classification Report: Closure-66

- Version: `66b`
- Work directory: `C:\d4j_work\prefix\Closure_66b`
- Generated: `2026-07-26T06:29:22+00:00`

## Failure Summary
- `com.google.javascript.jscomp.TypeCheckTest::testGetTypedPercent5`: junit.framework.AssertionFailedError: expected:<100.0> but was:<62.5>
- `com.google.javascript.jscomp.TypeCheckTest::testGetTypedPercent6`: junit.framework.AssertionFailedError: expected:<100.0> but was:<66.66666666666667>

## Suspicious Frames
- `com.google.javascript.jscomp.TypeCheckTest.testGetTypedPercent5` at `TypeCheckTest.java:7784`
- `com.google.javascript.jscomp.TypeCheckTest.testGetTypedPercent6` at `TypeCheckTest.java:7789`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a failure to correctly validate/check the type status of enum properties. This falls under 'Checking' because the logic for determining if a node is 'typed' is missing the necessary predicate or validation for enum-annotated objects.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
