# Batch Study Analysis

- Created: `2026-08-04T17:45:42+00:00`
- Total pairs: **61**
- Projects covered: **1**
- Type changed: **15** (24.6%)
- Type unchanged: **46** (75.4%)
- No alternative overlap: **0** (0.0%)
- No family match: **1** (1.6%)
- Family match: **60** (98.4%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **61** of 61
- Capability: 35 (57.4%)
- Reliability: 26 (42.6%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **54/61** (88.5%)
- Kappa: 0.7665
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 26
- Reliability × Checking: 12
- Reliability × Algorithm/Method: 10
- Capability × Checking: 9
- Reliability × Assignment/Initialization: 3
- Reliability × Function/Class/Object: 1

## Alternative Match Cases (Type Changed)

### Lang-12
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The root cause is an incorrect index calculation in the character selection logic (line 248). The code uses 'random.nextInt(gap) + start' as an index into the 'chars' array without validating that this index is within the array's bounds. This is a procedural error in the algorithm used to select a random character, rather than a missing guard (though a guard might prevent the crash, the underlying logic for index selection is fundamentally flawed).
- Postfix reasoning summary: The fix involves adding explicit validation checks (e.g., checking if the 'chars' array is empty) and correcting the initialization logic for 'start' and 'end' parameters when they are zero. These are classic guard/validation issues that prevent invalid state from reaching the core computation, fitting the 'Checking' ODC type.
- Prefix context signal: org.apache.commons.lang3.RandomStringUtilsTest::testExceptions: java.lang.ArrayIndexOutOfBoundsException: Index 304389849 out of bounds for length 0
- Postfix context signal: org.apache.commons.lang3.RandomStringUtilsTest::testExceptions: java.lang.ArrayIndexOutOfBoundsException: Index 1490277398 out of bounds for length 0

### Lang-16
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is in the procedural logic of the number parsing algorithm. The method is designed to handle various numeric formats, but the current implementation lacks the logic to recognize the '0X' prefix as a valid hexadecimal indicator, causing it to fall through to an error-throwing default case. This is a procedural oversight in the parsing algorithm rather than a missing guard or a simple value assignment error.
- Postfix reasoning summary: The bug is caused by a missing condition in the validation logic that identifies hexadecimal strings. The fix adds the missing '0X' and '-0X' prefixes to the existing 'if' condition, ensuring these valid hexadecimal formats are correctly recognized and processed. This is a classic case of a missing guard/validation check.
- Prefix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: java.lang.NumberFormatException: 0Xfade is not a valid number.
- Postfix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: java.lang.NumberFormatException: 0Xfade is not a valid number.

### Lang-20
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The root cause is a missing validation check. The code at line 3298 and 3383 attempts to calculate the initial capacity of a StringBuilder by calling toString() on an array element without verifying if the result of that toString() call is null. While the code checks if the array element itself is null, it fails to handle the case where the element exists but its string representation is null. This is a classic missing guard/validation issue.
- Postfix reasoning summary: The fix replaces a complex, error-prone calculation (which attempted to estimate the initial capacity of a StringBuilder by calling toString().length() on the first element) with a simpler, more robust algorithmic approach (using a fixed multiplier of 16). This is a correction of the procedural logic used to initialize the buffer, fitting the Algorithm/Method category as it re-implements the capacity estimation strategy.
- Prefix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException

### Lang-26
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The bug is caused by the implementation of the date formatting logic failing to correctly account for locale-specific calendar settings (first day of week, minimal days in first week). This is a procedural error in how the date is processed into a week number, rather than a missing guard (Checking), a wrong constant (Assignment), or a design-level capability omission (Function/Class/Object). The logic for calculating the week number needs to be corrected to properly utilize the provided locale's calendar rules.
- Postfix reasoning summary: The bug is caused by an incorrect initialization of the GregorianCalendar object. The code was initializing the calendar using only the time zone, ignoring the locale. The fix involves passing the locale to the GregorianCalendar constructor, ensuring that locale-specific settings like firstDayOfWeek and minimalDaysInFirstWeek are correctly applied. This is a classic initialization error.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>

### Lang-34
- Type shift: Assignment/Initialization -> Checking.
- Comparison detail: Pre-fix primary 'Assignment/Initialization' found in post-fix alternative types
- Prefix reasoning summary: The root cause is the failure to properly manage the lifecycle of a ThreadLocal variable. The registry is initialized but never cleaned up (reset to null or removed), which is a classic state management/initialization error. It is not an algorithmic error (the logic works, but the state persists incorrectly), nor a missing guard (the check is present, but the state is wrong).
- Postfix reasoning summary: The bug is caused by the lack of proper null-checking for the ThreadLocal registry. The fix adds a null check in `isRegistered` to prevent NullPointerExceptions and modifies `getRegistry` to return the actual value (null) instead of an empty map, which was causing the registry to appear non-empty and breaking cycle detection logic.
- Prefix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}
- Postfix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}

