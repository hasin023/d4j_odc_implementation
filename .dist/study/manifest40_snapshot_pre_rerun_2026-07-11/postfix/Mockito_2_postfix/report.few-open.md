# Defects4J ODC Classification Report: Mockito-2

- Version: `2b`
- Work directory: `C:\d4j_work\postfix\Mockito_2b`
- Generated: `2026-07-08T16:52:08+00:00`

## Failure Summary
- `org.mockito.internal.util.TimerTest::should_throw_friendly_reminder_exception_when_duration_is_negative`: junit.framework.AssertionFailedError: It is forbidden to create timer with negative value of timer's duration.
- `org.mockito.verification.NegativeDurationTest::should_throw_exception_when_duration_is_negative_for_timeout_method`: junit.framework.AssertionFailedError: It is forbidden to invoke Mockito.timeout() with negative value.
- `org.mockito.verification.NegativeDurationTest::should_throw_exception_when_duration_is_negative_for_after_method`: junit.framework.AssertionFailedError: It is forbidden to invoke Mockito.after() with negative value.
- `org.mockitousage.verification.VerificationAfterDelayTest::shouldFailVerificationWithWrongTimes`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$ccb6d0f1.clear` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$ccb6d0f1.clear(<generated>)`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a classic missing guard condition. The code allowed an invalid parameter (negative duration) to propagate into the system state. The fix introduces a validation check to enforce the contract that durations must be non-negative, which is the definition of a 'Checking' defect in ODC.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Recovery/Exception, Test Sequencing, Test Variation`
- Inferred Impact: `Reliability`
