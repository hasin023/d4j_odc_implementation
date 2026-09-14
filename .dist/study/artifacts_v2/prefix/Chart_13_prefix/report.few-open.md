# Defects4J ODC Classification Report: Chart-13

- Version: `13b`
- Work directory: `C:\d4j-work\study-work\prefix\Chart_13b`
- Generated: `2026-09-14T05:20:13+00:00`

## Failure Summary
- `org.jfree.chart.block.junit.BorderArrangementTests::testSizingWithWidthConstraint`: java.lang.IllegalArgumentException: Range(double, double): require lower (0.0) <= upper (-2.3000000000000007).

## Suspicious Frames
- `org.jfree.data.Range.<init>` at `Range.java:87`
- `org.jfree.chart.block.BorderArrangement.arrangeFF` at `BorderArrangement.java:455`
- `org.jfree.chart.block.BorderArrangement.arrange` at `BorderArrangement.java:152`
- `org.jfree.chart.block.BorderArrangement.arrangeFN` at `BorderArrangement.java:323`
- `org.jfree.chart.block.BorderArrangement.arrange` at `BorderArrangement.java:149`
- `org.jfree.chart.block.BlockContainer.arrange` at `BlockContainer.java:182`
- `org.jfree.chart.ChartMouseListener.` at `coverage: line_rate=1.00`
- `org.jfree.chart.Drawable.` at `coverage: line_rate=1.00`
- `org.jfree.chart.Effect3D.` at `coverage: line_rate=1.00`
- `org.jfree.chart.LegendItemSource.` at `coverage: line_rate=1.00`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The root cause is a missing guard condition in BorderArrangement.arrangeFF. The code calculates a range for the right block using 'constraint.getWidth() - w[2]'. If w[2] (the width of the left block) is greater than the total constraint width, the resulting upper bound becomes negative. The Range constructor correctly enforces the invariant (lower <= upper), but the calling code fails to validate that the calculated width is non-negative before creating the Range object. Adding a check to ensure the width is at least 0.0 before creating the Range would prevent the exception.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
