# Defects4J ODC Classification Report: Lang-50

- Version: `50b`
- Work directory: `C:\d4j_work\postfix\Lang_50b`
- Generated: `2026-07-10T19:47:20+00:00`

## Failure Summary
- `org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateInstance`: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>
- `org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateTimeInstance`: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>

## Suspicious Frames
- `org.apache.commons.lang.time.FastDateFormatTest.test_changeDefault_Locale_DateInstance` at `FastDateFormatTest.java:146`
- `org.apache.commons.lang.time.FastDateFormatTest.test_changeDefault_Locale_DateTimeInstance` at `FastDateFormatTest.java:166`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is an algorithmic flaw in how the cache key is constructed. The procedure for generating the key was inconsistent with the procedure for creating the object, leading to incorrect cache hits. This is a local procedural logic error rather than a missing guard (Checking) or a simple value assignment error.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
