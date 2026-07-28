# Defects4J ODC Classification Report: Mockito-27

- Version: `27b`
- Work directory: `C:\d4j_work\postfix\Mockito_27b`
- Generated: `2026-07-25T12:53:20+00:00`

## Failure Summary
- `org.mockitousage.bugs.ListenersLostOnResetMockTest::listener`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `org.mockitousage.bugs.ListenersLostOnResetMockTest.listener` at `ListenersLostOnResetMockTest.java:23`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a procedural error in how the mock is reset. The original implementation failed to preserve the existing configuration (specifically the invocation listeners) during the reset process. This is a logic error in the method's implementation of the reset operation, making it an Algorithm/Method defect.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
