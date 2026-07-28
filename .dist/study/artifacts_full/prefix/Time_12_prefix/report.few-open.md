# Defects4J ODC Classification Report: Time-12

- Version: `12b`
- Work directory: `C:\d4j_work\prefix\Time_12b`
- Generated: `2026-07-25T12:34:20+00:00`

## Failure Summary
- `org.joda.time.TestLocalDateTime_Constructors::testFactory_fromDateFields_beforeYearZero1`: junit.framework.AssertionFailedError: expected:<0000-02-03T04:05:06.007> but was:<0001-02-03T04:05:06.007>
- `org.joda.time.TestLocalDateTime_Constructors::testFactory_fromDateFields_beforeYearZero3`: junit.framework.AssertionFailedError: expected:<-0002-02-03T04:05:06.007> but was:<0003-02-03T04:05:06.007>
- `org.joda.time.TestLocalDateTime_Constructors::testFactory_fromCalendarFields_beforeYearZero1`: junit.framework.AssertionFailedError: expected:<0000-02-03T04:05:06.007> but was:<0001-02-03T04:05:06.007>
- `org.joda.time.TestLocalDateTime_Constructors::testFactory_fromCalendarFields_beforeYearZero3`: junit.framework.AssertionFailedError: expected:<-0002-02-03T04:05:06.007> but was:<0003-02-03T04:05:06.007>
- `org.joda.time.TestLocalDate_Constructors::testFactory_fromDateFields_beforeYearZero1`: junit.framework.AssertionFailedError: expected:<0000-02-03> but was:<0001-02-03>
- `org.joda.time.TestLocalDate_Constructors::testFactory_fromDateFields_beforeYearZero3`: junit.framework.AssertionFailedError: expected:<-0002-02-03> but was:<0003-02-03>
- `org.joda.time.TestLocalDate_Constructors::testFactory_fromCalendarFields_beforeYearZero1`: junit.framework.AssertionFailedError: expected:<0000-02-03> but was:<0001-02-03>
- `org.joda.time.TestLocalDate_Constructors::testFactory_fromCalendarFields_beforeYearZero3`: junit.framework.AssertionFailedError: expected:<-0002-02-03> but was:<0003-02-03>

## Suspicious Frames
- `org.joda.time.TestLocalDateTime_Constructors.testFactory_fromDateFields_beforeYearZero1` at `TestLocalDateTime_Constructors.java:155`
- `org.joda.time.TestLocalDateTime_Constructors.testFactory_fromDateFields_beforeYearZero3` at `TestLocalDateTime_Constructors.java:163`
- `org.joda.time.TestLocalDateTime_Constructors.testFactory_fromCalendarFields_beforeYearZero1` at `TestLocalDateTime_Constructors.java:117`
- `org.joda.time.TestLocalDateTime_Constructors.testFactory_fromCalendarFields_beforeYearZero3` at `TestLocalDateTime_Constructors.java:125`
- `org.joda.time.TestLocalDate_Constructors.testFactory_fromDateFields_beforeYearZero1` at `TestLocalDate_Constructors.java:147`
- `org.joda.time.TestLocalDate_Constructors.testFactory_fromDateFields_beforeYearZero3` at `TestLocalDate_Constructors.java:155`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is a classic missing validation/guard. The code fails to account for the ERA field in the input Calendar object, which is a necessary condition for correctly interpreting dates before year zero. This is a 'Checking' defect because the logic is missing a check on the input data (the ERA field) to determine the correct year value.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Capability`
