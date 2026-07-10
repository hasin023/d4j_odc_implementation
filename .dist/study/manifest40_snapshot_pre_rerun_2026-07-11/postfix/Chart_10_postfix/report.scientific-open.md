# Defects4J ODC Classification Report: Chart-10

- Version: `10b`
- Work directory: `C:\d4j_work\postfix\Chart_10b`
- Generated: `2026-07-08T17:00:47+00:00`

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

The bug is a failure to validate/sanitize input data before using it in a context where special characters (quotes) have semantic meaning (HTML attributes). This is a classic 'Checking' defect as it involves missing logic to ensure data integrity for the output format.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Unit Test`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Test Variation`
- Inferred Impact: `Capability`
