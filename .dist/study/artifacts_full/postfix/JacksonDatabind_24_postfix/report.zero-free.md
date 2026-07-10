# Defects4J ODC Classification Report: JacksonDatabind-24

- Version: `24b`
- Work directory: `C:\d4j_work\postfix\JacksonDatabind_24b`
- Generated: `2026-07-10T18:53:58+00:00`

## Failure Summary
- `com.fasterxml.jackson.databind.ser.TestConfig::testDateFormatConfig`: junit.framework.AssertionFailedError: expected:<sun.util.calendar.ZoneInfo[id="America/Los_Angeles",offset=-28800000,dstSavings=3600000,useDaylight=true,transitions=185,lastRule=java.util.SimpleTimeZone[id=America/Los_Angeles,offset=-28800000,dstSavings=3600000,useDaylight=true,startYear=0,startMode=3,startMonth=2,startDay=8,startDayOfWeek=1,startTime=7200000,startTimeMode=0,endMode=3,endMonth=10,endDay=1,endDayOfWeek=1,endTime=7200000,endTimeMode=0]]> but was:<sun.util.calendar.ZoneInfo[id="GMT",offset=0,dstSavings=0,useDaylight=false,transitions=0,lastRule=null]>

## Suspicious Frames
- `com.fasterxml.jackson.databind.ser.TestConfig.testDateFormatConfig` at `TestConfig.java:221`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `unintended side effect`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug was introduced when the `BaseSettings` class was updated to automatically extract and apply the `TimeZone` from a provided `DateFormat` object whenever `setDateFormat` was called. This behavior caused the `ObjectMapper`'s configured `TimeZone` to be overwritten by the `TimeZone` of the `DateFormat` object, which is often the system default. The fix involved reverting this logic to ensure that the `ObjectMapper` retains its existing `TimeZone` configuration regardless of the `DateFormat` being set, thereby preserving the expected behavior from previous versions.
