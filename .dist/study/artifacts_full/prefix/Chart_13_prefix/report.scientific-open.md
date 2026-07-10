# Defects4J ODC Classification Report: Chart-13

- Version: `13b`
- Work directory: `C:\d4j_work\prefix\Chart_13b`
- Generated: `2026-07-10T18:35:16+00:00`

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

The failure is a direct result of an invalid parameter being passed to a constructor. The logic in BorderArrangement.arrangeFF assumes that the remaining width for the right block will always be positive. Since this is a validation error on input data (the calculated width), it falls under the 'Checking' category.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
