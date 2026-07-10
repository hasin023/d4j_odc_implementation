# Batch Study Analysis

- Created: `2026-07-10T19:56:52+00:00`
- Total pairs: **44**
- Projects covered: **17**
- Type changed: **39** (88.6%)
- Type unchanged: **5** (11.4%)
- No alternative overlap: **39** (88.6%)
- No family match: **0** (0.0%)
- Family match: **44** (100.0%)

## Alternative Match Cases (Type Changed)

- No qualifying cases found.
## Type Changed (No Alternative Overlap)

### JxPath-20
- Type shift: Incorrect operator precedence or evaluation logic for relational expressions -> Incorrect argument order in method call.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect operator precedence or evaluation logic for relational expressions' vs 'Incorrect argument order in method call')
- Prefix reasoning summary: The bug report and failing test indicate that JXPath fails to correctly evaluate relational expressions involving variables when arithmetic operations are present. The failure in 'testComplexOperationWithVariables' ($a + $b <= $c) suggests that the expression parser or evaluator is not correctly handling the order of operations or the types resulting from the arithmetic sub-expression when compared against the right-hand side. Given the JIRA description, the issue likely stems from how the engine handles the evaluation of the left-hand side (LHS) versus the right-hand side (RHS) when one or both involve iterators or specific variable types, leading to an incorrect boolean result.
- Postfix reasoning summary: The bug occurred in the CoreOperationRelationalExpression class when handling relational operations involving an Iterator on the right-hand side. The original code incorrectly passed the arguments to the 'containsMatch' method by swapping the 'left' (non-Iterator) and 'right' (Iterator) objects, effectively treating the non-Iterator as the iterator to be traversed. The fix involved correcting the argument order and implementing a specific 'containsMatch' method that correctly handles a single value compared against an Iterator.
- Prefix context signal: org.apache.commons.jxpath.ri.compiler.JXPath149Test::testComplexOperationWithVariables: junit.framework.AssertionFailedError: Evaluating <$a + $b <= $c> expected:<true> but was:<false>
- Postfix context signal: org.apache.commons.jxpath.ri.compiler.JXPath149Test::testComplexOperationWithVariables: junit.framework.AssertionFailedError: Evaluating <$a + $b <= $c> expected:<true> but was:<false>

### Chart-10
- Type shift: Improper HTML character escaping -> Improper Output Encoding.
- Comparison detail: Family match only: both 'None' but types differ ('Improper HTML character escaping' vs 'Improper Output Encoding')
- Prefix reasoning summary: The test failure indicates that the tool tip generator is failing to escape double quotes within the tool tip string when generating HTML attributes. The expected output contains '&quot;' for the double quotes, while the actual output contains raw double quotes, which breaks the HTML attribute structure. This indicates a failure to properly sanitize or encode special characters for HTML output.
- Postfix reasoning summary: The code failed to escape special characters in the toolTipText string before embedding it into an HTML attribute. As a result, characters like double quotes were rendered literally in the HTML output, which violates HTML attribute syntax and causes the test to fail when it expects HTML-encoded entities (e.g., &quot;). The fix introduces a call to an HTML escaping utility to ensure the string is safe for inclusion in an HTML attribute.
- Prefix context signal: org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">
- Postfix context signal: org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">

### Chart-13
- Type shift: invalid range construction due to negative width calculation -> invalid argument range calculation.
- Comparison detail: Family match only: both 'None' but types differ ('invalid range construction due to negative width calculation' vs 'invalid argument range calculation')
- Prefix reasoning summary: The error occurs in BorderArrangement.arrangeFF, where a new Range object is created using 'constraint.getWidth() - w[2]' as the upper bound. When the width of the left block (w[2]) exceeds the total available width defined by the constraint, the resulting upper bound becomes negative. Since the Range constructor enforces that the lower bound (0.0) must be less than or equal to the upper bound, this negative value triggers an IllegalArgumentException.
- Postfix reasoning summary: The bug occurs because the code calculates a range for a layout constraint using a subtraction that can result in a negative value. Specifically, in BorderArrangement.java, the upper bound of a Range object is calculated as 'constraint.getWidth() - w[2]'. If the width of the left block (w[2]) exceeds the total available width, this calculation produces a negative number. The Range constructor explicitly throws an IllegalArgumentException if the lower bound (0.0) is greater than the upper bound, which is exactly what happens here. The fix correctly uses Math.max(..., 0.0) to ensure the upper bound is never negative, preventing the invalid range state.
- Prefix context signal: org.jfree.chart.block.junit.BorderArrangementTests::testSizingWithWidthConstraint: java.lang.IllegalArgumentException: Range(double, double): require lower (0.0) <= upper (-2.3000000000000007).
- Postfix context signal: org.jfree.chart.block.junit.BorderArrangementTests::testSizingWithWidthConstraint: java.lang.IllegalArgumentException: Range(double, double): require lower (0.0) <= upper (-2.3000000000000007).

### Cli-15
- Type shift: Incorrect default argument handling logic -> logic error in default value handling.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect default argument handling logic' vs 'logic error in default value handling')
- Prefix reasoning summary: The bug occurs because the command-line parser fails to merge user-provided arguments with default values when the number of provided arguments is less than the maximum allowed. The evidence shows that when an option is configured with multiple default values and a maximum argument count, providing fewer arguments than the maximum causes the parser to ignore the remaining default values instead of appending them to the user-provided list. This indicates a flaw in the logic responsible for populating the argument list when the user input is partial.
- Postfix reasoning summary: The bug occurs because the command-line parser fails to merge default values with user-provided arguments when the number of provided arguments is less than the maximum allowed but greater than zero. The original implementation only considered default values if the user provided no arguments at all. The fix modifies the logic to check if the number of provided values is less than the number of available default values, and if so, appends the remaining default values to the user-provided list.
- Prefix context signal: org.apache.commons.cli2.bug.BugCLI158Test::testSingleOptionSingleArgument: junit.framework.ComparisonFailure: expected:<[1[, 1000]]> but was:<[1[]]>
- Postfix context signal: org.apache.commons.cli2.bug.BugCLI158Test::testSingleOptionSingleArgument: junit.framework.ComparisonFailure: expected:<[1[, 1000]]> but was:<[1[]]>

### Cli-17
- Type shift: Incorrect logic in command-line argument parsing -> Incorrect control flow logic.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect logic in command-line argument parsing' vs 'Incorrect control flow logic')
- Prefix reasoning summary: The PosixParser fails to correctly implement the 'stopAtNonOption' behavior. When parsing a burst token (e.g., '-azc'), if the parser encounters a character that does not correspond to a valid option, it should stop processing the current token and treat the remainder as a non-option argument. Instead, the parser continues to process the remaining characters in the burst token, leading to an incorrect number of arguments being returned in the command line object.
- Postfix reasoning summary: The PosixParser was designed to stop processing tokens when a non-option character is encountered if the 'stopAtNonOption' flag is set. However, the original implementation processed the remaining part of the token but failed to terminate the loop, causing it to continue processing subsequent characters as if they were options. The fix introduces a 'break' statement to correctly exit the loop once the non-option segment is handled, ensuring the parser stops as intended.
- Prefix context signal: org.apache.commons.cli.PosixParserTest::testStopBursting: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2
- Postfix context signal: org.apache.commons.cli.PosixParserTest::testStopBursting: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2

### Closure-140
- Type shift: spurious state change notification -> incorrect state management in module processing.
- Comparison detail: Family match only: both 'None' but types differ ('spurious state change notification' vs 'incorrect state management in module processing')
- Prefix reasoning summary: The test failure indicates that the compiler's 'reportCodeChange()' method was invoked during a transformation pass even though the resulting AST remained identical to the original. In the context of 'CrossModuleCodeMotion', the compiler logic incorrectly identifies a need to move code or update the module structure when encountering empty modules, triggering a change notification that is not actually reflected in the final code state. This violates the compiler's internal contract that 'reportCodeChange()' should only be called when a meaningful modification to the AST occurs.
- Postfix reasoning summary: The bug occurs because the compiler fails to handle empty JS modules correctly during cross-module code motion. When a module is empty, the compiler's internal logic for tracking code changes or finding AST roots becomes inconsistent, leading to false positives in the test suite (reporting a code change when none occurred). The fix introduces a 'fillEmptyModules' method that ensures every module has at least one placeholder file, preventing the compiler from encountering empty module states that cause logic errors in subsequent passes.
- Prefix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed
- Postfix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed

