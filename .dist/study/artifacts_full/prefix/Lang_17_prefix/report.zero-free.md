# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j_work\prefix\Lang_17b`
- Generated: `2026-07-10T19:28:13+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringEscapeUtilsTest::testLang720`: junit.framework.ComparisonFailure: expected:<𠮷[A]> but was:<𠮷[?]>

## Suspicious Frames
- `org.apache.commons.lang3.StringEscapeUtilsTest.testLang720` at `StringEscapeUtilsTest.java:431`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect loop iteration logic for Unicode supplementary characters`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the translation logic iterates over the input string using code point counts rather than character indices. In Java, supplementary characters (outside the Basic Multilingual Plane) are represented as surrogate pairs (two 16-bit char values). By iterating based on code point count, the logic incorrectly processes the string, leading to the corruption of surrogate pairs and the insertion of replacement characters (like '?') when the translator encounters these multi-char sequences.
