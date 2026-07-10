# Defects4J ODC Classification Report: Cli-32

- Version: `32b`
- Work directory: `C:\d4j_work\prefix\Cli_32b`
- Generated: `2026-07-10T18:55:11+00:00`

## Failure Summary
- `org.apache.commons.cli.HelpFormatterTest::testRenderWrappedTextWordCut`: java.lang.StringIndexOutOfBoundsException: String index out of range: 12
- `org.apache.commons.cli.HelpFormatterTest::testFindWrapPos`: junit.framework.AssertionFailedError: wrap position 3 expected:<3> but was:<4>

## Suspicious Frames
- `org.apache.commons.cli.HelpFormatter.findWrapPos` at `HelpFormatter.java:937`
- `org.apache.commons.cli.HelpFormatter.renderWrappedText` at `HelpFormatter.java:848`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `off-by-one error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code in HelpFormatter.findWrapPos uses a while loop condition 'pos <= text.length()' to check for characters in the string. When 'pos' equals 'text.length()', the subsequent call to 'text.charAt(pos)' attempts to access an index equal to the string's length, which is out of bounds for a zero-indexed string. This causes a StringIndexOutOfBoundsException. The logic should only check up to 'text.length() - 1' or ensure the index is strictly less than the length before accessing the character.
