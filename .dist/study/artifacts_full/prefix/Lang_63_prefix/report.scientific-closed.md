# Defects4J ODC Classification Report: Lang-63

- Version: `63b`
- Work directory: `C:\d4j_work\prefix\Lang_63b`
- Generated: `2026-07-10T19:42:28+00:00`

## Failure Summary
- `org.apache.commons.lang.time.DurationFormatUtilsTest::testJiraLang281`: junit.framework.ComparisonFailure: expected:<[09]> but was:<[-2]>

## Suspicious Frames
- `org.apache.commons.lang.time.DurationFormatUtilsTest.testJiraLang281` at `DurationFormatUtilsTest.java:436`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a classic date-math error where the algorithm fails to correctly handle month-end rollovers. This is a procedural error in the calculation logic, fitting the Algorithm/Method classification.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
