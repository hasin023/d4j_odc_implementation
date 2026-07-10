# Defects4J ODC Classification Report: Cli-17

- Version: `17b`
- Work directory: `C:\d4j_work\postfix\Cli_17b`
- Generated: `2026-07-08T16:46:36+00:00`

## Failure Summary
- `org.apache.commons.cli.PosixParserTest::testStopBursting`: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2

## Suspicious Frames
- `org.apache.commons.cli.PosixParserTest.testStopBursting` at `PosixParserTest.java:141`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Logic Error / Missing Control Flow Termination`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the PosixParser continues to process (burst) tokens even after encountering a non-option character when 'stopAtNonOption' is enabled. The fix introduces a 'break' statement immediately after processing the remaining token fragment, which correctly halts the bursting process as intended by the configuration. The failure in the test case 'testStopBursting' confirms that the parser was incorrectly treating subsequent characters as options instead of treating them as remaining arguments.
