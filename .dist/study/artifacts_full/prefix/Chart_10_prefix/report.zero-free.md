# Defects4J ODC Classification Report: Chart-10

- Version: `10b`
- Work directory: `C:\d4j_work\prefix\Chart_10b`
- Generated: `2026-07-10T18:55:03+00:00`

## Failure Summary
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment`: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">

## Suspicious Frames
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests.testGenerateURLFragment` at `StandardToolTipTagFragmentGeneratorTests.java:80`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Improper HTML character escaping`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The test failure indicates that the tool tip generator is failing to escape double quotes within the tool tip string when generating HTML attributes. The expected output contains '&quot;' for the double quotes, while the actual output contains raw double quotes, which breaks the HTML attribute structure. This indicates a failure to properly sanitize or encode special characters for HTML output.
