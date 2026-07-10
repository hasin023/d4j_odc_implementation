# Defects4J ODC Classification Report: Cli-17

- Version: `17b`
- Work directory: `C:\d4j_work\prefix\Cli_17b`
- Generated: `2026-07-08T16:46:34+00:00`

## Failure Summary
- `org.apache.commons.cli.PosixParserTest::testStopBursting`: junit.framework.AssertionFailedError: Confirm  1 extra arg: 2

## Suspicious Frames
- `org.apache.commons.cli.PosixParserTest.testStopBursting` at `PosixParserTest.java:141`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect logic in token parsing loop`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The PosixParser is designed to handle 'bursting' of combined short options (e.g., -azc). When the 'stopAtNonOption' flag is set to true, the parser should stop processing tokens as soon as it encounters a character that is not a valid option. The failing test 'testStopBursting' demonstrates that the parser incorrectly continues to process the remainder of the token string even after encountering a non-option character, resulting in an incorrect number of arguments being returned in the command line object.
