# Defects4J ODC Classification Report: Mockito-27

- Version: `27b`
- Work directory: `C:\d4j_work\postfix\Mockito_27b`
- Generated: `2026-07-25T14:50:04+00:00`

## Failure Summary
- `org.mockitousage.bugs.ListenersLostOnResetMockTest::listener`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `org.mockitousage.bugs.ListenersLostOnResetMockTest.listener` at `ListenersLostOnResetMockTest.java:23`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `State loss during object reset`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the `resetMock` method in `MockUtil` was creating a new `MethodInterceptorFilter` using default settings instead of preserving the existing configuration (such as invocation listeners) of the mock being reset. The fix replaces the creation of a new filter with default settings with a call that retrieves and uses the existing `MockSettings` from the old handler, ensuring that listeners and other configurations are maintained after the reset.
