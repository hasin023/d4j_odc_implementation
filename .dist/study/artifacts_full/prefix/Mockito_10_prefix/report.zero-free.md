# Defects4J ODC Classification Report: Mockito-10

- Version: `10b`
- Work directory: `C:\d4j_work\prefix\Mockito_10b`
- Generated: `2026-07-25T14:48:42+00:00`

## Failure Summary
- `org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest::should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub`: org.mockito.exceptions.base.MockitoException:
- `org.mockitousage.verification.VerificationAfterDelayTest::shouldFailVerificationWithWrongTimes`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$37217199.clear` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$37217199.clear(<generated>)`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect default configuration propagation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The issue arises because the 'RETURNS_DEEP_STUBS' answer incorrectly propagates the 'serializable' setting from the parent mock to the automatically generated deep stub mocks. When a user creates a deep stub, Mockito attempts to validate that the return type is serializable, even if the user did not explicitly request serialization for the nested mock. This causes a 'MockitoException' when the return type does not meet the strict requirements for serialization (e.g., missing no-arg constructor or not implementing Serializable), which is an overly restrictive and incorrect default behavior for deep stubs.
