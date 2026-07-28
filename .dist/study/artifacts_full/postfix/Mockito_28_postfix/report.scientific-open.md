# Defects4J ODC Classification Report: Mockito-28

- Version: `28b`
- Work directory: `C:\d4j_work\postfix\Mockito_28b`
- Generated: `2026-07-25T12:46:46+00:00`

## Failure Summary
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest::mock_should_be_injected_once_and_in_the_best_matching_type`: junit.framework.AssertionFailedError: expected same:<java.lang.Object@59d3495a> was not:<mockedBean>

## Suspicious Frames
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.mock_should_be_injected_once_and_in_the_best_matching_type` at `InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.java:33`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic case of an incorrect iteration strategy where the state (the set of available mocks) is not updated after a successful operation, leading to incorrect subsequent behavior. This is a procedural/algorithmic flaw.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
