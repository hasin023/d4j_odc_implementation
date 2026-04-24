# Defects4J ODC Classification Report: Time-27

- Version: `27b`
- Work directory: `work\Time_27_prefix`
- Generated: `2026-04-24T14:07:49+00:00`

## Failure Summary

- `org.joda.time.format.TestPeriodFormatterBuilder::testBug2495455`: java.lang.IllegalArgumentException: Invalid format: "PT1003199059S" is malformed at "1003199059S"

## Suspicious Frames

- `org.joda.time.format.PeriodFormatter.parseMutablePeriod` at `PeriodFormatter.java:326`
- `org.joda.time.format.PeriodFormatter.parsePeriod` at `PeriodFormatter.java:304`

## ODC Result

- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.85`
- Needs Human Review: `False`

The defect is in the procedural logic of how the PeriodFormatterBuilder assembles the parser components. It is not a missing guard (Checking) or a simple value assignment (Assignment/Initialization), but rather an incorrect implementation of the builder's assembly algorithm that results in a malformed parser state.

## ODC Attribute Mapping (Optional)

- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Recovery/Exception, Test Variation`
- Inferred Impact: `Reliability`
