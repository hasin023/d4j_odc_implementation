# Defects4J ODC Classification Report: Lang-37

- Version: `37b`
- Work directory: `C:\d4j_work\postfix\Lang_37b`
- Generated: `2026-07-10T19:24:46+00:00`

## Failure Summary
- `org.apache.commons.lang3.ArrayUtilsAddTest::testJira567`: java.lang.ArrayStoreException: arraycopy: type mismatch: can not copy java.lang.Long[] into java.lang.Integer[]

## Suspicious Frames
- `org.apache.commons.lang3.ArrayUtils.addAll` at `ArrayUtils.java:2962`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic case of missing validation logic. The code attempts an operation (arraycopy) that is inherently unsafe for mixed types without checking compatibility first. The fix introduces a check (via exception handling) to validate the types and provide a meaningful error, which falls squarely under the 'Checking' category.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Capability`
