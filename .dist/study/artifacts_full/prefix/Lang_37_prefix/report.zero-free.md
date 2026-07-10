# Defects4J ODC Classification Report: Lang-37

- Version: `37b`
- Work directory: `C:\d4j_work\prefix\Lang_37b`
- Generated: `2026-07-10T19:29:10+00:00`

## Failure Summary
- `org.apache.commons.lang3.ArrayUtilsAddTest::testJira567`: java.lang.ArrayStoreException: arraycopy: type mismatch: can not copy java.lang.Long[] into java.lang.Integer[]

## Suspicious Frames
- `org.apache.commons.lang3.ArrayUtils.addAll` at `ArrayUtils.java:2962`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Type safety violation in array concatenation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The method ArrayUtils.addAll uses the component type of the first array (array1) to create a new array for the result. When the second array (array2) contains elements that are not assignable to the component type of the first array, System.arraycopy throws an ArrayStoreException. The implementation fails to validate that the elements of the second array are compatible with the type of the destination array before attempting the copy operation.
