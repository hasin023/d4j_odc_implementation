# Defects4J ODC Classification Report: Mockito-28

- Version: `28b`
- Work directory: `C:\d4j_work\prefix\Mockito_28b`
- Generated: `2026-07-25T12:46:38+00:00`

## Failure Summary
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest::mock_should_be_injected_once_and_in_the_best_matching_type`: junit.framework.AssertionFailedError: expected same:<java.lang.Object@59d3495a> was not:<mockedBean>

## Suspicious Frames
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.mock_should_be_injected_once_and_in_the_best_matching_type` at `InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.java:33`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a classic case of an incorrect selection algorithm where the order of processing or the lack of specificity checking leads to an incorrect result. This is a procedural logic error in the injection mechanism.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
