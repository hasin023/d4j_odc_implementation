# Defects4J ODC Classification Report: Math-75

- Version: `75b`
- Work directory: `C:\d4j_work\postfix\Math_75b`
- Generated: `2026-07-25T17:07:20+00:00`

## Failure Summary
- `org.apache.commons.math.stat.FrequencyTest::testPcts`: junit.framework.AssertionFailedError: three (Object) pct expected:<0.5> but was:<1.0>

## Suspicious Frames
- `org.apache.commons.math.stat.FrequencyTest.testPcts` at `FrequencyTest.java:148`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a clear case of an incorrect method call within a procedure. The method getPct(Object) was intended to calculate the percentage of a specific value, but it was erroneously calling the cumulative percentage method (getCumPct). This is a procedural/algorithmic error rather than a missing check, a wrong value assignment, or a design-level capability gap.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
