# Defects4J ODC Classification Report: Mockito-36

- Version: `36b`
- Work directory: `C:\d4j-work\study-work\prefix\Mockito_36b`
- Generated: `2026-09-14T06:25:16+00:00`

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
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is caused by the absence of a guard condition that checks if the object being mocked is an interface. When `callRealMethod()` is invoked on an interface, the system proceeds with an invalid operation (attempting to call a real method on an interface which has no implementation), leading to runtime exceptions. Adding a check to validate the type of the mock before proceeding is a classic 'Checking' defect.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
