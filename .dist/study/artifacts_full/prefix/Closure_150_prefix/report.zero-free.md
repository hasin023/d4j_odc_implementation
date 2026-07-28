# Defects4J ODC Classification Report: Closure-150

- Version: `150b`
- Work directory: `C:\d4j_work\prefix\Closure_150b`
- Generated: `2026-07-26T07:26:16+00:00`

## Failure Summary
- `com.google.javascript.jscomp.TypedScopeCreatorTest::testNamespacedFunctionStubLocal`: junit.framework.AssertionFailedError
- `com.google.javascript.jscomp.TypedScopeCreatorTest::testCollectedFunctionStubLocal`: junit.framework.AssertionFailedError

## Suspicious Frames
- `com.google.javascript.jscomp.TypedScopeCreatorTest.testNamespacedFunctionStubLocal` at `TypedScopeCreatorTest.java:251`
- `com.google.javascript.jscomp.TypedScopeCreatorTest.testCollectedFunctionStubLocal` at `TypedScopeCreatorTest.java:222`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Scope resolution failure for nested function definitions`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The failing tests indicate that the compiler fails to correctly associate JSDoc annotations with functions defined inside local scopes (e.g., within an anonymous function). The TypedScopeCreator is failing to properly register properties or types when they are defined within a nested scope, leading to the 'AssertionFailedError' where the expected properties are missing from the object type. This aligns with the bug report describing how JSDoc annotations are ignored when functions are defined inside an anonymous function wrapper.
