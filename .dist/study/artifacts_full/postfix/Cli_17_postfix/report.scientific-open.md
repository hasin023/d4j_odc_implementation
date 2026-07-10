# Defects4J ODC Classification Report: Cli-17

- Version: `17b`
- Work directory: `C:\d4j_work\postfix\Cli_17b`
- Generated: `2026-07-10T18:35:31+00:00`

## Failure Summary
- `org.apache.commons.cli.PosixParserTest::testStopBursting`: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2

## Suspicious Frames
- `org.apache.commons.cli.PosixParserTest.testStopBursting` at `PosixParserTest.java:141`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a failure to correctly implement the 'stopAtNonOption' requirement. The parser identifies the non-option character but does not stop, which is a failure in the conditional logic (Checking).

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
