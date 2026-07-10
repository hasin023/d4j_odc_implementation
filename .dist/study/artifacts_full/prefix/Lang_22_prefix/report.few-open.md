# Defects4J ODC Classification Report: Lang-22

- Version: `22b`
- Work directory: `C:\d4j_work\prefix\Lang_22b`
- Generated: `2026-07-10T19:23:31+00:00`

## Failure Summary
- `org.apache.commons.lang3.math.FractionTest::testReducedFactory_int_int`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>
- `org.apache.commons.lang3.math.FractionTest::testReduce`: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>

## Suspicious Frames
- `org.apache.commons.lang3.math.FractionTest.testReducedFactory_int_int` at `FractionTest.java:336`
- `org.apache.commons.lang3.math.FractionTest.testReduce` at `FractionTest.java:654`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The issue is a failure in the computational logic (GCD calculation) used to reduce fractions. It is not a missing check (Checking), a simple wrong constant (Assignment/Initialization), or a design-level capability gap (Function/Class/Object). It is a procedural error in the mathematical algorithm used to compute the GCD, which is a classic Algorithm/Method defect.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
