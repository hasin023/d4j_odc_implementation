# Batch Study Analysis

- Created: `2026-07-25T14:34:22+00:00`
- Total pairs: **26**
- Projects covered: **1**
- Type changed: **7** (26.9%)
- Type unchanged: **19** (73.1%)
- No alternative overlap: **1** (3.8%)
- No family match: **1** (3.8%)
- Family match: **25** (96.2%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **26** of 26
- Capability: 15 (57.7%)
- Reliability: 11 (42.3%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **23/26** (88.5%)
- Kappa: 0.7665
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Reliability × Checking: 9
- Capability × Algorithm/Method: 7
- Capability × Checking: 5
- Capability × Assignment/Initialization: 3
- Reliability × Assignment/Initialization: 1
- Reliability × Algorithm/Method: 1

## Alternative Match Cases (Type Changed)

### Chart-2
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Pre-fix primary 'Checking' found in post-fix alternative types
- Prefix reasoning summary: The failure is a classic case of missing validation for a return value that can be null, which is a 'Checking' defect as it involves missing predicate logic to handle the boundary condition of empty/NaN data.
- Postfix reasoning summary: The bug is an algorithmic error in the calculation of range/domain bounds within DatasetUtilities. The methods iterateDomainBounds and iterateRangeBounds do not correctly handle NaN values, leading to incorrect or null results. This is a classic Algorithm/Method defect as it involves the procedural logic of calculating bounds.
- Prefix context signal: org.jfree.data.general.junit.DatasetUtilitiesTests::testBug2849731_2: java.lang.NullPointerException
- Postfix context signal: org.jfree.data.general.junit.DatasetUtilitiesTests::testBug2849731_2: java.lang.NullPointerException

### Chart-3
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The bug is localized to the logic within the createCopy method. It is not a missing check (Checking), not an incorrect initialization of a single variable (Assignment/Initialization), but a failure in the procedural logic to correctly derive the state of the new object from the subset of data.
- Postfix reasoning summary: The bug is caused by an incorrect initialization of the state of a cloned object. The fields minY and maxY are cached values that become stale when the object is cloned and its data is modified. Resetting them to NaN forces a recalculation, which is the correct behavior.
- Prefix context signal: org.jfree.data.time.junit.TimeSeriesTests::testCreateCopy3: junit.framework.AssertionFailedError: expected:<101.0> but was:<102.0>
- Postfix context signal: org.jfree.data.time.junit.TimeSeriesTests::testCreateCopy3: junit.framework.AssertionFailedError: expected:<101.0> but was:<102.0>

### Chart-16
- Type shift: Assignment/Initialization -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Assignment/Initialization' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The root cause is the lack of proper initialization of 'categoryKeys' and 'seriesKeys' in the constructor, which violates the implicit contract that these fields should be non-null arrays. This is a classic initialization defect.
- Postfix reasoning summary: The defect is a missing validation (null-check) for internal state variables that are expected to be initialized but are not in all cases. This fits the 'Checking' ODC type perfectly as it involves missing parameter/data validation in conditional logic (or lack thereof).
- Prefix context signal: org.jfree.data.category.junit.DefaultIntervalCategoryDatasetTests::testGetCategoryIndex: java.lang.NullPointerException
- Postfix context signal: org.jfree.data.category.junit.DefaultIntervalCategoryDatasetTests::testGetCategoryIndex: java.lang.NullPointerException

### Chart-18
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The failure is a classic case of inconsistent internal state (a cache `indexMap` vs. the source-of-truth `keys` list) after a mutation operation (`removeValue`). This is an algorithmic error in the maintenance of the data structure's internal state.
- Postfix reasoning summary: The failure is caused by improper handling of collection state during removal. The code assumes keys exist or that indices remain valid, which is a failure of validation (Checking).
- Prefix context signal: org.jfree.data.category.junit.DefaultCategoryDatasetTests::testBug1835955: java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0
- Postfix context signal: org.jfree.data.category.junit.DefaultCategoryDatasetTests::testBug1835955: java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0

### Chart-24
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The code snippet for GrayPaintScale.getPaint shows that the input 'value' is clamped to 'v' (lines 124-125), but the subsequent calculation of 'g' (line 126) uses the original 'value'. This causes 'g' to fall outside the [0, 255] range when 'value' is outside the bounds, triggering an exception in the Color constructor.
- Postfix reasoning summary: The bug is a classic case of using the wrong variable in a calculation. The code correctly computes a clamped value 'v' but fails to use it in the subsequent formula, leading to an invalid state that violates the contract of the java.awt.Color constructor.
- Prefix context signal: org.jfree.chart.renderer.junit.GrayPaintScaleTests::testGetPaint: java.lang.IllegalArgumentException: Color parameter outside of expected range: Red Green Blue
- Postfix context signal: org.jfree.chart.renderer.junit.GrayPaintScaleTests::testGetPaint: java.lang.IllegalArgumentException: Color parameter outside of expected range: Red Green Blue

### Chart-5
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug report explicitly identifies that addOrUpdate was not updated to support duplicate X values. The code snippet shows the logic for adding items based on the index returned by binarySearch, which is insufficient for handling duplicates correctly. This is a procedural/algorithmic error in how the series data is managed.
- Postfix reasoning summary: The bug is caused by missing validation logic (Checking) that should have checked the allowDuplicateXValues flag before proceeding with the index-based insertion. The failure is a direct result of an incorrect conditional path in the addOrUpdate method.
- Prefix context signal: org.jfree.data.xy.junit.XYSeriesTests::testBug1955483: java.lang.IndexOutOfBoundsException: Index: -1, Size: 1
- Postfix context signal: org.jfree.data.xy.junit.XYSeriesTests::testBug1955483: java.lang.IndexOutOfBoundsException: Index: -1, Size: 1

## Type Changed (No Alternative Overlap)

### Chart-23
- Type shift: Checking -> Function/Class/Object.
- Comparison detail: No match: pre-fix 'Checking' (Control and Data Flow) vs post-fix 'Function/Class/Object' (Structural)
- Prefix reasoning summary: The test failure at line 99 (assertFalse(r1.equals(r2))) after setting r1.setDrawLines(true) confirms that the equals method fails to account for the 'drawLines' property. This is a failure in the conditional logic of the equals method, which falls under the 'Checking' category.
- Postfix reasoning summary: The class MinMaxCategoryRenderer lacks an equals() method. This is a structural deficiency where the class fails to provide the expected capability of object equality comparison, which is a standard requirement for such renderer classes in this framework.
- Prefix context signal: org.jfree.chart.renderer.category.junit.MinMaxCategoryRendererTests::testEquals: junit.framework.AssertionFailedError
- Postfix context signal: org.jfree.chart.renderer.category.junit.MinMaxCategoryRendererTests::testEquals: junit.framework.AssertionFailedError

## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Checking: 2
  - Bugs: Chart-18, Chart-5
- Checking -> Algorithm/Method: 2
  - Bugs: Chart-24, Chart-2
- Assignment/Initialization -> Checking: 1
  - Bugs: Chart-16
- Checking -> Function/Class/Object: 1
  - Bugs: Chart-23 (no alt overlap, no family match)
- Algorithm/Method -> Assignment/Initialization: 1
  - Bugs: Chart-3

### Type Unchanged

- Checking -> Checking: 11
  - Bugs: Chart-13, Chart-14, Chart-15, Chart-17, Chart-19, Chart-1, Chart-22, Chart-25, Chart-26, Chart-4, Chart-9
- Algorithm/Method -> Algorithm/Method: 5
  - Bugs: Chart-10, Chart-11, Chart-21, Chart-6, Chart-7
- Assignment/Initialization -> Assignment/Initialization: 3
  - Bugs: Chart-12, Chart-20, Chart-8
