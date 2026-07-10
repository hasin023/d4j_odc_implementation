# Defects4J ODC Classification Report: Lang-17

- Version: `17b`
- Work directory: `C:\d4j_work\prefix\Lang_17b`
- Generated: `2026-07-10T19:36:47+00:00`

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

The failure is a direct result of an incorrect iteration strategy in the translation algorithm. The code attempts to process characters based on code points, which breaks when supplementary characters (represented as surrogate pairs) are present, as they occupy two char slots but one code point.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
