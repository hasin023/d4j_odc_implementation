# Defects4J ODC Classification Report: Lang-47

- Version: `47b`
- Work directory: `C:\d4j_work\prefix\Lang_47b`
- Generated: `2026-07-10T19:25:31+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderTest::testLang412Left`: java.lang.NullPointerException
- `org.apache.commons.lang.text.StrBuilderTest::testLang412Right`: java.lang.NullPointerException

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.appendFixedWidthPadLeft` at `StrBuilder.java:1186`
- `org.apache.commons.lang.text.StrBuilder.appendFixedWidthPadRight` at `StrBuilder.java:1230`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic missing guard/validation. The code performs an operation (str.length()) on a variable that can be null without checking for that nullity first. This fits the definition of 'Checking' perfectly.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Reliability`
