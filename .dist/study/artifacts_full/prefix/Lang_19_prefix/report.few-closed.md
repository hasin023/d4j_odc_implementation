# Defects4J ODC Classification Report: Lang-19

- Version: `19b`
- Work directory: `C:\d4j_work\prefix\Lang_19b`
- Generated: `2026-07-10T19:44:43+00:00`

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
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic missing boundary check. The logic correctly identifies the start of an entity but fails to validate the end boundary when searching for the terminating semicolon, leading to an out-of-bounds access. This is a 'Checking' defect because the primary issue is the lack of a guard condition to prevent the loop from overrunning the string length.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Reliability`
