# Batch Study Analysis

- Created: `2026-07-10T19:57:08+00:00`
- Total pairs: **61**
- Projects covered: **1**
- Type changed: **11** (18.0%)
- Type unchanged: **50** (82.0%)
- No alternative overlap: **0** (0.0%)
- No family match: **2** (3.3%)
- Family match: **59** (96.7%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **61** of 61
- Capability: 43 (70.5%)
- Reliability: 17 (27.9%)
- Serviceability: 1 (1.6%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **58/61** (95.1%)
- Kappa: 0.8862
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 21
- Capability × Checking: 19
- Reliability × Checking: 12
- Reliability × Algorithm/Method: 3
- Reliability × Assignment/Initialization: 2
- Serviceability × Checking: 1
- Capability × Assignment/Initialization: 1
- Capability × Function/Class/Object: 1
- Capability × Relationship: 1

## Alternative Match Cases (Type Changed)

### Lang-4
- Type shift: Function/Class/Object -> Algorithm/Method.
- Comparison detail: Post-fix primary 'Algorithm/Method' found in pre-fix alternative types
- Prefix reasoning summary: The issue is not a simple algorithmic error or a missing check, but a fundamental misuse of the CharSequence interface as a key in a Map, which violates the interface's contract and leads to incorrect behavior for non-String implementations. This requires a design-level change to how keys are stored or compared.
- Postfix reasoning summary: The bug is an algorithmic flaw in how the lookup map is keyed. By using the interface CharSequence as a key in a HashMap, the implementation relies on the equals/hashCode contracts of arbitrary implementations, which are not guaranteed. Converting to String is a procedural fix to ensure the lookup algorithm functions correctly regardless of the input CharSequence implementation.
- Prefix context signal: org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>
- Postfix context signal: org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>

### Lang-20
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report explicitly states that the issue is caused by an object's toString() returning null. The code at line 3298 and 3383 performs `array[startIndex].toString().length()`. If `array[startIndex]` is not null but its `toString()` returns null, this will throw an NPE. This is a failure to check the validity of the data returned by an external method.
- Postfix reasoning summary: The defect is an incorrect algorithmic approach to estimating the initial capacity of a StringBuilder. Instead of relying on the actual content of the objects (which might return null from toString()), the implementation should use a safe default capacity or a different estimation strategy. This is a procedural/algorithmic error in how the buffer is initialized.
- Prefix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException

### Lang-26
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The failure is a direct result of the class failing to use the provided locale to configure the Calendar instance, which is a procedural logic error in the initialization phase of the formatting process.
- Postfix reasoning summary: The defect is an initialization error where the object state (the locale) is not correctly applied to the internal calendar used for formatting. This falls under Assignment/Initialization as it involves setting the correct state for the calendar object.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>

### Lang-50
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and test failure confirm that FastDateFormat caches instances based on the default locale, but fails to update or invalidate these instances when the default locale changes. This is a classic caching defect where the key is insufficient or the cache is not properly managed.
- Postfix reasoning summary: The bug report and test failure confirm that FastDateFormat caches instances based on a key that does not include the default locale when the locale parameter is null. When the default locale changes, the cache returns the old instance, violating the expected behavior. This is a validation/checking error in the cache key generation logic.
- Prefix context signal: org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateInstance: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>
- Postfix context signal: org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateInstance: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>

### Lang-53
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic rounding error where the logic fails to correctly increment the target field. This is a procedural/algorithmic issue within the DateUtils class, specifically in the method responsible for modifying the calendar state during rounding.
- Postfix reasoning summary: The bug is a classic control-flow error where the 'done' flag, which controls whether further rounding steps are performed, is set regardless of whether the rounding condition was actually met. This is a 'Checking' type defect because the logic governing the execution path (the conditional check) is flawed.
- Prefix context signal: org.apache.commons.lang.time.DateUtilsTest::testRoundLang346: junit.framework.AssertionFailedError: Minute Round Up Failed expected:<Mon Jul 02 08:09:00 PDT 2007> but was:<Mon Jul 02 08:01:00 PDT 2007>
- Postfix context signal: org.apache.commons.lang.time.DateUtilsTest::testRoundLang346: junit.framework.AssertionFailedError: Minute Round Up Failed expected:<Mon Jul 02 08:09:00 PDT 2007> but was:<Mon Jul 02 08:01:00 PDT 2007>

### Lang-65
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic issue with Java's Calendar API where modifying fields can trigger unexpected time shifts due to DST rules. The implementation of DateUtils.truncate uses a procedural approach (setting fields) that is inherently flawed for this specific edge case. This is an algorithmic/methodological error in how the truncation is performed.
- Postfix reasoning summary: The defect is a failure to validate whether a state change (setting a Calendar field) is actually necessary before performing it. Because the `Calendar` API has side effects (recalculating DST offsets) when `set()` is called, the lack of a guard condition (checking if the value is already correct) leads to incorrect behavior during DST transitions. This is a classic 'Checking' defect where a missing guard condition causes incorrect state transitions.
- Prefix context signal: org.apache.commons.lang.time.DateUtilsTest::testTruncateLang59: junit.framework.AssertionFailedError: Truncate Calendar.SECOND expected:<Sun Oct 31 01:02:03 MDT 2004> but was:<Sun Oct 31 01:02:03 MST 2004>
- Postfix context signal: org.apache.commons.lang.time.DateUtilsTest::testTruncateLang59: junit.framework.AssertionFailedError: Truncate Calendar.SECOND expected:<Sun Oct 31 01:02:03 MDT 2004> but was:<Sun Oct 31 01:02:03 MST 2004>

### Lang-23
- Type shift: Algorithm/Method -> Function/Class/Object.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Function/Class/Object' is in pre-fix alternatives
- Prefix reasoning summary: The failure is caused by the lack of proper equals/hashCode implementation in the subclass, which is a procedural/algorithmic oversight in defining object identity. This fits the Algorithm/Method ODC type as it requires implementing the correct logic for these methods.
- Postfix reasoning summary: The class ExtendedMessageFormat extends MessageFormat but fails to override equals and hashCode. This is a classic structural defect where the class fails to maintain its own identity contract when extended with new fields. The fix requires implementing these methods to include the new fields, which is a structural correction.
- Prefix context signal: org.apache.commons.lang3.text.ExtendedMessageFormatTest::testEqualsHashcode: junit.framework.AssertionFailedError: registry, hashcode()
- Postfix context signal: org.apache.commons.lang3.text.ExtendedMessageFormatTest::testEqualsHashcode: junit.framework.AssertionFailedError: registry, hashcode()

### Lang-34
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Post-fix primary 'Assignment/Initialization' found in pre-fix alternative types
- Prefix reasoning summary: The failure is a direct consequence of the algorithm not cleaning up its state (the ThreadLocal registry) after completion. This is a procedural error in the method's execution flow, fitting the Algorithm/Method ODC type.
- Postfix reasoning summary: The bug report and the fix diff clearly show that `getRegistry` was returning `Collections.emptyMap()` instead of `null`. The tests were asserting that the registry should be `null` after completion. This is an initialization/assignment issue where the default value returned by the method was changed, leading to incorrect state representation.
- Prefix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}
- Postfix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}