### Closure-143
- Type shift: Input validation logic error -> input validation and logic error.
- Comparison detail: Family match only: both 'None' but types differ ('Input validation logic error' vs 'input validation and logic error')
- Prefix reasoning summary: The code in AbstractCommandLineRunner.createDefineReplacements attempts to parse command-line define flags by checking if they can be parsed as doubles. If parsing fails, it throws a RuntimeException, effectively rejecting any string-based definitions or complex values that do not conform to a numeric format. The stack trace confirms that valid string definitions (like FOO="x'") trigger this exception because the parser is too restrictive and lacks a fallback mechanism to handle non-numeric string literals.
- Postfix reasoning summary: The bug consists of two distinct issues. First, the command-line argument parser for the '--define' flag was overly restrictive, only accepting single-quoted strings and failing on double-quoted strings. The fix updated the parsing logic to explicitly check for and handle double-quoted strings. Second, the 'RemoveConstantExpressions' pass was incorrectly identifying expressions as having no side effects. It failed to account for 'NEW' and 'CALL' expressions, which can have side effects even if they are not assigned to anything. The fix updated the condition to include these node types, ensuring they are not incorrectly removed by the compiler.
- Prefix context signal: com.google.javascript.jscomp.CommandLineRunnerTest::testDefineFlag3: java.lang.RuntimeException: --define flag syntax invalid: FOO="x'"
- Postfix context signal: com.google.javascript.jscomp.CommandLineRunnerTest::testDefineFlag3: java.lang.RuntimeException: --define flag syntax invalid: FOO="x'"

### Closure-25
- Type shift: Type Inference Failure -> Type Inference Logic Error.
- Comparison detail: Family match only: both 'None' but types differ ('Type Inference Failure' vs 'Type Inference Logic Error')
- Prefix reasoning summary: The bug occurs because the type inference engine fails to propagate type information backwards when a function is invoked as a constructor using the 'new' keyword. While standard function calls correctly infer the expected object structure from the parameter type, the 'new' operator bypasses this inference logic, resulting in an empty object type instead of the expected record type. This indicates a missing or incomplete implementation in the type inference pass specifically for constructor invocations.
- Postfix reasoning summary: The bug occurs because the type inference engine fails to perform backwards inference when a constructor is invoked. In the buggy code, the `traverseNew` method did not correctly propagate type information from the constructor call site to the arguments. The fix introduces a call to `backwardsInferenceFromCallSite` and ensures that children are traversed correctly, allowing the compiler to infer the expected object structure (e.g., properties of an anonymous object) when passed as an argument to a constructor.
- Prefix context signal: com.google.javascript.jscomp.TypeInferenceTest::testBackwardsInferenceNew: junit.framework.ComparisonFailure: expected:<{[foo: (number|undefined)]}> but was:<{[]}>
- Postfix context signal: com.google.javascript.jscomp.TypeInferenceTest::testBackwardsInferenceNew: junit.framework.ComparisonFailure: expected:<{[foo: (number|undefined)]}> but was:<{[]}>

### Codec-15
- Type shift: incorrect algorithm logic -> Incorrect algorithm implementation of Soundex HW rule.
- Comparison detail: Family match only: both 'None' but types differ ('incorrect algorithm logic' vs 'Incorrect algorithm implementation of Soundex HW rule')
- Prefix reasoning summary: The Soundex algorithm requires that consonants mapping to the same code group, when separated by 'H' or 'W', should be treated as a single consonant. The current implementation incorrectly handles the sequence of characters, specifically failing to correctly identify when a consonant should be ignored based on the presence of 'H' or 'W' separators. The test case 'yhwdyt' expects 'Y330' because the 'h' and 'w' act as separators between consonants that map to the same code, but the implementation fails to correctly suppress the redundant code, resulting in 'Y300'.
- Postfix reasoning summary: The Soundex algorithm specifies that if two characters mapping to the same code are separated by 'H' or 'W', the second character should be ignored. The original implementation only checked the immediate predecessor and the character before that, failing to account for cases where multiple 'H' or 'W' characters might separate the consonants. The fix replaces this limited check with a loop that traverses backwards from the current character, checking for the same mapping code while skipping any 'H' or 'W' characters encountered, which correctly implements the rule.
- Prefix context signal: org.apache.commons.codec.language.SoundexTest::testHWRuleEx1: junit.framework.AssertionFailedError: expected:<Y3[3]0> but was:<Y3[0]0>
- Postfix context signal: org.apache.commons.codec.language.SoundexTest::testHWRuleEx1: junit.framework.AssertionFailedError: expected:<Y3[3]0> but was:<Y3[0]0>

### Collections-21
- Type shift: Incorrect subList implementation -> API contract violation / Inconsistent state management.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect subList implementation' vs 'API contract violation / Inconsistent state management')
- Prefix reasoning summary: The SetUniqueList class fails to correctly implement the subList method. According to the Java List contract, a subList should be a view of the parent list. In this implementation, the subList returned is not properly synchronized with the parent SetUniqueList's uniqueness constraints and internal state. When modifications are performed on the subList, they do not correctly propagate to the parent list or maintain the required set-like uniqueness properties, leading to inconsistent states between the subList and the parent list.
- Postfix reasoning summary: The SetUniqueList class maintains both a list and a set to ensure uniqueness. When subList() is called, the returned sub-list is a new SetUniqueList instance that is backed by the parent list. However, modifications to this sub-list do not correctly synchronize with the parent's internal set or handle the complex structural requirements of maintaining uniqueness across the entire parent list. Because implementing full synchronization for sub-lists is error-prone and violates the expected behavior of a list decorator, the fix was to return an unmodifiable view of the sub-list, preventing structural modifications that would lead to inconsistent states.
- Prefix context signal: org.apache.commons.collections4.list.SetUniqueListTest::testSubListIsUnmodifiable: junit.framework.AssertionFailedError: subList should be unmodifiable
- Postfix context signal: org.apache.commons.collections4.list.SetUniqueListTest::testSubListIsUnmodifiable: junit.framework.AssertionFailedError: subList should be unmodifiable

### Compress-15
- Type shift: Inconsistent Object Equality -> Logical inconsistency in object equality.
- Comparison detail: Family match only: both 'None' but types differ ('Inconsistent Object Equality' vs 'Logical inconsistency in object equality')
- Prefix reasoning summary: The defect arises because ZipArchiveEntry instances created from different sources (ZipArchiveInputStream vs ZipFile) treat null and empty string comments differently during equality checks. The test case demonstrates that an entry with a null comment is not considered equal to an entry with an empty string comment, despite them being semantically equivalent in the context of ZIP file metadata. This inconsistency causes failures when comparing entries retrieved from different ZIP processing mechanisms.
- Postfix reasoning summary: The bug was caused by an overly strict implementation of the equals() method in the ZipArchiveEntry class. Specifically, it treated a null comment and an empty string comment as distinct values, causing two entries that were semantically identical to be considered unequal. The fix involved normalizing both comments to empty strings before performing the equality comparison, ensuring that null and empty comments are treated as equivalent.
- Prefix context signal: org.apache.commons.compress.archivers.zip.ZipArchiveEntryTest::testNullCommentEqualsEmptyComment: junit.framework.AssertionFailedError: expected:<foo> but was:<foo>
- Postfix context signal: org.apache.commons.compress.archivers.zip.ZipArchiveEntryTest::testNullCommentEqualsEmptyComment: junit.framework.AssertionFailedError: expected:<foo> but was:<foo>

