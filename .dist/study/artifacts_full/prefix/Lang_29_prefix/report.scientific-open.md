# Defects4J ODC Classification Report: Lang-29

- Version: `29b`
- Work directory: `C:\d4j_work\prefix\Lang_29b`
- Generated: `2026-07-10T19:16:20+00:00`

## Failure Summary
- `org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt`: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>

## Suspicious Frames
- `org.apache.commons.lang3.SystemUtilsTest.testJavaVersionAsInt` at `SystemUtilsTest.java:210`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The test expects an integer but receives a float, which is a classic case of an incorrect implementation of a conversion method.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