### Lang-46
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The issue is that the escapeJava method includes logic that treats '/' as a character requiring an escape sequence. This is a procedural error in the implementation of the escaping algorithm, as it performs an unnecessary and incorrect transformation on the input string. It is not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object), but rather an incorrect implementation of the string processing logic.
- Postfix reasoning summary: The fix involves adding a conditional check ('if (escapeForwardSlash)') around the logic that writes the escape character ('\') before a forward slash. This is a classic 'Checking' defect where a validation guard was missing, causing the code to perform an unnecessary and incorrect operation (escaping a character that shouldn't be escaped) in certain contexts.
- Prefix context signal: org.apache.commons.lang.StringEscapeUtilsTest::testEscapeJavaWithSlash: junit.framework.ComparisonFailure: expected:<...tring with a slash ([]/) in it> but was:<...tring with a slash ([\]/) in it>
- Postfix context signal: org.apache.commons.lang.StringEscapeUtilsTest::testEscapeJavaWithSlash: junit.framework.ComparisonFailure: expected:<...tring with a slash ([]/) in it> but was:<...tring with a slash ([\]/) in it>

### Lang-49
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug report indicates an infinite loop in the reduction logic when the numerator is 0. The test failure shows that the denominator is not being reduced to 1 when the numerator is 0. This is a procedural error in the reduction algorithm, which should handle the zero-numerator case as a special condition or ensure the reduction logic correctly simplifies 0/n to 0/1. This is a classic algorithmic flaw in the implementation of the reduction method.
- Postfix reasoning summary: The fix introduces a guard clause at the beginning of the reduce() method to explicitly handle the case where the numerator is 0. This is a classic validation/guard check issue where the method lacked the necessary logic to handle a specific edge case in the input data, making 'Checking' the correct ODC classification.
- Prefix context signal: org.apache.commons.lang.math.FractionTest::testReduce: junit.framework.AssertionFailedError: expected:<1> but was:<100>
- Postfix context signal: org.apache.commons.lang.math.FractionTest::testReduce: junit.framework.AssertionFailedError: expected:<1> but was:<100>

### Lang-55
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The issue is a procedural error in how the StopWatch calculates time when transitioning between states (suspend to stop). The internal logic for calculating the elapsed time is flawed because it fails to correctly account for the suspended state, leading to an incorrect final time value. This is a classic algorithmic error in state management rather than a missing guard (Checking) or a simple variable initialization error.
- Postfix reasoning summary: The fix involves adding a conditional check (if(this.runningState == STATE_RUNNING)) before updating the stopTime variable. This ensures that the stopTime is only captured if the watch is currently running, preventing the incorrect update when the watch is already in a suspended state. This is a classic missing guard/validation check.
- Prefix context signal: org.apache.commons.lang.time.StopWatchTest::testLang315: junit.framework.AssertionFailedError
- Postfix context signal: org.apache.commons.lang.time.StopWatchTest::testLang315: junit.framework.AssertionFailedError

### Lang-60
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report explicitly states that the methods are using the wrong boundary (buffer length instead of size). This is a classic boundary check error where the loop or search condition is incorrectly bounded, which falls under the 'Checking' category in ODC.
- Postfix reasoning summary: The defect is an algorithmic error in the loop termination condition. The methods were using the buffer's capacity (thisBuf.length) as the loop bound instead of the current string size (this.size). This is a procedural logic error in how the search algorithm traverses the data structure, which is corrected by updating the loop condition.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

