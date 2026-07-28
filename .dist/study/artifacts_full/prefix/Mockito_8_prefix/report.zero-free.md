# Defects4J ODC Classification Report: Mockito-8

- Version: `8b`
- Work directory: `C:\d4j_work\prefix\Mockito_8b`
- Generated: `2026-07-25T14:48:31+00:00`

## Failure Summary
- `org.mockito.internal.util.reflection.GenericMetadataSupportTest::typeVariable_of_self_type`: java.lang.StackOverflowError
- `org.mockitousage.verification.VerificationAfterDelayTest::shouldFailVerificationWithWrongTimes`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$fea7c363.clear` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$fea7c363.clear(<generated>)`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Infinite recursion in generic type resolution`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The stack trace shows a StackOverflowError occurring within the 'getActualTypeArgumentFor' method of 'GenericMetadataSupport'. This method is called recursively when processing generic types. When a type variable has itself as an upper bound (a self-referential generic type), the resolution logic fails to detect the cycle, leading to an infinite loop of recursive calls until the stack is exhausted.
