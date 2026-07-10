# Defects4J ODC Classification Report: Lang-61

- Version: `61b`
- Work directory: `C:\d4j_work\postfix\Lang_61b`
- Generated: `2026-07-10T19:48:19+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderTest::testIndexOfLang294`: junit.framework.AssertionFailedError: expected:<-1> but was:<6>
- `org.apache.commons.lang.text.StrBuilderTest::testLang294`: java.lang.ArrayIndexOutOfBoundsException: arraycopy: length -6 is negative

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.deleteImpl` at `StrBuilder.java:1114`
- `org.apache.commons.lang.text.StrBuilder.deleteAll` at `StrBuilder.java:1188`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic algorithmic error where the search procedure uses an incorrect boundary (buffer capacity) instead of the logical boundary (current size). This is a procedural logic error within the method, fitting the Algorithm/Method definition perfectly. It is not a missing check (Checking) because the logic itself is fundamentally flawed in its calculation of the search range, nor is it a simple initialization error.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Reliability`
