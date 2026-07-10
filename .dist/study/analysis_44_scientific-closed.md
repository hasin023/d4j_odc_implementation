# Batch Study Analysis

- Created: `2026-07-10T19:56:52+00:00`
- Total pairs: **44**
- Projects covered: **17**
- Type changed: **14** (31.8%)
- Type unchanged: **30** (68.2%)
- No alternative overlap: **3** (6.8%)
- No family match: **5** (11.4%)
- Family match: **39** (88.6%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **44** of 44
- Capability: 39 (88.6%)
- Reliability: 5 (11.4%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **42/44** (95.5%)
- Kappa: 0.8079
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Checking: 21
- Capability × Algorithm/Method: 13
- Reliability × Checking: 4
- Capability × Assignment/Initialization: 3
- Capability × Function/Class/Object: 2
- Reliability × Algorithm/Method: 1

## Alternative Match Cases (Type Changed)

### Collections-21
- Type shift: Function/Class/Object -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Function/Class/Object' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and test failures confirm that modifications to the subList of a SetUniqueList do not respect the uniqueness constraint. Since SetUniqueList is a decorator, it must provide a specialized subList view that delegates operations back to the parent while maintaining the set-based uniqueness check. The absence of this logic is a structural design defect.
- Postfix reasoning summary: The defect is a failure to adhere to the expected behavior of the subList() method. By returning a mutable list, the class allows operations that corrupt the internal state of the SetUniqueList. The fix is to wrap the returned sublist in an unmodifiable decorator, which is a local procedural change to the method.
- Prefix context signal: org.apache.commons.collections4.list.SetUniqueListTest::testSubListIsUnmodifiable: junit.framework.AssertionFailedError: subList should be unmodifiable
- Postfix context signal: org.apache.commons.collections4.list.SetUniqueListTest::testSubListIsUnmodifiable: junit.framework.AssertionFailedError: subList should be unmodifiable

### Closure-140
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The error message explicitly states that reportCodeChange() was called when nothing changed. This is a classic 'Checking' defect where a guard condition (checking if the move is valid/necessary) is missing or insufficient.
- Postfix reasoning summary: The bug is caused by the absence of a necessary initialization step (filling empty modules) which leads to inconsistent state during optimization passes. This is a procedural/algorithmic issue in the compiler's setup logic, fitting the 'Algorithm/Method' ODC type.
- Prefix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed
- Postfix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed

### JacksonXml-3
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Post-fix primary 'Algorithm/Method' found in pre-fix alternative types
- Prefix reasoning summary: The failure is a classic case of a missing check for a specific state (attribute value) in a conditional block, which is the definition of a 'Checking' defect in ODC.
- Postfix reasoning summary: The bug is a procedural error where a method fails to return a value in a specific control flow branch (XML_ATTRIBUTE_VALUE), which is a classic Algorithm/Method defect.
- Prefix context signal: com.fasterxml.jackson.dataformat.xml.stream.XmlParserNextXxxTest::testXmlAttributesWithNextTextValue: junit.framework.ComparisonFailure: expected:<7> but was:<null>
- Postfix context signal: com.fasterxml.jackson.dataformat.xml.stream.XmlParserNextXxxTest::testXmlAttributesWithNextTextValue: junit.framework.ComparisonFailure: expected:<7> but was:<null>

### Jsoup-12
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The failure is a classic parsing error where the grammar implementation (the Selector class) lacks the necessary validation or handling for a specific character (the pipe) within a specific context (attribute regex). This is a 'Checking' defect because the parser's predicate logic for identifying tokens is insufficient for the provided input.
- Postfix reasoning summary: The bug is a failure to correctly parse CSS selectors when they contain nested structures (like attribute selectors) following a combinator. The original implementation used a simple 'consumeToAny' which is not context-aware regarding nested brackets. The fix introduces a stateful, balanced-token-aware parsing method, which is a classic algorithmic correction.
- Prefix context signal: org.jsoup.select.SelectorTest::testByAttributeRegexCombined: org.jsoup.select.Selector$SelectorParseException: Could not parse query '=x|y]': unexpected token at '=x|y]'
- Postfix context signal: org.jsoup.select.SelectorTest::testByAttributeRegexCombined: org.jsoup.select.Selector$SelectorParseException: Could not parse query '=x|y]': unexpected token at '=x|y]'

### Time-2
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The code checks if two consecutive fields have null range duration types. If they do, it throws an exception. This logic is flawed because it assumes that having a null range duration type implies the fields are identical, which is not true for all Joda-Time field types (e.g., era and year).
- Postfix reasoning summary: The bug is caused by an incorrect implementation of the ordering algorithm in Partial.java and the supporting compareTo method in UnsupportedDurationField. The logic fails to correctly handle cases where fields have unsupported durations or null range types, leading to incorrect validation failures.
- Prefix context signal: org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year
- Postfix context signal: org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year

### Time-14
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic 'Checking' defect where the validation logic (checking if the day is valid for the month) is applied in a context (a generic 1970 instant) that is too restrictive for the data being processed (a leap day). The fix requires either using a leap year as the base or bypassing the strict validation for partials that don't have a year.
- Postfix reasoning summary: The defect is an algorithmic flaw where the procedure for adding months to a partial date (MonthDay) relies on an invalid assumption that the partial can be represented as a specific point in time (1970). This is a procedural error in how the library handles partial date arithmetic.
- Prefix context signal: org.joda.time.TestMonthDay_Basics::testPlusMonths_int_negativeFromLeap: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- Postfix context signal: org.joda.time.TestMonthDay_Basics::testPlusMonths_int_negativeFromLeap: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]

### Compress-33
- Type shift: Checking -> Function/Class/Object.
- Comparison detail: Pre-fix primary 'Checking' found in post-fix alternative types
- Prefix reasoning summary: The bug report explicitly states that zlib-headered deflate streams are not detected. The provided code snippet shows the final fallback to an exception when no signature matches. Since the system is designed to detect various formats, the absence of a specific check for the zlib header is the root cause.
- Postfix reasoning summary: The bug report explicitly states that the factory fails to detect zlib-compressed streams. The fix involves adding a 'matches' method to the stream class and calling it from the factory. This is a missing capability (a new feature/functionality) rather than a local algorithmic error or a simple assignment fix.
- Prefix context signal: org.apache.commons.compress.compressors.DetectCompressorTestCase::testDetection: org.apache.commons.compress.compressors.CompressorException: No Compressor found for the stream signature.
- Postfix context signal: org.apache.commons.compress.compressors.DetectCompressorTestCase::testDetection: org.apache.commons.compress.compressors.CompressorException: No Compressor found for the stream signature.

### Jsoup-28
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and failing tests confirm that Jsoup's unescape logic is over-eager. The fix requires adding a check to ensure that only valid, terminated entities are decoded, which falls under the 'Checking' ODC category.
- Postfix reasoning summary: The bug is a classic case of an incorrect algorithmic strategy for parsing entities. The regex-based approach in `Entities.unescape` fails to correctly handle entity boundaries, leading to spurious matches. The fix replaces this with a robust tokenization strategy, which is a procedural/algorithmic change.
- Prefix context signal: org.jsoup.nodes.EntitiesTest::unescape: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>
- Postfix context signal: org.jsoup.nodes.EntitiesTest::unescape: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>

### JxPath-22
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Pre-fix primary 'Checking' found in post-fix alternative types
- Prefix reasoning summary: The failure is a direct result of missing conditional logic (a check for an empty string namespace) in the path generation algorithm. This falls squarely under the 'Checking' ODC type.
- Postfix reasoning summary: The fix modifies the return value of getNamespaceURI() to ensure it returns null instead of an empty string. This is a classic case of incorrect initialization/assignment of a variable representing object state, which then propagates to incorrect logic in asPath().
- Prefix context signal: org.apache.commons.jxpath.ri.model.JXPath154Test::testInnerEmptyNamespaceDOM: junit.framework.ComparisonFailure: expected:</b:foo[1]/[test[1]]> but was:</b:foo[1]/[node()[2]]>
- Postfix context signal: org.apache.commons.jxpath.ri.model.JXPath154Test::testInnerEmptyNamespaceDOM: junit.framework.ComparisonFailure: expected:</b:foo[1]/[test[1]]> but was:</b:foo[1]/[node()[2]]>

### Lang-60
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and the failing test case provide sufficient evidence that the methods are failing to respect the logical boundary of the string builder, instead iterating over the entire physical buffer. This is a 'Checking' defect as it involves an incorrect loop termination condition.
- Postfix reasoning summary: The defect is a classic off-by-one/boundary error where the loop condition uses the buffer capacity rather than the current size of the data, which is a procedural logic error in the implementation of the search methods.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

### Mockito-26
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The failure is consistent across multiple tests that expect specific primitive types (double, float, etc.) but receive an Integer. This is a procedural error in the method responsible for providing default values.
- Postfix reasoning summary: The failure symptoms (ClassCastException: Integer cannot be cast to Double) directly point to an incorrect value being returned for a double primitive type. The fix diff confirms that the initialization of the primitiveValues map was using an integer literal for the double key.
- Prefix context signal: org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')
- Postfix context signal: org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')

## Type Changed (No Alternative Overlap)

### Collections-24
- Type shift: Algorithm/Method -> Function/Class/Object.
- Comparison detail: No match: pre-fix 'Algorithm/Method' (Control and Data Flow) vs post-fix 'Function/Class/Object' (Structural)
- Prefix reasoning summary: The bug is a combination of a missing interface implementation (structural) and a missing check in the factory method (procedural). Given the ODC rules, the procedural fix in the factory method is the primary driver for the observed behavior in the test.
- Postfix reasoning summary: The defect is a missing interface implementation (a structural capability gap) and a missing optimization/check in the factory method. This is a design-level omission where the class failed to adhere to the expected contract of the library.
- Prefix context signal: org.apache.commons.collections4.collection.UnmodifiableBoundedCollectionTest::testDecorateFactory: junit.framework.AssertionFailedError: expected same:<[, One, 2, Three, null, 4, One, 5.0, 6.0, Seven, Eight, Nine, 10, 11, 12, Thirteen, 14, 15, 16]> was not:<[, One, 2, Three, null, 4, One, 5.0, 6.0, Seven, Eight, Nine, 10, 11, 12, Thirteen, 14, 15, 16]>
- Postfix context signal: org.apache.commons.collections4.collection.UnmodifiableBoundedCollectionTest::testDecorateFactory: junit.framework.AssertionFailedError: expected same:<[, One, 2, Three, null, 4, One, 5.0, 6.0, Seven, Eight, Nine, 10, 11, 12, Thirteen, 14, 15, 16]> was not:<[, One, 2, Three, null, 4, One, 5.0, 6.0, Seven, Eight, Nine, 10, 11, 12, Thirteen, 14, 15, 16]>

### JacksonCore-24
- Type shift: Algorithm/Method -> Interface/O-O Messages.
- Comparison detail: No match: pre-fix 'Algorithm/Method' (Control and Data Flow) vs post-fix 'Interface/O-O Messages' (Structural)
- Prefix reasoning summary: The bug is a failure to use the correct exception type for coercion errors. The fix involves changing the method call from _reportError to _reportInputCoercion, which is a local procedural change.
- Postfix reasoning summary: The bug is not a logic error in the algorithm, but a design-level requirement to improve the exception hierarchy and metadata. By changing the exception type thrown by the parser, the interface between the parser and the calling application is modified to provide more specific information.
- Prefix context signal: com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)
- Postfix context signal: com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)

