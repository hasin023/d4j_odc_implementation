# Defects4J ODC Classification Report: Mockito-36

- Version: `36b`
- Work directory: `C:\d4j_work\prefix\Mockito_36b`
- Generated: `2026-07-25T14:51:07+00:00`

## Failure Summary
- `org.mockito.internal.invocation.InvocationTest::shouldScreamWhenCallingRealMethodOnInterface`: java.lang.NullPointerException
- `org.mockitousage.spies.SpyingOnInterfacesTest::shouldFailInRuntimeWhenCallingRealMethodOnInterface`: java.lang.NoSuchMethodError: 'java.lang.Object java.lang.Object.get(int)'

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2.CGLIB$get$9` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2.CGLIB$get$9(<generated>)`
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2$$FastClassByMockitoWithCGLIB$$6401d195.invoke` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$673aa9b2$$FastClassByMockitoWithCGLIB$$6401d195.invoke(<generated>)`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Invalid invocation of real methods on interfaces`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The system attempts to invoke a 'real method' on an interface mock. Since interfaces do not have implementation code for their methods, the underlying CGLIB proxy mechanism fails to find a method body to execute. This results in either a NullPointerException when the proxy logic attempts to access non-existent method metadata or a NoSuchMethodError when the generated proxy class tries to delegate to a non-existent superclass method. The framework lacks a guard clause to prevent the execution of real methods on interface-based mocks.
