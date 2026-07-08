# Defects4J ODC Classification Report: Time-14

- Version: `14b`
- Work directory: `C:\d4j_work\prefix\Time_14b`
- Generated: `2026-07-08T17:00:29+00:00`

## Failure Summary
- `org.joda.time.TestMonthDay_Basics::testPlusMonths_int_negativeFromLeap`: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- `org.joda.time.TestMonthDay_Basics::testMinusDays_int_negativeFromLeap`: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- `org.joda.time.TestMonthDay_Basics::testPlusMonths_int_fromLeap`: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- `org.joda.time.TestMonthDay_Basics::testPlusMonths_int_negativeEndOfMonthAdjust`: junit.framework.AssertionFailedError: expected:<--02-29> but was:<--02-28>
- `org.joda.time.TestMonthDay_Basics::testMinusMonths_int_endOfMonthAdjust`: junit.framework.AssertionFailedError: expected:<--02-29> but was:<--02-28>
- `org.joda.time.TestMonthDay_Basics::testMinusMonths_int_negativeFromLeap`: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- `org.joda.time.TestMonthDay_Basics::testMinusMonths_int_fromLeap`: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- `org.joda.time.TestMonthDay_Basics::testPlusDays_int_fromLeap`: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]

## Suspicious Frames
- `org.joda.time.field.FieldUtils.verifyValueBounds` at `FieldUtils.java:220`
- `org.joda.time.field.PreciseDurationDateTimeField.set` at `PreciseDurationDateTimeField.java:78`
- `org.joda.time.chrono.BasicMonthOfYearDateTimeField.add` at `BasicMonthOfYearDateTimeField.java:213`
- `org.joda.time.MonthDay.withFieldAdded` at `MonthDay.java:519`
- `org.joda.time.MonthDay.plusMonths` at `MonthDay.java:592`
- `org.joda.time.field.BaseDateTimeField.add` at `BaseDateTimeField.java:324`
- `org.joda.time.MonthDay.minusDays` at `MonthDay.java:672`
- `org.joda.time.MonthDay.minusMonths` at `MonthDay.java:652`
- `org.joda.time.MonthDay.plusDays` at `MonthDay.java:612`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The implementation of 'add' in 'BasicMonthOfYearDateTimeField' attempts to perform arithmetic on a 'ReadablePartial' by converting it to a 'long' instant. It uses 0L as the base. For a 'MonthDay' of '--02-29', this conversion fails because 1970 (the year of 0L) does not have a February 29th. This is a classic algorithmic error where the procedure assumes a fixed year context that is incompatible with the data being processed.