### Math-34
- Type shift: Checking -> Interface/O-O Messages.
- Comparison detail: No match: pre-fix 'Checking' (Control and Data Flow) vs post-fix 'Interface/O-O Messages' (Structural)
- Prefix reasoning summary: The bug is a classic case of missing validation/guarding of internal state access. The iterator should not allow modification of the underlying collection. Adding an unmodifiable wrapper is a 'Checking' fix as it enforces the contract of the collection's immutability.
- Postfix reasoning summary: The bug is an interface contract violation where the internal state is exposed to external modification. This is a structural issue regarding how the object exposes its internal data structure to clients.
- Prefix context signal: org.apache.commons.math3.genetics.ListPopulationTest::testIterator: junit.framework.AssertionFailedError: Expected exception: java.lang.UnsupportedOperationException
- Postfix context signal: org.apache.commons.math3.genetics.ListPopulationTest::testIterator: junit.framework.AssertionFailedError: Expected exception: java.lang.UnsupportedOperationException

## Type Transitions

### Type Changed (Prefix → Postfix)

- Checking -> Algorithm/Method: 7
  - Bugs: Closure-140, JacksonXml-3, Jsoup-12, Jsoup-28, Lang-60, Time-14, Time-2
- Function/Class/Object -> Algorithm/Method: 1
  - Bugs: Collections-21 (no family match)
