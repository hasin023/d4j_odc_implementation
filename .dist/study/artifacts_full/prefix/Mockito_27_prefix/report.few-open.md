# Defects4J ODC Classification Report: Mockito-27

- Version: `27b`
- Work directory: `C:\d4j_work\prefix\Mockito_27b`
- Generated: `2026-07-25T12:53:16+00:00`

## Failure Summary
- `org.mockitousage.bugs.ListenersLostOnResetMockTest::listener`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `org.mockitousage.bugs.ListenersLostOnResetMockTest.listener` at `ListenersLostOnResetMockTest.java:23`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The bug is a procedural error where the 'reset' operation performs an overly aggressive cleanup of the mock's state. It is not a missing check (Checking) or a simple value assignment (Assignment/Initialization), but rather an incorrect implementation of the 'reset' procedure that fails to maintain the required state (listeners).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
