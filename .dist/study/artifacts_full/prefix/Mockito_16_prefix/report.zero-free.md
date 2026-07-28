# Defects4J ODC Classification Report: Mockito-16

- Version: `16b`
- Work directory: `C:\d4j_work\prefix\Mockito_16b`
- Generated: `2026-07-25T14:49:20+00:00`

## Failure Summary
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest::shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS`: org.mockito.exceptions.misusing.MissingMethodInvocationException:

## Suspicious Frames
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest.shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS` at `StubbingMocksThatAreConfiguredToReturnMocksTest.java:19`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect Mock State Handling`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The error 'MissingMethodInvocationException' occurs when using 'when()' on a mock configured with 'RETURNS_MOCKS'. This happens because the 'RETURNS_MOCKS' answer creates a new mock object during the invocation of the method, which interferes with Mockito's internal state tracking for the 'when()' call. The framework incorrectly identifies the nested mock creation as the active invocation, causing the stubbing process to fail to register the intended method call.
