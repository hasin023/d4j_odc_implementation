# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j_work\postfix\Lang_17b`
- Generated: `2026-07-10T19:15:01+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringEscapeUtilsTest::testLang720`: junit.framework.ComparisonFailure: expected:<𠮷[A]> but was:<𠮷[?]>

## Suspicious Frames
- `org.apache.commons.lang3.StringEscapeUtilsTest.testLang720` at `StringEscapeUtilsTest.java:431`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic off-by-one/incorrect-iteration-strategy error where the algorithm assumes a 1:1 mapping between code points and string indices, which is false for surrogate pairs. This is a procedural/algorithmic error.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
