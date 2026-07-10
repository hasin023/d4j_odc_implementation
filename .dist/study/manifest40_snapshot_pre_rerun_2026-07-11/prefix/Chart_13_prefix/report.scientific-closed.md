# Defects4J ODC Classification Report: Chart-13

- Version: `13b`
- Work directory: `C:\d4j_work\prefix\Chart_13b`
- Generated: `2026-07-08T17:02:09+00:00`

## Failure Summary
- `org.jfree.chart.block.junit.BorderArrangementTests::testSizingWithWidthConstraint`: java.lang.IllegalArgumentException: Range(double, double): require lower (0.0) <= upper (-2.3000000000000007).

## Suspicious Frames
- `org.jfree.data.Range.<init>` at `Range.java:87`
- `org.jfree.chart.block.BorderArrangement.arrangeFF` at `BorderArrangement.java:455`
- `org.jfree.chart.block.BorderArrangement.arrange` at `BorderArrangement.java:152`
- `org.jfree.chart.block.BorderArrangement.arrangeFN` at `BorderArrangement.java:323`
- `org.jfree.chart.block.BorderArrangement.arrange` at `BorderArrangement.java:149`
- `org.jfree.chart.block.BlockContainer.arrange` at `BlockContainer.java:182`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The failure is a direct result of an invalid parameter (negative upper bound) being passed to the Range class. The logic in BorderArrangement.arrangeFF performs a subtraction that can result in a negative value, which is then used to construct a Range object without any prior validation or clamping.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Age: `New`
- Source: `Requirement`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Recovery/Exception`
- Inferred Impact: `Reliability`
