# Defects4J ODC Classification Report: Chart-24

- Version: `24b`
- Work directory: `C:\d4j_work\prefix\Chart_24b`
- Generated: `2026-07-25T12:24:44+00:00`

## Failure Summary
- `org.jfree.chart.renderer.junit.GrayPaintScaleTests::testGetPaint`: java.lang.IllegalArgumentException: Color parameter outside of expected range: Red Green Blue

## Suspicious Frames
- `org.jfree.chart.renderer.GrayPaintScale.getPaint` at `GrayPaintScale.java:128`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code snippet for GrayPaintScale.getPaint shows that the input 'value' is clamped to 'v' (lines 124-125), but the subsequent calculation of 'g' (line 126) uses the original 'value'. This causes 'g' to fall outside the [0, 255] range when 'value' is outside the bounds, triggering an exception in the Color constructor.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
