# Defects4J ODC Classification Report: Mockito-7

- Version: `7b`
- Work directory: `C:\d4j_work\prefix\Mockito_7b`
- Generated: `2026-07-25T12:51:03+00:00`

## Failure Summary
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest::discoverDeepMockingOfGenerics`: org.mockito.exceptions.base.MockitoException: Raw extraction not supported for : 'null'

## Suspicious Frames
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest$MyClass2$$EnhancerByMockitoWithCGLIB$$6c8501ef.getNested` at `at org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest$MyClass2$$EnhancerByMockitoWithCGLIB$$6c8501ef.getNested(<generated>)`
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest.discoverDeepMockingOfGenerics` at `DeepStubFailingWhenGenricNestedAsRawTypeTest.java:26`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The issue is a failure in the procedural logic that traverses and extracts generic type information. It is not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object), but rather an incorrect implementation of the algorithm used to resolve nested generic types.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Reliability`
