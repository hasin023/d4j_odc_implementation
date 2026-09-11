# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j_work\postfix\Lang_17b`
- Generated: `2026-08-04T17:37:44+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringEscapeUtilsTest::testLang720`: junit.framework.ComparisonFailure: expected:<𠮷[A]> but was:<𠮷[?]>

## Suspicious Frames
- `org.apache.commons.lang3.StringEscapeUtilsTest.testLang720` at `StringEscapeUtilsTest.java:431`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by an incorrect iteration strategy in the translate method. The original code used Character.codePointCount to determine the loop limit and incremented the position variable incorrectly, failing to account for surrogate pairs correctly. The fix involves rewriting the loop logic to iterate based on the string length and correctly incrementing the position by the character count of the processed code points. This is a procedural/algorithmic error in how the string is traversed and translated.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
