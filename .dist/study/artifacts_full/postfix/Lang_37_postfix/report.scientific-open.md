# Defects4J ODC Classification Report: Lang-37

- Version: `37b`
- Work directory: `C:\d4j_work\postfix\Lang_37b`
- Generated: `2026-07-10T19:17:37+00:00`

## Failure Summary
- `org.apache.commons.lang3.ArrayUtilsAddTest::testJira567`: java.lang.ArrayStoreException: arraycopy: type mismatch: can not copy java.lang.Long[] into java.lang.Integer[]

## Suspicious Frames
- `org.apache.commons.lang3.ArrayUtils.addAll` at `ArrayUtils.java:2962`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a missing validation of input parameters (the component types of the arrays). The code assumes compatibility and relies on the JVM to throw an ArrayStoreException, which is not the desired API behavior. Adding a check or catching the exception to rethrow a more descriptive one is a classic 'Checking' defect fix.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
