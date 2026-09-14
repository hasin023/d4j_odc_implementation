# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j-work\study-work\prefix\Lang_42b`
- Generated: `2026-09-13T17:44:55+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`
- `org.apache.commons.lang.exception.Nestable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang.text.FormatFactory.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang.Entities.` at `org/apache/commons/lang/Entities.java:737`
- `org.apache.commons.lang.IntHashMap.` at `org/apache/commons/lang/IntHashMap.java:268`
- `org.apache.commons.lang.StringEscapeUtils.` at `org/apache/commons/lang/StringEscapeUtils.java:46`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is an algorithmic flaw where the procedure assumes a 1:1 mapping between a Java 'char' and a Unicode character. This assumption is incorrect for supplementary characters. The fix requires changing the iteration logic to handle surrogate pairs, which is a local procedural change.

## Scientific Loop

- Turns: `3`
- Termination: `model concluded on its own`
- Loop duration: `6.766s`
- Probe misses: `0`

### Turn 1

**Hypothesis.** The StringEscapeUtils.escapeHtml method iterates over the string using char-by-char processing, which fails to correctly handle supplementary characters (Unicode codepoints > U+FFFF) that are represented as surrogate pairs in Java's UTF-16 encoding. The implementation treats each surrogate as an individual character, resulting in two separate HTML entities instead of one.

**Prediction.** The implementation of escapeHtml (or the underlying Entities class it uses) will show a loop that iterates over the string using charAt(i) and processes each char independently, without checking if a char is a high surrogate that should be combined with the next low surrogate.

**Probe.** `snippet` `StringEscapeUtils`

**Observation.**

```json
{
  "snippets": [
    {
      "class_name": "org.apache.commons.lang.StringEscapeUtilsTest",
      "reason": "Stack frame from org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode",
      "file_path": "C:\\d4j-work\\study-work\\prefix\\Lang_42b\\src\\test\\org\\apache\\commons\\lang\\StringEscapeUtilsTest.java",
      "start_line": 418,
      "end_line": 432,
      "focus_line": 430,
      "content": "    418: \n    419:     // https://issues.apache.org/jira/browse/LANG-480\n    420:     public void testEscapeHtmlHighUnicode() throws java.io.UnsupportedEncodingException {\n    421:         // this is the utf8 representation of the character:\n    422:         // COUNTING ROD UNIT DIGIT THREE\n    423:         // in unicode\n    424:         // codepoint: U+1D362\n    425:         byte[] data = new byte[] { (byte)0xF0, (byte)0x9D, (byte)0x8D, (byte)0xA2 };\n    426: \n    427:         String escaped = StringEscapeUtils.escapeHtml( new String(data, \"UTF8\") );\n    428:         String unescaped = StringEscapeUtils.unescapeHtml( escaped );\n    429: \n>>  430:         assertEquals( \"High unicode was not escaped correctly\", \"&#119650;\", escaped);\n    431:     }\n    432: }"
    },
    {
      "class_name": "org.apache.commons.lang.StringEscapeUtils",
      "reason": "Most-executed line in org.apache.commons.lang.StringEscapeUtils (touched by the trigger test, not in its stack trace)",
      "file_path": "C:\\d4j-work\\study-work\\prefix\\Lang_42b\\src\\java\\org\\apache\\commons\\lang\\StringEscapeUtils.java",
      "start_line": 34,
      "end_line": 58,
      "focus_line": 46,
      "content": "     34:  * @author Helge Tesgaard\n     35:  * @author <a href=\"sean@boohai.com\">Sean Brown</a>\n     36:  * @author <a href=\"mailto:ggregory@seagullsw.com\">Gary Gregory</a>\n     37:  * @author Phil Steitz\n     38:  * @author Pete Gieser\n     39:  * @since 2.0\n     40:  * @version $Id$\n     41:  */\n     42: public class StringEscapeUtils {\n 
... [truncated — full observation was 2825 chars]
```

_1.71s_

### Turn 2

**Hypothesis.** The StringEscapeUtils.escapeHtml method relies on an underlying implementation (likely in the Entities class) that iterates over the input string using char-based indexing. This approach fails to account for supplementary characters (codepoints > U+FFFF) which are represented as surrogate pairs in Java. The logic processes each surrogate as a distinct character, leading to incorrect HTML entity generation.

**Prediction.** The actual logic for escaping HTML is delegated to the Entities class, which will show a loop iterating over the string character by character without checking for surrogate pairs.

**Probe.** `snippet` `Entities`

**Observation.**

```json
{
  "snippets": [
    {
      "class_name": "org.apache.commons.lang.Entities",
      "reason": "Most-executed line in org.apache.commons.lang.Entities (touched by the trigger test, not in its stack trace)",
      "file_path": "C:\\d4j-work\\study-work\\prefix\\Lang_42b\\src\\java\\org\\apache\\commons\\lang\\Entities.java",
      "start_line": 725,
      "end_line": 749,
      "focus_line": 737,
      "content": "    725:     // package scoped for testing\n    726:     EntityMap map = new Entities.LookupEntityMap();\n    727: \n    728:     /**\n    729:      * <p>\n    730:      * Adds entities to this entity.\n    731:      * </p>\n    732:      * \n    733:      * @param entityArray\n    734:      *            array of entities to be added\n    735:      */\n    736:     public void addEntities(String[][] entityArray) {\n>>  737:         for (int i = 0; i < entityArray.length; ++i) {\n    738:             addEntity(entityArray[i][0], Integer.parseInt(entityArray[i][1]));\n    739:         }\n    740:     }\n    741: \n    742:     /**\n    743:      * <p>\n    744:      * Add an entity to this entity.\n    745:      * </p>\n    746:      * \n    747:      * @param name\n    748:      *            name of the entity\n    749:      * @param value"
    }
  ]
}
```

_1.736s_

### Turn 3

**Hypothesis.** The StringEscapeUtils.escapeHtml method uses an iterative approach that processes strings character-by-character (using charAt), which is fundamentally incapable of handling Unicode supplementary characters (codepoints > U+FFFF) that are represented as surrogate pairs in Java. The algorithm needs to be updated to detect surrogate pairs and treat them as a single codepoint.

**Prediction.** The implementation of escapeHtml in StringEscapeUtils or its helper methods will show a loop over the string's length, accessing characters via charAt(i) and processing them individually, without any logic to check for Character.isHighSurrogate(c) or to combine surrogate pairs.

**Concluded**: `Algorithm/Method`

_3.32s_
