# Defects4J ODC Classification Report: Mockito-16

- Version: `16b`
- Work directory: `C:\d4j_work\prefix\Mockito_16b`
- Generated: `2026-07-25T12:50:01+00:00`

## Failure Summary
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest::shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS`: org.mockito.exceptions.misusing.MissingMethodInvocationException:

## Suspicious Frames
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest.shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS` at `StubbingMocksThatAreConfiguredToReturnMocksTest.java:19`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Interface/O-O Messages`
- Family: `Structural`
- Target: `Design/Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The failure occurs because the mock, configured with RETURNS_MOCKS, returns a value during the 'when' call, which interferes with the framework's ability to record the method call as a stubbing target. This is a mismatch in the expected interaction between the 'when' API and the mock's internal handler.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
