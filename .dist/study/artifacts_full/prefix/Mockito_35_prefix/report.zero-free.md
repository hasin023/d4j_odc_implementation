# Defects4J ODC Classification Report: Mockito-35

- Version: `35b`
- Work directory: `C:\d4j_work\prefix\Mockito_35b`
- Generated: `2026-07-25T14:50:34+00:00`

## Failure Summary
- `org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenIntPassed`: java.lang.NullPointerException
- `org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenIntegerPassed`: java.lang.NullPointerException
- `org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenIntegerPassedToEq`: java.lang.NullPointerException
- `org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenIntegerPassedToSame`: java.lang.NullPointerException

## Suspicious Frames
- `org.mockitousage.bugs.NPEWithCertainMatchersTest.shouldNotThrowNPEWhenIntPassed` at `NPEWithCertainMatchersTest.java:38`
- `org.mockitousage.bugs.NPEWithCertainMatchersTest.shouldNotThrowNPEWhenIntegerPassed` at `NPEWithCertainMatchersTest.java:31`
- `org.mockitousage.bugs.NPEWithCertainMatchersTest.shouldNotThrowNPEWhenIntegerPassedToEq` at `NPEWithCertainMatchersTest.java:45`
- `org.mockitousage.bugs.NPEWithCertainMatchersTest.shouldNotThrowNPEWhenIntegerPassedToSame` at `NPEWithCertainMatchersTest.java:52`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `NullPointerException due to unhandled null argument in matcher`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The failing tests demonstrate that Mockito throws a NullPointerException when using argument matchers (like isA, eq, or same) with primitive-type methods on a mock. The stack traces and test context indicate that the framework fails to handle the internal processing of these matchers when the underlying argument is a primitive type, likely due to an improper null check or an attempt to perform an operation on a null object during the argument matching phase.
