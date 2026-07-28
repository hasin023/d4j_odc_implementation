# Batch Study Analysis

- Created: `2026-07-25T14:34:22+00:00`
- Total pairs: **26**
- Projects covered: **1**
- Type changed: **3** (11.5%)
- Type unchanged: **23** (88.5%)
- No alternative overlap: **0** (0.0%)
- No family match: **1** (3.8%)
- Family match: **25** (96.2%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **26** of 26
- Capability: 24 (92.3%)
- Reliability: 2 (7.7%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **25/26** (96.2%)
- Kappa: 0.7797
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 12
- Capability × Checking: 11
- Reliability × Assignment/Initialization: 1
- Capability × Assignment/Initialization: 1
- Reliability × Checking: 1

## Alternative Match Cases (Type Changed)

### Time-26
- Type shift: Algorithm/Method -> Relationship.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The failure to maintain the correct offset during field modification in DST cutover scenarios points to an algorithmic flaw in how the library handles the conversion between local time and UTC when the offset is ambiguous or changing. This is a procedural error in the calculation logic.
- Postfix reasoning summary: The bug is a classic ODC Relationship defect where the interaction between ZonedChronology and DateTimeZone was insufficient to maintain the required state (the offset) across a transformation. The fix adds the necessary context (the original instant) to the interface between these components.
- Prefix context signal: org.joda.time.TestDateTimeZoneCutover::testWithSecondOfMinuteInDstChange: junit.framework.ComparisonFailure: expected:<...10-31T02:30:00.123+0[2]:00> but was:<...10-31T02:30:00.123+0[1]:00>
- Postfix context signal: org.joda.time.TestDateTimeZoneCutover::testWithSecondOfMinuteInDstChange: junit.framework.ComparisonFailure: expected:<...10-31T02:30:00.123+0[2]:00> but was:<...10-31T02:30:00.123+0[1]:00>

### Time-18
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug is an algorithmic error in the GJChronology class where the validation logic is incorrectly ordered or scoped. It attempts to validate using the Gregorian chronology before determining if the date belongs to the Julian chronology, leading to incorrect rejection of valid Julian leap days.
- Postfix reasoning summary: The bug is a classic case of incorrect validation logic (Checking). The system enforces Gregorian rules on a date that should be evaluated against Julian rules if it falls before the cutover. The fix adds a conditional check (a try-catch block) to allow the date to be processed as a Julian date if the Gregorian validation fails for a leap day.
- Prefix context signal: org.joda.time.chrono.TestGJChronology::testLeapYearRulesConstruction: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- Postfix context signal: org.joda.time.chrono.TestGJChronology::testLeapYearRulesConstruction: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]

### Time-23
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The test failure is a classic case of relying on an unstable external dependency (JDK's TimeZone ID resolution) for a stable requirement (legacy ID mapping). The fix is to implement a local, hardcoded mapping table within the method or class to override the JDK's behavior, which is an algorithmic/method-level correction.
- Postfix reasoning summary: The bug is caused by incorrect values in a static map used for time zone ID resolution. This is a clear case of incorrect initialization of a data structure, fitting the Assignment/Initialization category.
- Prefix context signal: org.joda.time.TestDateTimeZone::testForID_String_old: junit.framework.ComparisonFailure: expected:<[WET]> but was:<[Europe/London]>
- Postfix context signal: org.joda.time.TestDateTimeZone::testForID_String_old: junit.framework.ComparisonFailure: expected:<[WET]> but was:<[Europe/London]>

## Type Changed (No Alternative Overlap)

- No qualifying cases found.
## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Checking: 1
  - Bugs: Time-18
- Algorithm/Method -> Assignment/Initialization: 1
  - Bugs: Time-23
- Algorithm/Method -> Relationship: 1
  - Bugs: Time-26 (no family match)

### Type Unchanged

- Checking -> Checking: 12
  - Bugs: Time-12, Time-13, Time-15, Time-19, Time-1, Time-2, Time-3, Time-4, Time-5, Time-6, Time-8, Time-9
- Algorithm/Method -> Algorithm/Method: 9
  - Bugs: Time-10, Time-14, Time-17, Time-20, Time-22, Time-24, Time-25, Time-27, Time-7
- Assignment/Initialization -> Assignment/Initialization: 2
  - Bugs: Time-11, Time-16
