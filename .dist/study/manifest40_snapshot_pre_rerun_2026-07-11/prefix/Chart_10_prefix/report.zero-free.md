# Defects4J ODC Classification Report: Chart-10

- Version: `10b`
- Work directory: `C:\d4j_work\prefix\Chart_10b`
- Generated: `2026-07-08T16:48:18+00:00`

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

The failing test indicates that the StandardToolTipTagFragmentGenerator is failing to escape double quotes within the tooltip string. The test expects the double quotes to be converted to the HTML entity '&quot;', but the actual output contains raw double quotes. This indicates that the generator class is not performing the necessary character escaping required for valid HTML attribute values, leading to a malformed tooltip fragment.
