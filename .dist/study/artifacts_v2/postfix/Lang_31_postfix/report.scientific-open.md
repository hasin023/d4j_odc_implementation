# Defects4J ODC Classification Report: Lang-31

- Version: `31b`
- Work directory: `C:\d4j-work\study-work\postfix\Lang_31b`
- Generated: `2026-09-13T17:43:03+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:696`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:680`
- `org.apache.commons.lang3.exception.ExceptionContext.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.FormatFactory.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.ArrayUtils.` at `org/apache/commons/lang3/ArrayUtils.java:3279`
- `org.apache.commons.lang3.StringUtils.` at `org/apache/commons/lang3/StringUtils.java:194`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic case of an algorithm failing to account for a specific data representation (Unicode surrogate pairs). The fix involves adding logic to check for surrogate pairs during the iteration, which is a modification of the method's internal procedure.

## Scientific Loop

- Turns: `2`
- Termination: `model concluded on its own`
- Loop duration: `5.799s`
- Probe misses: `0`

### Turn 1

**Hypothesis.** The StringUtils.containsAny method incorrectly treats individual surrogate characters as full matches when comparing strings containing Unicode supplementary characters (which are represented as surrogate pairs in Java). The current implementation iterates through characters and matches them individually, failing to account for the fact that a high surrogate followed by a low surrogate constitutes a single supplementary character.

**Prediction.** The implementation of StringUtils.containsAny will show a nested loop that compares individual char values without checking if a character is a high surrogate that should be paired with the next character to form a valid supplementary character.

**Probe.** `snippet` `StringUtils`

**Observation.**

```json
{
  "snippets": [
    {
      "class_name": "org.apache.commons.lang3.StringUtilsEqualsIndexOfTest",
      "reason": "Stack frame from org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyCharArrayWithSupplementaryChars",
      "file_path": "C:\\d4j-work\\study-work\\postfix\\Lang_31b\\src\\test\\java\\org\\apache\\commons\\lang3\\StringUtilsEqualsIndexOfTest.java",
      "start_line": 684,
      "end_line": 699,
      "focus_line": 696,
      "content": "    684: \t/**\n    685: \t * See http://java.sun.com/developer/technicalArticles/Intl/Supplementary/\n    686: \t */\n    687: \tpublic void testContainsAnyCharArrayWithSupplementaryChars() {\n    688: \t\tassertEquals(true, StringUtils.containsAny(CharU20000 + CharU20001, CharU20000.toCharArray()));\n    689: \t\tassertEquals(true, StringUtils.containsAny(CharU20000 + CharU20001, CharU20001.toCharArray()));\n    690: \t\tassertEquals(true, StringUtils.containsAny(CharU20000, CharU20000.toCharArray()));\n    691: \t\t// Sanity check:\n    692: \t\tassertEquals(-1, CharU20000.indexOf(CharU20001));\n    693: \t\tassertEquals(0, CharU20000.indexOf(CharU20001.charAt(0)));\n    694: \t\tassertEquals(-1, CharU20000.indexOf(CharU20001.charAt(1)));\n    695: \t\t// Test:\n>>  696: \t\tassertEquals(false, StringUtils.containsAny(CharU20000, CharU20001.toCharArray()));\n    697: \t\tassertEquals(false, StringUtils.containsAny(CharU20001, CharU20000.toCharArray()));\n    698: \t}\n    699: }"
    },
    {
      "class_name": "org.apache.commons.lang3.StringUtilsEqualsIndexOfTest",
      "reason": "Stack frame from org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAnyStringWithSupplementaryChars",
      "file_path": "C:\\d4j-work\\study-work\\postfix\\Lang_31b\\src\\test\\java\\org\\apache\\commons\\lang3\\StringUtilsEqualsIndexOfTest.java",
      "start_line": 668,
      "end_line": 692,
      "focus_line": 680,
      "content": "    668: \t/**\n    669: \t * See http://java.sun.com/developer/
... [truncated — full observation was 5044 chars]
```

_2.285s_

### Turn 2

**Hypothesis.** The StringUtils.containsAny method is implemented using a naive character-by-character comparison that fails to account for Unicode supplementary characters (represented as surrogate pairs in Java). When a high surrogate is encountered, the method incorrectly treats it as a standalone character match, leading to false positives when comparing strings containing supplementary characters.

**Prediction.** The implementation of StringUtils.containsAny will show a nested loop that iterates over characters and performs a direct equality check (char == char) without validating if the character is part of a surrogate pair, thus failing to distinguish between a single character and a surrogate component.

**Concluded**: `Algorithm/Method`

_3.513s_
