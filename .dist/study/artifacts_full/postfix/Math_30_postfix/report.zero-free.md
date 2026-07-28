# Defects4J ODC Classification Report: Math-30

- Version: `30b`
- Work directory: `C:\d4j_work\postfix\Math_30b`
- Generated: `2026-07-25T17:12:49+00:00`

## Failure Summary
- `org.apache.commons.math3.stat.inference.MannWhitneyUTestTest::testBigDataSet`: junit.framework.AssertionFailedError

## Suspicious Frames
- `org.apache.commons.math3.stat.inference.MannWhitneyUTestTest.testBigDataSet` at `MannWhitneyUTestTest.java:113`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Integer overflow`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the product of two integers (n1 * n2) is stored in an integer variable (n1n2prod). When the input data sets are large, this multiplication exceeds the maximum value representable by a 32-bit signed integer, causing an overflow. This leads to incorrect calculations for the Mann-Whitney U test statistic. The fix changes the data type of the intermediate product variable from 'int' to 'double' to accommodate larger values and prevent overflow.
