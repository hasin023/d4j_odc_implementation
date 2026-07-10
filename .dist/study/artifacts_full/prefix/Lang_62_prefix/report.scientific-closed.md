# Defects4J ODC Classification Report: Lang-62

- Version: `62b`
- Work directory: `C:\d4j_work\prefix\Lang_62b`
- Generated: `2026-07-10T19:42:19+00:00`

## Failure Summary
- `org.apache.commons.lang.EntitiesTest::testNumberOverflow`: junit.framework.ComparisonFailure: expected:<[&#12345678;]> but was:<[慎]>

## Suspicious Frames
- `org.apache.commons.lang.EntitiesTest.doTestUnescapeEntity` at `EntitiesTest.java:101`
- `org.apache.commons.lang.EntitiesTest.testNumberOverflow` at `EntitiesTest.java:201`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report explicitly states that the maximum value for a char is 0xFFFF and that values exceeding this should be left as-is. The failure confirms that the code is performing an invalid conversion. This is a missing guard/validation check.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
