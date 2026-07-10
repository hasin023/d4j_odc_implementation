# Defects4J ODC Classification Report: JacksonDatabind-24

- Version: `24b`
- Work directory: `C:\d4j_work\prefix\JacksonDatabind_24b`
- Generated: `2026-07-08T16:47:30+00:00`

## Failure Summary
- `com.fasterxml.jackson.databind.ser.TestConfig::testDateFormatConfig`: junit.framework.AssertionFailedError: expected:<sun.util.calendar.ZoneInfo[id="America/Los_Angeles",offset=-28800000,dstSavings=3600000,useDaylight=true,transitions=185,lastRule=java.util.SimpleTimeZone[id=America/Los_Angeles,offset=-28800000,dstSavings=3600000,useDaylight=true,startYear=0,startMode=3,startMonth=2,startDay=8,startDayOfWeek=1,startTime=7200000,startTimeMode=0,endMode=3,endMonth=10,endDay=1,endDayOfWeek=1,endTime=7200000,endTimeMode=0]]> but was:<sun.util.calendar.ZoneInfo[id="GMT",offset=0,dstSavings=0,useDaylight=false,transitions=0,lastRule=null]>

## Suspicious Frames
- `com.fasterxml.jackson.databind.ser.TestConfig.testDateFormatConfig` at `TestConfig.java:221`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `unintended side effect in configuration setter`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report and failing test indicate that calling 'mapper.setDateFormat(DateFormat)' unexpectedly modifies the 'ObjectMapper''s configured time zone to the JVM default. This behavior was introduced in version 2.6.0 as an attempt to allow 'DateFormat' to propagate its time zone configuration, but it violates the expected behavior where the 'ObjectMapper''s time zone should remain stable unless explicitly changed. The evidence shows that the 'ObjectMapper''s time zone is reset to GMT (or the system default) after 'setDateFormat' is called, causing downstream serialization issues.
