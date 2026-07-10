# Defects4J ODC Classification Report: JacksonDatabind-111

- Version: `111b`
- Work directory: `C:\d4j_work\prefix\JacksonDatabind_111b`
- Generated: `2026-07-10T18:46:30+00:00`

## Failure Summary
- `com.fasterxml.jackson.databind.deser.jdk.JDKAtomicTypesDeserTest::testNullWithinNested`: junit.framework.AssertionFailedError

## Suspicious Frames
- `com.fasterxml.jackson.databind.deser.jdk.JDKAtomicTypesDeserTest.testNullWithinNested` at `JDKAtomicTypesDeserTest.java:298`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Assignment/Initialization`
- Family: `Control and Data Flow`
- Target: `null`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug report provides a clear explanation of the root cause: the bean property creator has distinct deserializer and nullProvider, and when the ReferenceTypeDeserializer is contextualized, the nullProvider is not updated. This is an initialization error where the state of the deserializer is not correctly set up for the nested case.

## ODC Attribute Mapping (Optional)
- Qualifier: `null`
- Impact: `Capability`
