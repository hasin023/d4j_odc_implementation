# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j-work\study-work\prefix\Lang_28b`
- Generated: `2026-09-13T17:42:18+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping`: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping` at `NumericEntityUnescaperTest.java:33`
- `org.apache.commons.lang3.builder.Builder.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.concurrent.ConcurrentInitializer.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.exception.ExceptionContext.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.FormatFactory.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.` at `org/apache/commons/lang3/text/translate/NumericEntityUnescaper.java:48`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.` at `org/apache/commons/lang3/text/translate/CharSequenceTranslator.java:93`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Method`
- Confidence: `0.9`
- Needs Human Review: `False`

The code snippet for NumericEntityUnescaper shows the parsing of the entity value but no subsequent code to write the value to the output. This is a procedural error in the implementation of the unescaping algorithm.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`

## Scientific Loop

- Turns: `2`
- Termination: `model concluded on its own`
- Loop duration: `5.479s`
- Probe misses: `0`

### Turn 1

**Hypothesis.** The NumericEntityUnescaper.translate method fails to correctly handle supplementary characters because it does not account for the fact that supplementary characters (code points > 0xFFFF) are represented as surrogate pairs in Java strings. The current implementation likely treats the surrogate pair as two separate characters or fails to correctly convert the parsed integer entity value back into the appropriate surrogate pair in the output string.

**Prediction.** I expect to see that the NumericEntityUnescaper.translate method parses the numeric entity correctly but fails to use Character.toChars(entityValue) to convert the code point into a surrogate pair, instead perhaps casting the integer to a char, which truncates the supplementary character.

**Probe.** `snippet` `NumericEntityUnescaper`

**Observation.**

```json
{
  "snippets": [
    {
      "class_name": "org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest",
      "reason": "Stack frame from org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest.testSupplementaryUnescaping",
      "file_path": "C:\\d4j-work\\study-work\\prefix\\Lang_28b\\src\\test\\java\\org\\apache\\commons\\lang3\\text\\translate\\NumericEntityUnescaperTest.java",
      "start_line": 21,
      "end_line": 36,
      "focus_line": 33,
      "content": "     21: \n     22: /**\n     23:  * Unit tests for {@link org.apache.commons.lang3.text.translate.NumericEntityUnescaper}.\n     24:  */\n     25: public class NumericEntityUnescaperTest extends TestCase {\n     26: \n     27:     public void testSupplementaryUnescaping() {\n     28:         NumericEntityUnescaper neu = new NumericEntityUnescaper();\n     29:         String input = \"&#68642;\";\n     30:         String expected = \"\\uD803\\uDC22\";\n     31: \n     32:         String result = neu.translate(input);\n>>   33:         assertEquals(\"Failed to unescape numeric entities supplementary characters\", expected, result);\n     34:     }\n     35: \n     36: }"
    },
    {
      "class_name": "org.apache.commons.lang3.text.translate.NumericEntityUnescaper",
      "reason": "Most-executed line in org.apache.commons.lang3.text.translate.NumericEntityUnescaper (touched by the trigger test, not in its stack trace)",
      "file_path": "C:\\d4j-work\\study-work\\prefix\\Lang_28b\\src\\main\\java\\org\\apache\\commons\\lang3\\text\\translate\\NumericEntityUnescaper.java",
      "start_line": 36,
      "end_line": 60,
      "focus_line": 48,
      "content": "     36:         // TODO: Protect from ArrayIndexOutOfBounds\n     37:         if(input.charAt(index) == '&' && input.charAt(index + 1) == '#') {\n     38:             int start = index + 2;\n     39:             boolean isHex = false;\n     40: \n     41:             char firstChar = input.charAt(start);\n     42:         
... [truncated — full observation was 2811 chars]
```

_1.738s_

### Turn 2

**Hypothesis.** The NumericEntityUnescaper class is missing the logic to write the unescaped entity value to the output stream. The current implementation (as seen in the snippet) only parses the entity value but does not contain the code to write it to the 'out' Writer. It likely relies on the base class or a missing implementation step to perform the actual writing, and it fails to handle the conversion of the integer entity value into the correct character(s) (especially for supplementary characters) before writing.

**Prediction.** I expect to find that the translate method in NumericEntityUnescaper is incomplete or missing the call to out.write() for the parsed entityValue, or that it incorrectly casts the integer to a char instead of using Character.toChars().

**Concluded**: `Algorithm/Method`

_3.741s_
