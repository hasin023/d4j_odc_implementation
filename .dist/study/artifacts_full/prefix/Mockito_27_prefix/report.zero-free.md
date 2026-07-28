# Defects4J ODC Classification Report: Mockito-27

- Version: `27b`
- Work directory: `C:\d4j_work\prefix\Mockito_27b`
- Generated: `2026-07-25T14:50:02+00:00`

## Failure Summary
- `org.mockitousage.bugs.ListenersLostOnResetMockTest::listener`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `org.mockitousage.bugs.ListenersLostOnResetMockTest.listener` at `ListenersLostOnResetMockTest.java:23`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `State management error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs because the `reset()` method in Mockito clears the mock's internal state, including the registered invocation listeners. When `reset(mockedList)` is called, the `InvocationListener` that was configured during the mock's creation is discarded. Consequently, subsequent interactions with the mock (like `mockedList.clear()`) do not trigger the listener, causing the verification of the listener's activity to fail.
