# Defects4J ODC Classification Report: Lang-22

- Version: `22b`
- Work directory: `C:\d4j_work\postfix\Lang_22b`
- Generated: `2026-07-10T19:45:02+00:00`

## Failure Summary
- `org.apache.commons.lang3.math.FractionTest::testReducedFactory_int_int`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>
- `org.apache.commons.lang3.math.FractionTest::testReduce`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>

## Suspicious Frames
- `org.apache.commons.lang3.math.FractionTest.testReducedFactory_int_int` at `FractionTest.java:336`
- `org.apache.commons.lang3.math.FractionTest.testReduce` at `FractionTest.java:654`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is in the computational logic of the greatestCommonDivisor method. It is not a simple missing guard (Checking) because the logic itself is fundamentally flawed for the specific input range of Integer.MIN_VALUE. It is not an Assignment/Initialization issue because the error is in the procedural calculation of the GCD. Therefore, it is an Algorithm/Method defect.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Reliability`
