# Batch Study Analysis

- Created: `2026-07-08T17:08:39+00:00`
- Total pairs: **44**
- Projects covered: **17**
- Type changed: **8** (18.2%)
- Type unchanged: **36** (81.8%)
- No alternative overlap: **1** (2.3%)
- No family match: **1** (2.3%)
- Family match: **43** (97.7%)

## Alternative Match Cases (Type Changed)

### Collections-21
- Type shift: Checking -> Function/Class/Object.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Function/Class/Object' is in pre-fix alternatives
- Prefix reasoning summary: The bug is caused by the lack of a restriction on the sublist returned by SetUniqueList. The developer's intent, as evidenced by the test case, is that the sublist should be unmodifiable to maintain the integrity of the SetUniqueList. Since the current code fails to enforce this constraint, it is a missing validation/check.
- Postfix reasoning summary: The defect is a structural design issue where the subList view of a SetUniqueList does not correctly maintain the uniqueness invariant of the parent list. The fix is to change the return type/behavior of the subList method to return an unmodifiable list, which is a design-level correction.
- Prefix context signal: org.apache.commons.collections4.list.SetUniqueListTest::testSubListIsUnmodifiable: junit.framework.AssertionFailedError: subList should be unmodifiable
- Postfix context signal: org.apache.commons.collections4.list.SetUniqueListTest::testSubListIsUnmodifiable: junit.framework.AssertionFailedError: subList should be unmodifiable

### Chart-10
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic case of missing data sanitization/encoding in a string generation method. Since the method logic is responsible for the correct formatting of the output string, and it fails to handle special characters correctly, it falls under Algorithm/Method.
- Postfix reasoning summary: The bug is a failure to validate/sanitize input data before using it in a context where special characters (quotes) have semantic meaning (HTML attributes). This is a classic 'Checking' defect as it involves missing logic to ensure data integrity for the output format.
- Prefix context signal: org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">
- Postfix context signal: org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">

### Jsoup-12
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic parsing error where the logic for identifying and consuming tokens (specifically attribute selectors with regex) is incomplete or incorrect when the parser state is influenced by a preceding combinator. This is a 'Checking' defect because the parser's conditional logic (the 'if-else' chain in findElements or the main select loop) fails to validate or correctly branch for this specific valid CSS syntax.
- Postfix reasoning summary: The bug is a classic parsing error where the algorithm for tokenizing the sub-query was too simplistic. It failed to account for nested structures (brackets/parentheses) within the selector, which is a procedural/algorithmic flaw in how the query string is processed. It is not a simple assignment error, nor a missing guard (Checking), but a fundamental flaw in the implementation of the parsing logic.
- Prefix context signal: org.jsoup.select.SelectorTest::testByAttributeRegexCombined: org.jsoup.select.Selector$SelectorParseException: Could not parse query '=x|y]': unexpected token at '=x|y]'
- Postfix context signal: org.jsoup.select.SelectorTest::testByAttributeRegexCombined: org.jsoup.select.Selector$SelectorParseException: Could not parse query '=x|y]': unexpected token at '=x|y]'

### Jsoup-28
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic 'Checking' defect where the parser fails to correctly validate the boundary conditions of an HTML entity. By not enforcing the presence of a semicolon or strict matching, the code incorrectly treats arbitrary text as entities.
- Postfix reasoning summary: The bug is a classic case of an incorrect algorithmic strategy for parsing. The regex-based `unescape` method is too greedy and lacks the context-awareness (like checking for valid entity names or the required semicolon) needed to distinguish between actual HTML entities and plain text that happens to contain an ampersand. The fix replaces this with a proper `Tokeniser` implementation, which is a change to the computational strategy/procedure.
- Prefix context signal: org.jsoup.nodes.EntitiesTest::unescape: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>
- Postfix context signal: org.jsoup.nodes.EntitiesTest::unescape: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>

### Time-27
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic case of incorrect algorithmic implementation in a builder pattern. The builder fails to correctly chain the separator logic, which is a procedural/algorithmic issue rather than a simple initialization or interface mismatch.
- Postfix reasoning summary: The defect is a missing guard condition in the PeriodFormatterBuilder. The code failed to verify if a Separator was properly initialized before using it to construct the formatter. This missing check caused the builder to produce an incorrectly configured formatter, leading to parsing failures. This fits the ODC definition of 'Checking' (missing validation of data/state).
- Prefix context signal: org.joda.time.format.TestPeriodFormatterBuilder::testBug2495455: java.lang.IllegalArgumentException: Invalid format: "PT1003199059S" is malformed at "1003199059S"
- Postfix context signal: org.joda.time.format.TestPeriodFormatterBuilder::testBug2495455: java.lang.IllegalArgumentException: Invalid format: "PT1003199059S" is malformed at "1003199059S"

