# Defects4J ODC Classification Report: Mockito-7

- Version: `7b`
- Work directory: `C:\d4j_work\postfix\Mockito_7b`
- Generated: `2026-07-25T12:51:07+00:00`

## Failure Summary
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest::discoverDeepMockingOfGenerics`: org.mockito.exceptions.base.MockitoException: Raw extraction not supported for : 'null'
- `org.mockitousage.verification.VerificationAfterDelayTest::shouldFailVerificationWithWrongTimes`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$325b00db.clear` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$325b00db.clear(<generated>)`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The fix involves adding a missing procedural step (registering type parameters) to the metadata extraction algorithm. This is a classic Algorithm/Method defect where the logic for traversing and registering generic type information was incomplete, causing it to fail on nested generic structures. It is not a 'Checking' bug because no guard was missing; rather, the computational process of metadata registration was insufficient.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Capability`
