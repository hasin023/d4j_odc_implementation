# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j_work\postfix\Lang_17b`
- Generated: `2026-07-10T19:44:40+00:00`

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

The defect is a procedural error in the translation loop logic. The algorithm for traversing the input string was flawed because it used code point counts to manage a loop that needed to account for character-level indices and surrogate pair lengths. This is a classic algorithmic/method-level correction of a traversal strategy.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
