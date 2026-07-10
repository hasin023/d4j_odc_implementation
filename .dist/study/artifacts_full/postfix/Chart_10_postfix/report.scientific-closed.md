# Defects4J ODC Classification Report: Chart-10

- Version: `10b`
- Work directory: `C:\d4j_work\postfix\Chart_10b`
- Generated: `2026-07-10T18:49:05+00:00`

## Failure Summary
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment`: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">

## Suspicious Frames
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests.testGenerateURLFragment` at `StandardToolTipTagFragmentGeneratorTests.java:80`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The failure is a direct result of failing to validate/sanitize the input string before embedding it into an HTML attribute. This is a classic 'Checking' defect where the code lacks the necessary guard/transformation to ensure data integrity in the output context.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
