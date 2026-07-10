# Defects4J ODC Classification Report: Lang-47

- Version: `47b`
- Work directory: `C:\d4j_work\postfix\Lang_47b`
- Generated: `2026-07-10T19:25:34+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderTest::testLang412Left`: java.lang.NullPointerException
- `org.apache.commons.lang.text.StrBuilderTest::testLang412Right`: java.lang.NullPointerException

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.appendFixedWidthPadLeft` at `StrBuilder.java:1186`
- `org.apache.commons.lang.text.StrBuilder.appendFixedWidthPadRight` at `StrBuilder.java:1230`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by a missing guard (null check) on the string variable before calling .length() on it. This fits the definition of 'Checking' perfectly, as the logic is correct for non-null strings, but it fails to validate the data (the string representation) before proceeding with the computation.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Reliability`
