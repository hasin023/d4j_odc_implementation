# Defects4J ODC Classification Report: Lang-62

- Version: `62b`
- Work directory: `C:\d4j_work\prefix\Lang_62b`
- Generated: `2026-07-10T19:20:45+00:00`

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

The bug report explicitly states that the maximum value for a char is 0xFFFF and that the entity should be left as is if it exceeds this. The failure is a direct result of missing this validation check.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
