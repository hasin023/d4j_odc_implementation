# Defects4J ODC Classification Report: Time-6

- Version: `6b`
- Work directory: `C:\d4j_work\prefix\Time_6b`
- Generated: `2026-07-25T14:45:44+00:00`

## Failure Summary
- `org.joda.time.chrono.TestGJDate::test_cutoverPreZero`: junit.framework.AssertionFailedError
- `org.joda.time.chrono.TestGJDate::test_plusWeekyears_positiveToNegative_crossCutover`: junit.framework.AssertionFailedError: expected:<-0002-06-30> but was:<-0001-06-28>
- `org.joda.time.chrono.TestGJDate::test_plusYears_positiveToZero_crossCutover`: org.joda.time.IllegalFieldValueException: Value 0 for year is not supported
- `org.joda.time.chrono.TestGJDate::test_plusYears_positiveToNegative_crossCutover`: junit.framework.AssertionFailedError: expected:<-0002-06-30> but was:<-0001-06-30>
- `org.joda.time.chrono.TestGJDate::test_plusWeekyears_positiveToZero_crossCutover`: org.joda.time.IllegalFieldValueException: Value 0 for year is not supported

## Suspicious Frames
- `org.joda.time.chrono.JulianChronology.adjustYearForSet` at `JulianChronology.java:81`
- `org.joda.time.chrono.JulianChronology.getDateMidnightMillis` at `JulianChronology.java:207`
- `org.joda.time.chrono.BasicChronology.getDateTimeMillis` at `BasicChronology.java:159`
- `org.joda.time.chrono.JulianChronology.getDateTimeMillis` at `JulianChronology.java:50`
- `org.joda.time.chrono.GJChronology.convertByYear` at `GJChronology.java:85`
- `org.joda.time.chrono.GJChronology.gregorianToJulianByYear` at `GJChronology.java:588`
- `org.joda.time.chrono.GJChronology$CutoverField.gregorianToJulian` at `GJChronology.java:924`
- `org.joda.time.chrono.GJChronology$ImpreciseCutoverField.add` at `GJChronology.java:979`
- `org.joda.time.chrono.GJChronology$LinkedDurationField.add` at `GJChronology.java:1099`
- `org.joda.time.LocalDate.plusYears` at `LocalDate.java:1205`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `incorrect handling of year zero in calendar arithmetic`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The defect arises because the Joda-Time library's Julian and Gregorian calendar implementations do not support a year zero, which is standard for these calendars. When performing date arithmetic (like adding or subtracting years) that crosses the boundary between 1 BC and 1 AD, the internal logic fails to automatically skip the non-existent year zero. This results in an IllegalFieldValueException when the calculation attempts to set the year to zero, or incorrect date results when the logic fails to account for the missing year in the transition.