### Compress-27
- Type shift: incorrect input validation logic -> Overly restrictive input validation.
- Comparison detail: Family match only: both 'None' but types differ ('incorrect input validation logic' vs 'Overly restrictive input validation')
- Prefix reasoning summary: The code in TarUtils.parseOctal attempts to trim trailing NULs and spaces from a byte buffer before parsing it as an octal number. The logic uses a while loop to decrement the 'end' pointer as long as the character is a NUL or a space. However, if the buffer consists entirely of NULs or spaces (or a mix thereof), the 'end' pointer eventually equals the 'start' pointer. The code then throws an IllegalArgumentException because it assumes that an empty buffer after trimming is invalid. This fails for valid TAR header fields that are intended to be empty or zero-filled, as demonstrated by the failing test case which provides a buffer of {' ', 0} and expects a result of 0.
- Postfix reasoning summary: The code was designed to parse octal values from a byte buffer, but it included a validation check that threw an IllegalArgumentException if the buffer contained only spaces or NUL bytes after trimming. This logic failed for valid TAR entries where fields (like username or group) might be empty or contain only padding characters, which are represented as all-zero or all-space buffers. The fix removed this mandatory check, allowing the parser to return 0 for such cases instead of crashing.
- Prefix context signal: org.apache.commons.compress.archivers.tar.TarUtilsTest::testParseOctal: java.lang.IllegalArgumentException: Invalid byte 32 at offset 1 in ' {NUL}' len=2
- Postfix context signal: org.apache.commons.compress.archivers.tar.TarUtilsTest::testParseOctal: java.lang.IllegalArgumentException: Invalid byte 32 at offset 1 in ' {NUL}' len=2

### Compress-33
- Type shift: Missing feature implementation -> Missing feature support for file format signature.
- Comparison detail: Family match only: both 'None' but types differ ('Missing feature implementation' vs 'Missing feature support for file format signature')
- Prefix reasoning summary: The CompressorStreamFactory class fails to detect and instantiate a DeflateCompressorInputStream for streams that contain a zlib header. The test case 'testDetection' expects the factory to identify 'bla.tar.deflatez' as a deflate stream, but the factory's detection logic lacks the necessary signature check for zlib-wrapped deflate streams, resulting in a 'No Compressor found' exception.
- Postfix reasoning summary: The system failed to detect and decompress deflate streams that included a zlib header. The CompressorStreamFactory lacked the logic to identify the specific byte signature associated with zlib-compressed data. The fix involved implementing a 'matches' method in the DeflateCompressorInputStream class to identify the zlib header bytes and updating the CompressorStreamFactory to utilize this detection logic during the stream creation process.
- Prefix context signal: org.apache.commons.compress.compressors.DetectCompressorTestCase::testDetection: org.apache.commons.compress.compressors.CompressorException: No Compressor found for the stream signature.
- Postfix context signal: org.apache.commons.compress.compressors.DetectCompressorTestCase::testDetection: org.apache.commons.compress.compressors.CompressorException: No Compressor found for the stream signature.

### Csv-13
- Type shift: Incorrect data escaping logic -> incorrect output formatting logic.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect data escaping logic' vs 'incorrect output formatting logic')
- Prefix reasoning summary: The issue arises because the CSVPrinter incorrectly applies escaping rules to the configured 'nullString' value. When the printer encounters a null value, it replaces it with the configured nullString (e.g., '\N'), but then proceeds to pass this string through the same escaping logic used for regular data fields. This causes the null representation to be double-escaped or incorrectly modified (e.g., '\N' becoming '\\N'), which violates the expected format for MySQL compatibility. The tests fail because the output contains these extra escape characters instead of the literal null representation.
- Postfix reasoning summary: The bug occurred because the CSVPrinter was applying escape characters to the 'nullString' representation (e.g., '\N') when it should have been treated as a literal value. The fix involved updating the CSVPrinter to explicitly check if an object is null and, if so, append the nullString directly without passing it through the escaping or quoting logic. Additionally, the default nullString for the MySQL format was missing, which was corrected in the CSVFormat class.
- Prefix context signal: org.apache.commons.csv.CSVPrinterTest::testMySqlNullOutput: junit.framework.AssertionFailedError: expected:<"NULL"	[NULL]
- Postfix context signal: org.apache.commons.csv.CSVPrinterTest::testMySqlNullOutput: junit.framework.AssertionFailedError: expected:<"NULL"	[NULL]

### Csv-1
- Type shift: incorrect line counting logic -> Incorrect line-ending detection logic.
- Comparison detail: Family match only: both 'None' but types differ ('incorrect line counting logic' vs 'Incorrect line-ending detection logic')
- Prefix reasoning summary: The bug report and failing test indicate that the CSV parser fails to increment the line number when encountering a carriage return (CR) as a line separator. The test expects the line number to increment after reading a record terminated by '\r', but the parser remains at 0. This confirms that the internal line counter logic is not correctly identifying or processing CR as a valid line terminator, leading to an off-by-one error in line tracking.
- Postfix reasoning summary: The bug was caused by the ExtendedBufferedReader only incrementing the line counter when encountering a newline character ('\n'). This failed to account for carriage return ('\r') characters as valid line terminators, which is required for certain CSV formats. The fix updated the read() method to increment the line counter for both '\r' and '\n' (while ensuring that a CRLF sequence is not double-counted by checking the previous character).
- Prefix context signal: org.apache.commons.csv.CSVParserTest::testGetLineNumberWithCR: junit.framework.AssertionFailedError: expected:<1> but was:<0>
- Postfix context signal: org.apache.commons.csv.CSVParserTest::testGetLineNumberWithCR: junit.framework.AssertionFailedError: expected:<1> but was:<0>

### Gson-7
- Type shift: Incorrect state handling in JSON parser -> Incomplete state handling in JSON parser.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect state handling in JSON parser' vs 'Incomplete state handling in JSON parser')
- Prefix reasoning summary: The issue arises because the JsonReader's nextInt() and nextLong() methods fail to correctly handle unquoted keys or values that are numeric in nature but are treated as strings by the parser. When the parser encounters an unquoted token, it identifies it as a string (PEEKED_UNQUOTED) rather than a number. The subsequent call to nextInt() or nextLong() expects a numeric token type and throws an IllegalStateException when it encounters a STRING token instead. This is a regression in the streaming API's ability to handle lenient JSON formats where keys or values might not be quoted.
- Postfix reasoning summary: The bug occurs because the JsonReader's nextLong() and nextInt() methods fail to handle the PEEKED_UNQUOTED state when parsing numeric values. In JSON, keys in maps are often unquoted, and when Gson attempts to deserialize these into numeric types (like Integer or Long), the parser encounters an unquoted string that represents a number. The original implementation only checked for PEEKED_NUMBER, PEEKED_SINGLE_QUOTED, and PEEKED_DOUBLE_QUOTED, causing it to throw an IllegalStateException when it encountered an unquoted numeric key. The fix adds logic to explicitly handle the PEEKED_UNQUOTED state by calling nextUnquotedValue() and then attempting to parse the resulting string as a number.
- Prefix context signal: com.google.gson.functional.MapTest::testMapDeserializationWithUnquotedLongKeys: com.google.gson.JsonSyntaxException: java.lang.IllegalStateException: Expected a long but was STRING at line 1 column 2 path $.
- Postfix context signal: com.google.gson.functional.MapTest::testMapDeserializationWithUnquotedLongKeys: com.google.gson.JsonSyntaxException: java.lang.IllegalStateException: Expected a long but was STRING at line 1 column 2 path $.

