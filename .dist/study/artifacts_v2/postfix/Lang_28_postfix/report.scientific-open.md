# Defects4J ODC Classification Report: Lang-28

- Version: `28b`
- Work directory: `C:\d4j-work\study-work\postfix\Lang_28b`
- Generated: `2026-09-13T17:42:21+00:00`

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
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a procedural error in the translation logic where the code assumes all characters fit into a single char. This is a classic algorithmic deficiency in handling character encoding boundaries.

## Scientific Loop

- Turns: `1`
- Termination: `model concluded on its own`
- Loop duration: `3.029s`
- Probe misses: `0`

### Turn 1

**Hypothesis.** The NumericEntityUnescaper class fails to correctly handle supplementary characters (code points > 0xFFFF) because it attempts to write the entityValue directly to the output stream as a single char, which is insufficient for characters requiring surrogate pairs in UTF-16.

**Prediction.** The fix will involve checking if the entityValue is greater than 0xFFFF and, if so, converting it to a surrogate pair (char array) using Character.toChars() before writing to the output.

**Concluded**: `Algorithm/Method`

_3.029s_
