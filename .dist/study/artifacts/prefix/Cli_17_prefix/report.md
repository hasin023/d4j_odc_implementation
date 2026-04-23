# Defects4J ODC Classification Report: Cli-17

- Version: `17b`
- Work directory: `.dist\study\work\prefix\Cli_17b`
- Generated: `2026-04-21T11:17:55+00:00`

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

The issue is a failure in the procedural logic of the parser. It is not a missing guard (Checking) because the parser is actively doing the wrong thing (continuing to burst) rather than failing to validate. It is not an Assignment/Initialization issue because the logic flow itself is flawed. It is an Algorithm/Method defect because the procedure for token bursting is implemented incorrectly.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Test Variation`
- Inferred Impact: `Capability`