### Lang-29
- Type shift: Algorithm/Method -> Interface/O-O Messages.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The failure indicates that the internal logic of 'toJavaVersionInt' is likely performing an incorrect conversion or using an incorrect data type during its calculation process, leading to a floating-point result where an integer is expected. This is a procedural error in the implementation of the conversion algorithm, not a missing guard or a simple initialization error.
- Postfix reasoning summary: The fix involved changing the return type of the method 'toJavaVersionInt' from 'float' to 'int'. This is a signature mismatch (contract violation) between what the method was intended to return (an integer representation of a version) and what it actually returned. While the underlying logic might have been updated as well, the primary issue identified by the failing test (expected 0 but was 0.0) and the fix diff is the incorrect method signature.
- Prefix context signal: org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>
- Postfix context signal: org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>

### Lang-32
- Type shift: Assignment/Initialization -> Algorithm/Method.
- Comparison detail: Post-fix primary 'Algorithm/Method' found in pre-fix alternative types
- Prefix reasoning summary: The root cause is the failure to properly manage the lifecycle of a ThreadLocal variable. Specifically, the registry used to track object cycles is not cleaned up (initialized/reset to null or cleared) after the reflection operation finishes. This is an initialization/state management issue where the state is not correctly reset to its expected null or empty state after use, causing subsequent assertions to fail and creating memory leaks.
- Postfix reasoning summary: The fix involves changing the lifecycle management of the ThreadLocal registry. Specifically, it changes how the registry is initialized (lazy initialization instead of eager), how it is checked for existence (null checks), and crucially, it adds logic to remove the ThreadLocal entry when the registry becomes empty. This is a procedural change to the algorithm managing the registry's lifecycle, ensuring it is cleaned up properly to prevent memory leaks. It is not a simple missing guard (Checking) because it involves a fundamental change to the lifecycle management strategy of the shared resource.
- Prefix context signal: org.apache.commons.lang3.builder.HashCodeBuilderTest::testReflectionObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: []
- Postfix context signal: org.apache.commons.lang3.builder.HashCodeBuilderTest::testReflectionObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: []

### Lang-3
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect lies in the procedural logic of the createNumber method, which uses an incorrect strategy for determining the numeric type of a string. It forces a Float parsing attempt before considering Double or BigDecimal, which is a flaw in the computational strategy of the method. This is an algorithmic error in how the input string is processed and converted, not a missing guard (Checking) or a simple wrong constant (Assignment/Initialization).
- Postfix reasoning summary: The fix introduces conditional checks (if(numDecimals <= 7) and if(numDecimals <= 16)) to validate whether a string can be safely represented as a Float or Double before attempting the conversion. This is a classic case of missing validation logic (a guard) that determines which path the algorithm should take to ensure data integrity. It is not an algorithmic rewrite of the conversion itself, but rather a missing check on the input data's characteristics to decide the appropriate target type.
- Prefix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testStringCreateNumberEnsureNoPrecisionLoss: junit.framework.AssertionFailedError
- Postfix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testStringCreateNumberEnsureNoPrecisionLoss: junit.framework.AssertionFailedError

### Lang-51
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a control flow error where a case block lacks a termination (return or break), causing it to incorrectly enter the logic for a different case (case 4). This is a procedural logic error in the implementation of the string parsing algorithm. It is not a missing guard (Checking) because the logic itself is fundamentally flawed in its flow, nor is it an assignment error.
- Postfix reasoning summary: The bug is caused by a missing return statement at the end of a case block, which allows execution to fall through into a subsequent case block that performs string indexing operations on a string that is too short. Adding the missing return statement prevents this invalid execution path, which is a classic example of a missing guard/validation logic error.
- Prefix context signal: org.apache.commons.lang.BooleanUtilsTest::test_toBoolean_String: java.lang.StringIndexOutOfBoundsException: String index out of range: 3
- Postfix context signal: org.apache.commons.lang.BooleanUtilsTest::test_toBoolean_String: java.lang.StringIndexOutOfBoundsException: String index out of range: 3

