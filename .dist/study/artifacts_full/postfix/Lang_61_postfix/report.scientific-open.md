# Defects4J ODC Classification Report: Lang-61

- Version: `61b`
- Work directory: `C:\d4j_work\postfix\Lang_61b`
- Generated: `2026-07-10T19:20:39+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderTest::testIndexOfLang294`: junit.framework.AssertionFailedError: expected:<-1> but was:<6>
- `org.apache.commons.lang.text.StrBuilderTest::testLang294`: java.lang.ArrayIndexOutOfBoundsException: arraycopy: length -6 is negative

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.deleteImpl` at `StrBuilder.java:1114`
- `org.apache.commons.lang.text.StrBuilder.deleteAll` at `StrBuilder.java:1188`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a failure to validate the search range against the current valid size of the StrBuilder. The fix involves changing the loop boundary from the buffer length to the valid string size, which is a classic Checking defect.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