### JacksonCore-16
- Type shift: Incorrect state management in composite parser -> State management error in iterator/sequence.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect state management in composite parser' vs 'State management error in iterator/sequence')
- Prefix reasoning summary: The issue arises because JsonParserSequence, when switching from one delegate parser to another, unconditionally calls nextToken() on the new delegate. If the new delegate is already positioned at a valid token (as is the case when the parser was initialized with data and partially consumed), this extra call causes the sequence to skip the first token of the second parser. The test failure confirms this, as the sequence returns the value '3' instead of '2' when expected, indicating that the first token of the second parser was skipped.
- Postfix reasoning summary: The bug occurs in JsonParserSequence, which manages a sequence of JsonParsers. When switching from one parser to the next, the implementation was unconditionally calling nextToken() on the new delegate. If the new delegate was already positioned at a valid token (e.g., via hasCurrentToken()), calling nextToken() would skip that token, leading to data loss. The fix introduces a state flag (_suppressNextToken) to track whether the current delegate is already initialized at a token, ensuring that the sequence correctly returns the current token instead of advancing prematurely.
- Prefix context signal: com.fasterxml.jackson.core.json.ParserSequenceTest::testInitialized: junit.framework.AssertionFailedError: expected:<2> but was:<3>
- Postfix context signal: com.fasterxml.jackson.core.json.ParserSequenceTest::testInitialized: junit.framework.AssertionFailedError: expected:<2> but was:<3>

### JacksonDatabind-111
- Type shift: Incorrect Null Value Provider Initialization -> Inconsistent Null Value Provider Synchronization.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Null Value Provider Initialization' vs 'Inconsistent Null Value Provider Synchronization')
- Prefix reasoning summary: The issue arises during the deserialization of nested reference types (e.g., AtomicReference<AtomicReference<T>>). When the deserializer for the outer reference is created, it correctly handles the non-null case by creating a contextual deserializer for the inner type. However, the 'nullProvider' associated with the property is not updated to reflect the nested structure. Consequently, when a null value is encountered, the system falls back to a default null provider that returns a simple null or an incorrectly wrapped object, rather than the expected nested structure (e.g., an AtomicReference containing a null AtomicReference).
- Postfix reasoning summary: The defect arises because the deserialization logic for nested reference types (like AtomicReference<AtomicReference<T>>) fails to correctly propagate the null value provider when a new contextual deserializer is created. Specifically, when a property's deserializer is updated during the contextualization process, the corresponding null value provider is not updated to match, leading to a mismatch where the system uses a default null provider instead of the one associated with the specific nested type. The fix ensures that if the original deserializer and null provider were linked, the new contextual deserializer and the null provider remain synchronized, and it also updates the AtomicReferenceDeserializer to correctly use the nested deserializer's null value instead of returning an empty AtomicReference.
- Prefix context signal: com.fasterxml.jackson.databind.deser.jdk.JDKAtomicTypesDeserTest::testNullWithinNested: junit.framework.AssertionFailedError
- Postfix context signal: com.fasterxml.jackson.databind.deser.jdk.JDKAtomicTypesDeserTest::testNullWithinNested: junit.framework.AssertionFailedError

### JacksonDatabind-24
- Type shift: unintended side effect in configuration setter -> unintended side effect.
- Comparison detail: Family match only: both 'None' but types differ ('unintended side effect in configuration setter' vs 'unintended side effect')
- Prefix reasoning summary: The bug report and test evidence indicate that calling 'mapper.setDateFormat(DateFormat)' causes the ObjectMapper's configured TimeZone to be overwritten by the JVM's default TimeZone. The test 'testDateFormatConfig' explicitly asserts that setting a custom DateFormat should not alter the previously configured TimeZone of the mapper. The evidence suggests that the implementation of 'setDateFormat' incorrectly synchronizes or resets the mapper's global TimeZone state to the default system timezone, which is an unintended side effect that breaks existing configuration consistency.
- Postfix reasoning summary: The bug was introduced when the `BaseSettings` class was updated to automatically extract and apply the `TimeZone` from a provided `DateFormat` object whenever `setDateFormat` was called. This behavior caused the `ObjectMapper`'s configured `TimeZone` to be overwritten by the `TimeZone` of the `DateFormat` object, which is often the system default. The fix involved reverting this logic to ensure that the `ObjectMapper` retains its existing `TimeZone` configuration regardless of the `DateFormat` being set, thereby preserving the expected behavior from previous versions.
- Prefix context signal: com.fasterxml.jackson.databind.ser.TestConfig::testDateFormatConfig: junit.framework.AssertionFailedError: expected:<sun.util.calendar.ZoneInfo[id="America/Los_Angeles",offset=-28800000,dstSavings=3600000,useDaylight=true,transitions=185,lastRule=java.util.SimpleTimeZone[id=America/Los_Angeles,offset=-28800000,dstSavings=3600000,useDaylight=true,startYear=0,startMode=3,startMonth=2,startDay=8,startDayOfWeek=1,startTime=7200000,startTimeMode=0,endMode=3,endMonth=10,endDay=1,endDayOfWeek=1,endTime=7200000,endTimeMode=0]]> but was:<sun.util.calendar.ZoneInfo[id="GMT",offset=0,dstSavings=0,useDaylight=false,transitions=0,lastRule=null]>
- Postfix context signal: com.fasterxml.jackson.databind.ser.TestConfig::testDateFormatConfig: junit.framework.AssertionFailedError: expected:<sun.util.calendar.ZoneInfo[id="America/Los_Angeles",offset=-28800000,dstSavings=3600000,useDaylight=true,transitions=185,lastRule=java.util.SimpleTimeZone[id=America/Los_Angeles,offset=-28800000,dstSavings=3600000,useDaylight=true,startYear=0,startMode=3,startMonth=2,startDay=8,startDayOfWeek=1,startTime=7200000,startTimeMode=0,endMode=3,endMonth=10,endDay=1,endDayOfWeek=1,endTime=7200000,endTimeMode=0]]> but was:<sun.util.calendar.ZoneInfo[id="GMT",offset=0,dstSavings=0,useDaylight=false,transitions=0,lastRule=null]>

### Jsoup-12
- Type shift: Incomplete CSS selector parsing logic -> Incorrect Tokenization/Parsing Logic.
- Comparison detail: Family match only: both 'None' but types differ ('Incomplete CSS selector parsing logic' vs 'Incorrect Tokenization/Parsing Logic')
- Prefix reasoning summary: The CSS selector parser fails when encountering attribute selectors containing regex patterns (e.g., [attr~=regex]) if they are preceded by a combinator. The stack trace indicates a SelectorParseException occurring in the findElements method, which is responsible for identifying and parsing specific selector tokens. The parser logic does not correctly handle the '~=' operator within the attribute selector context when it follows a combinator, leading the parser to treat the remaining part of the query as an unexpected token.
- Postfix reasoning summary: The bug occurs because the CSS selector parser uses a simple 'consumeToAny' approach when processing sub-queries after a combinator. This approach fails to account for nested structures like attribute selectors containing brackets (e.g., [attr~=x|y]) or parentheses, causing the parser to prematurely terminate the sub-query at the first occurrence of a character that might be part of a combinator or a special token. The fix introduces a 'consumeSubQuery' method that correctly balances brackets and parentheses, ensuring the entire sub-query is captured as a single unit before the next combinator is processed.
- Prefix context signal: org.jsoup.select.SelectorTest::testByAttributeRegexCombined: org.jsoup.select.Selector$SelectorParseException: Could not parse query '=x|y]': unexpected token at '=x|y]'
- Postfix context signal: org.jsoup.select.SelectorTest::testByAttributeRegexCombined: org.jsoup.select.Selector$SelectorParseException: Could not parse query '=x|y]': unexpected token at '=x|y]'

### JxPath-22
- Type shift: Incorrect Namespace Handling in XPath Generation -> Incorrect Namespace URI Handling.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Namespace Handling in XPath Generation' vs 'Incorrect Namespace URI Handling')
- Prefix reasoning summary: The bug occurs because the asPath() method in the DOM node pointer implementation fails to correctly identify nodes that have an empty namespace URI (xmlns=""). When a node explicitly resets its namespace to an empty string, the current logic treats it as having a namespace, leading to incorrect path generation (e.g., using 'node()' instead of the element name) or infinite loops during prefix resolution. The evidence from the bug report and the failing test confirms that the logic needs to treat an empty namespace URI the same as a null namespace URI to correctly generate the XPath string.
- Postfix reasoning summary: The bug occurs because the DOMNodePointer class was returning an empty string (" ") for nodes that do not have a namespace, whereas the JXPath framework expects a null value to represent the absence of a namespace. This discrepancy caused the NamespaceResolver to fail or loop when attempting to resolve prefixes for nodes that were explicitly defined with an empty namespace (xmlns=""). The fix ensures that any empty string returned as a namespace URI is normalized to null, aligning the DOM model's behavior with the rest of the JXPath framework.
- Prefix context signal: org.apache.commons.jxpath.ri.model.JXPath154Test::testInnerEmptyNamespaceDOM: junit.framework.ComparisonFailure: expected:</b:foo[1]/[test[1]]> but was:</b:foo[1]/[node()[2]]>
- Postfix context signal: org.apache.commons.jxpath.ri.model.JXPath154Test::testInnerEmptyNamespaceDOM: junit.framework.ComparisonFailure: expected:</b:foo[1]/[test[1]]> but was:</b:foo[1]/[node()[2]]>

