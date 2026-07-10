# Defects4J ODC Classification Report: Chart-10

- Version: `10b`
- Work directory: `C:\d4j_work\prefix\Chart_10b`
- Generated: `2026-07-10T18:49:01+00:00`

## Failure Summary
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment`: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">

## Suspicious Frames
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests.testGenerateURLFragment` at `StandardToolTipTagFragmentGeneratorTests.java:80`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The failure is a string comparison error where the output lacks necessary HTML escaping. This is a failure to validate/transform input data correctly before outputting it, which falls under the 'Checking' category.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
