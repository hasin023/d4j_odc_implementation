# Batch Study Analysis

- Created: `2026-07-10T19:50:15+00:00`
- Total pairs: **61**
- Projects covered: **1**
- Type changed: **8** (13.1%)
- Type unchanged: **53** (86.9%)
- No alternative overlap: **0** (0.0%)
- No family match: **0** (0.0%)
- Family match: **61** (100.0%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **61** of 61
- Capability: 43 (70.5%)
- Reliability: 17 (27.9%)
- Serviceability: 1 (1.6%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **58/61** (95.1%)
- Kappa: 0.8898
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 24
- Capability × Checking: 18
- Reliability × Checking: 9
- Reliability × Algorithm/Method: 6
- Reliability × Assignment/Initialization: 2
- Serviceability × Checking: 1
- Capability × Relationship: 1

## Alternative Match Cases (Type Changed)

### Lang-26
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The defect is in the procedural logic of how FastDateFormat initializes its internal Calendar. It fails to apply locale-specific calendar settings (firstDayOfWeek, minimalDaysInFirstWeek), which is a method-level computational strategy error. This fits the Algorithm/Method definition as it involves correcting the procedure for calendar initialization.
- Postfix reasoning summary: The fix involves passing the mLocale field to the GregorianCalendar constructor. This is a classic initialization error where a required state (the locale) was not used to initialize a dependent object (the calendar).
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>

### Lang-29
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The test expects an integer but receives a float, which is a classic case of an incorrect implementation of a conversion method.
- Postfix reasoning summary: The bug is a simple type declaration error. The method was intended to return an integer representation of the Java version but was defined as returning a float. This caused the test to fail when comparing the returned 0.0 to the expected 0. This is an Assignment/Initialization defect because the return value's type (and thus its initialization/representation) was incorrect.
- Prefix context signal: org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>
- Postfix context signal: org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>

### Lang-34
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Post-fix primary 'Checking' found in pre-fix alternative types
- Prefix reasoning summary: The failure to clear the ThreadLocal registry is a procedural defect in the lifecycle management of the object registry. This is an algorithmic/method-level issue because the logic for processing objects in ToStringBuilder/ToStringStyle fails to ensure the registry is cleaned up after the operation, violating the expected state.
- Postfix reasoning summary: The bug report and the failing tests confirm that the registry state is not being correctly managed, leading to leakage. The fix (as seen in the oracle) confirms that the logic for returning the registry was flawed (returning an empty map instead of null), which is a Checking defect.
- Prefix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}
- Postfix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}

### Lang-53
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and test failure confirm that DateUtils.round() is not rounding correctly. Since the issue is in the conditional logic determining whether to round up or down, it falls under the 'Checking' category.
- Postfix reasoning summary: The bug is a procedural error in the `DateUtils.modify` method where the rounding logic is bypassed due to incorrect control flow (the `done` flag). This fits the definition of Algorithm/Method as it involves correcting the procedure itself.
- Prefix context signal: org.apache.commons.lang.time.DateUtilsTest::testRoundLang346: junit.framework.AssertionFailedError: Minute Round Up Failed expected:<Mon Jul 02 08:09:00 PDT 2007> but was:<Mon Jul 02 08:01:00 PDT 2007>
- Postfix context signal: org.apache.commons.lang.time.DateUtilsTest::testRoundLang346: junit.framework.AssertionFailedError: Minute Round Up Failed expected:<Mon Jul 02 08:09:00 PDT 2007> but was:<Mon Jul 02 08:01:00 PDT 2007>

### Lang-21
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a logic error in a conditional check where the wrong field (HOUR vs HOUR_OF_DAY) is used to validate equality of time. This falls squarely under the 'Checking' category of ODC.
- Postfix reasoning summary: The bug is a procedural error in the comparison logic within the DateUtils.isSameLocalTime method. It uses the wrong field (Calendar.HOUR) for comparing time, which is a local algorithmic error. This fits the Algorithm/Method ODC type as it is a local procedural correction.
- Prefix context signal: org.apache.commons.lang3.time.DateUtilsTest::testIsSameLocalTime_Cal: junit.framework.AssertionFailedError: LANG-677
- Postfix context signal: org.apache.commons.lang3.time.DateUtilsTest::testIsSameLocalTime_Cal: junit.framework.AssertionFailedError: LANG-677

### Lang-43
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The code at line 421-422 in ExtendedMessageFormat.java handles an escaped quote but does not update the ParsePosition. Since this is called within a while loop in applyPattern (line 155), the parser gets stuck on the same character, leading to an infinite loop and eventual heap exhaustion.
- Postfix reasoning summary: The code at line 421 checks for an escaped quote but does not increment the ParsePosition. Consequently, the caller (applyPattern) continues to process the same index, resulting in an infinite loop. This is a classic missing check/update of a loop control variable.
- Prefix context signal: org.apache.commons.lang.text.ExtendedMessageFormatTest::testEscapedQuote_LANG_477: java.lang.OutOfMemoryError: Java heap space
- Postfix context signal: org.apache.commons.lang.text.ExtendedMessageFormatTest::testEscapedQuote_LANG_477: java.lang.OutOfMemoryError: Java heap space

### Lang-60
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic boundary check error where the loop condition uses the buffer capacity instead of the current string size. This falls under the 'Checking' category as it involves incorrect validation of the loop boundary.
- Postfix reasoning summary: The defect is a procedural error in the search algorithm (contains/indexOf) where the loop termination condition is incorrectly set to the buffer capacity rather than the current string size. This fits the definition of Algorithm/Method as it is a local procedural logic error.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

### Lang-61
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic algorithmic error in a loop control structure. The search index is not updated correctly after a mutation (deletion) of the underlying data structure, leading to an invalid state and subsequent crash.
- Postfix reasoning summary: The defect is a failure to validate the search range against the current valid size of the StrBuilder. The fix involves changing the loop boundary from the buffer length to the valid string size, which is a classic Checking defect.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testIndexOfLang294: junit.framework.AssertionFailedError: expected:<-1> but was:<6>
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testIndexOfLang294: junit.framework.AssertionFailedError: expected:<-1> but was:<6>

## Type Changed (No Alternative Overlap)

- No qualifying cases found.
## Type Transitions

### Type Changed (Prefix → Postfix)

- Checking -> Algorithm/Method: 3
  - Bugs: Lang-21, Lang-53, Lang-60
- Algorithm/Method -> Checking: 3
  - Bugs: Lang-34, Lang-43, Lang-61
- Algorithm/Method -> Assignment/Initialization: 2
  - Bugs: Lang-26, Lang-29

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 25
  - Bugs: Lang-10, Lang-13, Lang-14, Lang-15, Lang-17, Lang-20, Lang-22, Lang-23, Lang-28, Lang-30, Lang-31, Lang-38, Lang-3, Lang-40, Lang-41, Lang-42, Lang-46, Lang-4, Lang-50, Lang-52, Lang-59, Lang-63, Lang-65, Lang-6, Lang-8
- Checking -> Checking: 25
  - Bugs: Lang-11, Lang-12, Lang-16, Lang-19, Lang-1, Lang-24, Lang-27, Lang-33, Lang-35, Lang-36, Lang-37, Lang-39, Lang-44, Lang-45, Lang-47, Lang-49, Lang-51, Lang-54, Lang-55, Lang-58, Lang-5, Lang-62, Lang-64, Lang-7, Lang-9
- Assignment/Initialization -> Assignment/Initialization: 2
  - Bugs: Lang-32, Lang-57
- Relationship -> Relationship: 1
  - Bugs: Lang-56
