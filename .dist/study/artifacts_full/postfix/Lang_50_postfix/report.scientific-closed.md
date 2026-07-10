# Defects4J ODC Classification Report: Lang-50

- Version: `50b`
- Work directory: `C:\d4j_work\postfix\Lang_50b`
- Generated: `2026-07-10T19:40:52+00:00`

## Failure Summary
- `org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateInstance`: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>
- `org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateTimeInstance`: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>

## Suspicious Frames
- `org.apache.commons.lang.time.FastDateFormatTest.test_changeDefault_Locale_DateInstance` at `FastDateFormatTest.java:146`
- `org.apache.commons.lang.time.FastDateFormatTest.test_changeDefault_Locale_DateTimeInstance` at `FastDateFormatTest.java:166`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report and test failure confirm that FastDateFormat caches instances based on a key that does not include the default locale when the locale parameter is null. When the default locale changes, the cache returns the old instance, violating the expected behavior. This is a validation/checking error in the cache key generation logic.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