### Codec-3
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defects are clearly procedural: they involve incorrect constants (4 vs 3), incorrect index arithmetic (value.length - 2 vs index - 1), and incorrect control flow (appending 'L' unconditionally). These are not design-level omissions (Function/Class/Object), nor are they interface mismatches (Interface/O-O Messages), nor are they simple initialization errors (Assignment/Initialization). They are errors in the implementation of the algorithm itself.
- Postfix reasoning summary: The defect is a classic 'Checking' error where the logic intended to identify a specific suffix ('IER') fails because the length parameter passed to the 'contains' method is incorrect (4 instead of 3). This is a validation/predicate error.
- Prefix context signal: org.apache.commons.codec.language.DoubleMetaphone2Test::testDoubleMetaphoneAlternate: junit.framework.ComparisonFailure: Test [19]=Angier expected:<AN[J]R> but was:<AN[K]R>
- Postfix context signal: org.apache.commons.codec.language.DoubleMetaphone2Test::testDoubleMetaphoneAlternate: junit.framework.ComparisonFailure: Test [19]=Angier expected:<AN[J]R> but was:<AN[K]R>

### JacksonXml-3
- Type shift: Assignment/Initialization -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Assignment/Initialization' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug report states the fix was 'a simple case of not actually returning the text'. This indicates that the logic to retrieve the text exists, but the assignment or return of that value is missing or incorrect in the specific code path for attributes.
- Postfix reasoning summary: The defect is a missing return value in a specific branch of a switch-case statement within the parser's token processing logic. This is a classic Algorithm/Method defect as it pertains to the correctness of the procedural implementation of the parser's state machine.
- Prefix context signal: com.fasterxml.jackson.dataformat.xml.stream.XmlParserNextXxxTest::testXmlAttributesWithNextTextValue: junit.framework.ComparisonFailure: expected:<7> but was:<null>
- Postfix context signal: com.fasterxml.jackson.dataformat.xml.stream.XmlParserNextXxxTest::testXmlAttributesWithNextTextValue: junit.framework.ComparisonFailure: expected:<7> but was:<null>

## Type Changed (No Alternative Overlap)

### Closure-140
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Checking' vs 'Assignment/Initialization')
- Prefix reasoning summary: The error message explicitly states that reportCodeChange() was called when nothing changed. This is a failure in the conditional logic (the 'check') that determines whether a code change has occurred. The fix involves adding a guard condition to ensure reportCodeChange() is only called when a meaningful transformation is performed.
- Postfix reasoning summary: The bug is caused by the lack of proper initialization of empty modules, which causes the cross-module code motion logic to behave incorrectly. By adding a placeholder file to empty modules, the compiler ensures that the module state is consistent, which is an initialization/assignment issue.
- Prefix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed
- Postfix context signal: com.google.javascript.jscomp.CrossModuleCodeMotionTest::testEmptyModule: junit.framework.AssertionFailedError: compiler.reportCodeChange() was called even though nothing changed

## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Checking: 3
  - Bugs: Chart-10, Codec-3, Time-27
- Checking -> Algorithm/Method: 2
  - Bugs: Jsoup-12, Jsoup-28
- Checking -> Assignment/Initialization: 1
  - Bugs: Closure-140 (no alt overlap)
- Checking -> Function/Class/Object: 1
  - Bugs: Collections-21 (no family match)
- Assignment/Initialization -> Algorithm/Method: 1
  - Bugs: JacksonXml-3

### Type Unchanged

- Checking -> Checking: 16
  - Bugs: Chart-13, Chart-17, Cli-17, Cli-32, Closure-143, Compress-15, Compress-27, Compress-33, Compress-44, Gson-7, JacksonCore-24, Lang-27, Lang-43, Lang-60, Mockito-2, Time-2
- Algorithm/Method -> Algorithm/Method: 12
  - Bugs: Cli-15, Closure-25, Codec-15, Collections-3, Csv-13, Csv-1, Gson-14, JacksonCore-16, JxPath-20, Math-56, Time-14, Time-25
- Assignment/Initialization -> Assignment/Initialization: 5
  - Bugs: Codec-16, JacksonDatabind-111, JacksonDatabind-24, JxPath-22, Mockito-26
- Function/Class/Object -> Function/Class/Object: 3
  - Bugs: Collections-24, JacksonXml-6, Math-34
