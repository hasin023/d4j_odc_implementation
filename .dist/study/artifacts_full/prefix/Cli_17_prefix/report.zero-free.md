# Defects4J ODC Classification Report: Cli-17

- Version: `17b`
- Work directory: `C:\d4j_work\prefix\Cli_17b`
- Generated: `2026-07-10T18:52:58+00:00`

## Failure Summary
- `org.apache.commons.cli.PosixParserTest::testStopBursting`: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2

## Suspicious Frames
- `org.apache.commons.cli.PosixParserTest.testStopBursting` at `PosixParserTest.java:141`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect logic in command-line argument parsing`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The PosixParser fails to correctly implement the 'stopAtNonOption' behavior. When parsing a burst token (e.g., '-azc'), if the parser encounters a character that does not correspond to a valid option, it should stop processing the current token and treat the remainder as a non-option argument. Instead, the parser continues to process the remaining characters in the burst token, leading to an incorrect number of arguments being returned in the command line object.
