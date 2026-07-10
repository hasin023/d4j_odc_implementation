# Defects4J ODC Classification Report: Cli-17

- Version: `17b`
- Work directory: `C:\d4j_work\prefix\Cli_17b`
- Generated: `2026-07-10T18:56:12+00:00`

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

The defect is in the procedural logic of the parser's tokenization algorithm. It fails to correctly implement the 'stop at non-option' requirement, which is a procedural control flow issue. It is not a missing guard (Checking) because the logic for stopping is present but incorrectly implemented, nor is it a design-level capability issue (Function/Class/Object) as the parser is designed to handle this, but the implementation of the algorithm is flawed.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
