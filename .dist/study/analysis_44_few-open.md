# Batch Study Analysis

- Created: `2026-07-10T19:56:52+00:00`
- Total pairs: **44**
- Projects covered: **17**
- Type changed: **9** (20.5%)
- Type unchanged: **35** (79.5%)
- No alternative overlap: **3** (6.8%)
- No family match: **2** (4.5%)
- Family match: **42** (95.5%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **44** of 44
- Capability: 31 (70.5%)
- Reliability: 12 (27.3%)
- Serviceability: 1 (2.3%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **41/44** (93.2%)
- Kappa: 0.835
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 21
- Reliability × Checking: 10
- Capability × Checking: 4
- Capability × Assignment/Initialization: 4
- Capability × Function/Class/Object: 2
- Reliability × Algorithm/Method: 2
- Serviceability × Checking: 1

## Alternative Match Cases (Type Changed)

### Chart-17
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a missing guard/validation check for the empty series case. The clone() method blindly calls createCopy(0, getItemCount() - 1). When getItemCount() is 0, it passes (0, -1), which violates the 'start <= end' check in createCopy(). This is a classic 'Checking' defect where the boundary condition (empty series) was not properly validated before invoking a method with strict parameter requirements.
- Postfix reasoning summary: The bug was caused by an incorrect procedural approach to cloning an object. The clone() method relied on a range-based copy method (createCopy) that was not designed to handle empty ranges (start=0, end=-1). The fix replaces this procedural logic with a direct deep clone of the data structure, which is a correction of the method's implementation strategy. It is not a 'Checking' bug because the fix is not just adding a guard, but replacing the entire cloning strategy. It is not 'Function/Class/Object' because it is a local implementation detail of the clone method.
- Prefix context signal: org.jfree.data.time.junit.TimeSeriesTests::testBug1832432: java.lang.IllegalArgumentException: Requires start <= end.
- Postfix context signal: org.jfree.data.time.junit.TimeSeriesTests::testBug1832432: java.lang.IllegalArgumentException: Requires start <= end.

### Closure-140
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic case of an incorrect guard or missing validation. The compiler pass is performing a 'reportCodeChange()' action without first verifying if the state has actually changed. This is a failure in the conditional logic that governs when a change is reported, making 'Checking' the most appropriate ODC type.
- Postfix reasoning summary: The bug is an algorithmic issue where the compiler's module processing logic did not correctly handle empty modules, leading to incorrect reporting of code changes. The fix involves implementing a new procedural step (filling empty modules) to ensure the algorithm operates on a consistent data structure. This is a classic algorithmic correction rather than a simple guard (Checking) or a value assignment.
- Prefix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed
- Postfix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed

### Compress-27
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is in the procedural logic of the 'parseOctal' method. The algorithm incorrectly treats a buffer that trims down to an empty range as an invalid input, whereas it should be treated as a valid representation of the value 0. This is a procedural/algorithmic error in how the input buffer is processed, not a missing guard or a wrong constant.
- Postfix reasoning summary: The bug is caused by an incorrect validation check (a guard) that prevents valid (empty/zero) input from being processed. The fix is to remove this incorrect check, which is a classic 'Checking' defect.
- Prefix context signal: org.apache.commons.compress.archivers.tar.TarUtilsTest::testParseOctal: java.lang.IllegalArgumentException: Invalid byte 32 at offset 1 in ' {NUL}' len=2
- Postfix context signal: org.apache.commons.compress.archivers.tar.TarUtilsTest::testParseOctal: java.lang.IllegalArgumentException: Invalid byte 32 at offset 1 in ' {NUL}' len=2

### Lang-60
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a boundary condition error where the search logic uses the wrong limit (buffer capacity vs. current string size). This is a classic 'Checking' defect because the loop condition or boundary validation is incorrect.
- Postfix reasoning summary: The bug is an algorithmic error where the iteration strategy for searching the string builder was incorrect. It was scanning the entire allocated buffer rather than the active portion of the string. This is a procedural logic error within the methods, fitting the Algorithm/Method category perfectly.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

### Collections-24
- Type shift: Function/Class/Object -> Algorithm/Method.
- Comparison detail: Pre-fix primary 'Function/Class/Object' found in post-fix alternative types
- Prefix reasoning summary: This is a structural defect where a class is missing a required interface implementation. It is not a local algorithmic error, a wrong value, or a missing guard, but a fundamental design-level omission of a capability (the marker interface) required by the system's architecture.
- Postfix reasoning summary: The fix involves adding an interface implementation and a conditional check (guard) in the factory method to optimize and correctly handle existing unmodifiable collections. This is a procedural correction to the factory method's logic and the class's structural contract, which fits best under Algorithm/Method as it corrects the implementation strategy of the factory.
- Prefix context signal: org.apache.commons.collections4.collection.UnmodifiableBoundedCollectionTest::testDecorateFactory: junit.framework.AssertionFailedError: expected same:<[, One, 2, Three, null, 4, One, 5.0, 6.0, Seven, Eight, Nine, 10, 11, 12, Thirteen, 14, 15, 16]> was not:<[, One, 2, Three, null, 4, One, 5.0, 6.0, Seven, Eight, Nine, 10, 11, 12, Thirteen, 14, 15, 16]>
- Postfix context signal: org.apache.commons.collections4.collection.UnmodifiableBoundedCollectionTest::testDecorateFactory: junit.framework.AssertionFailedError: expected same:<[, One, 2, Three, null, 4, One, 5.0, 6.0, Seven, Eight, Nine, 10, 11, 12, Thirteen, 14, 15, 16]> was not:<[, One, 2, Three, null, 4, One, 5.0, 6.0, Seven, Eight, Nine, 10, 11, 12, Thirteen, 14, 15, 16]>

### Time-2
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic 'Checking' error. The code implements a validation check (to prevent duplicates) that is logically flawed because it uses an insufficient condition (checking only the range duration type) to determine equality, leading to a false positive exception. It is not an Algorithm/Method issue because the procedure is correct, just the guard condition is too broad. It is not a Function/Class/Object issue because the capability exists and is correctly designed, just incorrectly guarded.
- Postfix reasoning summary: The bug is caused by incorrect procedural logic in how duration fields are compared and validated within the Partial class. The fix involves rewriting the comparison strategy (in UnsupportedDurationField) and the validation logic (in Partial), which fits the definition of an Algorithm/Method defect. It is not a simple missing check (Checking) because the existing logic was fundamentally flawed in its comparison strategy, nor is it a design-level capability issue (Function/Class/Object).
- Prefix context signal: org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year
- Postfix context signal: org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year

## Type Changed (No Alternative Overlap)

### Math-34
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Checking' vs 'Algorithm/Method')
- Prefix reasoning summary: The defect is a missing validation/restriction on the iterator's capability to modify the underlying collection. This is a classic 'Checking' defect where a guard (in this case, the enforcement of an unmodifiable contract) is missing, allowing an operation that should be prohibited.
- Postfix reasoning summary: The bug is an incorrect implementation of the iterator() method. It is not a missing check (Checking), nor a wrong value (Assignment/Initialization), nor a design-level capability omission (Function/Class/Object). It is a procedural error in how the iterator is provided, which is best classified as an Algorithm/Method defect as it involves correcting the internal logic of the method to ensure proper data encapsulation.
- Prefix context signal: org.apache.commons.math3.genetics.ListPopulationTest::testIterator: junit.framework.AssertionFailedError: Expected exception: java.lang.UnsupportedOperationException
- Postfix context signal: org.apache.commons.math3.genetics.ListPopulationTest::testIterator: junit.framework.AssertionFailedError: Expected exception: java.lang.UnsupportedOperationException

### JacksonCore-24
- Type shift: Checking -> Interface/O-O Messages.
- Comparison detail: No match: pre-fix 'Checking' (Control and Data Flow) vs post-fix 'Interface/O-O Messages' (Structural)
- Prefix reasoning summary: The defect is classified as Checking because the core issue is the lack of a specific validation check that distinguishes between a syntax error (parse error) and a type coercion error. The current implementation uses a generic error reporting mechanism (JsonParseException) for both cases. The fix requires adding a check or a specialized error-reporting path to handle coercion failures distinctly, which aligns with the ODC definition of Checking (missing or incorrect validation of data).
- Postfix reasoning summary: The bug is classified as Interface/O-O Messages because the fix involves changing the error reporting contract. By introducing a new exception type and passing additional metadata (inputType, targetType) through the error reporting methods, the system now correctly communicates the nature of the coercion failure to the caller, which was previously obscured by a generic exception.
- Prefix context signal: com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)
- Postfix context signal: com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)

