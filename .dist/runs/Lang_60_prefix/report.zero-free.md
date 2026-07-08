# Defects4J ODC Classification Report: Lang-60

- Version: `60b`
- Work directory: `work/Lang_60b`
- Generated: `2026-07-07T13:58:07+00:00`

## Failure Summary
- `org.apache.commons.lang.text.StrBuilderTest::testLang295`: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

## Suspicious Frames
- `org.apache.commons.lang.text.StrBuilderTest.testLang295` at `StrBuilderTest.java:1748`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect boundary condition usage`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report and failing test indicate that StrBuilder methods like contains() and indexOf() are incorrectly referencing the internal buffer's total capacity (thisBuf.length) instead of the current logical size of the string builder (size). This causes the methods to search beyond the valid data range, leading to incorrect results when the buffer has been modified (e.g., via delete operations).
