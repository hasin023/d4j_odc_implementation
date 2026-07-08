# Defects4J ODC Classification Report: Mockito-26

- Version: `26b`
- Work directory: `C:\d4j_work\postfix\Mockito_26b`
- Generated: `2026-07-08T16:48:05+00:00`

## Failure Summary
- `org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive`: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')
- `org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_primitive`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>
- `org.mockito.internal.stubbing.defaultanswers.ReturnsMocksTest::should_return_the_usual_default_values_for_primitives`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>
- `org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::should_return_the_usual_default_values_for_primitives`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>

## Suspicious Frames
- No suspicious stack frames were extracted.

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incorrect Type Initialization`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug was caused by an incorrect default value assignment in the Primitives utility class. Specifically, the map storing default values for primitive types was initialized with an integer (0) for the 'double.class' key instead of a double (0D). This led to a ClassCastException when the framework attempted to retrieve the default value for a double-returning method, as the retrieved Integer could not be cast to a Double.
