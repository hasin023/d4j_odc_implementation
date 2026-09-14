# Defects4J ODC Classification Report: Mockito-28

- Version: `28b`
- Work directory: `C:\d4j-work\study-work\prefix\Mockito_28b`
- Generated: `2026-09-14T06:24:30+00:00`

## Failure Summary
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest::mock_should_be_injected_once_and_in_the_best_matching_type`: junit.framework.AssertionFailedError: expected same:<java.lang.Object@59d3495a> was not:<mockedBean>

## Suspicious Frames
- `org.mockitousage.bugs.InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.mock_should_be_injected_once_and_in_the_best_matching_type` at `InjectionByTypeShouldFirstLookForExactTypeThenAncestorTest.java:33`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The bug involves the logic used to select the 'best matching' field for dependency injection. The failure to distinguish between an exact type match and a broader ancestor type match indicates that the selection algorithm (the procedure for iterating and matching fields) is flawed. This is a procedural logic error in how the injection algorithm evaluates candidates, rather than a missing guard or a simple assignment error.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
