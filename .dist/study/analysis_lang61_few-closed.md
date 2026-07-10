# Batch Study Analysis

- Created: `2026-07-10T19:57:08+00:00`
- Total pairs: **61**
- Projects covered: **1**
- Type changed: **15** (24.6%)
- Type unchanged: **46** (75.4%)
- No alternative overlap: **0** (0.0%)
- No family match: **1** (1.6%)
- Family match: **60** (98.4%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **61** of 61
- Capability: 38 (62.3%)
- Reliability: 23 (37.7%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **54/61** (88.5%)
- Kappa: 0.7619
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 29
- Reliability × Checking: 12
- Capability × Checking: 9
- Reliability × Algorithm/Method: 7
- Reliability × Assignment/Initialization: 3
- Reliability × Relationship: 1

## Alternative Match Cases (Type Changed)

### Lang-16
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is an algorithmic oversight in the input parsing logic. The method is designed to handle various number formats, but the procedure for identifying hexadecimal numbers is incomplete because it does not account for the case-insensitive nature of the '0x' prefix. This is a procedural logic error rather than a missing guard (Checking) or a simple value assignment error.
- Postfix reasoning summary: The bug is a classic 'Checking' defect. The logic for identifying hexadecimal numbers was present but incomplete, failing to account for valid upper-case prefixes. The fix simply adds these missing cases to the existing conditional guard, which is the definition of a Checking defect.
- Prefix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: java.lang.NumberFormatException: 0Xfade is not a valid number.
- Postfix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: java.lang.NumberFormatException: 0Xfade is not a valid number.

### Lang-26
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The issue is a procedural error in how the calendar is configured for formatting. It is not a missing check (Checking), nor a simple wrong value (Assignment/Initialization), but a flaw in the logic that determines how the date is processed based on the locale. This falls under Algorithm/Method as it involves the computational strategy for date formatting.
- Postfix reasoning summary: The defect is an incorrect initialization of a helper object (GregorianCalendar). The logic for formatting is correct, but the state of the calendar object used for the calculation is wrong because it was initialized with the wrong constructor parameters. This fits the definition of Assignment/Initialization.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>

### Lang-49
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The issue is a procedural error in the reduction algorithm. It is not a missing guard (Checking) because the logic for reducing fractions is present but flawed for the specific case of zero. It is not an Assignment/Initialization issue because the problem is in the logic of the reduction process itself, not just a wrong initial value.
- Postfix reasoning summary: The bug is caused by a missing guard condition for a specific input state (numerator == 0). Adding this check prevents the method from performing unnecessary or incorrect calculations, which is the definition of a Checking defect.
- Prefix context signal: org.apache.commons.lang.math.FractionTest::testReduce: junit.framework.AssertionFailedError: expected:<1> but was:<100>
- Postfix context signal: org.apache.commons.lang.math.FractionTest::testReduce: junit.framework.AssertionFailedError: expected:<1> but was:<100>

### Lang-54
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is an algorithmic error in the parsing logic of the toLocale() method. It incorrectly assumes that if a string is longer than 2 characters, it must contain a country code at positions 3 and 4. This is a procedural logic issue rather than a missing guard (Checking) or a simple value assignment error, as it requires a change in how the string is decomposed and validated.
- Postfix reasoning summary: The bug is caused by a missing conditional check for a valid but non-standard locale format. The fix introduces a new branch to handle this specific case, which is a classic 'Checking' defect where the input validation logic was incomplete.
- Prefix context signal: org.apache.commons.lang.LocaleUtilsTest::testLang328: java.lang.IllegalArgumentException: Invalid locale format: fr__POSIX
- Postfix context signal: org.apache.commons.lang.LocaleUtilsTest::testLang328: java.lang.IllegalArgumentException: Invalid locale format: fr__POSIX

### Lang-55
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The issue is a procedural error in how the StopWatch calculates its final time when stopped. It is not a missing guard (Checking) or a simple initialization error (Assignment/Initialization), but a flaw in the logic of the stop() method's state transition and time calculation, which is best classified as an Algorithm/Method defect.
- Postfix reasoning summary: The bug is caused by a missing validation check (a guard) in the stop() method. The method was unconditionally updating the stopTime, which is incorrect when the watch is already suspended. Adding the missing state check correctly prevents the time from being updated when it shouldn't be. This fits the definition of a 'Checking' defect.
- Prefix context signal: org.apache.commons.lang.time.StopWatchTest::testLang315: junit.framework.AssertionFailedError
- Postfix context signal: org.apache.commons.lang.time.StopWatchTest::testLang315: junit.framework.AssertionFailedError

### Lang-60
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic boundary condition error where the loop termination logic is incorrect. It is not an algorithmic flaw in the search logic itself, but rather an incorrect validation of the search range (the boundary of the valid data).
- Postfix reasoning summary: The defect is a classic algorithmic error where the loop termination condition was incorrectly defined. It is not a missing check (Checking) because the logic was present but used the wrong boundary variable. It is not an assignment error because the logic of the loop itself was flawed. It is an Algorithm/Method defect because the procedure for searching the string was implemented with an incorrect iteration strategy.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

### Lang-12
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is an incorrect computational strategy for indexing an array. While it involves an array, the root cause is the logic used to calculate the index, which is a procedural/algorithmic error rather than a missing guard (Checking) or a simple initialization error (Assignment/Initialization).
- Postfix reasoning summary: The defect is a classic missing validation check. The code fails to verify the state of the input (the character array and the range parameters) before using them in an array access operation. Adding these checks prevents the ArrayIndexOutOfBoundsException, which is the hallmark of a 'Checking' ODC type.
- Prefix context signal: org.apache.commons.lang3.RandomStringUtilsTest::testExceptions: java.lang.ArrayIndexOutOfBoundsException: Index 304389849 out of bounds for length 0
- Postfix context signal: org.apache.commons.lang3.RandomStringUtilsTest::testExceptions: java.lang.ArrayIndexOutOfBoundsException: Index 1490277398 out of bounds for length 0

### Lang-20
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic missing validation/guard. The code performs operations (toString().length()) on objects without verifying if the object or the result of its toString() method is null. This is a failure to validate input data before processing, which falls squarely under the 'Checking' category.
- Postfix reasoning summary: The defect is an algorithmic flaw in how the initial capacity of the StringBuilder is calculated. It is not a missing check (the code was checking for null, but the logic inside the ternary operator was still calling a method on the result of a potential null return) nor a simple assignment error. It is a procedural strategy for capacity estimation that was fundamentally flawed for the given input domain. Therefore, it is classified as Algorithm/Method.
- Prefix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException

### Lang-5
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a failure to validate a specific, valid input format (strings starting with an underscore). The fix involves adding a conditional check to handle this case, which is a classic 'Checking' defect type.
- Postfix reasoning summary: The fix adds a new procedural branch to handle a specific input format that was previously unhandled. This is an algorithmic correction to the parsing method, not a simple guard or initialization change, as it requires implementing a new parsing path for the locale components.
- Prefix context signal: org.apache.commons.lang3.LocaleUtilsTest::testLang865: java.lang.IllegalArgumentException: Invalid locale format: _GB
- Postfix context signal: org.apache.commons.lang3.LocaleUtilsTest::testLang865: java.lang.IllegalArgumentException: Invalid locale format: _GB

### Lang-4
- Type shift: Algorithm/Method -> Relationship.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The issue is an algorithmic flaw in how the translator performs lookups. It relies on the Map interface's default behavior, which is inappropriate for the CharSequence interface. This is a procedural/algorithmic error in the translation logic rather than a missing guard (Checking), a wrong value (Assignment), or a design-level capability gap (Function/Class/Object).
- Postfix reasoning summary: This is a Relationship defect because the failure arises from a broken association between the lookup map's key structure and the input data's equality contract. The fix corrects this by enforcing a consistent String-based relationship for all keys, ensuring that lookups succeed regardless of the specific CharSequence implementation provided.
- Prefix context signal: org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>
- Postfix context signal: org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>

### Lang-32
- Type shift: Assignment/Initialization -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Assignment/Initialization' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is an initialization/state management issue where a resource (the registry) is not properly reset or cleared after use. This is not an algorithmic error (the logic works) nor a missing guard (the check is present, but the state is wrong). It is a failure to manage the lifecycle of a persistent state variable.
- Postfix reasoning summary: The defect is an algorithmic/procedural issue regarding the lifecycle management of a shared resource (the ThreadLocal registry). The fix involves changing the initialization strategy (lazy vs eager) and adding logic to clean up the resource when no longer needed. This is a procedural correction to how the registry is maintained, fitting the Algorithm/Method category.
- Prefix context signal: org.apache.commons.lang3.builder.HashCodeBuilderTest::testReflectionObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: []
- Postfix context signal: org.apache.commons.lang3.builder.HashCodeBuilderTest::testReflectionObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: []

### Lang-34
- Type shift: Assignment/Initialization -> Checking.
- Comparison detail: Pre-fix primary 'Assignment/Initialization' found in post-fix alternative types
- Prefix reasoning summary: The defect is fundamentally about the lifecycle management of a stateful object (the ThreadLocal registry). It is not an algorithmic error, nor a missing guard, but a failure to properly initialize/reset the state of a variable (the ThreadLocal) after its intended use, which is a classic Assignment/Initialization defect.
- Postfix reasoning summary: The bug is fundamentally a missing null check. The system was designed to use `null` to represent an inactive registry, but the implementation of `getRegistry()` masked this by returning an empty map. The fix involves removing this incorrect default and adding a null check in `isRegistered` to handle the now-correct `null` return value. This is a classic 'Checking' defect where the logic failed to validate the state of the registry correctly.
- Prefix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}
- Postfix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}

