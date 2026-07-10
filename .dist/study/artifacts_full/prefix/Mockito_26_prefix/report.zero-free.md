# Defects4J ODC Classification Report: Mockito-26

- Version: `26b`
- Work directory: `C:\d4j_work\prefix\Mockito_26b`
- Generated: `2026-07-10T18:54:45+00:00`

## Failure Summary
- `org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive`: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')
- `org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_primitive`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>
- `org.mockito.internal.stubbing.defaultanswers.ReturnsMocksTest::should_return_the_usual_default_values_for_primitives`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>
- `org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::should_return_the_usual_default_values_for_primitives`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>

## Suspicious Frames
- No suspicious stack frames were extracted.

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Type Mismatch in Default Value Return`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The failing tests consistently show that when a mock is expected to return a primitive double (0.0), it is instead returning an integer (0). This indicates that the logic responsible for providing default return values for primitive types is incorrectly mapping or returning an integer type where a double is expected, leading to ClassCastExceptions or assertion failures when comparing the returned value against the expected double.
