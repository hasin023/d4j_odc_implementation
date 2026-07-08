# Defects4J ODC Classification Report: Chart-13

- Version: `13b`
- Work directory: `C:\d4j_work\prefix\Chart_13b`
- Generated: `2026-07-08T16:46:30+00:00`

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
- ODC Type: `invalid range calculation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The failing test triggers an IllegalArgumentException in the Range constructor because the upper bound is calculated as a negative value. In BorderArrangement.java, the code calculates the width constraint for the right block by subtracting the width of the left block (w[2]) from the total container width. If the left block's width exceeds the available container width, the resulting range upper bound becomes negative, violating the invariant that the lower bound (0.0) must be less than or equal to the upper bound.
