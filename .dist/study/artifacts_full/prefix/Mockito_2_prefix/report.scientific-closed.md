# Defects4J ODC Classification Report: Mockito-2

- Version: `2b`
- Work directory: `C:\d4j_work\prefix\Mockito_2b`
- Generated: `2026-07-10T18:48:36+00:00`

## Failure Summary
- `org.mockito.internal.util.TimerTest::should_throw_friendly_reminder_exception_when_duration_is_negative`: junit.framework.AssertionFailedError: It is forbidden to create timer with negative value of timer's duration.
- `org.mockito.verification.NegativeDurationTest::should_throw_exception_when_duration_is_negative_for_timeout_method`: junit.framework.AssertionFailedError: It is forbidden to invoke Mockito.timeout() with negative value.
- `org.mockito.verification.NegativeDurationTest::should_throw_exception_when_duration_is_negative_for_after_method`: junit.framework.AssertionFailedError: It is forbidden to invoke Mockito.after() with negative value.
- `org.mockitousage.verification.VerificationAfterDelayTest::shouldFailVerificationWithWrongTimes`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$71cb44f1.clear` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$71cb44f1.clear(<generated>)`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The failing tests explicitly check for a FriendlyReminderException when passing negative values to Timer, Mockito.timeout(), and Mockito.after(). Since the tests fail with an AssertionFailedError (meaning the exception was not thrown), the code is clearly missing the necessary guard/check for negative input values.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
