# Defects4J ODC Classification Report: Mockito-35

- Version: `35b`
- Work directory: `C:\d4j_work\postfix\Mockito_35b`
- Generated: `2026-07-25T12:48:30+00:00`

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
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Assignment/Initialization`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by the matcher methods returning null, which is incompatible with primitive types in Java due to auto-unboxing. The fix correctly initializes the return value based on the class type, which is an Assignment/Initialization issue.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
