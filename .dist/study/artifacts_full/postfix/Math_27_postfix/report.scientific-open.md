# Defects4J ODC Classification Report: Math-27

- Version: `27b`
- Work directory: `C:\d4j_work\postfix\Math_27b`
- Generated: `2026-07-25T16:44:26+00:00`

## Failure Summary
- `org.apache.commons.math3.fraction.FractionTest::testMath835`: junit.framework.AssertionFailedError: expected:<2.1691754E9> but was:<-2.125791896E9>

## Suspicious Frames
- `org.apache.commons.math3.fraction.FractionTest.testMath835` at `FractionTest.java:253`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by an incorrect order of operations in the percentageValue() method. By multiplying by 100 while still in the integer-based Fraction domain, the code triggers an overflow. Changing the order to convert to double first avoids this overflow. This is a procedural/algorithmic error.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
