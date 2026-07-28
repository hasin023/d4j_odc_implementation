# Defects4J ODC Classification Report: Mockito-16

- Version: `16b`
- Work directory: `C:\d4j_work\postfix\Mockito_16b`
- Generated: `2026-07-25T12:42:44+00:00`

## Failure Summary
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest::shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS`: org.mockito.exceptions.misusing.MissingMethodInvocationException:

## Suspicious Frames
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest.shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS` at `StubbingMocksThatAreConfiguredToReturnMocksTest.java:19`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The `MissingMethodInvocationException` occurs because the framework's `mockingProgress` state is not being correctly reset or validated when a mock is created with `RETURNS_MOCKS`. The fix explicitly adds a `resetOngoingStubbing()` call in `MockitoCore.mock` to ensure that the state is clean before the mock is used, which is a validation/checking issue regarding the internal state of the stubbing process.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