### Math-56
- Type shift: incorrect index calculation logic -> incorrect algorithm implementation.
- Comparison detail: Family match only: both 'None' but types differ ('incorrect index calculation logic' vs 'incorrect algorithm implementation')
- Prefix reasoning summary: The bug report and failing test indicate that the MultidimensionalCounter.getCounts(int) method produces incorrect multidimensional indices for certain unidimensional inputs. Specifically, the output shows that the last dimension index is being incorrectly calculated or truncated, as seen in the example where index 3 results in [0, 2] instead of [0, 3]. This suggests an off-by-one error or an incorrect modulo/division operation within the index conversion algorithm used to map a flat index back to multidimensional coordinates.
- Postfix reasoning summary: The bug was caused by an incorrect iterative calculation used to determine the final index in a multidimensional array mapping. The original implementation used a while loop to increment a counter until it reached the target index, which failed to correctly map the remaining offset. The fix replaced this flawed loop with a simple arithmetic subtraction (index - count), which correctly calculates the final dimension index based on the accumulated count.
- Prefix context signal: org.apache.commons.math.util.MultidimensionalCounterTest::testIterationConsistency: junit.framework.AssertionFailedError: Wrong multidimensional index for [3][2] expected:<3> but was:<2>
- Postfix context signal: org.apache.commons.math.util.MultidimensionalCounterTest::testIterationConsistency: junit.framework.AssertionFailedError: Wrong multidimensional index for [3][2] expected:<3> but was:<2>

### Mockito-26
- Type shift: Type Mismatch in Default Value Return -> Incorrect primitive type mapping.
- Comparison detail: Family match only: both 'None' but types differ ('Type Mismatch in Default Value Return' vs 'Incorrect primitive type mapping')
- Prefix reasoning summary: The failing tests consistently show that when a mock is expected to return a primitive double (0.0), it is instead returning an integer (0). This indicates that the logic responsible for providing default return values for primitive types is incorrectly mapping or returning an integer type where a double is expected, leading to ClassCastExceptions or assertion failures when comparing the returned value against the expected double.
- Postfix reasoning summary: The bug was caused by an incorrect entry in the `primitiveValues` map within the `Primitives` utility class. Specifically, the entry for `double.class` was mapped to an integer `0` instead of a double `0D`. This caused type mismatch errors (ClassCastException) and assertion failures in tests expecting a double value when the framework attempted to retrieve default values for primitive types.
- Prefix context signal: org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')
- Postfix context signal: org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')

### Mockito-2
- Type shift: Input Validation Failure -> Missing Input Validation.
- Comparison detail: Family match only: both 'None' but types differ ('Input Validation Failure' vs 'Missing Input Validation')
- Prefix reasoning summary: The bug report and failing tests indicate that Mockito's verification methods (like 'after' and 'timeout') fail to validate that the provided duration is non-negative. The tests explicitly expect a 'FriendlyReminderException' when a negative duration is passed, but the current implementation allows these negative values to proceed, leading to incorrect verification behavior where verifications that should fail or throw exceptions instead pass incorrectly.
- Postfix reasoning summary: The bug was caused by the absence of input validation in the Timer class constructor. When negative duration values were passed to Mockito.timeout() or Mockito.after(), the system accepted them without verification, leading to incorrect verification behavior. The fix introduces a validation check in the Timer constructor that triggers a reporter exception if the provided duration is negative, ensuring that invalid configurations are caught early.
- Prefix context signal: org.mockito.internal.util.TimerTest::should_throw_friendly_reminder_exception_when_duration_is_negative: junit.framework.AssertionFailedError: It is forbidden to create timer with negative value of timer's duration.
- Postfix context signal: org.mockito.internal.util.TimerTest::should_throw_friendly_reminder_exception_when_duration_is_negative: junit.framework.AssertionFailedError: It is forbidden to create timer with negative value of timer's duration.

### Time-25
- Type shift: Incorrect Daylight Saving Time (DST) transition handling -> incorrect DST transition handling.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Daylight Saving Time (DST) transition handling' vs 'incorrect DST transition handling')
- Prefix reasoning summary: The failing tests indicate that during a DST transition (specifically the Moscow Autumn transition), the library incorrectly resolves the local time offset. The tests expect a +04:00 offset for a specific local time, but the system returns +03:00. This suggests that the logic within 'getOffsetFromLocal' fails to correctly identify the appropriate offset when a local time exists in an ambiguous period or during a transition, leading to an incorrect UTC conversion.
- Postfix reasoning summary: The bug occurs during Daylight Saving Time (DST) transitions where a local time is ambiguous (the 'overlap' period). The original implementation failed to consistently return the correct offset for these ambiguous times, leading to inconsistent behavior across different hemispheres. The fix introduces logic in 'DateTimeZone.getOffsetFromLocal' to explicitly check for previous transitions and adjust the offset to ensure the earlier instant (typically the daylight/summer time offset) is returned, standardizing the behavior as intended by the developers.
- Prefix context signal: org.joda.time.TestDateTimeZoneCutover::test_DateTime_constructor_Moscow_Autumn: junit.framework.ComparisonFailure: expected:<...10-28T02:30:00.000+0[4]:00> but was:<...10-28T02:30:00.000+0[3]:00>
- Postfix context signal: org.joda.time.TestDateTimeZoneCutover::test_DateTime_constructor_Moscow_Autumn: junit.framework.ComparisonFailure: expected:<...10-28T02:30:00.000+0[4]:00> but was:<...10-28T02:30:00.000+0[3]:00>

### Time-27
- Type shift: Incorrect parsing logic for ISO period formats -> Incorrect logic in composite formatter construction.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect parsing logic for ISO period formats' vs 'Incorrect logic in composite formatter construction')
- Prefix reasoning summary: The failing test case demonstrates that the standard ISO period formatter fails to parse a valid ISO 8601 duration string ('PT1003199059S') that contains a large number of seconds. The error occurs in the PeriodFormatter's parsing logic, which is unable to correctly handle the transition or the magnitude of the value provided in the string. Since the custom formatter (pfmt1) and the standard ISO formatter (pfmt2) are expected to handle this input, the failure indicates an issue in the underlying parsing implementation of the ISO period format.
- Postfix reasoning summary: The bug occurs because the PeriodFormatterBuilder fails to correctly handle the construction of composite formatters when a separator is present at the beginning of the element list. The fix introduces a conditional check to ensure that the separator is properly finished with the appropriate printer and parser components before returning the formatter. This indicates that the original implementation was incorrectly bypassing the necessary initialization steps for separators in certain configurations, leading to malformed parsing behavior for ISO-like period formats.
- Prefix context signal: org.joda.time.format.TestPeriodFormatterBuilder::testBug2495455: java.lang.IllegalArgumentException: Invalid format: "PT1003199059S" is malformed at "1003199059S"
- Postfix context signal: org.joda.time.format.TestPeriodFormatterBuilder::testBug2495455: java.lang.IllegalArgumentException: Invalid format: "PT1003199059S" is malformed at "1003199059S"

