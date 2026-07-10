# Defects4J ODC Classification Report: Cli-17

- Version: `17b`
- Work directory: `C:\d4j_work\postfix\Cli_17b`
- Generated: `2026-07-10T18:56:16+00:00`

## Failure Summary
- `org.apache.commons.cli.PosixParserTest::testStopBursting`: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2

## Suspicious Frames
- `org.apache.commons.cli.PosixParserTest.testStopBursting` at `PosixParserTest.java:141`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The defect is a procedural error in the token bursting algorithm. The parser failed to stop processing when it should have, which is a classic algorithmic control flow issue. It is not a missing guard (Checking) because the condition 'stopAtNonOption' was already being checked; the issue was the lack of a 'break' to terminate the loop/process, which is a procedural/algorithmic step correction.

## ODC Attribute Mapping (Optional)
- Qualifier: `Missing`
- Impact: `Capability`
