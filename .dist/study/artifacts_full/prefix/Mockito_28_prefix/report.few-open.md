# Defects4J ODC Classification Report: Mockito-28

- Version: `28b`
- Work directory: `C:\d4j_work\prefix\Mockito_28b`
- Generated: `2026-07-25T12:53:24+00:00`

## Failure Summary
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest::mock_should_be_injected_once_and_in_the_best_matching_type`: junit.framework.AssertionFailedError: expected same:<java.lang.Object@59d3495a> was not:<mockedBean>

## Suspicious Frames
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.mock_should_be_injected_once_and_in_the_best_matching_type` at `InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.java:33`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The issue is a failure in the selection logic (the 'algorithm') used to determine which field to inject a mock into. It is not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object). The injection mechanism exists, but its internal procedure for matching types is incorrect, making Algorithm/Method the most appropriate ODC type.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