- Algorithm/Method -> Function/Class/Object: 1
  - Bugs: Collections-24 (no alt overlap, no family match)
- Checking -> Function/Class/Object: 1
  - Bugs: Compress-33 (no family match)
- Algorithm/Method -> Interface/O-O Messages: 1
  - Bugs: JacksonCore-24 (no alt overlap, no family match)
- Checking -> Assignment/Initialization: 1
  - Bugs: JxPath-22
- Checking -> Interface/O-O Messages: 1
  - Bugs: Math-34 (no alt overlap, no family match)
- Algorithm/Method -> Assignment/Initialization: 1
  - Bugs: Mockito-26

### Type Unchanged

- Checking -> Checking: 15
  - Bugs: Chart-10, Chart-13, Chart-17, Cli-17, Cli-32, Closure-143, Codec-3, Compress-15, Compress-27, Compress-44, Csv-1, Gson-7, Lang-27, Lang-43, Mockito-2
- Algorithm/Method -> Algorithm/Method: 11
  - Bugs: Cli-15, Closure-25, Codec-15, Collections-3, Csv-13, Gson-14, JacksonCore-16, JxPath-20, Math-56, Time-25, Time-27
- Assignment/Initialization -> Assignment/Initialization: 3
  - Bugs: Codec-16, JacksonDatabind-111, JacksonDatabind-24
- Function/Class/Object -> Function/Class/Object: 1
  - Bugs: JacksonXml-6
