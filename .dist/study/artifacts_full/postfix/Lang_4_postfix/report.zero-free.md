# Defects4J ODC Classification Report: Lang-4

- Version: `4b`
- Work directory: `C:\d4j_work\postfix\Lang_4b`
- Generated: `2026-07-10T19:27:29+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882`: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>

## Suspicious Frames
- `org.apache.commons.lang3.text.translate.LookupTranslatorTest.testLang882` at `LookupTranslatorTest.java:48`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Inappropriate use of mutable/non-standard CharSequence as Map key`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The LookupTranslator used a HashMap with CharSequence keys. Because CharSequence implementations (like StringBuffer or CharBuffer) do not guarantee consistent equals() and hashCode() behavior, and specifically because CharBuffer explicitly states it is not equal to other types, lookups in the map failed when the input type did not match the key type stored in the map. The fix involved converting all keys to String, which provides a stable and consistent contract for equality and hashing, ensuring that any CharSequence representation of the same text correctly matches the map entry.
