# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j_work\prefix\Lang_17b`
- Generated: `2026-07-10T19:23:09+00:00`

## Failure Summary
- `org.apache.commons.lang3.StringEscapeUtilsTest::testLang720`: junit.framework.ComparisonFailure: expected:<𠮷[A]> but was:<𠮷[?]>

## Suspicious Frames
- `org.apache.commons.lang3.StringEscapeUtilsTest.testLang720` at `StringEscapeUtilsTest.java:431`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a procedural error in the translation algorithm. The loop iteration strategy is fundamentally flawed for the data structure (CharSequence) being processed, as it misinterprets the relationship between code points and character indices. This is a classic Algorithm/Method defect.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
