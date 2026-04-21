# Defects4J ODC Classification Report: Gson-14

- Version: `14b`
- Work directory: `.dist\study\work\prefix\Gson_14b`
- Generated: `2026-04-21T13:44:46+00:00`

## Failure Summary
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testDoubleSupertype`: junit.framework.AssertionFailedError: expected:<? super java.lang.Number> but was:<? super ? super java.lang.Number>
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testIssue440WeakReference`: java.lang.StackOverflowError
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testSubSupertype`: junit.framework.AssertionFailedError: expected:<?> but was:<? extends ? super java.lang.Number>
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testDoubleSubtype`: junit.framework.AssertionFailedError: expected:<? extends java.lang.Number> but was:<? extends ? extends java.lang.Number>
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testIssue603PrintStream`: java.lang.StackOverflowError
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testSuperSubtype`: junit.framework.AssertionFailedError: expected:<?> but was:<? super ? extends java.lang.Number>
- `com.google.gson.internal.bind.RecursiveTypesResolveTest::testRecursiveResolveSimple`: java.lang.StackOverflowError

## Suspicious Frames
- `com.google.gson.internal.$Gson$Types.resolve` at `$Gson$Types.java:387`
- `com.google.gson.internal.$Gson$Types.resolve` at `$Gson$Types.java:382`
- `com.google.gson.internal.$Gson$Types.resolve` at `$Gson$Types.java:362`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.getBoundFields` at `ReflectiveTypeAdapterFactory.java:158`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.create` at `ReflectiveTypeAdapterFactory.java:100`
- `com.google.gson.Gson.getAdapter` at `Gson.java:423`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.createBoundField` at `ReflectiveTypeAdapterFactory.java:115`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.getBoundFields` at `ReflectiveTypeAdapterFactory.java:164`
- `com.google.gson.internal.$Gson$Types.resolve` at `$Gson$Types.java:378`
- `com.google.gson.internal.$Gson$Types.declaringClassOf` at `$Gson$Types.java:431`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

This is an Algorithm/Method defect because the procedure for resolving generic types is computationally incomplete. It fails to handle recursive cases by not implementing the necessary simplification/collapsing logic for wildcard bounds. It is not a Checking bug because the issue is not a missing guard, but a missing algorithmic step to handle the recursive structure of the data.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Test Sequencing, Test Variation`
- Inferred Impact: `Reliability`
