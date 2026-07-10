# Defects4J ODC Classification Report: Chart-13

- Version: `13b`
- Work directory: `C:\d4j_work\prefix\Chart_13b`
- Generated: `2026-07-10T18:43:52+00:00`

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
- Confidence: `0.9`
- Needs Human Review: `False`

The code at BorderArrangement.java:455 performs a subtraction that can result in a negative value if the left block's width (w[2]) is greater than the total width. This violates the precondition of the Range constructor (lower <= upper). This is a classic missing validation/guard defect.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
