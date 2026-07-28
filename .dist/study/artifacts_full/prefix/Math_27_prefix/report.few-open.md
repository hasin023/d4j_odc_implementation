# Defects4J ODC Classification Report: Math-27

- Version: `27b`
- Work directory: `C:\d4j_work\prefix\Math_27b`
- Generated: `2026-07-25T17:01:55+00:00`

## Failure Summary
- `org.apache.commons.math3.fraction.FractionTest::testMath835`: junit.framework.AssertionFailedError: expected:<2.1691754E9> but was:<-2.125791896E9>

## Suspicious Frames
- `org.apache.commons.math3.fraction.FractionTest.testMath835` at `FractionTest.java:253`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is a classic case of an incorrect computational strategy (order of operations) leading to overflow. It is not a missing check (Checking), not a wrong constant (Assignment/Initialization), and not a design-level capability gap (Function/Class/Object). It is a procedural error in the implementation of the percentage calculation.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
