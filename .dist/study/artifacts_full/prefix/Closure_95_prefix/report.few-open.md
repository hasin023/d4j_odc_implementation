# Defects4J ODC Classification Report: Closure-95

- Version: `95b`
- Work directory: `C:\d4j_work\prefix\Closure_95b`
- Generated: `2026-07-26T07:04:49+00:00`

## Failure Summary
- `com.google.javascript.jscomp.TypeCheckTest::testQualifiedNameInference5`: junit.framework.AssertionFailedError: expected a warning
- `com.google.javascript.jscomp.TypedScopeCreatorTest::testGlobalQualifiedNameInLocalScope`: junit.framework.AssertionFailedError

## Suspicious Frames
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:7365`
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:7345`
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:7298`
- `com.google.javascript.jscomp.TypeCheckTest.testQualifiedNameInference5` at `TypeCheckTest.java:4761`
- `com.google.javascript.jscomp.TypedScopeCreatorTest.testGlobalQualifiedNameInLocalScope` at `TypedScopeCreatorTest.java:781`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The issue is a failure in the type inference procedure for qualified names. It is not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object). It is a procedural error in how the compiler's type inference algorithm resolves and tracks qualified names across scopes, which is a classic Algorithm/Method defect.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
