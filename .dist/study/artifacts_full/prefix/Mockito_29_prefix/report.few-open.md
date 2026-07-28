# Defects4J ODC Classification Report: Mockito-29

- Version: `29b`
- Work directory: `C:\d4j_work\prefix\Mockito_29b`
- Generated: `2026-07-25T12:53:30+00:00`

## Failure Summary
- `org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenNullPassedToSame`: java.lang.Exception: Unexpected exception, expected<java.lang.AssertionError> but was<java.lang.NullPointerException>

## Suspicious Frames
- `org.mockitousage.IMethods$$EnhancerByMockitoWithCGLIB$$96085465.objectArgMethod` at `at org.mockitousage.IMethods$$EnhancerByMockitoWithCGLIB$$96085465.objectArgMethod(<generated>)`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a NullPointerException triggered by passing 'null' to a matcher. This indicates that the matcher's internal logic assumes non-null input and lacks a guard to handle null values, which should result in an assertion failure rather than an unhandled exception. This fits the 'Checking' ODC type perfectly.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Reliability`