### Lang-43
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is an infinite loop caused by an incorrect algorithmic step (failing to advance the parser position). This is a classic Algorithm/Method defect where the procedure for parsing the string is flawed. It is not a Checking defect because the logic for identifying the quote is correct, but the state update (advancing the position) is missing.
- Postfix reasoning summary: The bug is a classic infinite loop caused by a missing state update (advancing the parse position). In ODC, missing a guard or a necessary state update in a conditional branch is classified as 'Checking'.
- Prefix context signal: org.apache.commons.lang.text.ExtendedMessageFormatTest::testEscapedQuote_LANG_477: java.lang.OutOfMemoryError: Java heap space
- Postfix context signal: org.apache.commons.lang.text.ExtendedMessageFormatTest::testEscapedQuote_LANG_477: java.lang.OutOfMemoryError: Java heap space

### Lang-51
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic missing guard/termination issue. The logic fails to validate that the string length is sufficient before proceeding to access indices in the next case block. Because the primary issue is the lack of a control flow termination (or validation) to prevent invalid index access, 'Checking' is the most appropriate ODC type.
- Postfix reasoning summary: The bug is a classic fall-through error in a switch statement. The procedure for handling 3-character strings was incomplete because it failed to return a result, allowing execution to proceed into the 4-character handling logic. This is a procedural/algorithmic error in the control flow of the method, not a missing guard (the guard for length 4 is present, but it is reached incorrectly) or a simple initialization error.
- Prefix context signal: org.apache.commons.lang.BooleanUtilsTest::test_toBoolean_String: java.lang.StringIndexOutOfBoundsException: String index out of range: 3
- Postfix context signal: org.apache.commons.lang.BooleanUtilsTest::test_toBoolean_String: java.lang.StringIndexOutOfBoundsException: String index out of range: 3

