# Defects4J ODC Classification Report: Closure-95

- Version: `95b`
- Work directory: `C:\d4j_work\postfix\Closure_95b`
- Generated: `2026-07-26T07:21:13+00:00`

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
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `incorrect scope resolution for qualified names`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs because the compiler fails to correctly resolve qualified names (like 'ns.foo') when they are defined within a local scope but intended to be part of the global namespace. The fix introduces logic to check if a property access (GETPROP) is rooted in the global scope; if it is, and the variable is not already declared in the local scope, the compiler now correctly promotes the declaration to the global scope. This ensures that qualified names are consistently tracked across different scopes, preventing type inference errors and scope lookup failures.
