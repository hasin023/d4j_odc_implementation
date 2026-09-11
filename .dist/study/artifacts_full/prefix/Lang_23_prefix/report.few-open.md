# Defects4J ODC Classification Report: Lang-23

- Version: `23b`
- Work directory: `C:\d4j_work\prefix\Lang_23b`
- Generated: `2026-08-04T17:38:10+00:00`

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

The bug report indicates that ExtendedMessageFormat extends a class but fails to override equals() and hashCode() to account for its own fields (like the registry). This is a procedural logic error in the implementation of the object's equality contract. Since the fix involves implementing these methods correctly to include the class's state, it falls under Algorithm/Method as it is a local procedural correction to the class's internal logic.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
