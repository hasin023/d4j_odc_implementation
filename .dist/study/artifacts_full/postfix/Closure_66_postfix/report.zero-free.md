# Defects4J ODC Classification Report: Closure-66

- Version: `66b`
- Work directory: `C:\d4j_work\postfix\Closure_66b`
- Generated: `2026-07-26T07:19:17+00:00`

## Failure Summary
- `com.google.javascript.jscomp.TypeCheckTest::testGetTypedPercent5`: junit.framework.AssertionFailedError: expected:<100.0> but was:<62.5>
- `com.google.javascript.jscomp.TypeCheckTest::testGetTypedPercent6`: junit.framework.AssertionFailedError: expected:<100.0> but was:<66.66666666666667>

## Suspicious Frames
- `com.google.javascript.jscomp.TypeCheckTest.testGetTypedPercent5` at `TypeCheckTest.java:7784`
- `com.google.javascript.jscomp.TypeCheckTest.testGetTypedPercent6` at `TypeCheckTest.java:7789`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `incorrect type coverage calculation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the type checker incorrectly counts object literal keys as untyped nodes when calculating the percentage of typed code. In the buggy version, the code attempted to ensure a string type for nodes that were not object literal keys, but failed to explicitly mark object literal keys as 'not typeable' in the tally logic. The fix introduces a flag to correctly identify these keys as non-typeable, ensuring they do not negatively impact the typed percentage calculation.