### Chart-17
- Type shift: Boundary condition error -> Boundary condition error in object cloning.
- Comparison detail: Family match only: both 'None' but types differ ('Boundary condition error' vs 'Boundary condition error in object cloning')
- Prefix reasoning summary: The bug occurs when cloning an empty TimeSeries object. The clone() method calls createCopy(0, getItemCount() - 1). When the series is empty, getItemCount() returns 0, resulting in a call to createCopy(0, -1). The createCopy method explicitly checks if end < start and throws an IllegalArgumentException if this condition is met. The code fails to handle the case where the series is empty, which is a valid state for a TimeSeries object.
- Postfix reasoning summary: The bug occurs because the clone() method attempts to copy a TimeSeries by calling createCopy(0, getItemCount() - 1). When the TimeSeries is empty, getItemCount() returns 0, resulting in a call to createCopy(0, -1). The createCopy method contains a validation check that throws an IllegalArgumentException if the end index is less than the start index, causing the cloning process to fail for empty series. The fix replaces this logic with a direct deep clone of the data list, bypassing the index-based validation entirely.
- Prefix context signal: org.jfree.data.time.junit.TimeSeriesTests::testBug1832432: java.lang.IllegalArgumentException: Requires start <= end.
- Postfix context signal: org.jfree.data.time.junit.TimeSeriesTests::testBug1832432: java.lang.IllegalArgumentException: Requires start <= end.

### Cli-32
- Type shift: off-by-one error -> Off-by-one error leading to index out of bounds.
- Comparison detail: Family match only: both 'None' but types differ ('off-by-one error' vs 'Off-by-one error leading to index out of bounds')
- Prefix reasoning summary: The code in HelpFormatter.findWrapPos uses a while loop condition 'pos <= text.length()' to check for characters in the string. When 'pos' equals 'text.length()', the subsequent call to 'text.charAt(pos)' attempts to access an index equal to the string's length, which is out of bounds for a zero-indexed string. This causes a StringIndexOutOfBoundsException. The logic should only check up to 'text.length() - 1' or ensure the index is strictly less than the length before accessing the character.
- Postfix reasoning summary: The code contained a while loop that attempted to scan for whitespace characters beyond the end of the string. The loop condition used 'pos <= text.length()' and then immediately called 'text.charAt(pos)', which causes a StringIndexOutOfBoundsException when 'pos' equals 'text.length()'. The fix removed this redundant and dangerous loop entirely, as the logic was intended to simply return the calculated wrap position if no whitespace was found, rather than searching for the next whitespace character beyond the specified width.
- Prefix context signal: org.apache.commons.cli.HelpFormatterTest::testRenderWrappedTextWordCut: java.lang.StringIndexOutOfBoundsException: String index out of range: 12
- Postfix context signal: org.apache.commons.cli.HelpFormatterTest::testRenderWrappedTextWordCut: java.lang.StringIndexOutOfBoundsException: String index out of range: 12

### Codec-16
- Type shift: Incorrect validation logic due to flawed alphabet definition -> Incorrect lookup table data.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect validation logic due to flawed alphabet definition' vs 'Incorrect lookup table data')
- Prefix reasoning summary: The Base32 class includes a validation check in its constructor that prevents the use of characters present in the alphabet as padding. The bug report indicates that the HEX_DECODE_TABLE incorrectly includes the value 32, which corresponds to the character 'W'. Because 'W' is erroneously considered part of the Base32 Hex alphabet, the constructor's validation logic (isInAlphabet(pad)) incorrectly flags 'W' as an invalid padding character, causing an IllegalArgumentException when a user attempts to use it.
- Postfix reasoning summary: The bug was caused by an erroneous entry in the HEX_DECODE_TABLE used by the Base32 codec. The table included the value '32' at an index corresponding to the character 'W', which caused the Base32 constructor to incorrectly identify 'W' as part of the alphabet. Consequently, when a user attempted to use 'W' as a padding character, the validation logic (which checks if the pad character is in the alphabet) threw an IllegalArgumentException. Removing the incorrect value from the lookup table resolved the issue.
- Prefix context signal: org.apache.commons.codec.binary.Base32Test::testCodec200: java.lang.IllegalArgumentException: pad must not be in alphabet or whitespace
- Postfix context signal: org.apache.commons.codec.binary.Base32Test::testCodec200: java.lang.IllegalArgumentException: pad must not be in alphabet or whitespace

### Codec-3
- Type shift: Incorrect parameter usage in string matching logic -> incorrect parameter in string matching logic.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect parameter usage in string matching logic' vs 'incorrect parameter in string matching logic')
- Prefix reasoning summary: The bug report explicitly identifies that the Double Metaphone implementation uses incorrect parameters in the 'contains' method within the 'handleG' function. Specifically, it uses a length of 4 instead of 3 when checking for the suffix 'IER'. This causes the algorithm to fail to match the intended substring, leading to incorrect phonetic encoding results as observed in the failing test case 'Angier' (expected 'ANJR', got 'ANKR').
- Postfix reasoning summary: The bug was identified as an incorrect length parameter passed to a 'contains' method within the 'handleG' logic of the Double Metaphone algorithm. The code was checking for a 4-character substring ('IER') when it should have been checking for a 3-character substring. This caused the algorithm to fail to match the intended pattern, leading to incorrect phonetic encoding for words like 'Angier'. The fix involved updating the length parameter from 4 to 3, which correctly aligns the substring search with the expected input.
- Prefix context signal: org.apache.commons.codec.language.DoubleMetaphone2Test::testDoubleMetaphoneAlternate: junit.framework.ComparisonFailure: Test [19]=Angier expected:<AN[J]R> but was:<AN[K]R>
- Postfix context signal: org.apache.commons.codec.language.DoubleMetaphone2Test::testDoubleMetaphoneAlternate: junit.framework.ComparisonFailure: Test [19]=Angier expected:<AN[J]R> but was:<AN[K]R>

### Collections-3
- Type shift: Incorrect Method Invocation -> incorrect method invocation.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Method Invocation' vs 'incorrect method invocation')
- Prefix reasoning summary: The bug report explicitly states that CollectionUtils.removeAll incorrectly invokes ListUtils.retainAll instead of ListUtils.removeAll. The failing test confirms this behavior: when removing elements 'A' and 'C' from a collection containing 'A', 'B', and 'C', the expected result is a collection containing only 'B' (size 1). The actual result size of 2 indicates that the method performed a retain operation (keeping 'A' and 'C') rather than a removal operation.
- Postfix reasoning summary: The bug report and the fix diff clearly indicate that the CollectionUtils.removeAll method was incorrectly calling ListUtils.retainAll instead of ListUtils.removeAll. This caused the method to return the intersection of the two collections rather than the difference, leading to an incorrect result size in the test case.
- Prefix context signal: org.apache.commons.collections.TestCollectionUtils::testRemoveAll: junit.framework.AssertionFailedError: expected:<1> but was:<2>
- Postfix context signal: org.apache.commons.collections.TestCollectionUtils::testRemoveAll: junit.framework.AssertionFailedError: expected:<1> but was:<2>

### Gson-14
- Type shift: Infinite recursion in type resolution -> Infinite recursion in generic type resolution.
- Comparison detail: Family match only: both 'None' but types differ ('Infinite recursion in type resolution' vs 'Infinite recursion in generic type resolution')
- Prefix reasoning summary: The defect is caused by the lack of normalization or collapsing logic for nested wildcard type bounds during generic type resolution. When the `resolve` method encounters nested wildcards (e.g., '? extends ? extends T'), it recursively processes them without checking if the resulting type is already in a simplified form. This leads to the creation of increasingly complex, redundant type chains, eventually causing a StackOverflowError or incorrect type equality assertions as seen in the failing tests.
- Postfix reasoning summary: The bug occurs because the type resolution logic in '$Gson$Types.resolve' fails to handle nested wildcard types correctly. When resolving recursive generic types, the system generates increasingly complex nested bounds (e.g., '? super ? super T'), which leads to infinite recursion during the resolution process. This manifests as a 'StackOverflowError' and incorrect type equality assertions. The fix requires implementing logic to collapse these nested wildcard chains into a canonical form, as specified in the bug report.
- Prefix context signal: com.google.gson.internal.bind.RecursiveTypesResolveTest::testDoubleSupertype: junit.framework.AssertionFailedError: expected:<? super java.lang.Number> but was:<? super ? super java.lang.Number>
- Postfix context signal: com.google.gson.internal.bind.RecursiveTypesResolveTest::testDoubleSupertype: junit.framework.AssertionFailedError: expected:<? super java.lang.Number> but was:<? super ? super java.lang.Number>

