# Defects4J ODC Classification Report: Math-75

- Version: `75b`
- Work directory: `C:\d4j_work\postfix\Math_75b`
- Generated: `2026-07-25T16:53:13+00:00`

## Failure Summary
- `org.apache.commons.math.stat.FrequencyTest::testPcts`: junit.framework.AssertionFailedError: three (Object) pct expected:<0.5> but was:<1.0>

## Suspicious Frames
- `org.apache.commons.math.stat.FrequencyTest.testPcts` at `FrequencyTest.java:148`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a clear case of an incorrect method call within the implementation of Frequency.getPct(Object). This is a procedural error where the wrong method is invoked to calculate the desired result.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
