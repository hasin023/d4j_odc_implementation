# Defects4J ODC Classification Report: Time-10

- Version: `10b`
- Work directory: `C:\d4j_work\postfix\Time_10b`
- Generated: `2026-07-25T12:30:00+00:00`

## Failure Summary
- `org.joda.time.TestDays::testFactory_daysBetween_RPartial_MonthDay`: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- `org.joda.time.TestMonths::testFactory_monthsBetween_RPartial_MonthDay`: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]

## Suspicious Frames
- `org.joda.time.field.FieldUtils.verifyValueBounds` at `FieldUtils.java:220`
- `org.joda.time.field.PreciseDurationDateTimeField.set` at `PreciseDurationDateTimeField.java:78`
- `org.joda.time.chrono.BaseChronology.set` at `BaseChronology.java:240`
- `org.joda.time.base.BaseSingleFieldPeriod.between` at `BaseSingleFieldPeriod.java:104`
- `org.joda.time.Days.daysBetween` at `Days.java:141`
- `org.joda.time.Months.monthsBetween` at `Months.java:161`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by an incorrect algorithmic choice of the reference year (1970) for date calculations involving `MonthDay`. This is a procedural error in how the library handles partial dates that might include leap days. The fix is to use a leap year as the reference point, which is a local algorithmic correction.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
