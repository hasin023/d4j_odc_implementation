# Defects4J ODC Classification Report: Closure-95

- Version: `95b`
- Work directory: `C:\d4j_work\prefix\Closure_95b`
- Generated: `2026-07-26T07:21:10+00:00`

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
- ODC Type: `Incorrect Scope Resolution for Qualified Names`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The failing tests indicate that the compiler is failing to correctly resolve or infer types for qualified names (e.g., 'ns.foo') when they are defined within a local scope (like an IIFE) but intended to be accessible globally. The compiler's type inference mechanism is likely failing to correctly associate the qualified name with the global scope, leading to missing type information or incorrect warnings during type checking. This is evidenced by the failure of 'testGlobalQualifiedNameInLocalScope' to find the variable in the global scope and the failure of 'testQualifiedNameInference5' to trigger expected type mismatch warnings.
