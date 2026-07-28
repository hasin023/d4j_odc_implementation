# Batch Study Analysis

- Created: `2026-07-25T14:34:22+00:00`
- Total pairs: **26**
- Projects covered: **1**
- Type changed: **8** (30.8%)
- Type unchanged: **18** (69.2%)
- No alternative overlap: **0** (0.0%)
- No family match: **0** (0.0%)
- Family match: **26** (100.0%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **26** of 26
- Capability: 16 (61.5%)
- Reliability: 10 (38.5%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **24/26** (92.3%)
- Kappa: 0.8434
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 12
- Reliability × Checking: 8
- Capability × Checking: 4
- Reliability × Algorithm/Method: 2

## Alternative Match Cases (Type Changed)

### Time-19
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The issue is not a missing check (Checking) or a simple wrong constant (Assignment/Initialization). It is a failure in the logic that determines the correct offset for a given time during a DST transition. This is a procedural calculation error, which falls under Algorithm/Method.
- Postfix reasoning summary: The bug is caused by an incorrect conditional check in the logic that determines the time zone offset during a DST transition. The fix modifies the predicate logic (changing > to >=), which falls squarely under the 'Checking' category as it involves correcting a boundary condition in a conditional statement.
- Prefix context signal: org.joda.time.TestDateTimeZoneCutover::testDateTimeCreation_london: junit.framework.ComparisonFailure: expected:<...1-10-30T01:15:00.000[+01:00]> but was:<...1-10-30T01:15:00.000[Z]>
- Postfix context signal: org.joda.time.TestDateTimeZoneCutover::testDateTimeCreation_london: junit.framework.ComparisonFailure: expected:<...1-10-30T01:15:00.000[+01:00]> but was:<...1-10-30T01:15:00.000[Z]>

### Time-23
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The issue is not a missing check (Checking) or a simple initialization error (Assignment/Initialization). It is a flaw in the procedural logic that maps legacy time zone identifiers to the library's internal representation. This is a classic algorithmic mapping error where the procedure for resolving the ID produces an incorrect result.
- Postfix reasoning summary: The bug is a classic case of incorrect data initialization. The system relies on a lookup table (a Map) to resolve legacy time zone IDs. The values in this map were hardcoded incorrectly, and the fix simply updates these values to the correct ones. This does not involve changing the algorithm, adding guards, or modifying interfaces; it is purely an assignment/initialization correction.
- Prefix context signal: org.joda.time.TestDateTimeZone::testForID_String_old: junit.framework.ComparisonFailure: expected:<[WET]> but was:<[Europe/London]>
- Postfix context signal: org.joda.time.TestDateTimeZone::testForID_String_old: junit.framework.ComparisonFailure: expected:<[WET]> but was:<[Europe/London]>

### Time-10
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Pre-fix primary 'Checking' found in post-fix alternative types
- Prefix reasoning summary: The defect is a classic 'Checking' issue. The code performs a validation check (verifyValueBounds) that is too restrictive for the input data (Feb 29). It is not an algorithmic error in the calculation itself, but a failure to correctly validate or permit a valid date value due to an overly rigid boundary check.
- Postfix reasoning summary: The bug is caused by an incorrect initialization value (the epoch 0L) used in a calculation. The fix involves changing this constant to a leap year (1972) to ensure that leap days are valid during the calculation process. This is a classic Assignment/Initialization defect where the initial state for a computation was incorrectly defined.
- Prefix context signal: org.joda.time.TestDays::testFactory_daysBetween_RPartial_MonthDay: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- Postfix context signal: org.joda.time.TestDays::testFactory_daysBetween_RPartial_MonthDay: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]

### Time-12
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic missing validation/guard. The code fails to account for the ERA field in the input Calendar object, which is a necessary condition for correctly interpreting dates before year zero. This is a 'Checking' defect because the logic is missing a check on the input data (the ERA field) to determine the correct year value.
- Postfix reasoning summary: The bug is a failure in the computational logic used to convert legacy Java date objects into Joda-Time objects. The fix involves modifying the calculation of the year based on the ERA field and adding a conditional path for negative time values. This is a classic algorithmic correction to a data transformation procedure.
- Prefix context signal: org.joda.time.TestLocalDateTime_Constructors::testFactory_fromDateFields_beforeYearZero1: junit.framework.AssertionFailedError: expected:<0000-02-03T04:05:06.007> but was:<0001-02-03T04:05:06.007>
- Postfix context signal: org.joda.time.TestLocalDateTime_Constructors::testFactory_fromDateFields_beforeYearZero1: junit.framework.AssertionFailedError: expected:<0000-02-03T04:05:06.007> but was:<0001-02-03T04:05:06.007>

### Time-16
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The issue is a procedural error in how the date parsing algorithm merges partial date information into an existing date object. It is not a missing guard (Checking) or a simple wrong constant (Assignment), but a flaw in the logic that determines the year during the parsing process. Therefore, it is classified as Algorithm/Method.
- Postfix reasoning summary: The bug is a classic case of incorrect initialization. The code was using a fixed default year when it should have been using the year from the existing instant. This is not a missing check (Checking), nor a procedural logic error (Algorithm/Method), but a simple assignment of the wrong value during object initialization.
- Prefix context signal: org.joda.time.format.TestDateTimeFormatter::testParseInto_monthOnly_baseStartYear: junit.framework.AssertionFailedError: expected:<2004-05-01T12:20:30.000+09:00> but was:<2000-05-01T12:20:30.000+09:00>
- Postfix context signal: org.joda.time.format.TestDateTimeFormatter::testParseInto_monthOnly_baseStartYear: junit.framework.AssertionFailedError: expected:<2004-05-01T12:20:30.000+09:00> but was:<2000-05-01T12:20:30.000+09:00>

### Time-3
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The issue is not a missing guard (Checking) or a wrong constant (Assignment/Initialization), but a flaw in the procedural logic that calculates the new date-time state. The method performs an unnecessary or incorrect re-calculation of the time zone offset when it should simply preserve the current state when the added duration is zero. This is a classic algorithmic error in handling state transitions.
- Postfix reasoning summary: The bug is caused by the absence of a validation check (a guard) that prevents the execution of a state-changing calculation when the input parameter is zero. Since the fix is to add this missing conditional check, it is classified as 'Checking'.
- Prefix context signal: org.joda.time.TestMutableDateTime_Adds::testAddYears_int_dstOverlapWinter_addZero: junit.framework.ComparisonFailure: expected:<...10-30T02:30:00.000+0[1]:00> but was:<...10-30T02:30:00.000+0[2]:00>
- Postfix context signal: org.joda.time.TestMutableDateTime_Adds::testAddYears_int_dstOverlapWinter_addZero: junit.framework.ComparisonFailure: expected:<...10-30T02:30:00.000+0[1]:00> but was:<...10-30T02:30:00.000+0[2]:00>

### Time-11
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic 'Checking' issue. The code assumes that the ThreadLocal variable will always contain a non-null Boolean value, but this assumption fails in multi-threaded contexts. The fix is to add a guard (null check) to validate the data before proceeding with the operation (autoboxing).
- Postfix reasoning summary: The bug is fundamentally an initialization error. The ThreadLocal was not properly initialized for new threads, leading to a null value where a boolean was expected. The fix corrects the initialization mechanism to ensure a default value is provided for all threads, which is a classic Assignment/Initialization defect.
- Prefix context signal: org.joda.time.tz.TestCompiler::testDateTimeZoneBuilder: junit.framework.AssertionFailedError
- Postfix context signal: org.joda.time.tz.TestCompiler::testDateTimeZoneBuilder: junit.framework.AssertionFailedError

### Time-2
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic 'Checking' error. The code implements a validation check (to prevent duplicates) that is logically flawed because it uses an insufficient condition (checking only the range duration type) to determine equality, leading to a false positive exception. It is not an Algorithm/Method issue because the procedure is correct, just the guard condition is too broad. It is not a Function/Class/Object issue because the capability exists and is correctly designed, just incorrectly guarded.
- Postfix reasoning summary: The bug is caused by incorrect procedural logic in how duration fields are compared and validated within the Partial class. The fix involves rewriting the comparison strategy (in UnsupportedDurationField) and the validation logic (in Partial), which fits the definition of an Algorithm/Method defect. It is not a simple missing check (Checking) because the existing logic was fundamentally flawed in its comparison strategy, nor is it a design-level capability issue (Function/Class/Object).
- Prefix context signal: org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year
- Postfix context signal: org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year

## Type Changed (No Alternative Overlap)

- No qualifying cases found.
## Type Transitions

### Type Changed (Prefix → Postfix)

- Checking -> Assignment/Initialization: 2
  - Bugs: Time-10, Time-11
- Checking -> Algorithm/Method: 2
  - Bugs: Time-12, Time-2
- Algorithm/Method -> Assignment/Initialization: 2
  - Bugs: Time-16, Time-23
- Algorithm/Method -> Checking: 2
  - Bugs: Time-19, Time-3

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 10
  - Bugs: Time-13, Time-14, Time-17, Time-20, Time-22, Time-24, Time-25, Time-26, Time-6, Time-7
- Checking -> Checking: 8
  - Bugs: Time-15, Time-18, Time-1, Time-27, Time-4, Time-5, Time-8, Time-9