### JacksonCore-24
- Type shift: Incorrect Exception Type Usage -> Inappropriate Exception Handling.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Exception Type Usage' vs 'Inappropriate Exception Handling')
- Prefix reasoning summary: The bug report explicitly states that the current implementation uses 'JsonParseException' for numeric overflow errors, which is semantically incorrect because these are coercion failures rather than parsing errors. The stack traces confirm that the code currently throws 'JsonParseException' via 'ParserMinimalBase._reportError' when a number exceeds the range of the requested target type (int or long). The desired behavior is to use a more specific 'InputCoercionException' that extends 'JsonProcessingException' instead of 'JsonParseException', allowing for better error handling and metadata reporting.
- Postfix reasoning summary: The bug was identified as a design flaw where numeric overflow errors during coercion were being reported as generic JsonParseExceptions. The fix involved introducing a more specific exception type, InputCoercionException, which provides better metadata (such as the target type and input token type) to the calling application. The code changes updated the error reporting methods in ParserBase and ParserMinimalBase to utilize this new exception type instead of the generic _reportError method, allowing for better error handling and differentiation between parsing errors and type mismatch/coercion errors.
- Prefix context signal: com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)
- Postfix context signal: com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)

### JacksonXml-6
- Type shift: Missing API implementation -> missing feature implementation.
- Comparison detail: Family match only: both 'None' but types differ ('Missing API implementation' vs 'missing feature implementation')
- Prefix reasoning summary: The ToXmlGenerator class fails to implement the writeBinary(Base64Variant, InputStream, int) method, which is required for serializing binary data from an InputStream. When the Jackson serializer attempts to write binary data using this method, it falls back to the default implementation in the base class, which throws an 'Operation not supported' exception. This is a functional gap where the XML generator lacks the necessary logic to handle streaming binary data, unlike other Jackson generators.
- Postfix reasoning summary: The bug is caused by the absence of an implementation for the 'writeBinary(Base64Variant, InputStream, int)' method in the 'ToXmlGenerator' class. When the Jackson serialization process encounters binary data that is provided via an InputStream (often as a fallback from other serializers), it attempts to call this method. Since 'ToXmlGenerator' did not override this method from the base 'JsonGenerator' class, it triggered an 'UnsupportedOperationException' (wrapped in a 'JsonMappingException'), causing the serialization to fail.
- Prefix context signal: com.fasterxml.jackson.dataformat.xml.ser.TestBinaryStreamToXMLSerialization::testWith0Bytes: com.fasterxml.jackson.databind.JsonMappingException: Operation not supported by generator of type com.fasterxml.jackson.dataformat.xml.ser.ToXmlGenerator (through reference chain: com.fasterxml.jackson.dataformat.xml.ser.TestBinaryStreamToXMLSerialization$TestPojo["field"])
- Postfix context signal: com.fasterxml.jackson.dataformat.xml.ser.TestBinaryStreamToXMLSerialization::testWith0Bytes: com.fasterxml.jackson.databind.JsonMappingException: Operation not supported by generator of type com.fasterxml.jackson.dataformat.xml.ser.ToXmlGenerator (through reference chain: com.fasterxml.jackson.dataformat.xml.ser.TestBinaryStreamToXMLSerialization$TestPojo["field"])

### Jsoup-28
- Type shift: Incorrect Entity Decoding Logic -> incorrect entity decoding logic.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Entity Decoding Logic' vs 'incorrect entity decoding logic')
- Prefix reasoning summary: The library's entity decoding logic is overly aggressive, incorrectly identifying substrings within URLs (like '&num', '&chi', or '&int') as HTML entities and replacing them with their corresponding Unicode characters. This behavior causes data corruption in contexts where ampersands are used for query parameters rather than HTML markup. The failing tests demonstrate that the parser fails to distinguish between valid HTML entities and plain text sequences that happen to start with an ampersand, leading to spurious decoding.
- Postfix reasoning summary: The bug was caused by an overly aggressive entity decoding mechanism that incorrectly identified substrings in URLs (like '&num' or '&int') as HTML entities. The original implementation used a regex-based approach that attempted to match and replace entities without properly validating if they were intended to be HTML entities or just part of a query string. The fix involved replacing the regex-based unescaper with a more robust tokenization-based approach that correctly respects HTML5 entity parsing rules, specifically requiring a semicolon for extended entities and distinguishing between base and extended entity sets.
- Prefix context signal: org.jsoup.nodes.EntitiesTest::unescape: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>
- Postfix context signal: org.jsoup.nodes.EntitiesTest::unescape: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>

### Lang-27
- Type shift: IndexOutOfBoundsException due to improper string slicing -> Improper Input Validation.
- Comparison detail: Family match only: both 'None' but types differ ('IndexOutOfBoundsException due to improper string slicing' vs 'Improper Input Validation')
- Prefix reasoning summary: The code in NumberUtils.createNumber attempts to perform a substring operation using an index (expPos) that is calculated based on the presence of an exponent character. When a string like '1eE' is provided, the logic fails to validate the bounds of the string before calling substring, leading to a StringIndexOutOfBoundsException. The code assumes that if an exponent character exists, the substring operation will be valid, but it does not account for cases where the index might be invalid or the string structure is malformed.
- Postfix reasoning summary: The code fails to validate the position of the exponent character ('e' or 'E') relative to the string length before performing substring operations. When an invalid string like '1eE' is provided, the logic incorrectly assumes the exponent position is valid, leading to a StringIndexOutOfBoundsException when attempting to extract substrings. The fix introduces explicit checks to ensure the exponent position is within the bounds of the string, throwing a NumberFormatException instead of crashing.
- Prefix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: java.lang.StringIndexOutOfBoundsException: begin 0, end 4, length 3
- Postfix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: java.lang.StringIndexOutOfBoundsException: begin 0, end 4, length 3

### Lang-60
- Type shift: Off-by-one boundary condition error -> Off-by-one boundary error.
- Comparison detail: Family match only: both 'None' but types differ ('Off-by-one boundary condition error' vs 'Off-by-one boundary error')
- Prefix reasoning summary: The bug report and test failure indicate that the StrBuilder class incorrectly references the internal buffer's length (thisBuf.length) instead of the actual logical size of the string (size) when performing search operations like contains() or indexOf(). This causes the methods to scan beyond the valid data stored in the buffer, leading to incorrect results when the buffer capacity exceeds the current string length.
- Postfix reasoning summary: The StrBuilder class maintains an internal character buffer that may be larger than the actual string content stored within it. The methods 'contains(char)' and 'indexOf(char, int)' were incorrectly iterating over the entire length of the underlying buffer ('thisBuf.length') instead of the current logical size of the string ('this.size'). This caused the methods to scan stale or uninitialized data beyond the valid string content, leading to incorrect results when the character being searched for existed in the unused portion of the buffer.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