### Lang-56
- Type shift: Function/Class/Object -> Relationship.
- Comparison detail: Cross-alternative match: pre-fix 'Function/Class/Object' is in post-fix alternatives, and post-fix 'Relationship' is in pre-fix alternatives
- Prefix reasoning summary: The bug report explicitly states that the 'mRules' field is not serializable and suggests either making the Rule interface serializable or marking the field transient and adding custom deserialization logic. This is a design-level capability issue regarding the object's serialization contract, rather than a local algorithmic or assignment error. The fix requires structural changes to the class definition and its lifecycle management (deserialization).
- Postfix reasoning summary: The defect is a structural inconsistency between the object's state and its serialization contract. The fields mRules and mMaxLengthEstimate were not serializable, but the class itself was intended to be. The fix involved marking these fields as 'transient' (to exclude them from default serialization) and implementing a 'readObject' method to re-initialize them upon deserialization. This is a classic relationship/consistency issue between the object's internal state and the serialization mechanism, requiring a structural adjustment to how the object is persisted.
- Prefix context signal: org.apache.commons.lang.time.FastDateFormatTest::testLang303: org.apache.commons.lang.SerializationException: java.io.NotSerializableException: org.apache.commons.lang.time.FastDateFormat$PaddedNumberField
- Postfix context signal: org.apache.commons.lang.time.FastDateFormatTest::testLang303: org.apache.commons.lang.SerializationException: java.io.NotSerializableException: org.apache.commons.lang.time.FastDateFormat$PaddedNumberField

### Lang-57
- Type shift: Assignment/Initialization -> Algorithm/Method.
- Comparison detail: Pre-fix primary 'Assignment/Initialization' found in post-fix alternative types
- Prefix reasoning summary: The bug is caused by a failure to initialize a static field (cAvailableLocaleSet) before its first use. The method isAvailableLocale directly accesses this field, which remains null if the lazy-initialization method availableLocaleSet() has not been called previously. This is a classic initialization defect.
- Postfix reasoning summary: The fix replaces the direct access to an uninitialized static field with a call to a method (availableLocaleList()) that ensures the collection is initialized before use. This is a correction of the procedural logic used to access the data, making it an Algorithm/Method fix rather than a simple initialization fix (which would have involved initializing the field in a constructor or static block) or a checking fix (which would have involved adding a null check).
- Prefix context signal: org.apache.commons.lang.LocaleUtilsTest::testAvailableLocaleSet: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang.LocaleUtilsTest::testAvailableLocaleSet: java.lang.NullPointerException

## Type Changed (No Alternative Overlap)

- No qualifying cases found.
## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Checking: 7
  - Bugs: Lang-12, Lang-16, Lang-3, Lang-46, Lang-49, Lang-51, Lang-55
- Checking -> Algorithm/Method: 2
  - Bugs: Lang-20, Lang-60
- Assignment/Initialization -> Algorithm/Method: 2
  - Bugs: Lang-32, Lang-57
- Algorithm/Method -> Assignment/Initialization: 1
  - Bugs: Lang-26
- Algorithm/Method -> Interface/O-O Messages: 1
  - Bugs: Lang-29 (no family match)
- Assignment/Initialization -> Checking: 1
  - Bugs: Lang-34
- Function/Class/Object -> Relationship: 1
  - Bugs: Lang-56

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 27
  - Bugs: Lang-10, Lang-13, Lang-14, Lang-15, Lang-17, Lang-1, Lang-21, Lang-22, Lang-23, Lang-28, Lang-30, Lang-31, Lang-38, Lang-40, Lang-41, Lang-42, Lang-43, Lang-4, Lang-50, Lang-52, Lang-53, Lang-59, Lang-61, Lang-63, Lang-65, Lang-6, Lang-8
- Checking -> Checking: 19
  - Bugs: Lang-11, Lang-19, Lang-24, Lang-27, Lang-33, Lang-35, Lang-36, Lang-37, Lang-39, Lang-44, Lang-45, Lang-47, Lang-54, Lang-58, Lang-5, Lang-62, Lang-64, Lang-7, Lang-9
