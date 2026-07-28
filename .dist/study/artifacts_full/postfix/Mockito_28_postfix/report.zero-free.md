# Defects4J ODC Classification Report: Mockito-28

- Version: `28b`
- Work directory: `C:\d4j_work\postfix\Mockito_28b`
- Generated: `2026-07-25T14:50:08+00:00`

## Failure Summary
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest::mock_should_be_injected_once_and_in_the_best_matching_type`: junit.framework.AssertionFailedError: expected same:<java.lang.Object@59d3495a> was not:<mockedBean>

## Suspicious Frames
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.mock_should_be_injected_once_and_in_the_best_matching_type` at `InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.java:33`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incorrect state management during dependency injection`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurred because the dependency injection engine was not tracking which mocks had already been successfully injected into the target object. When multiple fields were eligible for injection, the engine would repeatedly inject the same mock into all matching fields rather than consuming the mock once it was used. The fix introduces a mechanism to remove the successfully injected mock from the set of available candidates, ensuring each mock is injected only once and preventing subsequent fields from incorrectly receiving an already-injected mock.
