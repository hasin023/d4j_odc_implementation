# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j_work\postfix\Lang_17b`
- Generated: `2026-07-10T19:23:12+00:00`

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

The bug is a fundamental flaw in the iteration strategy of the translation algorithm. The original code used an incorrect loop limit (codePointCount) and incorrect index increment logic for handling multi-char (surrogate pair) characters. The fix replaces this entire procedural logic with a correct iteration strategy that respects character lengths. This is a classic Algorithm/Method defect.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
