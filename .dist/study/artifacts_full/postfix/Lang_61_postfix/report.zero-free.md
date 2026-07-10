# Defects4J ODC Classification Report: Lang-61

- Version: `61b`
- Work directory: `C:\d4j_work\postfix\Lang_61b`
- Generated: `2026-07-10T19:30:20+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderTest::testIndexOfLang294`: junit.framework.AssertionFailedError: expected:<-1> but was:<6>
- `org.apache.commons.lang.text.StrBuilderTest::testLang294`: java.lang.ArrayIndexOutOfBoundsException: arraycopy: length -6 is negative

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.deleteImpl` at `StrBuilder.java:1114`
- `org.apache.commons.lang.text.StrBuilder.deleteAll` at `StrBuilder.java:1188`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `incorrect boundary condition in search algorithm`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the indexOf method in StrBuilder was searching the entire underlying character buffer, including 'junk' data beyond the current valid size of the string. This caused the method to return incorrect indices (finding matches in the buffer's tail) and subsequently caused ArrayIndexOutOfBoundsException in methods like deleteImpl and replaceImpl, which relied on these incorrect indices to perform array operations. The fix correctly limits the search range to the current valid size of the string.
