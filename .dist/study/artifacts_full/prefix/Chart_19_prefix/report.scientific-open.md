# Defects4J ODC Classification Report: Chart-19

- Version: `19b`
- Work directory: `C:\d4j_work\prefix\Chart_19b`
- Generated: `2026-07-25T12:23:53+00:00`

## Failure Summary
- `org.jfree.chart.plot.junit.CategoryPlotTests::testGetRangeAxisIndex`: junit.framework.AssertionFailedError
- `org.jfree.chart.plot.junit.CategoryPlotTests::testGetDomainAxisIndex`: junit.framework.AssertionFailedError

## Suspicious Frames
- `org.jfree.chart.plot.junit.CategoryPlotTests.testGetRangeAxisIndex` at `CategoryPlotTests.java:761`
- `org.jfree.chart.plot.junit.CategoryPlotTests.testGetDomainAxisIndex` at `CategoryPlotTests.java:737`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The test code explicitly checks for an IllegalArgumentException when passing null to the axis index methods. Since the test fails, the production code must be missing the corresponding check, which is a 'Checking' defect.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
