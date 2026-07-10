# Defects4J ODC Classification Report: Lang-19

- Version: `19b`
- Work directory: `C:\d4j_work\postfix\Lang_19b`
- Generated: `2026-07-10T19:23:17+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testUnfinishedEntity`: java.lang.StringIndexOutOfBoundsException: String index out of range: 19
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testOutOfBounds`: java.lang.StringIndexOutOfBoundsException: String index out of range: 7

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:54`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:86`
- `org.apache.commons.lang3.text.translate.CharSequenceTranslator.translate` at `CharSequenceTranslator.java:59`
- `org.apache.commons.lang3.text.translate.NumericEntityUnescaper.translate` at `NumericEntityUnescaper.java:44`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic 'Checking' issue. The code failed to validate the input bounds before performing character access, leading to an exception. The fix adds the necessary conditional logic to ensure the index remains within the valid range of the input string.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Reliability`
