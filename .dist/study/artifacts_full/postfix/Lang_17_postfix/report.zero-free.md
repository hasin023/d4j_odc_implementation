# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j_work\postfix\Lang_17b`
- Generated: `2026-07-10T19:28:15+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringEscapeUtilsTest::testLang720`: junit.framework.ComparisonFailure: expected:<𠮷[A]> but was:<𠮷[?]>

## Suspicious Frames
- `org.apache.commons.lang3.StringEscapeUtilsTest.testLang720` at `StringEscapeUtilsTest.java:431`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incorrect loop iteration logic for Unicode supplementary characters`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect occurred because the translation loop in CharSequenceTranslator was iterating based on the number of code points rather than the actual character sequence length. When encountering characters in the Supplementary Planes (which consist of surrogate pairs), the loop logic incorrectly calculated the position index, leading to the corruption of surrogate pairs and the insertion of replacement characters (like '?'). The fix involved changing the loop termination condition to use the string length and correctly incrementing the position index by the number of chars consumed by the translation, ensuring that surrogate pairs are handled as single units.
