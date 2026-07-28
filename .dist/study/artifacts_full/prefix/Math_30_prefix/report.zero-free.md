# Defects4J ODC Classification Report: Math-30

- Version: `30b`
- Work directory: `C:\d4j_work\prefix\Math_30b`
- Generated: `2026-07-25T17:12:47+00:00`

## Failure Summary
- `org.apache.commons.math3.stat.inference.MannWhitneyUTestTest::testBigDataSet`: junit.framework.AssertionFailedError

## Suspicious Frames
- `org.apache.commons.math3.stat.inference.MannWhitneyUTestTest.testBigDataSet` at `MannWhitneyUTestTest.java:113`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Integer Overflow`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report explicitly identifies that the Mann-Whitney U test implementation uses integer arithmetic for intermediate calculations in large data sets. When the data set size is large (e.g., 1500 elements), these intermediate values exceed the capacity of a 32-bit signed integer, causing an overflow. This leads to incorrect p-value calculations, which causes the assertion in the test case to fail.
