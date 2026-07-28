# Defects4J ODC Classification Report: Chart-22

- Version: `22b`
- Work directory: `C:\d4j_work\prefix\Chart_22b`
- Generated: `2026-07-25T12:27:26+00:00`

## Failure Summary
- `org.jfree.data.junit.KeyedObjects2DTests::testRemoveColumnByKey`: org.jfree.data.UnknownKeyException: The key (C2) is not recognised.
- `org.jfree.data.junit.KeyedObjects2DTests::testRemoveValue`: junit.framework.AssertionFailedError: expected:<1> but was:<2>
- `org.jfree.data.junit.KeyedObjects2DTests::testGetValueByKey`: org.jfree.data.UnknownKeyException: The key (C2) is not recognised.
- `org.jfree.data.junit.KeyedObjects2DTests::testRemoveColumnByIndex`: org.jfree.data.UnknownKeyException: The key (C1) is not recognised.
- `org.jfree.data.junit.KeyedObjects2DTests::testSetObject`: org.jfree.data.UnknownKeyException: The key (C2) is not recognised.
- `org.jfree.data.junit.KeyedObjects2DTests::testRemoveRowByKey`: java.lang.IndexOutOfBoundsException: Index -1 out of bounds for length 1

## Suspicious Frames
- `org.jfree.data.KeyedObjects.removeValue` at `KeyedObjects.java:268`
- `org.jfree.data.KeyedObjects2D.removeColumn` at `KeyedObjects2D.java:378`
- `org.jfree.data.KeyedObjects.getObject` at `KeyedObjects.java:171`
- `org.jfree.data.KeyedObjects2D.getObject` at `KeyedObjects2D.java:233`
- `org.jfree.data.KeyedObjects2D.removeColumn` at `KeyedObjects2D.java:357`
- `org.jfree.data.KeyedObjects2D.removeRow` at `KeyedObjects2D.java:330`
- `org.jfree.data.KeyedObjects2D.removeRow` at `KeyedObjects2D.java:345`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is an algorithmic failure in maintaining the consistency of the data structure during removal operations. It is not a missing check (the check is present and correctly identifying that the index is invalid, but the index is invalid because the structure is corrupted) nor a simple assignment error. It is a procedural logic error in how the collection is updated.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Reliability`
