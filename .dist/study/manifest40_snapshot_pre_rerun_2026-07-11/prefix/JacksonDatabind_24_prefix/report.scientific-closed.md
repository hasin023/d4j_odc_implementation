# Defects4J ODC Classification Report: JacksonDatabind-24

- Version: `24b`
- Work directory: `C:\d4j_work\prefix\JacksonDatabind_24b`
- Generated: `2026-07-08T17:05:07+00:00`

## Failure Summary
- `com.fasterxml.jackson.databind.ser.TestConfig::testDateFormatConfig`: junit.framework.AssertionFailedError: expected:<sun.util.calendar.ZoneInfo[id="America/Los_Angeles",offset=-28800000,dstSavings=3600000,useDaylight=true,transitions=185,lastRule=java.util.SimpleTimeZone[id=America/Los_Angeles,offset=-28800000,dstSavings=3600000,useDaylight=true,startYear=0,startMode=3,startMonth=2,startDay=8,startDayOfWeek=1,startTime=7200000,startTimeMode=0,endMode=3,endMonth=10,endDay=1,endDayOfWeek=1,endTime=7200000,endTimeMode=0]]> but was:<sun.util.calendar.ZoneInfo[id="GMT",offset=0,dstSavings=0,useDaylight=false,transitions=0,lastRule=null]>

## Suspicious Frames
- `com.fasterxml.jackson.databind.ser.TestConfig.testDateFormatConfig` at `TestConfig.java:221`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Assignment/Initialization`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug report describes a state change (timezone) that occurs as a side effect of a configuration method (setDateFormat). This is an assignment error where the new state is incorrectly initialized/assigned based on the input parameter.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `New`
- Source: `Requirement`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Test Variation`
- Inferred Impact: `Reliability`
