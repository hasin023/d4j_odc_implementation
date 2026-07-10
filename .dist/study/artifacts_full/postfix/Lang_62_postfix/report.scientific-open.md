# Defects4J ODC Classification Report: Lang-62

- Version: `62b`
- Work directory: `C:\d4j_work\postfix\Lang_62b`
- Generated: `2026-07-10T19:20:49+00:00`

## Failure Summary
- `org.apache.commons.lang.EntitiesTest::testNumberOverflow`: junit.framework.ComparisonFailure: expected:<[&#12345678;]> but was:<[慎]>

## Suspicious Frames
- `org.apache.commons.lang.EntitiesTest.doTestUnescapeEntity` at `EntitiesTest.java:101`
- `org.apache.commons.lang.EntitiesTest.testNumberOverflow` at `EntitiesTest.java:201`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by the absence of a guard condition (check) for the numeric value of an entity. The code attempts to convert an integer to a character without verifying if the integer is a valid character code point. This is a quintessential Checking defect.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
