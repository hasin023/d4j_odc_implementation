# Batch Study Analysis

- Created: `2026-07-10T19:01:43+00:00`
- Total pairs: **44**
- Projects covered: **17**
- Type changed: **12** (27.3%)
- Type unchanged: **32** (72.7%)
- No alternative overlap: **2** (4.5%)
- No family match: **3** (6.8%)
- Family match: **41** (93.2%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **44** of 44
- Capability: 37 (84.1%)
- Reliability: 7 (15.9%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **43/44** (97.7%)
- Kappa: 0.9197
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 16
- Capability × Checking: 14
- Reliability × Checking: 5
- Capability × Function/Class/Object: 4
- Capability × Assignment/Initialization: 3
- Reliability × Algorithm/Method: 2

## Alternative Match Cases (Type Changed)

### JacksonCore-24
- Type shift: Checking -> Function/Class/Object.
- Comparison detail: Post-fix primary 'Function/Class/Object' found in pre-fix alternative types
- Prefix reasoning summary: The stack traces show JsonParseException being thrown from ParserMinimalBase._reportError. The bug report identifies this as a design goal to use InputCoercionException instead. This is a 'Checking' defect because the logic for validating the numeric range is present, but the error handling mechanism (the exception type) is incorrect.
- Postfix reasoning summary: The bug is a requested design improvement to the exception hierarchy. The existing code uses a generic exception, and the fix introduces a new, more specific exception type to satisfy a requirement for better error metadata. This is a structural change to the API/contract of the error handling mechanism.
- Prefix context signal: com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)
- Postfix context signal: com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)

### Cli-17
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and test failure confirm that the parser continues to process tokens when it should stop. This is a procedural logic error in the parsing algorithm.
- Postfix reasoning summary: The bug is a failure to correctly implement the 'stopAtNonOption' requirement. The parser identifies the non-option character but does not stop, which is a failure in the conditional logic (Checking).
- Prefix context signal: org.apache.commons.cli.PosixParserTest::testStopBursting: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2
- Postfix context signal: org.apache.commons.cli.PosixParserTest::testStopBursting: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2

### Compress-15
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug report explicitly states that ZipArchiveInputStream and ZipFile produce different representations for the same entry (null vs empty string comment), and the test case confirms that these should be treated as equal. The fix requires updating the equals() method to handle this normalization, which is a local algorithmic correction.
- Postfix reasoning summary: The bug report and test failure confirm that the equality logic is too strict regarding null vs empty comments. This is a validation/predicate logic error within the equals() method.
- Prefix context signal: org.apache.commons.compress.archivers.zip.ZipArchiveEntryTest::testNullCommentEqualsEmptyComment: junit.framework.AssertionFailedError: expected:<foo> but was:<foo>
- Postfix context signal: org.apache.commons.compress.archivers.zip.ZipArchiveEntryTest::testNullCommentEqualsEmptyComment: junit.framework.AssertionFailedError: expected:<foo> but was:<foo>

### Jsoup-28
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and failing tests demonstrate that `Entities.unescape` incorrectly treats substrings like '&num' as entities. This indicates a failure in the validation logic (Checking) that determines whether a sequence starting with '&' is a valid entity. The fix requires adding a check to ensure the entity is properly terminated or valid.
- Postfix reasoning summary: The bug is a classic case of an incorrect algorithmic approach (regex-based parsing) for a task that requires context-aware parsing (HTML entity decoding). The fix replaces the flawed algorithm with a correct one (tokenization).
- Prefix context signal: org.jsoup.nodes.EntitiesTest::unescape: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>
- Postfix context signal: org.jsoup.nodes.EntitiesTest::unescape: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>

### Mockito-26
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The failure is a classic type mismatch in a factory-like method that returns default values for primitives. Since the code fails to return the correct type for 'double', the logic within the method is incomplete.
- Postfix reasoning summary: The bug is a classic initialization error where the wrong type (Integer) was assigned to a map entry intended for a double primitive. This is a local assignment issue that does not require algorithmic changes or structural design changes.
- Prefix context signal: org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')
- Postfix context signal: org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')

### Math-34
- Type shift: Checking -> Interface/O-O Messages.
- Comparison detail: Post-fix primary 'Interface/O-O Messages' found in pre-fix alternative types
- Prefix reasoning summary: The defect is a failure to enforce an access constraint (immutability of the iterator). This is a classic validation/checking issue where the code fails to validate the operation (removal) against the expected contract (read-only).
- Postfix reasoning summary: The defect is a violation of the encapsulation contract where an internal mutable structure is exposed via an iterator. This is an Interface/O-O Messages issue because the component's public interface (iterator) does not enforce the expected immutability contract, leading to unexpected behavior in the client code.
- Prefix context signal: org.apache.commons.math3.genetics.ListPopulationTest::testIterator: junit.framework.AssertionFailedError: Expected exception: java.lang.UnsupportedOperationException
- Postfix context signal: org.apache.commons.math3.genetics.ListPopulationTest::testIterator: junit.framework.AssertionFailedError: Expected exception: java.lang.UnsupportedOperationException

