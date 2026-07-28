# Defects4J ODC Classification Report: Mockito-7

- Version: `7b`
- Work directory: `C:\d4j_work\prefix\Mockito_7b`
- Generated: `2026-07-25T14:48:18+00:00`

## Failure Summary
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest::discoverDeepMockingOfGenerics`: org.mockito.exceptions.base.MockitoException: Raw extraction not supported for : 'null'

## Suspicious Frames
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest$MyClass2$$EnhancerByMockitoWithCGLIB$$6c8501ef.getNested` at `at org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest$MyClass2$$EnhancerByMockitoWithCGLIB$$6c8501ef.getNested(<generated>)`
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest.discoverDeepMockingOfGenerics` at `DeepStubFailingWhenGenricNestedAsRawTypeTest.java:26`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incomplete Generic Type Metadata Resolution`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The issue arises when Mockito's deep stubbing mechanism attempts to resolve nested generic types in a call chain. When the chain involves multiple levels of generics, the internal metadata support class fails to correctly extract the raw type for the nested generic, resulting in a null value being passed to a method that expects a valid type. The stack trace confirms that 'Raw extraction not supported for : null' occurs within the GenericMetadataSupport class, indicating that the system fails to propagate or resolve the generic type information correctly through the chain of nested interfaces.
