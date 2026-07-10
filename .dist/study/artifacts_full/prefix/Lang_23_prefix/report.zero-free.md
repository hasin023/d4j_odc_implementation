# Defects4J ODC Classification Report: Lang-23

- Version: `23b`
- Work directory: `C:\d4j_work\prefix\Lang_23b`
- Generated: `2026-07-10T19:28:30+00:00`

## Failure Summary
- `org.apache.commons.lang3.text.ExtendedMessageFormatTest::testEqualsHashcode`: junit.framework.AssertionFailedError: registry, hashcode()

## Suspicious Frames
- `org.apache.commons.lang3.text.ExtendedMessageFormatTest.testEqualsHashcode` at `ExtendedMessageFormatTest.java:301`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Inconsistent hashCode implementation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The class ExtendedMessageFormat extends java.text.MessageFormat but fails to override the equals() and hashCode() methods to account for its own internal state (specifically the registry field). As a result, two instances with different registries are considered equal by the inherited equals() method, and they produce identical hash codes, violating the contract that unequal objects should ideally have different hash codes and that the hashCode must be consistent with equals.
