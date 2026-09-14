# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j-work\study-work\prefix\Lang_42b`
- Generated: `2026-09-13T17:58:48+00:00`

## Failure Summary
- `org.apache.commons.lang.StringEscapeUtilsTest::testEscapeHtmlHighUnicode`: junit.framework.ComparisonFailure: High unicode was not escaped correctly expected:<&#[119650];> but was:<&#[55348;&#57186];>

## Suspicious Frames
- `org.apache.commons.lang.StringEscapeUtilsTest.testEscapeHtmlHighUnicode` at `StringEscapeUtilsTest.java:430`
- `org.apache.commons.lang.exception.Nestable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang.mutable.Mutable.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang.text.FormatFactory.` at `coverage: line_rate=1.00`
- `org.apache.commons.lang.Entities.` at `org/apache/commons/lang/Entities.java:737`
- `org.apache.commons.lang.IntHashMap.` at `org/apache/commons/lang/IntHashMap.java:268`
- `org.apache.commons.lang.StringEscapeUtils.` at `org/apache/commons/lang/StringEscapeUtils.java:46`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The issue is a procedural error in how the character escaping algorithm processes high-unicode characters. The code treats surrogate pairs as two distinct characters rather than a single character, which is a flaw in the computational logic of the escaping method. This is a classic algorithmic defect where the procedure for identifying and converting characters needs to be updated to correctly handle multi-char surrogate pairs.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
