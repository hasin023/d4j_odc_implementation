# Defects4J ODC Classification Report: Lang-59

- Version: `59b`
- Work directory: `C:\d4j_work\prefix\Lang_59b`
- Generated: `2026-07-10T19:42:00+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderAppendInsertTest::testLang299`: java.lang.StringIndexOutOfBoundsException: offset 0, count 3, length 1

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.appendFixedWidthPadRight` at `StrBuilder.java:884`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code logic at line 884 uses 'strLen' as the end index for 'getChars', but the buffer was only ensured to have capacity for 'width'. When 'strLen > width', this exceeds the buffer bounds. The fix is to truncate the string to 'width' by using 'width' as the end index.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