### Lang-38
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The failure is caused by the library's failure to ensure the input Calendar object is in a consistent state before reading its fields. This is a validation/checking issue where the library assumes the input is already synchronized.
- Postfix reasoning summary: The defect is a procedural error where the code assumes the Calendar object is ready for formatting after setTimeZone, but the JDK Calendar implementation requires a call to getTime() to synchronize its internal fields. This is a local procedural fix within the FastDateFormat class.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang538: junit.framework.ComparisonFailure: dateTime expected:<2009-10-16T[16]:42:16.000Z> but was:<2009-10-16T[08]:42:16.000Z>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang538: junit.framework.ComparisonFailure: dateTime expected:<2009-10-16T[16]:42:16.000Z> but was:<2009-10-16T[08]:42:16.000Z>

### Lang-46
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a clear case of an incorrect algorithmic step where a character ('/') is being processed as an escapable character when it should not be. This does not involve missing guards (Checking) or incorrect initialization (Assignment/Initialization), but rather an incorrect implementation of the escaping procedure itself.
- Postfix reasoning summary: The defect is a missing conditional check (a guard) that determines whether to perform an escape operation on a specific character ('/'). This falls under the 'Checking' category as it involves validating the necessity of an action based on a condition.
- Prefix context signal: org.apache.commons.lang.StringEscapeUtilsTest::testEscapeJavaWithSlash: junit.framework.ComparisonFailure: expected:<...tring with a slash ([]/) in it> but was:<...tring with a slash ([\]/) in it>
- Postfix context signal: org.apache.commons.lang.StringEscapeUtilsTest::testEscapeJavaWithSlash: junit.framework.ComparisonFailure: expected:<...tring with a slash ([]/) in it> but was:<...tring with a slash ([\]/) in it>

### Lang-60
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and the failing test case provide sufficient evidence that the methods are failing to respect the logical boundary of the string builder, instead iterating over the entire physical buffer. This is a 'Checking' defect as it involves an incorrect loop termination condition.
- Postfix reasoning summary: The defect is a classic off-by-one/boundary error where the loop condition uses the buffer capacity rather than the current size of the data, which is a procedural logic error in the implementation of the search methods.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

## Type Changed (No Alternative Overlap)

- No qualifying cases found.
## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Checking: 4
  - Bugs: Lang-46, Lang-50, Lang-53, Lang-65
- Checking -> Algorithm/Method: 3
  - Bugs: Lang-20, Lang-38, Lang-60
- Algorithm/Method -> Assignment/Initialization: 2
  - Bugs: Lang-26, Lang-34
- Algorithm/Method -> Function/Class/Object: 1
  - Bugs: Lang-23 (no family match)
- Function/Class/Object -> Algorithm/Method: 1
  - Bugs: Lang-4 (no family match)

### Type Unchanged

- Checking -> Checking: 29
  - Bugs: Lang-11, Lang-12, Lang-13, Lang-16, Lang-19, Lang-1, Lang-21, Lang-24, Lang-27, Lang-33, Lang-35, Lang-36, Lang-37, Lang-39, Lang-43, Lang-44, Lang-45, Lang-47, Lang-49, Lang-51, Lang-54, Lang-55, Lang-58, Lang-5, Lang-61, Lang-62, Lang-64, Lang-7, Lang-9
- Algorithm/Method -> Algorithm/Method: 17
  - Bugs: Lang-10, Lang-14, Lang-15, Lang-17, Lang-22, Lang-28, Lang-30, Lang-31, Lang-3, Lang-40, Lang-41, Lang-42, Lang-52, Lang-59, Lang-63, Lang-6, Lang-8
- Assignment/Initialization -> Assignment/Initialization: 3
  - Bugs: Lang-29, Lang-32, Lang-57
- Relationship -> Relationship: 1
  - Bugs: Lang-56
