# Defects4J ODC Classification Report: JacksonDatabind-24

- Version: `24b`
- Work directory: `C:\d4j_work\prefix\JacksonDatabind_24b`
- Generated: `2026-07-10T18:53:56+00:00`

## Failure Summary
- `com.fasterxml.jackson.databind.ser.TestConfig::testDateFormatConfig`: junit.framework.AssertionFailedError: expected:<sun.util.calendar.ZoneInfo[id="America/Los_Angeles",offset=-28800000,dstSavings=3600000,useDaylight=true,transitions=185,lastRule=java.util.SimpleTimeZone[id=America/Los_Angeles,offset=-28800000,dstSavings=3600000,useDaylight=true,startYear=0,startMode=3,startMonth=2,startDay=8,startDayOfWeek=1,startTime=7200000,startTimeMode=0,endMode=3,endMonth=10,endDay=1,endDayOfWeek=1,endTime=7200000,endTimeMode=0]]> but was:<sun.util.calendar.ZoneInfo[id="GMT",offset=0,dstSavings=0,useDaylight=false,transitions=0,lastRule=null]>

## Suspicious Frames
- `com.fasterxml.jackson.databind.ser.TestConfig.testDateFormatConfig` at `TestConfig.java:221`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `unintended side effect in configuration setter`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug report and test evidence indicate that calling 'mapper.setDateFormat(DateFormat)' causes the ObjectMapper's configured TimeZone to be overwritten by the JVM's default TimeZone. The test 'testDateFormatConfig' explicitly asserts that setting a custom DateFormat should not alter the previously configured TimeZone of the mapper. The evidence suggests that the implementation of 'setDateFormat' incorrectly synchronizes or resets the mapper's global TimeZone state to the default system timezone, which is an unintended side effect that breaks existing configuration consistency.
