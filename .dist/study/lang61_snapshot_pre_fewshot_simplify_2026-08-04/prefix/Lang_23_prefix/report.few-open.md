# Defects4J ODC Classification Report: Lang-23

- Version: `23b`
- Work directory: `C:\d4j_work\prefix\Lang_23b`
- Generated: `2026-07-10T19:23:36+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.ExtendedMessageFormatTest::testEqualsHashcode`: junit.framework.AssertionFailedError: registry, hashcode()

## Suspicious Frames
- `org.apache.commons.lang3.text.ExtendedMessageFormatTest.testEqualsHashcode` at `ExtendedMessageFormatTest.java:301`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is a failure to correctly implement the 'hashCode()' and 'equals()' contract for a class that adds state ('registry') to its parent. This is a procedural logic error in the implementation of the class's identity methods, which falls under Algorithm/Method as it requires correcting the computational strategy for object equality and hashing.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
