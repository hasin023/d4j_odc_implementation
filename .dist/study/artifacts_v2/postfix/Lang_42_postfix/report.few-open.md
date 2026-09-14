# Defects4J ODC Classification Report: Lang-42

- Version: `42b`
- Work directory: `C:\d4j-work\study-work\postfix\Lang_42b`
- Generated: `2026-09-13T17:58:51+00:00`

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
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The fix involves changing the iteration logic from using charAt(i) (which only retrieves 16-bit units) to using Character.codePointAt(str, i) (which correctly handles supplementary characters). Additionally, the logic for processing these characters was updated to account for the multi-unit nature of supplementary characters by incrementing the loop index. This is a fundamental change to the computational procedure for processing characters, fitting the Algorithm/Method definition.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
