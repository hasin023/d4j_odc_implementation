# Defects4J ODC Classification Report: Lang-61

- Version: `61b`
- Work directory: `C:\d4j_work\prefix\Lang_61b`
- Generated: `2026-07-10T19:30:19+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderTest::testIndexOfLang294`: junit.framework.AssertionFailedError: expected:<-1> but was:<6>
- `org.apache.commons.lang.text.StrBuilderTest::testLang294`: java.lang.ArrayIndexOutOfBoundsException: arraycopy: length -6 is negative

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilder.deleteImpl` at `StrBuilder.java:1114`
- `org.apache.commons.lang.text.StrBuilder.deleteAll` at `StrBuilder.java:1188`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Off-by-one error in array manipulation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs in the `deleteImpl` method of `StrBuilder`, which is called by `deleteAll`. The `System.arraycopy` call at line 1114 uses `size - endIndex` as the length parameter. When `endIndex` is equal to `size` (i.e., deleting until the end of the buffer), the length becomes 0, which is valid. However, the logic fails to account for cases where the internal state or index calculations in `deleteAll` lead to an invalid range or incorrect buffer shifting, resulting in an `ArrayIndexOutOfBoundsException` or incorrect string state. The stack trace confirms that `System.arraycopy` is receiving invalid parameters, specifically a negative length in some scenarios, indicating that the index arithmetic is flawed.
