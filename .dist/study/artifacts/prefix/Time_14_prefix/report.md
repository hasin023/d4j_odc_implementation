# Defects4J ODC Classification Report: Time-14

- Version: `14b`
- Work directory: `.dist\study\work\prefix\Time_14b`
- Generated: `2026-04-21T14:59:56+00:00`

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
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is an algorithmic error in how the library handles date arithmetic for partials (MonthDay) involving leap days. It is not a missing check (the check is present but incorrectly applied to the wrong context), nor is it a simple initialization error. It is a procedural flaw in the calculation logic that requires a change to the algorithm used to add/subtract time from a partial date.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Recovery/Exception, Test Interaction, Test Variation`
- Inferred Impact: `Reliability`
