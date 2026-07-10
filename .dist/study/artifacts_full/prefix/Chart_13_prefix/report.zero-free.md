# Defects4J ODC Classification Report: Chart-13

- Version: `13b`
- Work directory: `C:\d4j_work\prefix\Chart_13b`
- Generated: `2026-07-10T18:52:54+00:00`

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
- ODC Type: `invalid range construction due to negative width calculation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The error occurs in BorderArrangement.arrangeFF, where a new Range object is created using 'constraint.getWidth() - w[2]' as the upper bound. When the width of the left block (w[2]) exceeds the total available width defined by the constraint, the resulting upper bound becomes negative. Since the Range constructor enforces that the lower bound (0.0) must be less than or equal to the upper bound, this negative value triggers an IllegalArgumentException.
