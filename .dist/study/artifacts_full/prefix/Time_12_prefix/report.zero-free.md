# Defects4J ODC Classification Report: Time-12

- Version: `12b`
- Work directory: `C:\d4j_work\prefix\Time_12b`
- Generated: `2026-07-25T14:46:10+00:00`

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
- ODC Type: `incorrect calendar era handling`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The failing tests demonstrate that when converting from a java.util.Calendar or java.util.Date to Joda-Time's LocalDate or LocalDateTime, the conversion logic fails to correctly account for the BC (Before Christ) era. Specifically, the tests show that dates in the BC era are being incorrectly interpreted as AD dates (e.g., year 1 BC is being treated as year 1 AD, or year 3 BC as year 3 AD). This indicates that the factory methods (fromDateFields/fromCalendarFields) are ignoring the ERA field of the source calendar, leading to an off-by-one or incorrect year calculation for dates before year zero.
