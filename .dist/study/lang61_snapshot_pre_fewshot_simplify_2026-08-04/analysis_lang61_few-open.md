# Batch Study Analysis

- Created: `2026-07-10T19:57:08+00:00`
- Total pairs: **61**
- Projects covered: **1**
- Type changed: **13** (21.3%)
- Type unchanged: **48** (78.7%)
- No alternative overlap: **2** (3.3%)
- No family match: **2** (3.3%)
- Family match: **59** (96.7%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **61** of 61
- Capability: 34 (55.7%)
- Reliability: 26 (42.6%)
- Usability: 1 (1.6%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **56/61** (91.8%)
- Kappa: 0.8356
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 26
- Reliability × Checking: 16
- Reliability × Algorithm/Method: 8
- Capability × Checking: 8
- Usability × Checking: 1
- Reliability × Function/Class/Object: 1
- Reliability × Assignment/Initialization: 1

## Alternative Match Cases (Type Changed)

### Lang-4
- Type shift: Algorithm/Method -> Interface/O-O Messages.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Interface/O-O Messages' is in pre-fix alternatives
- Prefix reasoning summary: The defect is in the procedural logic of the translation method. It incorrectly assumes that any CharSequence can be used as a key in a HashMap for lookup purposes. This is a flaw in the computational strategy (the lookup algorithm) used to find the translation, rather than a missing guard (Checking) or a simple initialization error. It is not a design-level capability gap (Function/Class/Object) because the functionality exists but is implemented with an incorrect algorithmic approach for the given data type.
- Postfix reasoning summary: The defect is a classic interface contract mismatch. The component (LookupTranslator) expected a contract (reliable equality/hashing) from the CharSequence interface that the interface does not provide. By forcing the key to a String, the component enforces the contract it requires, which is a structural fix at the boundary of the component's internal data structure.
- Prefix context signal: org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>
- Postfix context signal: org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>

### Lang-20
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a missing validation check. The code performs an operation (calling .length() on the result of toString()) without verifying if the result of that operation is null. This is a classic 'Checking' defect where a guard or validation is missing for a potentially null value returned by an external object's method.
- Postfix reasoning summary: The bug is an algorithmic flaw in how the initial capacity of the StringBuilder is calculated. It is not a missing check (the code already had a null check for the array element itself, but not for the result of toString()), nor is it a simple assignment error. It is a procedural error in the computational strategy for memory allocation, which is best classified as Algorithm/Method.
- Prefix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException

### Lang-26
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The defect is an algorithmic error where the procedure for calculating the week-of-year fails to incorporate locale-specific calendar rules. It is not a missing check (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object), but rather an incorrect implementation of the date formatting procedure.
- Postfix reasoning summary: The bug is classified as Assignment/Initialization because the fix involves correcting the initialization of a local object (GregorianCalendar). The logic of the formatting algorithm itself is correct, but it was operating on a calendar object initialized with the wrong parameters (missing the locale).
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>

### Lang-31
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is in the procedural logic of the containsAny method. It fails to correctly handle Unicode supplementary characters because its internal search algorithm does not account for surrogate pairs, treating them as individual characters. This is a classic algorithmic error where the procedure for matching characters is insufficient for the data type being processed.
- Postfix reasoning summary: The bug is caused by a missing validation check for supplementary Unicode characters. The existing logic correctly identifies a match for characters in the Basic Multilingual Plane but fails to distinguish between a single character and the first half of a surrogate pair. The fix introduces a conditional guard to validate the full surrogate pair, which is a classic 'Checking' defect.
- Prefix context signal: org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- Postfix context signal: org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars: junit.framework.AssertionFailedError: expected:<false> but was:<true>

### Lang-46
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a procedural error where the method performs an incorrect transformation (escaping a character that should not be escaped). This fits the Algorithm/Method definition as it involves correcting the computational logic of the escape procedure. It is not a missing check (Checking), a wrong value assignment (Assignment/Initialization), or a design-level capability gap (Function/Class/Object).
- Postfix reasoning summary: The bug is caused by an incorrect conditional action (unconditionally escaping a character that should not be escaped in Java). The fix adds a guard (the 'escapeForwardSlash' boolean check) to ensure the character is only escaped when appropriate. This fits the 'Checking' ODC type, as it involves correcting the logic of a conditional check.
- Prefix context signal: org.apache.commons.lang.StringEscapeUtilsTest::testEscapeJavaWithSlash: junit.framework.ComparisonFailure: expected:<...tring with a slash ([]/) in it> but was:<...tring with a slash ([\]/) in it>
- Postfix context signal: org.apache.commons.lang.StringEscapeUtilsTest::testEscapeJavaWithSlash: junit.framework.ComparisonFailure: expected:<...tring with a slash ([]/) in it> but was:<...tring with a slash ([\]/) in it>

### Lang-49
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The issue is a procedural error in the reduction algorithm. It is not a missing check (Checking) because the logic is present but incorrect for this specific case, nor is it a simple assignment error. It is a flaw in the computational strategy for reducing fractions.
- Postfix reasoning summary: The bug is caused by a missing conditional check for a specific input state (numerator == 0). The fix adds this missing guard, which is the definition of a 'Checking' ODC type. It is not an algorithmic error because the logic for non-zero numerators remains correct, and it is not a design-level capability issue.
- Prefix context signal: org.apache.commons.lang.math.FractionTest::testReduce: junit.framework.AssertionFailedError: expected:<1> but was:<100>
- Postfix context signal: org.apache.commons.lang.math.FractionTest::testReduce: junit.framework.AssertionFailedError: expected:<1> but was:<100>

### Lang-55
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The issue is a procedural error in how the StopWatch calculates the final time when stop() is invoked. It is not a missing guard (Checking) or a simple wrong value (Assignment), but a flaw in the computational logic of the state machine's transition to the stopped state. Therefore, it is classified as Algorithm/Method.
- Postfix reasoning summary: The bug is caused by a missing validation check (guard) in the stop() method. The method was unconditionally updating the stop time, even when the stopwatch was already suspended. Adding the missing state check ensures the stop time is only captured when the stopwatch is actively running, which is the correct behavior for a stopwatch component.
- Prefix context signal: org.apache.commons.lang.time.StopWatchTest::testLang315: junit.framework.AssertionFailedError
- Postfix context signal: org.apache.commons.lang.time.StopWatchTest::testLang315: junit.framework.AssertionFailedError

### Lang-56
- Type shift: Function/Class/Object -> Relationship.
- Comparison detail: Cross-alternative match: pre-fix 'Function/Class/Object' is in post-fix alternatives, and post-fix 'Relationship' is in pre-fix alternatives
- Prefix reasoning summary: This is a design-level capability issue. The class FastDateFormat is intended to be serializable (as evidenced by the test attempting to serialize it), but its internal structure (specifically the rule components) lacks the necessary implementation to support this. This is not a local algorithmic error or a simple missing guard, but a structural deficiency in the class design regarding its serialization contract.
- Postfix reasoning summary: The defect is a failure to maintain the consistency of an object's state across serialization boundaries. The fields were not marked as transient, violating the contract required for serializing objects that contain non-serializable components. This is a classic structural relationship issue where the internal state representation (the rules) must be correctly associated with the serialized form (the pattern) during the deserialization process.
- Prefix context signal: org.apache.commons.lang.time.FastDateFormatTest::testLang303: org.apache.commons.lang.SerializationException: java.io.NotSerializableException: org.apache.commons.lang.time.FastDateFormat$PaddedNumberField
- Postfix context signal: org.apache.commons.lang.time.FastDateFormatTest::testLang303: org.apache.commons.lang.SerializationException: java.io.NotSerializableException: org.apache.commons.lang.time.FastDateFormat$PaddedNumberField

### Lang-5
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic 'Checking' issue. The code implements a validation check (lines 98-99) that is too restrictive, failing to account for a valid input format (strings starting with an underscore). The fix involves adding a guard or modifying the existing condition to correctly validate this input, rather than changing the underlying algorithm or data structure.
- Postfix reasoning summary: The fix adds a new procedural branch to handle a specific input format that was previously unhandled. This is a correction to the method's computational logic (how it parses the string) rather than a simple guard or value assignment. It is not a design-level capability gap (Function/Class/Object) because the method already existed and handled other formats correctly; it simply needed an additional algorithmic path to support a valid input format.
- Prefix context signal: org.apache.commons.lang3.LocaleUtilsTest::testLang865: java.lang.IllegalArgumentException: Invalid locale format: _GB
- Postfix context signal: org.apache.commons.lang3.LocaleUtilsTest::testLang865: java.lang.IllegalArgumentException: Invalid locale format: _GB

### Lang-60
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a boundary condition error where the search logic uses the wrong limit (buffer capacity vs. current string size). This is a classic 'Checking' defect because the loop condition or boundary validation is incorrect.
- Postfix reasoning summary: The bug is an algorithmic error where the iteration strategy for searching the string builder was incorrect. It was scanning the entire allocated buffer rather than the active portion of the string. This is a procedural logic error within the methods, fitting the Algorithm/Method category perfectly.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

### Lang-57
- Type shift: Assignment/Initialization -> Algorithm/Method.
- Comparison detail: Pre-fix primary 'Assignment/Initialization' found in post-fix alternative types
- Prefix reasoning summary: The defect is a failure to initialize a static field before its first use. This fits the definition of Assignment/Initialization perfectly, as the logic of the method is correct, but the state (the set) is missing its required initialization.
- Postfix reasoning summary: The bug is an incorrect procedural implementation where a method assumes a static field is already initialized. By changing the implementation to call the initialization method, the code ensures the required data structure is ready. This is a correction of the method's internal logic (Algorithm/Method) rather than a missing guard (Checking) or a simple value assignment (Assignment/Initialization).
- Prefix context signal: org.apache.commons.lang.LocaleUtilsTest::testAvailableLocaleSet: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang.LocaleUtilsTest::testAvailableLocaleSet: java.lang.NullPointerException

## Type Changed (No Alternative Overlap)

### Lang-34
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Algorithm/Method' vs 'Checking')
- Prefix reasoning summary: The defect is an algorithmic failure in managing the lifecycle of a ThreadLocal resource. It is not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object). It is a procedural error in the implementation of the string building process where the cleanup step is missing, which is best classified as an Algorithm/Method defect.
- Postfix reasoning summary: The bug is fundamentally a missing null check in the `isRegistered` method and an incorrect return value in `getRegistry` that masked the null state. This fits the 'Checking' category as it involves adding a guard condition to handle the null state of the registry.
- Prefix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}
- Postfix context signal: org.apache.commons.lang3.builder.ToStringBuilderTest::testObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: {}

