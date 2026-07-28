# Defects4J ODC Classification Report: Mockito-10

- Version: `10b`
- Work directory: `C:\d4j_work\postfix\Mockito_10b`
- Generated: `2026-07-25T14:48:46+00:00`

## Failure Summary
- `org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest::should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub`: org.mockito.exceptions.base.MockitoException:

## Suspicious Frames
- `org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest$ToBeDeepStubbed$$EnhancerByMockitoWithCGLIB$$2e47bb2e.getSomething` at `at org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest$ToBeDeepStubbed$$EnhancerByMockitoWithCGLIB$$2e47bb2e.getSomething(<generated>)`
- `org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest.should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub` at `DeepStubsWronglyReportsSerializationProblemsTest.java:16`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `incorrect propagation of mock configuration`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect occurred because the 'RETURNS_DEEP_STUBS' implementation was unconditionally forcing all nested deep-stubbed mocks to be serializable. This caused a 'MockitoException' when the nested type did not meet the requirements for serialization (e.g., missing a no-arg constructor or not implementing Serializable), even if the user never requested serialization for those specific nested mocks. The fix involved propagating the serialization settings from the parent mock to the child mock, ensuring that the child only attempts to be serializable if the parent was explicitly configured to be so.
