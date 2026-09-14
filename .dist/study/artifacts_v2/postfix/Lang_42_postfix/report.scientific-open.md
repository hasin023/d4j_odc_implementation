# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j-work\study-work\postfix\Lang_42b`
- Generated: `2026-09-13T17:45:01+00:00`

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
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic case of incorrect handling of Unicode surrogate pairs. The code iterates over the string using 'charAt', which treats surrogate pairs as two distinct characters. This is an algorithmic error in how the string is processed for escaping. It does not require a design change (Function/Class/Object) or a simple value assignment; it requires a change to the procedural logic of the loop.

## Scientific Loop

- Turns: `2`
- Termination: `model concluded on its own`
- Loop duration: `5.602s`
- Probe misses: `0`

### Turn 1

**Hypothesis.** The bug is caused by the use of 'str.charAt(i)' in 'Entities.escape', which only retrieves 16-bit char values. For Unicode characters outside the Basic Multilingual Plane (BMP), Java represents them as surrogate pairs (two 16-bit chars). The current implementation treats each half of the surrogate pair as a separate character, resulting in two separate HTML entities instead of one. The fix requires using 'Character.codePointAt(str, i)' to correctly identify the full Unicode codepoint.

**Prediction.** The 'Entities.escape' method will show a loop iterating over 'str.length()' and calling 'str.charAt(i)', which fails to handle surrogate pairs correctly for characters above U+FFFF.

**Probe.** `snippet` `org.apache.commons.lang.Entities`

**Observation.**

```json
{
  "snippets": [
    {
      "class_name": "org.apache.commons.lang.Entities",
      "reason": "Most-executed line in org.apache.commons.lang.Entities (touched by the trigger test, not in its stack trace)",
      "file_path": "C:\\d4j-work\\study-work\\postfix\\Lang_42b\\src\\java\\org\\apache\\commons\\lang\\Entities.java",
      "start_line": 725,
      "end_line": 749,
      "focus_line": 737,
      "content": "    725:     // package scoped for testing\n    726:     EntityMap map = new Entities.LookupEntityMap();\n    727: \n    728:     /**\n    729:      * <p>\n    730:      * Adds entities to this entity.\n    731:      * </p>\n    732:      * \n    733:      * @param entityArray\n    734:      *            array of entities to be added\n    735:      */\n    736:     public void addEntities(String[][] entityArray) {\n>>  737:         for (int i = 0; i < entityArray.length; ++i) {\n    738:             addEntity(entityArray[i][0], Integer.parseInt(entityArray[i][1]));\n    739:         }\n    740:     }\n    741: \n    742:     /**\n    743:      * <p>\n    744:      * Add an entity to this entity.\n    745:      * </p>\n    746:      * \n    747:      * @param name\n    748:      *            name of the entity\n    749:      * @param value"
    }
  ]
}
```

_1.865s_

### Turn 2

**Hypothesis.** The 'Entities.escape' method uses 'char' iteration which is insufficient for Unicode characters outside the Basic Multilingual Plane (BMP). These characters are represented as surrogate pairs in Java, and the current implementation processes each surrogate individually, leading to incorrect HTML entity generation. The fix requires using 'Character.codePointAt' to correctly handle these characters.

**Prediction.** The 'Entities.escape' method will be found to iterate using 'str.charAt(i)' instead of 'Character.codePointAt(str, i)', confirming the algorithmic flaw in handling multi-char Unicode sequences.

**Concluded**: `Algorithm/Method`

_3.737s_
