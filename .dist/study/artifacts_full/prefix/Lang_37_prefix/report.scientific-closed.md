# Defects4J ODC Classification Report: Lang-37

- Version: `37b`
- Work directory: `C:\d4j_work\prefix\Lang_37b`
- Generated: `2026-07-10T19:39:15+00:00`

## Failure Summary
- `org.apache.commons.lang3.ArrayUtilsAddTest::testJira567`: java.lang.ArrayStoreException: arraycopy: type mismatch: can not copy java.lang.Long[] into java.lang.Integer[]

## Suspicious Frames
- `org.apache.commons.lang3.ArrayUtils.addAll` at `ArrayUtils.java:2962`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a missing validation check (Checking) for the input parameters (array2 elements vs array1 component type). The failure is an unhandled runtime exception (ArrayStoreException) which should be caught and rethrown as an IllegalArgumentException to satisfy the API contract.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
