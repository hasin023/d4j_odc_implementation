# Defects4J ODC Classification Report: Chart-10

- Version: `10b`
- Work directory: `C:\d4j_work\postfix\Chart_10b`
- Generated: `2026-07-08T16:48:20+00:00`

## Failure Summary
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment`: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">

## Suspicious Frames
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests.testGenerateURLFragment` at `StandardToolTipTagFragmentGeneratorTests.java:80`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Improper Output Encoding`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The code was failing to properly escape special characters (specifically double quotes) in the toolTipText when generating an HTML attribute string. The fix introduced a call to 'ImageMapUtilities.htmlEscape(toolTipText)', which ensures that characters like '"' are converted to their HTML entity equivalents (e.g., '&quot;'), preventing the generated HTML attribute from being prematurely terminated or malformed.
