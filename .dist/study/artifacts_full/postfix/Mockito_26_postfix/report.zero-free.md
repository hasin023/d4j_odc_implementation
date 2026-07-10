# Defects4J ODC Classification Report: Mockito-26

- Version: `26b`
- Work directory: `C:\d4j_work\postfix\Mockito_26b`
- Generated: `2026-07-10T18:54:46+00:00`

## Failure Summary
- `org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive`: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')
- `org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_primitive`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>
- `org.mockito.internal.stubbing.defaultanswers.ReturnsMocksTest::should_return_the_usual_default_values_for_primitives`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>
- `org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::should_return_the_usual_default_values_for_primitives`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>

## Suspicious Frames
- No suspicious stack frames were extracted.

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incorrect primitive type mapping`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug was caused by an incorrect entry in the `primitiveValues` map within the `Primitives` utility class. Specifically, the entry for `double.class` was mapped to an integer `0` instead of a double `0D`. This caused type mismatch errors (ClassCastException) and assertion failures in tests expecting a double value when the framework attempted to retrieve default values for primitive types.
