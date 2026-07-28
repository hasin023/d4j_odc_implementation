# Defects4J ODC Classification Report: Mockito-8

- Version: `8b`
- Work directory: `C:\d4j_work\prefix\Mockito_8b`
- Generated: `2026-07-25T12:38:25+00:00`

## Failure Summary
- `org.mockito.internal.util.reflection.GenericMetadataSupportTest::typeVariable_of_self_type`: java.lang.StackOverflowError
- `org.mockitousage.verification.VerificationAfterDelayTest::shouldFailVerificationWithWrongTimes`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$fea7c363.clear` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$fea7c363.clear(<generated>)`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The failure is a classic infinite recursion in a recursive algorithm. The fix involves adding a state-tracking mechanism (like a set of visited types) to the method, which is a procedural/algorithmic change.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
