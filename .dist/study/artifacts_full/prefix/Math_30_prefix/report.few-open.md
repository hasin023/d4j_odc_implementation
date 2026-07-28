# Defects4J ODC Classification Report: Math-30

- Version: `30b`
- Work directory: `C:\d4j_work\prefix\Math_30b`
- Generated: `2026-07-25T17:02:14+00:00`

## Failure Summary
- `org.apache.commons.math3.stat.inference.MannWhitneyUTestTest::testBigDataSet`: junit.framework.AssertionFailedError

## Suspicious Frames
- `org.apache.commons.math3.stat.inference.MannWhitneyUTestTest.testBigDataSet` at `MannWhitneyUTestTest.java:113`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is a computational error where the algorithm uses an inappropriate data type (int) for intermediate steps, leading to overflow on large inputs. This is a classic Algorithm/Method defect as it involves correcting the computational strategy (data type selection for intermediate values) to ensure correctness.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