### Time-14
- Type shift: Invalid boundary validation in date arithmetic -> incorrect boundary validation logic.
- Comparison detail: Family match only: both 'None' but types differ ('Invalid boundary validation in date arithmetic' vs 'incorrect boundary validation logic')
- Prefix reasoning summary: The defect occurs when performing arithmetic operations (plus/minus months or days) on a 'MonthDay' object initialized to a leap day (February 29th). The code attempts to perform these operations by setting the date to a fixed epoch (1970-01-01) and then applying the field changes. When the operation involves a month or day that results in a non-leap year context, the underlying 'PreciseDurationDateTimeField.set' method triggers a 'verifyValueBounds' check. This check enforces a strict upper bound of 28 for the day of month in February, failing to account for the fact that 'MonthDay' is a partial date representation that should allow February 29th as a valid state regardless of the specific year context used for internal calculations.
- Postfix reasoning summary: The bug occurs because the `BasicMonthOfYearDateTimeField.add` method attempts to perform arithmetic on a `MonthDay` object by converting it to a full timestamp (using a default year) and then back to a partial. When the `MonthDay` is set to February 29th, this conversion process triggers a validation error because the default year used for the conversion is not a leap year, causing the `dayOfMonth` (29) to be rejected as out of bounds for February. The fix introduces a specialized path for `MonthDay` objects that performs the month arithmetic directly on the partial values, bypassing the problematic conversion to a full timestamp that enforces non-leap-year constraints.
- Prefix context signal: org.joda.time.TestMonthDay_Basics::testPlusMonths_int_negativeFromLeap: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]
- Postfix context signal: org.joda.time.TestMonthDay_Basics::testPlusMonths_int_negativeFromLeap: org.joda.time.IllegalFieldValueException: Value 29 for dayOfMonth must be in the range [1,28]

### Time-2
- Type shift: Incorrect validation logic for partial date-time fields -> Incorrect logic in field ordering validation.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect validation logic for partial date-time fields' vs 'Incorrect logic in field ordering validation')
- Prefix reasoning summary: The code in Partial.java enforces that fields must be ordered from largest to smallest duration. When comparing two fields with the same duration (e.g., both having null range duration types), the code incorrectly assumes they are duplicates and throws an IllegalArgumentException. In the case of 'era' and 'year', both have null range duration types, but they are distinct fields that should be allowed to coexist in a Partial object. The validation logic fails to distinguish between actual duplicate field types and different field types that happen to share the same (null) range duration.
- Postfix reasoning summary: The bug occurs because the validation logic in the Partial class incorrectly assumes that all duration fields are comparable and that unsupported fields should trigger an exception when encountered in a specific order. Specifically, the code failed to handle cases where fields have null range duration types (like 'era' or 'weekyear'), leading to either an IllegalArgumentException due to incorrect ordering assumptions or a NullPointerException when attempting to access the range duration field. The fix involved simplifying the comparison logic to rely on the result of compareTo and adding null checks for range duration types, as well as updating UnsupportedDurationField to correctly handle comparisons with supported fields.
- Prefix context signal: org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year
- Postfix context signal: org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year

## Type Transitions

### Type Changed (Prefix → Postfix)

- Improper HTML character escaping -> Improper Output Encoding: 1
  - Bugs: Chart-10 (no alt overlap)
- invalid range construction due to negative width calculation -> invalid argument range calculation: 1
  - Bugs: Chart-13 (no alt overlap)
- Boundary condition error -> Boundary condition error in object cloning: 1
  - Bugs: Chart-17 (no alt overlap)
- Incorrect default argument handling logic -> logic error in default value handling: 1
  - Bugs: Cli-15 (no alt overlap)
- Incorrect logic in command-line argument parsing -> Incorrect control flow logic: 1
  - Bugs: Cli-17 (no alt overlap)
- off-by-one error -> Off-by-one error leading to index out of bounds: 1
  - Bugs: Cli-32 (no alt overlap)
- spurious state change notification -> incorrect state management in module processing: 1
  - Bugs: Closure-140 (no alt overlap)
- Input validation logic error -> input validation and logic error: 1
  - Bugs: Closure-143 (no alt overlap)
- Type Inference Failure -> Type Inference Logic Error: 1
  - Bugs: Closure-25 (no alt overlap)
- incorrect algorithm logic -> Incorrect algorithm implementation of Soundex HW rule: 1
  - Bugs: Codec-15 (no alt overlap)
- Incorrect validation logic due to flawed alphabet definition -> Incorrect lookup table data: 1
  - Bugs: Codec-16 (no alt overlap)
- Incorrect parameter usage in string matching logic -> incorrect parameter in string matching logic: 1
  - Bugs: Codec-3 (no alt overlap)
- Incorrect subList implementation -> API contract violation / Inconsistent state management: 1
  - Bugs: Collections-21 (no alt overlap)
- Incorrect Method Invocation -> incorrect method invocation: 1
  - Bugs: Collections-3 (no alt overlap)
- Inconsistent Object Equality -> Logical inconsistency in object equality: 1
  - Bugs: Compress-15 (no alt overlap)
- incorrect input validation logic -> Overly restrictive input validation: 1
  - Bugs: Compress-27 (no alt overlap)
- Missing feature implementation -> Missing feature support for file format signature: 1
  - Bugs: Compress-33 (no alt overlap)
- Incorrect data escaping logic -> incorrect output formatting logic: 1
  - Bugs: Csv-13 (no alt overlap)
- incorrect line counting logic -> Incorrect line-ending detection logic: 1
  - Bugs: Csv-1 (no alt overlap)
- Infinite recursion in type resolution -> Infinite recursion in generic type resolution: 1
  - Bugs: Gson-14 (no alt overlap)
- Incorrect state handling in JSON parser -> Incomplete state handling in JSON parser: 1
  - Bugs: Gson-7 (no alt overlap)
- Incorrect state management in composite parser -> State management error in iterator/sequence: 1
  - Bugs: JacksonCore-16 (no alt overlap)
- Incorrect Exception Type Usage -> Inappropriate Exception Handling: 1
  - Bugs: JacksonCore-24 (no alt overlap)
- Incorrect Null Value Provider Initialization -> Inconsistent Null Value Provider Synchronization: 1
  - Bugs: JacksonDatabind-111 (no alt overlap)
- unintended side effect in configuration setter -> unintended side effect: 1
  - Bugs: JacksonDatabind-24 (no alt overlap)
- Missing API implementation -> missing feature implementation: 1
  - Bugs: JacksonXml-6 (no alt overlap)
- Incomplete CSS selector parsing logic -> Incorrect Tokenization/Parsing Logic: 1
  - Bugs: Jsoup-12 (no alt overlap)
- Incorrect Entity Decoding Logic -> incorrect entity decoding logic: 1
  - Bugs: Jsoup-28 (no alt overlap)
- Incorrect operator precedence or evaluation logic for relational expressions -> Incorrect argument order in method call: 1
  - Bugs: JxPath-20 (no alt overlap)
- Incorrect Namespace Handling in XPath Generation -> Incorrect Namespace URI Handling: 1
  - Bugs: JxPath-22 (no alt overlap)
- IndexOutOfBoundsException due to improper string slicing -> Improper Input Validation: 1
  - Bugs: Lang-27 (no alt overlap)
- Off-by-one boundary condition error -> Off-by-one boundary error: 1
  - Bugs: Lang-60 (no alt overlap)
- incorrect index calculation logic -> incorrect algorithm implementation: 1
  - Bugs: Math-56 (no alt overlap)
- Type Mismatch in Default Value Return -> Incorrect primitive type mapping: 1
  - Bugs: Mockito-26 (no alt overlap)
- Input Validation Failure -> Missing Input Validation: 1
  - Bugs: Mockito-2 (no alt overlap)
- Invalid boundary validation in date arithmetic -> incorrect boundary validation logic: 1
  - Bugs: Time-14 (no alt overlap)
- Incorrect Daylight Saving Time (DST) transition handling -> incorrect DST transition handling: 1
  - Bugs: Time-25 (no alt overlap)
- Incorrect parsing logic for ISO period formats -> Incorrect logic in composite formatter construction: 1
  - Bugs: Time-27 (no alt overlap)
- Incorrect validation logic for partial date-time fields -> Incorrect logic in field ordering validation: 1
  - Bugs: Time-2 (no alt overlap)

### Type Unchanged

- Missing Interface Implementation -> Missing Interface Implementation: 1
  - Bugs: Collections-24
- Missing Input Validation -> Missing Input Validation: 1
  - Bugs: Compress-44
- Incorrect API implementation -> Incorrect API implementation: 1
  - Bugs: JacksonXml-3
- infinite loop -> infinite loop: 1
  - Bugs: Lang-43
- Encapsulation Violation -> Encapsulation Violation: 1
  - Bugs: Math-34
