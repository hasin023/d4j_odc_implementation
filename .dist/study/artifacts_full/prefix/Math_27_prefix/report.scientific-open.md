# Defects4J ODC Classification Report: Math-27

- Version: `27b`
- Work directory: `C:\d4j_work\prefix\Math_27b`
- Generated: `2026-07-25T16:44:21+00:00`

## Failure Summary
- `org.apache.commons.math3.fraction.FractionTest::testMath835`: junit.framework.AssertionFailedError: expected:<2.1691754E9> but was:<-2.125791896E9>

## Suspicious Frames
- `org.apache.commons.math3.fraction.FractionTest.testMath835` at `FractionTest.java:253`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic order-of-operations error where an intermediate calculation (numerator * 100) overflows the integer type before the result is converted to a double. This is a procedural/algorithmic error in the implementation of the percentageValue method.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
