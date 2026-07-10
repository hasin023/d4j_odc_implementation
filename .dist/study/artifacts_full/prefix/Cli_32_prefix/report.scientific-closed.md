# Defects4J ODC Classification Report: Cli-32

- Version: `32b`
- Work directory: `C:\d4j_work\prefix\Cli_32b`
- Generated: `2026-07-10T18:49:07+00:00`

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

The code uses a boundary check that is inclusive of the string length, which is invalid for charAt access. This is a classic off-by-one error in a loop predicate.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
