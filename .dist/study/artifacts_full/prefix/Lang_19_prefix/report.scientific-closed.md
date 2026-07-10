# Defects4J ODC Classification Report: Lang-19

- Version: `19b`
- Work directory: `C:\d4j_work\prefix\Lang_19b`
- Generated: `2026-07-10T19:36:55+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testUnfinishedEntity`: java.lang.StringIndexOutOfBoundsException: String index out of range: 19
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testOutOfBounds`: java.lang.StringIndexOutOfBoundsException: String index out of range: 7

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:54`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:86`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:44`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code at line 54: 'while(input.charAt(end) != ';')' lacks a boundary check for 'end < input.length()'. When the input string ends without a semicolon, 'end' increments until it equals 'input.length()', at which point 'input.charAt(end)' throws the observed exception.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
