# Defects4J ODC Classification Report: Gson-14

- Version: `14b`
- Work directory: `C:\d4j_work\postfix\Gson_14b`
- Generated: `2026-07-10T18:46:03+00:00`

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
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.getBoundFields` at `ReflectiveTypeAdapterFactory.java:158`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.create` at `ReflectiveTypeAdapterFactory.java:100`
- `com.google.gson.Gson.getAdapter` at `Gson.java:423`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.createBoundField` at `ReflectiveTypeAdapterFactory.java:115`
- `com.google.gson.internal.bind.ReflectiveTypeAdapterFactory.getBoundFields` at `ReflectiveTypeAdapterFactory.java:164`
- `com.google.gson.internal.$Gson$Types$WildcardTypeImpl.<init>` at `$Gson$Types.java:556`
- `com.google.gson.internal.$Gson$Types.canonicalize` at `$Gson$Types.java:115`
- `com.google.gson.internal.$Gson$Types$WildcardTypeImpl.<init>` at `$Gson$Types.java:549`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a failure to implement the correct algorithmic logic for collapsing nested wildcard types. This is a procedural error in how types are resolved, not a missing check or an incorrect initialization. It fits the definition of Algorithm/Method as it requires implementing the specific collapsing rules provided in the bug report.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
