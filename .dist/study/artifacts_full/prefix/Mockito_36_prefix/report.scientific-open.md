# Defects4J ODC Classification Report: Mockito-36

- Version: `36b`
- Work directory: `C:\d4j_work\prefix\Mockito_36b`
- Generated: `2026-07-25T12:48:39+00:00`

## Failure Summary
- `org.mockito.internal.invocation.InvocationTest::shouldScreamWhenCallingRealMethodOnInterface`: java.lang.NullPointerException
- `org.mockitousage.spies.SpyingOnInterfacesTest::shouldFailInRuntimeWhenCallingRealMethodOnInterface`: java.lang.NoSuchMethodError: 'java.lang.Object java.lang.Object.get(int)'

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2.CGLIB$get$9` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2.CGLIB$get$9(<generated>)`
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2$$FastClassByMockitoWithCGLIB$$6401d195.invoke` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2$$FastClassByMockitoWithCGLIB$$6401d195.invoke(<generated>)`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is caused by the absence of a check to prevent calling real methods on interfaces, which is an invalid operation. Adding a check to validate the mock type before proceeding is a 'Checking' fix.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
