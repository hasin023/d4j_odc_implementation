# Defects4J ODC Classification Report: Mockito-14

- Version: `14b`
- Work directory: `C:\d4j_work\prefix\Mockito_14b`
- Generated: `2026-07-25T12:39:55+00:00`

## Failure Summary
- `org.mockitousage.bugs.VerifyingWithAnExtraCallToADifferentMockTest::shouldAllowVerifyingWhenOtherMockCallIsInTheSameLine`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `org.mockitousage.IMethods$$EnhancerByMockitoWithCGLIB$$e070360c.otherMethod` at `at org.mockitousage.IMethods$$EnhancerByMockitoWithCGLIB$$e070360c.otherMethod(<generated>)`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The failure occurs because Mockito's state machine for verification is not re-entrant or does not handle nested mock calls during the verification phase. This is a procedural logic error in how Mockito tracks the 'verification' state versus the 'invocation' state.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
