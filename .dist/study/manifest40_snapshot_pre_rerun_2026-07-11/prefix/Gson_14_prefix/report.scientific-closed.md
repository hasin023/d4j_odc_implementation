# Defects4J ODC Classification Report: Gson-14

- Version: `14b`
- Work directory: `C:\d4j_work\prefix\Gson_14b`
- Generated: `2026-07-08T17:04:25+00:00`

## Failure Summary
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testDoubleSupertype`: junit.framework.AssertionFailedError: expected:<? super java.lang.Number> but was:<? super ? super java.lang.Number>
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testIssue440WeakReference`: java.lang.StackOverflowError
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testSubSupertype`: junit.framework.AssertionFailedError: expected:<?> but was:<? extends ? super java.lang.Number>
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testDoubleSubtype`: junit.framework.AssertionFailedError: expected:<? extends java.lang.Number> but was:<? extends ? extends java.lang.Number>
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testIssue603PrintStream`: java.lang.StackOverflowError
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testSuperSubtype`: junit.framework.AssertionFailedError: expected:<?> but was:<? super ? extends java.lang.Number>
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testRecursiveResolveSimple`: java.lang.StackOverflowError

## Suspicious Frames
- `com.google.gson.internal.$Gson$Types.getGenericSupertype` at `$Gson$Types.java:238`
- `com.google.gson.internal.$Gson$Types.resolveTypeVariable` at `$Gson$Types.java:408`
- `com.google.gson.internal.$Gson$Types.resolve` at `$Gson$Types.java:333`
- `com.google.gson.internal.$Gson$Types.resolve` at `$Gson$Types.java:382`
- `com.google.gson.internal.$Gson$Types.resolve` at `$Gson$Types.java:387`
- `com.google.gson.internal.$Gson$Types.resolve` at `$Gson$Types.java:362`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.getBoundFields` at `ReflectiveTypeAdapterFactory.java:158`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.create` at `ReflectiveTypeAdapterFactory.java:100`
- `com.google.gson.Gson.getAdapter` at `Gson.java:423`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.createBoundField` at `ReflectiveTypeAdapterFactory.java:115`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The failure is a classic case of an algorithmic deficiency where the recursive resolution logic lacks a base case or simplification step for nested wildcard types. This is not a simple initialization error or a missing guard, but a flaw in the recursive strategy used to resolve generic types.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `New`
- Source: `Requirement`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Test Variation`
- Inferred Impact: `Reliability`
