# Defects4J ODC Classification Report: Closure-27

- Version: `27b`
- Work directory: `C:\d4j_work\prefix\Closure_27b`
- Generated: `2026-07-26T06:21:17+00:00`

## Failure Summary
- `com.google.javascript.rhino.IRTest::testIssue727_1`: java.lang.IllegalStateException
- `com.google.javascript.rhino.IRTest::testIssue727_2`: java.lang.IllegalStateException
- `com.google.javascript.rhino.IRTest::testIssue727_3`: java.lang.IllegalStateException

## Suspicious Frames
- `com.google.common.base.Preconditions.checkState` at `Preconditions.java:129`
- `com.google.javascript.rhino.IR.tryFinally` at `IR.java:224`
- `com.google.javascript.rhino.IR.block` at `IR.java:97`
- `com.google.javascript.rhino.IR.tryCatch` at `IR.java:233`
- `com.google.javascript.rhino.IR.tryCatchFinally` at `IR.java:240`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The IR factory methods are enforcing incorrect constraints on the nodes passed to them. Specifically, IR.tryCatch calls IR.block(catchNode), but IR.block(Node) requires the node to be a statement, which a CATCH node is not. IR.tryFinally incorrectly checks if the tryBody is a label name. These are validation errors in the factory methods.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
