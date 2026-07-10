# Defects4J ODC Classification Report: Chart-10

- Version: `10b`
- Work directory: `C:\d4j_work\postfix\Chart_10b`
- Generated: `2026-07-10T18:40:47+00:00`

## Failure Summary
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment`: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">

## Suspicious Frames
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests.testGenerateURLFragment` at `StandardToolTipTagFragmentGeneratorTests.java:80`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The method generateToolTipFragment is responsible for creating an HTML fragment. It fails to handle special characters, which is a standard requirement for such a method. Adding the missing escaping logic is a procedural correction to the method's implementation.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
