# Defects4J ODC Classification Report: Mockito-36

- Version: `36b`
- Work directory: `C:\d4j_work\postfix\Mockito_36b`
- Generated: `2026-07-25T14:51:10+00:00`

## Failure Summary
- `org.mockito.internal.invocation.InvocationTest::shouldScreamWhenCallingRealMethodOnInterface`: java.lang.NullPointerException
- `org.mockitousage.spies.SpyingOnInterfacesTest::shouldFailInRuntimeWhenCallingRealMethodOnInterface`: java.lang.NoSuchMethodError: 'java.lang.Object java.lang.Object.get(int)'

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2.CGLIB$get$9` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2.CGLIB$get$9(<generated>)`
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2$$FastClassByMockitoWithCGLIB$$6401d195.invoke` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2$$FastClassByMockitoWithCGLIB$$6401d195.invoke(<generated>)`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Missing Input Validation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code failed to check if the method being invoked was declared in an interface before attempting to call the real method. In Java, interfaces do not have implementations for their methods, so calling a 'real method' on an interface proxy leads to runtime errors (NullPointerException or NoSuchMethodError) because the underlying CGLIB proxy cannot find a concrete implementation to invoke. The fix introduces a guard clause that explicitly checks if the declaring class is an interface and throws a descriptive MockitoException if it is, preventing the invalid invocation.
