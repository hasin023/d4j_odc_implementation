# Defects4J ODC Classification Report: Lang-37

- Version: `37b`
- Work directory: `C:\d4j_work\postfix\Lang_37b`
- Generated: `2026-07-10T19:29:11+00:00`

## Failure Summary
- `org.apache.commons.lang3.ArrayUtilsAddTest::testJira567`: java.lang.ArrayStoreException: arraycopy: type mismatch: can not copy java.lang.Long[] into java.lang.Integer[]

## Suspicious Frames
- `org.apache.commons.lang3.ArrayUtils.addAll` at `ArrayUtils.java:2962`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Inadequate Exception Handling`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The method ArrayUtils.addAll attempts to perform an array copy using System.arraycopy without validating that the component types of the two input arrays are compatible. When incompatible types are provided (e.g., attempting to copy a Long[] into an Integer[]), the JVM throws an ArrayStoreException, which is a low-level runtime exception that does not clearly communicate the nature of the failure to the API user. The fix introduces a try-catch block around the array copy operation to catch the ArrayStoreException, verify the type incompatibility, and rethrow a more descriptive IllegalArgumentException, which is the expected behavior for an API utility method.
