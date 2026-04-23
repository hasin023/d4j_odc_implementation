# Defects4J ODC Classification Report: Cli-32

- Version: `32b`
- Work directory: `.dist\study\work\prefix\Cli_32b`
- Generated: `2026-04-21T15:06:43+00:00`

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
- Target: `Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The defect is a classic boundary condition error where a loop continues one iteration too far, causing an out-of-bounds access. This falls squarely under 'Checking' as it involves an incorrect predicate in a conditional statement (the while loop guard).

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Recovery/Exception, Test Variation`
- Inferred Impact: `Reliability`
