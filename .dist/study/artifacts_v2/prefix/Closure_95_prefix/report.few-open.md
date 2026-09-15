# Defects4J ODC Classification Report: Closure-95

- Version: `95b`
- Work directory: `.dist\study\work\prefix\Closure_95b`
- Generated: `2026-09-15T08:43:13+00:00`

## Failure Summary
- `com.google.javascript.jscomp.TypeCheckTest::testQualifiedNameInference5`: junit.framework.AssertionFailedError: expected a warning
- `com.google.javascript.jscomp.TypedScopeCreatorTest::testGlobalQualifiedNameInLocalScope`: junit.framework.AssertionFailedError

## Suspicious Frames
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:7365`
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:7345`
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:7298`
- `com.google.javascript.jscomp.TypeCheckTest.testQualifiedNameInference5` at `TypeCheckTest.java:4761`
- `com.google.javascript.jscomp.TypedScopeCreatorTest.testGlobalQualifiedNameInLocalScope` at `TypedScopeCreatorTest.java:781`
- `com.google.javascript.jscomp.AbstractCompiler.` at `com/google/javascript/jscomp/AbstractCompiler.java:35`
- `com.google.javascript.jscomp.CheckLevel.` at `com/google/javascript/jscomp/CheckLevel.java:30`
- `com.google.javascript.jscomp.CodeChangeHandler.` at `coverage: line_rate=1.00`
- `com.google.javascript.jscomp.CodingConvention.` at `coverage: line_rate=1.00`
- `com.google.javascript.jscomp.CompilerPass.` at `coverage: line_rate=1.00`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The bug involves incorrect type inference logic for qualified names (e.g., 'ns.foo') when they are defined inside a function scope. This is a procedural logic error in how the compiler tracks and resolves qualified names across scopes, which is a core algorithmic task of the type checker. It is not a missing guard (Checking), a simple initialization error (Assignment), or a design-level capability gap (Function/Class/Object).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
