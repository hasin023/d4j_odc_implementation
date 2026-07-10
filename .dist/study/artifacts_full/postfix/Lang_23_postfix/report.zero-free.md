# Defects4J ODC Classification Report: Lang-23

- Version: `23b`
- Work directory: `C:\d4j_work\postfix\Lang_23b`
- Generated: `2026-07-10T19:28:32+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.ExtendedMessageFormatTest::testEqualsHashcode`: junit.framework.AssertionFailedError: registry, hashcode()

## Suspicious Frames
- `org.apache.commons.lang3.text.ExtendedMessageFormatTest.testEqualsHashcode` at `ExtendedMessageFormatTest.java:301`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Missing Override of equals() and hashCode()`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The class ExtendedMessageFormat extends java.text.MessageFormat but introduces new fields (registry and toPattern) that affect the logical equality of the object. The original implementation failed to override equals() and hashCode(), causing instances with different registries or patterns to be considered equal by the default implementation inherited from the superclass or Object. The fix correctly implements these methods to include the new fields in the equality and hash calculation, ensuring that the object's state is properly accounted for.
