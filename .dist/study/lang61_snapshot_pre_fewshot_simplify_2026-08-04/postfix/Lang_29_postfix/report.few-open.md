# Defects4J ODC Classification Report: Lang-29

- Version: `29b`
- Work directory: `C:\d4j_work\postfix\Lang_29b`
- Generated: `2026-07-10T19:24:01+00:00`

## Failure Summary
- `org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt`: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>

## Suspicious Frames
- `org.apache.commons.lang3.SystemUtilsTest.testJavaVersionAsInt` at `SystemUtilsTest.java:210`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Interface/O-O Messages`
- Family: `Structural`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a classic interface/contract mismatch. The method was intended to return an integer representation of a version (e.g., 131), but was declared to return a float. This caused the test suite to fail when it expected an integer but received a float (e.g., 0.0). The fix is a signature change, which falls under Interface/O-O Messages.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Reliability`
