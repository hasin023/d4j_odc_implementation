# Defects4J ODC Classification Report: Mockito-16

- Version: `16b`
- Work directory: `C:\d4j-work\study-work\prefix\Mockito_16b`
- Generated: `2026-09-14T06:01:23+00:00`

## Failure Summary
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest::shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS`: org.mockito.exceptions.misusing.MissingMethodInvocationException:

## Suspicious Frames
- `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest.shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS` at `StubbingMocksThatAreConfiguredToReturnMocksTest.java:19`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is a classic 'Checking' issue where the framework's internal validation logic (checking if a valid mock invocation occurred) is failing due to an interference between the stubbing process and the mock's internal behavior (RETURNS_MOCKS). The fix involves ensuring the invocation is correctly captured before the mock's internal handler processes the return value.

## Scientific Loop

- Turns: `2`
- Termination: `model concluded on its own`
- Loop duration: `5.87s`
- Probe misses: `0`

### Turn 1

**Hypothesis.** The Mockito framework fails to correctly register the method invocation when a mock is configured with RETURNS_MOCKS, because the internal state tracking for 'when()' calls is not correctly handling the nested mock creation triggered by RETURNS_MOCKS.

**Prediction.** The stack trace will reveal that the Mockito internal 'MockHandler' or 'InvocationContainer' is not correctly capturing the invocation because it is being intercepted or cleared by the recursive mock creation logic.

**Probe.** `full_stack_trace` `org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest`

**Observation.**

```json
{
  "traces": [
    {
      "test_name": "org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest::shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS",
      "headline": "org.mockito.exceptions.misusing.MissingMethodInvocationException:",
      "stack_trace": [
        "org.mockito.exceptions.misusing.MissingMethodInvocationException: ",
        "when() requires an argument which has to be a method call on a mock.",
        "For example:",
        "    when(mock.getArticles()).thenReturn(articles);",
        "",
        "Also, this error might show up because you stub final/private/equals() or hashCode() method.",
        "Those methods *cannot* be stubbed/verified.",
        "",
        "\tat org.mockito.exceptions.Reporter.missingMethodInvocation(Reporter.java:77)",
        "\tat org.mockito.internal.MockitoCore.stub(MockitoCore.java:43)",
        "\tat org.mockito.internal.MockitoCore.when(MockitoCore.java:56)",
        "\tat org.mockito.Mockito.when(Mockito.java:994)",
        "\tat org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest.shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS(StubbingMocksThatAreConfiguredToReturnMocksTest.java:19)",
        "\tat java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)",
        "\tat java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)",
        "\tat java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)",
        "\tat java.base/java.lang.reflect.Method.invoke(Method.java:566)",
        "\tat org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:50)",
        "\tat org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)",
        "\tat org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:47)",
        "\tat org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)",

... [truncated — full observation was 4951 chars]
```

_1.861s_

### Turn 2

**Hypothesis.** The MissingMethodInvocationException occurs because when RETURNS_MOCKS is used, the mock object's internal state is modified during the invocation of the method being stubbed. Specifically, the invocation is consumed or cleared by the mock's internal handler before 'when()' can register it, because the mock is already in a state where it is actively creating new mocks for return values.

**Prediction.** The Mockito internal code responsible for tracking the last method invocation (likely in MockitoCore or a related InvocationContainer) is being reset or bypassed when the mock is configured with RETURNS_MOCKS, because the mock's own internal logic for handling method calls interferes with the global state used by 'when()'.

**Concluded**: `Checking`

_4.009s_
