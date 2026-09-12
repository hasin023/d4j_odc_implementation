# Defects4J ODC Classification Report: Lang-23

- Version: `23b`
- Work directory: `C:\d4j_work\postfix\Lang_23b`
- Generated: `2026-07-10T19:23:40+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.ExtendedMessageFormatTest::testEqualsHashcode`: junit.framework.AssertionFailedError: registry, hashcode()

## Suspicious Frames
- `org.apache.commons.lang3.text.ExtendedMessageFormatTest.testEqualsHashcode` at `ExtendedMessageFormatTest.java:301`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a failure to correctly implement the object equality and hashing contract for a subclass. While this is a structural issue, the fix is a procedural implementation of the required methods (the algorithm for equality and hashing). It is not a design-level capability omission (Function/Class/Object) because the class existed and functioned, but its internal logic for equality was incomplete/incorrect. It is not a Checking bug because it is not a missing guard, but a missing implementation of a standard method.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Capability`
