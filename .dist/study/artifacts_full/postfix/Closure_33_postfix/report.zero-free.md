# Defects4J ODC Classification Report: Closure-33

- Version: `33b`
- Work directory: `C:\d4j_work\postfix\Closure_33b`
- Generated: `2026-07-26T07:16:49+00:00`

## Failure Summary
- `com.google.javascript.jscomp.TypeCheckTest::testIssue700`: junit.framework.AssertionFailedError: unexpected warnings(s):

## Suspicious Frames
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:9908`
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:9882`
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:9820`
- `com.google.javascript.jscomp.TypeCheckTest.testTypes` at `TypeCheckTest.java:9816`
- `com.google.javascript.jscomp.TypeCheckTest.testIssue700` at `TypeCheckTest.java:5777`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `incorrect type constraint propagation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs because the type checker incorrectly applies property constraints from one object type to another unrelated object type. Specifically, the `matchConstraint` method in `PrototypeObjectType` was attempting to reconcile properties even for named types, which should not be subject to anonymous record type constraint matching. By adding a check to return early if the object has a reference name, the compiler prevents the accidental leakage of property requirements (like making a property optional/undefined) from unrelated code paths into the type inference of other objects.