### Lang-29
- Type shift: Algorithm/Method -> Interface/O-O Messages.
- Comparison detail: No match: pre-fix 'Algorithm/Method' (Control and Data Flow) vs post-fix 'Interface/O-O Messages' (Structural)
- Prefix reasoning summary: The bug is an algorithmic issue where the method 'toJavaVersionInt' is not correctly producing an integer result. It is not a missing guard (Checking) because the method is executing but returning the wrong type/value. It is not an Assignment/Initialization issue because the logic itself is flawed in its computational strategy. It is not a design-level capability issue (Function/Class/Object) because the method exists and is intended to perform this conversion; it just does so incorrectly.
- Postfix reasoning summary: The bug is a classic interface/contract mismatch. The method was intended to return an integer representation of a version (e.g., 131), but was declared to return a float. This caused the test suite to fail when it expected an integer but received a float (e.g., 0.0). The fix is a signature change, which falls under Interface/O-O Messages.
- Prefix context signal: org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>
- Postfix context signal: org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>

## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Checking: 5
  - Bugs: Lang-31, Lang-34 (no alt overlap), Lang-46, Lang-49, Lang-55
- Checking -> Algorithm/Method: 3
  - Bugs: Lang-20, Lang-5, Lang-60
- Algorithm/Method -> Interface/O-O Messages: 2
  - Bugs: Lang-29 (no alt overlap, no family match), Lang-4 (no family match)
- Algorithm/Method -> Assignment/Initialization: 1
  - Bugs: Lang-26
- Function/Class/Object -> Relationship: 1
  - Bugs: Lang-56
- Assignment/Initialization -> Algorithm/Method: 1
  - Bugs: Lang-57

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 26
  - Bugs: Lang-10, Lang-13, Lang-14, Lang-15, Lang-17, Lang-1, Lang-21, Lang-22, Lang-23, Lang-28, Lang-30, Lang-32, Lang-38, Lang-3, Lang-40, Lang-41, Lang-42, Lang-50, Lang-52, Lang-53, Lang-59, Lang-61, Lang-63, Lang-65, Lang-6, Lang-8
- Checking -> Checking: 22
  - Bugs: Lang-11, Lang-12, Lang-16, Lang-19, Lang-24, Lang-27, Lang-33, Lang-35, Lang-36, Lang-37, Lang-39, Lang-43, Lang-44, Lang-45, Lang-47, Lang-51, Lang-54, Lang-58, Lang-62, Lang-64, Lang-7, Lang-9
