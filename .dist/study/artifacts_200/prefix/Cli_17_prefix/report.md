# Defects4J ODC Classification Report: Cli-17

- Version: `17b`
- Work directory: `.dist\study\work\prefix\Cli_17b`
- Generated: `2026-04-24T18:56:52+00:00`

## Failure Summary
- `org.apache.commons.cli.PosixParserTest::testStopBursting`: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2

## Suspicious Frames
- `org.apache.commons.cli.PosixParserTest.testStopBursting` at `PosixParserTest.java:141`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is a failure in the procedural logic of the parser's token-bursting algorithm. It is not a missing guard (Checking) because the logic exists but is flawed in its execution flow, nor is it an initialization issue. It is a classic algorithmic error where the iteration strategy fails to respect the stop condition.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Test Variation`
- Inferred Impact: `Capability`
