# Defects4J ODC Classification Report: Closure-141

- Version: `141b`
- Work directory: `C:\d4j_work\prefix\Closure_141b`
- Generated: `2026-07-26T06:45:02+00:00`

## Failure Summary
- `com.google.javascript.jscomp.ExpresssionDecomposerTest::testCanExposeExpression2`: junit.framework.AssertionFailedError: expected:<MOVABLE> but was:<DECOMPOSABLE>
- `com.google.javascript.jscomp.ExpresssionDecomposerTest::testCanExposeExpression7`: junit.framework.AssertionFailedError: expected:<MOVABLE> but was:<DECOMPOSABLE>
- `com.google.javascript.jscomp.InlineFunctionsTest::testDecomposeAnonymousInCall`: java.lang.IllegalStateException: Call site missed.
- `com.google.javascript.jscomp.PureFunctionIdentifierTest::testCallFunctionFOrGViaHookWithSideEffects`: junit.framework.AssertionFailedError: expected:<[(g : g), k]> but was:<[]>
- `com.google.javascript.jscomp.PureFunctionIdentifierTest::testCallFunctionForGorH`: junit.framework.AssertionFailedError: expected:<[(f : (g || h)), i]> but was:<[]>
- `com.google.javascript.jscomp.PureFunctionIdentifierTest::testCallFunctionFOrG`: junit.framework.AssertionFailedError: expected:<[(f || g), h]> but was:<[]>
- `com.google.javascript.jscomp.PureFunctionIdentifierTest::testCallFunctionFOrGViaHook`: junit.framework.AssertionFailedError: expected:<[(f : g), h]> but was:<[]>
- `com.google.javascript.jscomp.PureFunctionIdentifierTest::testCallFunctionFOrGWithSideEffects`: junit.framework.AssertionFailedError: expected:<[(g || g), k]> but was:<[]>

## Suspicious Frames
- `com.google.javascript.jscomp.InlineFunctions.verifyAllReferencesInlined` at `InlineFunctions.java:754`
- `com.google.javascript.jscomp.InlineFunctions.removeInlinedFunctions` at `InlineFunctions.java:740`
- `com.google.javascript.jscomp.InlineFunctions.process` at `InlineFunctions.java:143`
- `com.google.javascript.jscomp.CompilerTestCase.test` at `CompilerTestCase.java:694`
- `com.google.javascript.jscomp.CompilerTestCase.test` at `CompilerTestCase.java:372`
- `com.google.javascript.jscomp.CompilerTestCase.test` at `CompilerTestCase.java:302`
- `com.google.javascript.jscomp.CompilerTestCase.test` at `CompilerTestCase.java:271`
- `com.google.javascript.jscomp.CompilerTestCase.test` at `CompilerTestCase.java:259`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug report explicitly mentions that side effects of 'function1||function2' are not calculated. The failing tests confirm that expressions with logical/ternary operators are misclassified. This is a classic algorithmic error in the compiler's analysis pass where the traversal logic for side-effect detection is incomplete for specific node types.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
