# Batch Study Analysis

- Created: `2026-07-25T14:34:22+00:00`
- Total pairs: **26**
- Projects covered: **1**
- Type changed: **9** (34.6%)
- Type unchanged: **17** (65.4%)
- No alternative overlap: **0** (0.0%)
- No family match: **1** (3.8%)
- Family match: **25** (96.2%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **26** of 26
- Reliability: 17 (65.4%)
- Capability: 9 (34.6%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **24/26** (92.3%)
- Kappa: 0.8385
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Reliability × Checking: 13
- Capability × Algorithm/Method: 8
- Reliability × Algorithm/Method: 4
- Capability × Assignment/Initialization: 1

## Alternative Match Cases (Type Changed)

### Chart-7
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The defect is in the procedural logic that determines the index of the maximum middle value. It is not a missing guard (Checking), a simple wrong constant (Assignment/Initialization), or a design-level capability gap (Function/Class/Object). It is a failure in the computational strategy used to maintain the index, fitting the Algorithm/Method definition.
- Postfix reasoning summary: The bug is caused by using the wrong variable ('minMiddleIndex' instead of 'maxMiddleIndex') during the initialization of local variables 's' and 'e' within the 'getMaxMiddleIndex' method. This is a classic case of an incorrect assignment/initialization of values used in a computation, rather than a flaw in the algorithm's logic or a missing guard.
- Prefix context signal: org.jfree.data.time.junit.TimePeriodValuesTests::testGetMaxMiddleIndex: junit.framework.AssertionFailedError: expected:<1> but was:<3>
- Postfix context signal: org.jfree.data.time.junit.TimePeriodValuesTests::testGetMaxMiddleIndex: junit.framework.AssertionFailedError: expected:<1> but was:<3>

### Chart-8
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The issue is a failure in the calculation of a week number based on a date and timezone. This is a procedural logic error within the 'Week' class constructor, which falls under Algorithm/Method as it involves correcting the computational strategy for determining the week.
- Postfix reasoning summary: The bug is a classic case of using the wrong variable (a hardcoded default constant) instead of the provided parameter during object initialization. This is a direct assignment/initialization error. It is not an Algorithm/Method error because the logic of the constructor itself is fine; it just received the wrong input due to the incorrect assignment. It is not a Checking error because no validation was missing.
- Prefix context signal: org.jfree.data.time.junit.WeekTests::testConstructor: junit.framework.AssertionFailedError: expected:<35> but was:<34>
- Postfix context signal: org.jfree.data.time.junit.WeekTests::testConstructor: junit.framework.AssertionFailedError: expected:<35> but was:<34>

### Chart-12
- Type shift: Algorithm/Method -> Relationship.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The issue is a missing procedural step (listener registration) within the constructor's logic. This is an algorithmic/procedural omission rather than a design-level capability gap (the capability exists in setDataset) or a simple value assignment error.
- Postfix reasoning summary: The bug is a failure to maintain the consistency of the relationship between the plot and the dataset. The constructor bypassed the setter method that handles the registration logic, leading to a broken association. This is a classic Relationship defect where the internal state of one object (the plot) fails to correctly associate with another (the dataset) as required by the system's design.
- Prefix context signal: org.jfree.chart.plot.junit.MultiplePiePlotTests::testConstructor: junit.framework.AssertionFailedError
- Postfix context signal: org.jfree.chart.plot.junit.MultiplePiePlotTests::testConstructor: junit.framework.AssertionFailedError

### Chart-11
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The defect is a failure in the computational logic of the equality check. It is not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object). It is a procedural error in how the algorithm compares two complex objects, making it an Algorithm/Method defect.
- Postfix reasoning summary: The bug is a simple initialization error where the wrong variable was used to initialize an iterator. This fits the definition of Assignment/Initialization perfectly, as it is a value/initialization correction rather than a procedural rewrite or a missing guard.
- Prefix context signal: org.jfree.chart.util.junit.ShapeUtilitiesTests::testEqualGeneralPaths: junit.framework.AssertionFailedError
- Postfix context signal: org.jfree.chart.util.junit.ShapeUtilitiesTests::testEqualGeneralPaths: junit.framework.AssertionFailedError

### Chart-17
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a missing guard/validation check for the empty series case. The clone() method blindly calls createCopy(0, getItemCount() - 1). When getItemCount() is 0, it passes (0, -1), which violates the 'start <= end' check in createCopy(). This is a classic 'Checking' defect where the boundary condition (empty series) was not properly validated before invoking a method with strict parameter requirements.
- Postfix reasoning summary: The bug was caused by an incorrect procedural approach to cloning an object. The clone() method relied on a range-based copy method (createCopy) that was not designed to handle empty ranges (start=0, end=-1). The fix replaces this procedural logic with a direct deep clone of the data structure, which is a correction of the method's implementation strategy. It is not a 'Checking' bug because the fix is not just adding a guard, but replacing the entire cloning strategy. It is not 'Function/Class/Object' because it is a local implementation detail of the clone method.
- Prefix context signal: org.jfree.data.time.junit.TimeSeriesTests::testBug1832432: java.lang.IllegalArgumentException: Requires start <= end.
- Postfix context signal: org.jfree.data.time.junit.TimeSeriesTests::testBug1832432: java.lang.IllegalArgumentException: Requires start <= end.

### Chart-3
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The issue is a failure in the internal logic of the 'createCopy' method, which is responsible for creating a new TimeSeries instance and correctly setting its state. Since the method exists and performs the copy, but calculates the wrong result for the new object's properties, it is an algorithmic/procedural error rather than a missing check or a simple initialization value error.
- Postfix reasoning summary: The bug is caused by the failure to properly initialize the state (minY and maxY) of a newly created object. The fix involves adding these missing initializations. This fits the 'Assignment/Initialization' category perfectly as it corrects the initial state of the object rather than changing procedural logic or adding a guard.
- Prefix context signal: org.jfree.data.time.junit.TimeSeriesTests::testCreateCopy3: junit.framework.AssertionFailedError: expected:<101.0> but was:<102.0>
- Postfix context signal: org.jfree.data.time.junit.TimeSeriesTests::testCreateCopy3: junit.framework.AssertionFailedError: expected:<101.0> but was:<102.0>

### Chart-16
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The defect is a classic missing guard/validation. The code assumes that 'categoryKeys' and 'seriesKeys' are always non-null, but they can be null in certain states (e.g., empty dataset). Adding a null check is the standard way to handle this, which falls under the 'Checking' ODC type.
- Postfix reasoning summary: The bug is a classic initialization error. The code was setting internal arrays to null, which caused downstream methods (like getRowCount and getColumnCount) to throw NullPointerExceptions when they attempted to access the length property of those arrays. The fix correctly changes these null assignments to empty array initializations, ensuring the object state is always valid for subsequent operations.
- Prefix context signal: org.jfree.data.category.junit.DefaultIntervalCategoryDatasetTests::testGetCategoryIndex: java.lang.NullPointerException
- Postfix context signal: org.jfree.data.category.junit.DefaultIntervalCategoryDatasetTests::testGetCategoryIndex: java.lang.NullPointerException

### Chart-18
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is an algorithmic failure in maintaining the consistency of internal data structures (keys, values, and indexMap) during removal operations. This is not a missing guard (Checking) or a simple wrong value (Assignment), but a procedural error in how the collection is managed during updates, fitting the Algorithm/Method category.
- Postfix reasoning summary: The bug is fundamentally a failure to validate input data (keys) against the current state of the data structure. The fix adds missing conditional checks (guards) to ensure that operations are only performed on valid, existing keys, which is the definition of a Checking defect.
- Prefix context signal: org.jfree.data.category.junit.DefaultCategoryDatasetTests::testBug1835955: java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0
- Postfix context signal: org.jfree.data.category.junit.DefaultCategoryDatasetTests::testBug1835955: java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0

### Chart-2
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The failure is a classic NullPointerException caused by the absence of a null check on the return value of a utility method. The code assumes a valid Range object is always returned, but the input data (containing NaNs) causes the utility to return null. This is a missing validation/guard issue, which falls under the Checking category.
- Postfix reasoning summary: The fix involves rewriting the computational logic within the loops of iterateDomainBounds and iterateRangeBounds to correctly include the primary value and update both min and max bounds for all components. This is a procedural correction to the algorithm used to calculate bounds, fitting the Algorithm/Method ODC type.
- Prefix context signal: org.jfree.data.general.junit.DatasetUtilitiesTests::testBug2849731_2: java.lang.NullPointerException
- Postfix context signal: org.jfree.data.general.junit.DatasetUtilitiesTests::testBug2849731_2: java.lang.NullPointerException

## Type Changed (No Alternative Overlap)

- No qualifying cases found.
## Type Transitions

### Type Changed (Prefix → Postfix)

- Algorithm/Method -> Assignment/Initialization: 4
  - Bugs: Chart-11, Chart-3, Chart-7, Chart-8
- Checking -> Algorithm/Method: 2
  - Bugs: Chart-17, Chart-2
- Algorithm/Method -> Relationship: 1
  - Bugs: Chart-12 (no family match)
- Checking -> Assignment/Initialization: 1
  - Bugs: Chart-16
- Algorithm/Method -> Checking: 1
  - Bugs: Chart-18

### Type Unchanged

- Checking -> Checking: 10
  - Bugs: Chart-13, Chart-14, Chart-15, Chart-19, Chart-1, Chart-25, Chart-26, Chart-4, Chart-5, Chart-9
- Algorithm/Method -> Algorithm/Method: 6
  - Bugs: Chart-10, Chart-21, Chart-22, Chart-23, Chart-24, Chart-6
- Assignment/Initialization -> Assignment/Initialization: 1
  - Bugs: Chart-20
