# Batch Study Analysis

- Created: `2026-07-25T14:34:23+00:00`
- Total pairs: **38**
- Projects covered: **1**
- Type changed: **9** (23.7%)
- Type unchanged: **29** (76.3%)
- No alternative overlap: **4** (10.5%)
- No family match: **3** (7.9%)
- Family match: **35** (92.1%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **38** of 38
- Reliability: 21 (55.3%)
- Capability: 17 (44.7%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **31/38** (81.6%)
- Kappa: 0.6376
- Note: impact marginal distribution is near-degenerate; prefer the raw agreement rate over kappa
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Reliability × Checking: 13
- Capability × Algorithm/Method: 13
- Reliability × Algorithm/Method: 5
- Capability × Checking: 2
- Reliability × Relationship: 2
- Capability × Assignment/Initialization: 2
- Reliability × Function/Class/Object: 1

## Alternative Match Cases (Type Changed)

### Mockito-30
- Type shift: Algorithm/Method -> Interface/O-O Messages.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The issue is a failure in the procedural logic that constructs the error message. It is not a missing guard (Checking), a wrong constant (Assignment), or a design-level capability gap (Function/Class/Object). It is a defect in the method responsible for formatting the output string, which is a classic Algorithm/Method defect.
- Postfix reasoning summary: The bug is classified as Interface/O-O Messages because the fix required changing the method signature of 'smartNullPointerException' to accept an additional parameter ('obj') that was previously missing, and updating the caller to provide this information. This is a communication/contract issue between the 'ReturnsSmartNulls' component and the 'Reporter' component.
- Prefix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::shouldPrintTheParametersOnSmartNullPointerExceptionMessage: junit.framework.AssertionFailedError: Exception message should include oompa and lumpa, but was:
- Postfix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::shouldPrintTheParametersOnSmartNullPointerExceptionMessage: junit.framework.AssertionFailedError: Exception message should include oompa and lumpa, but was:

### Mockito-18
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic missing validation/handling case. The system is expected to return an empty Iterable for Iterable types, but it currently returns null (as evidenced by the NPE). This is a failure to check the input type and provide the appropriate default value, which falls under the 'Checking' category.
- Postfix reasoning summary: The bug is a missing initialization case for a specific type (Iterable). The fix adds the missing assignment logic to the existing 'ReturnsEmptyValues' method. This is a classic case of missing initialization for a specific data type, which fits 'Assignment/Initialization' perfectly.
- Prefix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_empty_iterable: java.lang.NullPointerException
- Postfix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_empty_iterable: java.lang.NullPointerException

### Mockito-6
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic missing validation check. The matchers are designed to match specific types, but they are failing to exclude null values, which is a requirement for these matchers. Adding a null check to the matcher's evaluation logic will resolve the issue.
- Postfix reasoning summary: The defect was in the computational logic of the matcher methods. They were using an overly broad 'Any' matcher, which is a procedural/algorithmic error in how the matching strategy was implemented. The fix involved replacing this strategy with a more specific 'InstanceOf' check, which is a classic correction of an algorithmic/method-level procedure.
- Prefix context signal: org.mockitousage.matchers.AnyXMatchersAcceptNullsTest::shouldNotAcceptNullInAllAnyPrimitiveWrapperMatchers: junit.framework.ComparisonFailure: expected:<null> but was:<0>
- Postfix context signal: org.mockitousage.matchers.AnyXMatchersAcceptNullsTest::shouldNotAcceptNullInAllAnyPrimitiveWrapperMatchers: junit.framework.ComparisonFailure: expected:<null> but was:<0>

### Mockito-8
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The defect is an infinite recursion in a recursive method. This is a procedural logic error (Algorithm/Method) rather than a missing guard (Checking), as the logic itself is fundamentally flawed for the input domain of self-referential generics. It is not a design-level capability issue (Function/Class/Object) because the capability to resolve generics exists, but the implementation of the resolution algorithm is incorrect for this specific case.
- Postfix reasoning summary: The bug is caused by a missing guard condition in a recursive method. The fix adds a conditional check to prevent the infinite recursion, which is the definition of a 'Checking' defect in ODC.
- Prefix context signal: org.mockito.internal.util.reflection.GenericMetadataSupportTest::typeVariable_of_self_type: java.lang.StackOverflowError
- Postfix context signal: org.mockito.internal.util.reflection.GenericMetadataSupportTest::typeVariable_of_self_type: java.lang.StackOverflowError

### Mockito-10
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Post-fix primary 'Algorithm/Method' found in pre-fix alternative types
- Prefix reasoning summary: The bug is a classic 'Checking' defect. The framework is performing a validation check (serializability) that is inappropriate for the context (a deep stub that wasn't explicitly configured to be serializable). The fix involves adding a guard condition to ensure this validation only runs when serialization is actually requested.
- Postfix reasoning summary: The bug was caused by an incorrect procedural logic in how deep stubs were created. The code was unconditionally applying serialization settings to child mocks. The fix involved modifying the method-level logic to propagate serialization settings from the parent mock instead of forcing them, which is a correction of the internal computational strategy for mock creation.
- Prefix context signal: org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest::should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub: org.mockito.exceptions.base.MockitoException:
- Postfix context signal: org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest::should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub: org.mockito.exceptions.base.MockitoException:

## Type Changed (No Alternative Overlap)

### Mockito-5
- Type shift: Relationship -> Checking.
- Comparison detail: No match: pre-fix 'Relationship' (Structural) vs post-fix 'Checking' (Control and Data Flow)
- Prefix reasoning summary: The defect is a structural dependency issue where internal Mockito classes are coupled to JUnit classes. This is a 'Relationship' defect because it involves the consistency and association between Mockito's internal exception hierarchy and external library (JUnit) structures. It is not an 'Algorithm/Method' issue because the logic itself is fine; it is not a 'Checking' issue because the problem is not a missing guard but an invalid structural assumption about the environment. It is not 'Function/Class/Object' because the capability exists, but its implementation is incorrectly coupled to an external dependency.
- Postfix reasoning summary: The bug is a classic 'Checking' issue where the code's exception handling logic (the catch block) was too rigid, creating an implicit dependency on an external library (JUnit) that should not be required. By changing the caught exception type to a standard one, the code correctly validates the error condition without requiring the presence of the JUnit library.
- Prefix context signal: org.mockitointegration.NoJUnitDependenciesTest::pure_mockito_should_not_depend_JUnit: junit.framework.AssertionFailedError: 'org.mockito.internal.verification.VerificationOverTimeImpl' has some dependency to JUnit
- Postfix context signal: org.mockitointegration.NoJUnitDependenciesTest::pure_mockito_should_not_depend_JUnit: junit.framework.AssertionFailedError: 'org.mockito.internal.verification.VerificationOverTimeImpl' has some dependency to JUnit

### Mockito-14
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Algorithm/Method' vs 'Checking')
- Prefix reasoning summary: The issue is not a missing guard (Checking) or a simple value assignment (Assignment/Initialization). It is a procedural failure in how the framework processes nested method calls during verification. This requires an algorithmic change to the invocation tracking logic to correctly handle nested mock interactions, fitting the Algorithm/Method category.
- Postfix reasoning summary: The bug is caused by a missing validation check that ensures verification logic is only executed for the specific mock intended. The fix adds this missing guard, which is the hallmark of a 'Checking' defect.
- Prefix context signal: org.mockitousage.bugs.VerifyingWithAnExtraCallToADifferentMockTest::shouldAllowVerifyingWhenOtherMockCallIsInTheSameLine: junit.framework.AssertionFailedError:
- Postfix context signal: org.mockitousage.bugs.VerifyingWithAnExtraCallToADifferentMockTest::shouldAllowVerifyingWhenOtherMockCallIsInTheSameLine: junit.framework.AssertionFailedError:

### Mockito-17
- Type shift: Function/Class/Object -> Assignment/Initialization.
- Comparison detail: No match: pre-fix 'Function/Class/Object' (Structural) vs post-fix 'Assignment/Initialization' (Control and Data Flow)
- Prefix reasoning summary: The defect is not a local algorithmic error, a wrong value, or a missing guard. It is a structural failure where the generated proxy class lacks the necessary capability (Serializable) to support the requested operation. This requires a design-level correction in how proxy classes are constructed to ensure they correctly implement the required interfaces.
- Postfix reasoning summary: The fix involves changing how the 'serializable' state is stored and initialized (adding a boolean field) and correcting the logic that uses this state to determine the proxy's interfaces. This is a classic Assignment/Initialization issue where the internal state of the mock settings was not being tracked or initialized correctly, leading to incorrect behavior in the proxy generation logic.
- Prefix context signal: org.mockitousage.basicapi.MocksSerializationTest::shouldBeSerializeAndHaveExtraInterfaces: java.io.NotSerializableException: org.mockitousage.IMethods$$EnhancerByMockitoWithCGLIB$$7466ec53
- Postfix context signal: org.mockitousage.basicapi.MocksSerializationTest::shouldBeSerializeAndHaveExtraInterfaces: java.io.NotSerializableException: org.mockitousage.IMethods$$EnhancerByMockitoWithCGLIB$$7466ec53

### Mockito-35
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Checking' vs 'Assignment/Initialization')
- Prefix reasoning summary: The bug manifests as an unhandled NullPointerException during the verification of method arguments. This indicates that the framework's internal logic for processing matchers (like isA, eq, same) lacks a necessary guard or validation check to handle cases where the internal state or the argument being processed might be null or incompatible, causing the framework to crash instead of failing gracefully or succeeding.
- Postfix reasoning summary: The bug is caused by an incorrect return value (null) being assigned/returned by the matcher methods. The fix replaces this incorrect value with a correct one derived from the class type. This is a classic Assignment/Initialization defect where the state (the return value) was initialized incorrectly.
- Prefix context signal: org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenIntPassed: java.lang.NullPointerException
- Postfix context signal: org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenIntPassed: java.lang.NullPointerException

## Type Transitions

### Type Changed (Prefix → Postfix)

- Checking -> Algorithm/Method: 2
  - Bugs: Mockito-10, Mockito-6
- Algorithm/Method -> Checking: 2
  - Bugs: Mockito-14 (no alt overlap), Mockito-8
- Checking -> Assignment/Initialization: 2
  - Bugs: Mockito-18, Mockito-35 (no alt overlap)
- Function/Class/Object -> Assignment/Initialization: 1
  - Bugs: Mockito-17 (no alt overlap, no family match)
- Algorithm/Method -> Interface/O-O Messages: 1
  - Bugs: Mockito-30 (no family match)
- Relationship -> Checking: 1
  - Bugs: Mockito-5 (no alt overlap, no family match)

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 15
  - Bugs: Mockito-11, Mockito-13, Mockito-15, Mockito-19, Mockito-1, Mockito-20, Mockito-21, Mockito-24, Mockito-25, Mockito-27, Mockito-28, Mockito-31, Mockito-33, Mockito-3, Mockito-7
- Checking -> Checking: 11
  - Bugs: Mockito-12, Mockito-16, Mockito-22, Mockito-29, Mockito-2, Mockito-34, Mockito-36, Mockito-37, Mockito-38, Mockito-4, Mockito-9
- Assignment/Initialization -> Assignment/Initialization: 2
  - Bugs: Mockito-26, Mockito-32
- Relationship -> Relationship: 1
  - Bugs: Mockito-23
