# Defects4J ODC Classification Report: Mockito-7

- Version: `7b`
- Work directory: `C:\d4j_work\postfix\Mockito_7b`
- Generated: `2026-07-25T12:38:19+00:00`

## Failure Summary
- `org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest::discoverDeepMockingOfGenerics`: org.mockito.exceptions.base.MockitoException: Raw extraction not supported for : 'null'
- `org.mockitousage.verification.VerificationAfterDelayTest::shouldFailVerificationWithWrongTimes`: junit.framework.AssertionFailedError:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$325b00db.clear` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$325b00db.clear(<generated>)`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The failure occurs because the metadata extraction logic is incomplete for nested generics. The fix adds a missing step in the algorithm to register type parameters, which is a classic procedural/algorithmic correction.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
