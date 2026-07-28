# Defects4J ODC Classification Report: Mockito-7

- Version: `7b`
- Work directory: `C:\d4j_work\postfix\Mockito_7b`
- Generated: `2026-07-25T14:48:25+00:00`

## Failure Summary
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest::discoverDeepMockingOfGenerics`: org.mockito.exceptions.base.MockitoException: Raw extraction not supported for : 'null'
- `org.mockitousage.verification.VerificationAfterDelayTest::shouldFailVerificationWithWrongTimes`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$325b00db.clear` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$325b00db.clear(<generated>)`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incomplete Type Metadata Registration`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs during deep stubbing when dealing with nested generic types. The system fails to correctly resolve the metadata for nested generics, leading to a 'null' value during raw type extraction. The fix involves adding a call to 'registerTypeParametersOn' within the 'TypeVariableReturnType' constructor in 'GenericMetadataSupport'. This ensures that the type variables are properly registered in the metadata context before attempting to resolve their actual type arguments, preventing the null pointer or invalid state that caused the 'Raw extraction not supported' exception.
