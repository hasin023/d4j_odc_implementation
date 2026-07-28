# Defects4J ODC Classification Report: Math-30

- Version: `30b`
- Work directory: `C:\d4j_work\prefix\Math_30b`
- Generated: `2026-07-25T16:44:57+00:00`

## Failure Summary
- `org.apache.commons.math3.stat.inference.MannWhitneyUTestTest::testBigDataSet`: junit.framework.AssertionFailedError

## Suspicious Frames
- `org.apache.commons.math3.stat.inference.MannWhitneyUTestTest.testBigDataSet` at `MannWhitneyUTestTest.java:113`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is a classic case of using an inappropriate data type (int) for a calculation that can exceed the range of a 32-bit integer, which is a procedural/algorithmic error in the implementation of the Mann-Whitney U test.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
