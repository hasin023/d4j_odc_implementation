# Defects4J ODC Classification Report: Lang-30

- Version: `30b`
- Work directory: `C:\d4j-work\study-work\prefix\Lang_30b`
- Generated: `2026-09-13T17:42:42+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_CharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<true> but was:<false>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_StringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<true> but was:<false>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAny_StringCharArrayWithBadSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testIndexOfAnyBut_StringStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<2> but was:<3>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAny_StringWithBadSupplementaryChars`: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testIndexOfAny_StringCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<2> but was:<0>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testIndexOfAnyBut_StringCharArrayWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<2> but was:<3>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_StringWithBadSupplementaryChars`: junit.framework.AssertionFailedError: expected:<true> but was:<false>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testIndexOfAny_StringStringWithSupplementaryChars`: junit.framework.AssertionFailedError: expected:<2> but was:<0>
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_CharArrayWithBadSupplementaryChars`: junit.framework.AssertionFailedError: expected:<true> but was:<false>

## Suspicious Frames
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsNone_CharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:327`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsNone_StringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:381`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAny_StringCharArrayWithBadSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:138`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testIndexOfAnyBut_StringStringWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:616`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsAny_StringWithBadSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:186`
- `org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testIndexOfAny_StringCharArrayWithSupplementaryChars` at `StringUtilsEqualsIndexOfTest.java:528`
- `org.apache.commons.lang3.exception.ExceptionContext.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.FormatFactory.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.ArrayUtils.` at `org/apache/commons/lang3/ArrayUtils.java:3279`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by an incorrect algorithmic approach to string traversal. The code assumes a 1:1 mapping between a char and a character, which is false for supplementary characters. The fix requires updating the traversal logic to use code-point-aware methods (like Character.codePointAt) or to correctly handle surrogate pairs during iteration.

## Scientific Loop

- Turns: `2`
- Termination: `model concluded on its own`
- Loop duration: `6.318s`
- Probe misses: `0`

### Turn 1

**Hypothesis.** The StringUtils methods (containsAny, containsNone, indexOfAny, etc.) are manually iterating over the input string using char-based indexing (e.g., charAt) instead of code-point-based indexing, causing them to incorrectly split or misinterpret Unicode supplementary characters (which are represented as surrogate pairs in Java).

**Prediction.** I expect to see code in StringUtils that uses loops over string length and charAt() to compare characters, failing to account for Character.isSupplementaryCodePoint or Character.codePointAt.

**Probe.** `snippet` `StringUtils`

**Observation.**

```json
{
  "snippets": [
    {
      "class_name": "org.apache.commons.lang3.StringUtilsEqualsIndexOfTest",
      "reason": "Stack frame from org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsNone_CharArrayWithSupplementaryChars",
      "file_path": "C:\\d4j-work\\study-work\\prefix\\Lang_30b\\src\\test\\java\\org\\apache\\commons\\lang3\\StringUtilsEqualsIndexOfTest.java",
      "start_line": 315,
      "end_line": 339,
      "focus_line": 327,
      "content": "    315:     /**\n    316:      * See http://java.sun.com/developer/technicalArticles/Intl/Supplementary/\n    317:      */\n    318:     public void testContainsNone_CharArrayWithSupplementaryChars() {\n    319:         assertEquals(false, StringUtils.containsNone(CharU20000 + CharU20001, CharU20000.toCharArray()));\n    320:         assertEquals(false, StringUtils.containsNone(CharU20000 + CharU20001, CharU20001.toCharArray()));\n    321:         assertEquals(false, StringUtils.containsNone(CharU20000, CharU20000.toCharArray()));\n    322:         // Sanity check:\n    323:         assertEquals(-1, CharU20000.indexOf(CharU20001));\n    324:         assertEquals(0, CharU20000.indexOf(CharU20001.charAt(0)));\n    325:         assertEquals(-1, CharU20000.indexOf(CharU20001.charAt(1)));\n    326:         // Test:\n>>  327:         assertEquals(true, StringUtils.containsNone(CharU20000, CharU20001.toCharArray()));\n    328:         assertEquals(true, StringUtils.containsNone(CharU20001, CharU20000.toCharArray()));\n    329:     }\n    330: \n    331:     public void testContainsNone_String() {\n    332:         String str1 = \"a\";\n    333:         String str2 = \"b\";\n    334:         String str3 = \"ab.\";\n    335:         String chars1= \"b\";\n    336:         String chars2= \".\";\n    337:         String chars3= \"cd\";\n    338:         assertEquals(true, StringUtils.containsNone(null, (String) null));\n    339:         assertEquals(true, StringUtils.containsNone(\"\", (String) null));"
    
... [truncated — full observation was 14321 chars]
```

_2.955s_

### Turn 2

**Hypothesis.** The StringUtils methods (like containsNone, containsAny, indexOfAny) are implemented using char-based iteration (charAt) which treats supplementary characters (represented as surrogate pairs in Java) as two separate characters. This causes the logic to incorrectly match or skip parts of these surrogate pairs, leading to the observed failures.

**Prediction.** The implementation of containsNone (and similar methods) will show a loop over the CharSequence using charAt(i), which fails to check if the current character is a high surrogate that should be paired with the next character to form a single supplementary code point.

**Concluded**: `Algorithm/Method`

_3.363s_