### JxPath-22
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Checking' vs 'Assignment/Initialization')
- Prefix reasoning summary: The root cause is a missing validation check for an empty string namespace URI. The code currently only checks for null, failing to handle the case where the namespace is explicitly empty. This is a classic 'Checking' defect where a condition is incomplete.
- Postfix reasoning summary: The fix is a direct correction of a returned value (changing an empty string to null). This is an Assignment/Initialization defect because it corrects the state/value returned by a method to align with the expected contract of the system, rather than changing the procedural logic (Algorithm/Method) or adding a missing guard (Checking).
- Prefix context signal: org.apache.commons.jxpath.ri.model.JXPath154Test::testInnerEmptyNamespaceDOM: junit.framework.ComparisonFailure: expected:</b:foo[1]/[test[1]]> but was:</b:foo[1]/[node()[2]]>
- Postfix context signal: org.apache.commons.jxpath.ri.model.JXPath154Test::testInnerEmptyNamespaceDOM: junit.framework.ComparisonFailure: expected:</b:foo[1]/[test[1]]> but was:</b:foo[1]/[node()[2]]>

## Type Transitions

### Type Changed (Prefix → Postfix)

- Checking -> Algorithm/Method: 5
  - Bugs: Chart-17, Closure-140, Lang-60, Math-34 (no alt overlap), Time-2
- Function/Class/Object -> Algorithm/Method: 1
  - Bugs: Collections-24 (no family match)
- Algorithm/Method -> Checking: 1
  - Bugs: Compress-27
- Checking -> Interface/O-O Messages: 1
  - Bugs: JacksonCore-24 (no alt overlap, no family match)
- Checking -> Assignment/Initialization: 1
  - Bugs: JxPath-22 (no alt overlap)

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 22
  - Bugs: Chart-10, Cli-15, Cli-17, Closure-25, Codec-15, Codec-3, Collections-21, Collections-3, Compress-15, Compress-33, Csv-13, Csv-1, Gson-14, Gson-7, JacksonCore-16, JacksonXml-3, Jsoup-12, Jsoup-28, JxPath-20, Math-56, Time-14, Time-25
- Checking -> Checking: 8
  - Bugs: Chart-13, Cli-32, Closure-143, Compress-44, Lang-27, Lang-43, Mockito-2, Time-27
- Assignment/Initialization -> Assignment/Initialization: 4
  - Bugs: Codec-16, JacksonDatabind-111, JacksonDatabind-24, Mockito-26
- Function/Class/Object -> Function/Class/Object: 1
  - Bugs: JacksonXml-6
