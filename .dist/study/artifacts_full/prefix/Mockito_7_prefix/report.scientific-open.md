# Defects4J ODC Classification Report: Mockito-7

- Version: `7b`
- Work directory: `C:\d4j_work\prefix\Mockito_7b`
- Generated: `2026-07-25T12:38:12+00:00`

## Failure Summary
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest::discoverDeepMockingOfGenerics`: org.mockito.exceptions.base.MockitoException: Raw extraction not supported for : 'null'

## Suspicious Frames
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest$MyClass2$$EnhancerByMockitoWithCGLIB$$6c8501ef.getNested` at `at org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest$MyClass2$$EnhancerByMockitoWithCGLIB$$6c8501ef.getNested(<generated>)`
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest.discoverDeepMockingOfGenerics` at `DeepStubFailingWhenGenricNestedAsRawTypeTest.java:26`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The failure is a direct result of an unchecked null value being passed into a method that expects a valid type. This is a classic 'Checking' defect where the predicate logic is missing a null-check guard.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