### Cli-32
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The code uses a loop to find a wrap position. The condition 'pos <= text.length()' is incorrect because 'text.charAt(pos)' is evaluated inside the loop. If 'pos' equals 'text.length()', the access is out of bounds. This is a classic boundary check error.
- Postfix reasoning summary: The defect is a procedural error in the findWrapPos method where an incorrect loop condition leads to an out-of-bounds access. The fix involves removing the erroneous loop, which is a correction of the algorithmic strategy for finding the wrap position.
- Prefix context signal: org.apache.commons.cli.HelpFormatterTest::testRenderWrappedTextWordCut: java.lang.StringIndexOutOfBoundsException: String index out of range: 12
- Postfix context signal: org.apache.commons.cli.HelpFormatterTest::testRenderWrappedTextWordCut: java.lang.StringIndexOutOfBoundsException: String index out of range: 12

### JxPath-22
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Pre-fix primary 'Checking' found in post-fix alternative types
- Prefix reasoning summary: The failure is a direct result of missing predicate logic (checking for empty string in addition to null) when determining the namespace of a node. This is a classic 'Checking' defect.
- Postfix reasoning summary: The defect is a classic case of incorrect state initialization/representation (empty string vs null) for a namespace URI. This is an Assignment/Initialization issue because the value returned by the method is incorrect for the system's internal contract.
- Prefix context signal: org.apache.commons.jxpath.ri.model.JXPath154Test::testInnerEmptyNamespaceDOM: junit.framework.ComparisonFailure: expected:</b:foo[1]/[test[1]]> but was:</b:foo[1]/[node()[2]]>
- Postfix context signal: org.apache.commons.jxpath.ri.model.JXPath154Test::testInnerEmptyNamespaceDOM: junit.framework.ComparisonFailure: expected:</b:foo[1]/[test[1]]> but was:</b:foo[1]/[node()[2]]>

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

## Type Changed (No Alternative Overlap)

### JacksonXml-3
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Checking' vs 'Assignment/Initialization')
- Prefix reasoning summary: The bug is a classic 'Checking' defect where a conditional predicate (the check for valid tokens in nextTextValue) is missing or incorrect, preventing the method from returning the correct value for attributes.
- Postfix reasoning summary: The fix diff shows that the buggy code was missing a return statement for the XML_ATTRIBUTE_VALUE case, which is a classic assignment/initialization error where the expected value is not correctly propagated.
- Prefix context signal: com.fasterxml.jackson.dataformat.xml.stream.XmlParserNextXxxTest::testXmlAttributesWithNextTextValue: junit.framework.ComparisonFailure: expected:<7> but was:<null>
- Postfix context signal: com.fasterxml.jackson.dataformat.xml.stream.XmlParserNextXxxTest::testXmlAttributesWithNextTextValue: junit.framework.ComparisonFailure: expected:<7> but was:<null>

### Closure-140
- Type shift: Checking -> Function/Class/Object.
- Comparison detail: No match: pre-fix 'Checking' (Control and Data Flow) vs post-fix 'Function/Class/Object' (Structural)
- Prefix reasoning summary: The error message explicitly states that reportCodeChange() was called when nothing changed. This is a classic 'Checking' defect where the guard condition (checking if a change actually occurred) is missing or incorrect before the side-effect (reporting the change) is triggered.
- Postfix reasoning summary: The failure is a direct result of the compiler's inability to handle empty modules during cross-module optimization. The fix enforces a structural invariant (all modules must contain at least one input) which is a design-level correction to ensure the compiler's internal state remains consistent during optimization passes.
- Prefix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed
- Postfix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed

## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Checking: 3
  - Bugs: Cli-17, Compress-15, Lang-43
- Checking -> Algorithm/Method: 3
  - Bugs: Cli-32, Jsoup-28, Lang-60
- Checking -> Function/Class/Object: 2
  - Bugs: Closure-140 (no alt overlap, no family match), JacksonCore-24 (no family match)
- Checking -> Assignment/Initialization: 2
  - Bugs: JacksonXml-3 (no alt overlap), JxPath-22
- Checking -> Interface/O-O Messages: 1
  - Bugs: Math-34 (no family match)
- Algorithm/Method -> Assignment/Initialization: 1
  - Bugs: Mockito-26

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 14
  - Bugs: Chart-10, Cli-15, Closure-25, Codec-15, Collections-3, Csv-13, Gson-14, JacksonCore-16, Jsoup-12, JxPath-20, Math-56, Time-14, Time-25, Time-27
- Checking -> Checking: 11
  - Bugs: Chart-13, Chart-17, Closure-143, Codec-3, Compress-27, Compress-44, Csv-1, Gson-7, Lang-27, Mockito-2, Time-2
- Function/Class/Object -> Function/Class/Object: 4
  - Bugs: Collections-21, Collections-24, Compress-33, JacksonXml-6
- Assignment/Initialization -> Assignment/Initialization: 3
  - Bugs: Codec-16, JacksonDatabind-111, JacksonDatabind-24
