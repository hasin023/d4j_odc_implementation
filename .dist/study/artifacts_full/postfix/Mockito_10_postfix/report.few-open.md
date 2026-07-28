# Defects4J ODC Classification Report: Mockito-10

- Version: `10b`
- Work directory: `C:\d4j_work\postfix\Mockito_10b`
- Generated: `2026-07-25T12:51:27+00:00`

## Failure Summary
- `org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest::should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub`: org.mockito.exceptions.base.MockitoException:

## Suspicious Frames
- `org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest$ToBeDeepStubbed$$EnhancerByMockitoWithCGLIB$$2e47bb2e.getSomething` at `at org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest$ToBeDeepStubbed$$EnhancerByMockitoWithCGLIB$$2e47bb2e.getSomething(<generated>)`
- `org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest.should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub` at `DeepStubsWronglyReportsSerializationProblemsTest.java:16`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug was caused by an incorrect procedural logic in how deep stubs were created. The code was unconditionally applying serialization settings to child mocks. The fix involved modifying the method-level logic to propagate serialization settings from the parent mock instead of forcing them, which is a correction of the internal computational strategy for mock creation.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
