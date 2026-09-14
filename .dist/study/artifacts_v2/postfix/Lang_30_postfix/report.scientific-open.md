# Defects4J ODC Classification Report: Lang-30

- Version: `30b`
- Work directory: `C:\d4j-work\study-work\postfix\Lang_30b`
- Generated: `2026-09-13T17:42:49+00:00`

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
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is an algorithmic deficiency in how StringUtils handles Unicode supplementary characters. The current implementation iterates through the string and compares characters one by one. Because supplementary characters are represented as surrogate pairs (two 16-bit chars), the current algorithm incorrectly treats the high surrogate as a standalone character, leading to incorrect results. This is a classic case of an incorrect procedural implementation for the required data domain (Unicode), fitting the Algorithm/Method ODC type.

## Scientific Loop

- Turns: `2`
- Termination: `model concluded on its own`
- Loop duration: `6.977s`
- Probe misses: `0`

### Turn 1

**Hypothesis.** The StringUtils methods (containsAny, containsNone, indexOfAny, etc.) iterate over characters in a string and compare them individually against search characters. When a high surrogate character is encountered, the current implementation treats it as a single character, failing to account for the fact that supplementary characters are represented as a pair of surrogate characters (high and low). This leads to incorrect matching logic when supplementary characters are present in the input.

**Prediction.** The code will show loops that process characters one by one without checking for the presence of a low surrogate following a high surrogate, causing false positives or negatives when supplementary characters are involved.

**Probe.** `snippet` `StringUtils`

**Observation.**

```json
{
  "snippets": [
    {
      "class_name": "org.apache.commons.lang3.StringUtilsEqualsIndexOfTest",
      "reason": "Stack frame from org.apache.commons.lang3.StringUtilsEqualsIndexOfTest.testContainsNone_CharArrayWithSupplementaryChars",
      "file_path": "C:\\d4j-work\\study-work\\postfix\\Lang_30b\\src\\test\\java\\org\\apache\\commons\\lang3\\StringUtilsEqualsIndexOfTest.java",
      "start_line": 315,
      "end_line": 339,
      "focus_line": 327,
      "content": "    315:     /**\n    316:      * See http://java.sun.com/developer/technicalArticles/Intl/Supplementary/\n    317:      */\n    318:     public void testContainsNone_CharArrayWithSupplementaryChars() {\n    319:         assertEquals(false, StringUtils.containsNone(CharU20000 + CharU20001, CharU20000.toCharArray()));\n    320:         assertEquals(false, StringUtils.containsNone(CharU20000 + CharU20001, CharU20001.toCharArray()));\n    321:         assertEquals(false, StringUtils.containsNone(CharU20000, CharU20000.toCharArray()));\n    322:         // Sanity check:\n    323:         assertEquals(-1, CharU20000.indexOf(CharU20001));\n    324:         assertEquals(0, CharU20000.indexOf(CharU20001.charAt(0)));\n    325:         assertEquals(-1, CharU20000.indexOf(CharU20001.charAt(1)));\n    326:         // Test:\n>>  327:         assertEquals(true, StringUtils.containsNone(CharU20000, CharU20001.toCharArray()));\n    328:         assertEquals(true, StringUtils.containsNone(CharU20001, CharU20000.toCharArray()));\n    329:     }\n    330: \n    331:     public void testContainsNone_String() {\n    332:         String str1 = \"a\";\n    333:         String str2 = \"b\";\n    334:         String str3 = \"ab.\";\n    335:         String chars1= \"b\";\n    336:         String chars2= \".\";\n    337:         String chars3= \"cd\";\n    338:         assertEquals(true, StringUtils.containsNone(null, (String) null));\n    339:         assertEquals(true, StringUtils.containsNone(\"\", (String) null));"
   
... [truncated — full observation was 14328 chars]
```

_3.464s_

### Turn 2

**Hypothesis.** The StringUtils methods (like containsNone, containsAny, etc.) perform character-by-character iteration and comparison. When encountering a high surrogate character, the implementation fails to verify if it is part of a valid supplementary character pair (high surrogate followed by a low surrogate). This leads to incorrect results because the logic treats the high surrogate as an independent character, causing false matches or mismatches when supplementary characters are present.

**Prediction.** The implementation of these methods in StringUtils will show a simple nested loop structure that compares individual characters without checking for the existence of a low surrogate when a high surrogate is found.

**Concluded**: `Algorithm/Method`

_3.512s_
