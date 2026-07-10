# Defects4J ODC Classification Report: Lang-37

- Version: `37b`
- Work directory: `C:\d4j_work\prefix\Lang_37b`
- Generated: `2026-07-10T19:46:13+00:00`

## Failure Summary
- `org.apache.commons.lang3.ArrayUtilsAddTest::testJira567`: java.lang.ArrayStoreException: arraycopy: type mismatch: can not copy java.lang.Long[] into java.lang.Integer[]

## Suspicious Frames
- `org.apache.commons.lang3.ArrayUtils.addAll` at `ArrayUtils.java:2962`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The defect is a missing validation check. The code assumes that the second array can be copied into the destination array without verifying type compatibility, leading to a runtime exception. This is a classic 'Checking' defect where a guard condition is missing.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Reliability`
