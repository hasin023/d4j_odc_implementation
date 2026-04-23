# Defects4J ODC Classification Report: Chart-13

- Version: `13b`
- Work directory: `.dist\study\work\prefix\Chart_13b`
- Generated: `2026-04-21T13:12:41+00:00`

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
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is a classic boundary/validation issue. The code fails to validate that the calculated width is non-negative before using it to construct a Range object. This is a missing guard/check on the input parameters to the Range constructor.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Recovery/Exception, Test Sequencing`
- Inferred Impact: `Reliability`
