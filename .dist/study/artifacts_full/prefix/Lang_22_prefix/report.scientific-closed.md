# Defects4J ODC Classification Report: Lang-22

- Version: `22b`
- Work directory: `C:\d4j_work\prefix\Lang_22b`
- Generated: `2026-07-10T19:37:20+00:00`

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
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report explicitly states that the GCD method does not find the GCD of Integer.MIN_VALUE and 2^k. The failure to reduce correctly is a procedural error in the GCD algorithm implementation, which is a classic Algorithm/Method defect.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
