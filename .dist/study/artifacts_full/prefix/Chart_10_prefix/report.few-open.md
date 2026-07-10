# Defects4J ODC Classification Report: Chart-10

- Version: `10b`
- Work directory: `C:\d4j_work\prefix\Chart_10b`
- Generated: `2026-07-10T18:59:16+00:00`

## Failure Summary
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests::testGenerateURLFragment`: junit.framework.ComparisonFailure: expected:< title="Series [&quot;A&quot;], 100.0" alt=""> but was:< title="Series ["A"], 100.0" alt="">

## Suspicious Frames
- `org.jfree.chart.imagemap.junit.StandardToolTipTagFragmentGeneratorTests.testGenerateURLFragment` at `StandardToolTipTagFragmentGeneratorTests.java:80`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The defect is in the procedure used to generate the HTML fragment. It is not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object). It is a failure in the computational logic of the string generation method, which requires an algorithmic fix to correctly escape characters.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
