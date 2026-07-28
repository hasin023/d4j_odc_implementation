# Defects4J ODC Classification Report: Mockito-16

- Version: `16b`
- Work directory: `C:\d4j_work\postfix\Mockito_16b`
- Generated: `2026-07-25T14:49:23+00:00`

## Failure Summary
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest::shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS`: org.mockito.exceptions.misusing.MissingMethodInvocationException:

## Suspicious Frames
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest.shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS` at `StubbingMocksThatAreConfiguredToReturnMocksTest.java:19`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `improper state management in mock creation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs because the creation of a mock object using RETURNS_MOCKS triggers an internal invocation that interferes with the Mockito state machine. Specifically, when a mock is created with RETURNS_MOCKS, it may perform an internal call that is incorrectly interpreted by the framework as an ongoing stubbing attempt. The fix introduces a 'shouldResetOngoingStubbing' flag to ensure that the mocking progress state is properly reset during mock creation, preventing the framework from incorrectly reporting a 'MissingMethodInvocationException' when the user subsequently attempts to stub the mock.
