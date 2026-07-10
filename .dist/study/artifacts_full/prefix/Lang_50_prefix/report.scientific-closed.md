# Defects4J ODC Classification Report: Lang-50

- Version: `50b`
- Work directory: `C:\d4j_work\prefix\Lang_50b`
- Generated: `2026-07-10T19:40:48+00:00`

## Failure Summary
- `org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateInstance`: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>
- `org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateTimeInstance`: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>

## Suspicious Frames
- `org.apache.commons.lang.time.FastDateFormatTest.test_changeDefault_Locale_DateInstance` at `FastDateFormatTest.java:146`
- `org.apache.commons.lang.time.FastDateFormatTest.test_changeDefault_Locale_DateTimeInstance` at `FastDateFormatTest.java:166`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug report and test failure confirm that FastDateFormat caches instances based on the default locale, but fails to update or invalidate these instances when the default locale changes. This is a classic caching defect where the key is insufficient or the cache is not properly managed.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
