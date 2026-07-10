# Defects4J ODC Classification Report: Lang-59

- Version: `59b`
- Work directory: `C:\d4j_work\postfix\Lang_59b`
- Generated: `2026-07-10T19:20:31+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderAppendInsertTest::testLang299`: java.lang.StringIndexOutOfBoundsException: offset 0, count 3, length 1

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.appendFixedWidthPadRight` at `StrBuilder.java:884`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code uses 'strLen' as the end index for 'getChars' even when 'strLen' is greater than 'width'. Since the buffer is only ensured to have capacity for 'size + width', attempting to copy 'strLen' characters (where 'strLen > width') results in an out-of-bounds access. This is a classic algorithmic error in handling the copy operation.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
