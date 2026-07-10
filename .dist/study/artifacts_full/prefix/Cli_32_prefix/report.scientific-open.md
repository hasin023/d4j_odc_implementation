# Defects4J ODC Classification Report: Cli-32

- Version: `32b`
- Work directory: `C:\d4j_work\prefix\Cli_32b`
- Generated: `2026-07-10T18:40:50+00:00`

## Failure Summary
- `org.apache.commons.cli.HelpFormatterTest::testRenderWrappedTextWordCut`: java.lang.StringIndexOutOfBoundsException: String index out of range: 12
- `org.apache.commons.cli.HelpFormatterTest::testFindWrapPos`: junit.framework.AssertionFailedError: wrap position 3 expected:<3> but was:<4>

## Suspicious Frames
- `org.apache.commons.cli.HelpFormatter.findWrapPos` at `HelpFormatter.java:937`
- `org.apache.commons.cli.HelpFormatter.renderWrappedText` at `HelpFormatter.java:848`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code uses a loop to find a wrap position. The condition 'pos <= text.length()' is incorrect because 'text.charAt(pos)' is evaluated inside the loop. If 'pos' equals 'text.length()', the access is out of bounds. This is a classic boundary check error.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