### Lang-57
- Type shift: Assignment/Initialization -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Assignment/Initialization' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic initialization error where a static field is accessed while null. It is not a checking issue because the logic itself is correct; it is not an algorithm issue because the procedure is correct; it is an initialization issue where the required state is missing at the time of access.
- Postfix reasoning summary: The bug is a classic case of missing initialization/validation. The code relied on a static field that was not guaranteed to be initialized, causing a crash. By switching to a method call that handles the initialization logic, the code now correctly validates the state of the collection before performing the check. This is a 'Checking' type because the fix ensures the necessary condition (the collection being initialized) is met before proceeding with the operation.
- Prefix context signal: org.apache.commons.lang.LocaleUtilsTest::testAvailableLocaleSet: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang.LocaleUtilsTest::testAvailableLocaleSet: java.lang.NullPointerException

## Type Changed (No Alternative Overlap)

- No qualifying cases found.
## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Checking: 6
  - Bugs: Lang-12, Lang-16, Lang-43, Lang-49, Lang-54, Lang-55
- Checking -> Algorithm/Method: 4
  - Bugs: Lang-20, Lang-51, Lang-5, Lang-60
- Assignment/Initialization -> Checking: 2
  - Bugs: Lang-34, Lang-57
- Algorithm/Method -> Assignment/Initialization: 1
  - Bugs: Lang-26
- Assignment/Initialization -> Algorithm/Method: 1
  - Bugs: Lang-32
- Algorithm/Method -> Relationship: 1
  - Bugs: Lang-4 (no family match)

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 28
  - Bugs: Lang-10, Lang-13, Lang-14, Lang-15, Lang-17, Lang-1, Lang-21, Lang-22, Lang-23, Lang-28, Lang-29, Lang-30, Lang-31, Lang-38, Lang-3, Lang-40, Lang-41, Lang-42, Lang-46, Lang-50, Lang-52, Lang-53, Lang-59, Lang-61, Lang-63, Lang-65, Lang-6, Lang-8
- Checking -> Checking: 17
  - Bugs: Lang-11, Lang-19, Lang-24, Lang-27, Lang-33, Lang-35, Lang-36, Lang-37, Lang-39, Lang-44, Lang-45, Lang-47, Lang-58, Lang-62, Lang-64, Lang-7, Lang-9
- Relationship -> Relationship: 1
  - Bugs: Lang-56
