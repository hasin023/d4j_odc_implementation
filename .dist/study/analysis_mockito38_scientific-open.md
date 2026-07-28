# Batch Study Analysis

- Created: `2026-07-25T14:34:22+00:00`
- Total pairs: **38**
- Projects covered: **1**
- Type changed: **20** (52.6%)
- Type unchanged: **18** (47.4%)
- No alternative overlap: **4** (10.5%)
- No family match: **8** (21.1%)
- Family match: **30** (78.9%)

## Impact (Opener Attribute, Prefix Arm)

- Classifications with impact: **38** of 38
- Capability: 24 (63.2%)
- Reliability: 12 (31.6%)
- Serviceability: 2 (5.3%)

### Impact Stability (Drift Negative Control)

- Prefix↔postfix agreement: **33/38** (86.8%)
- Kappa: 0.7278
- Reading: impact is fix-independent (v5.2 §3.3), so its drift is pure instrument noise; type drift meaningfully above it indicates genuine fix-dependence.

### Impact × Type Cross-Tab (Orthogonality Check)

- Capability × Algorithm/Method: 13
- Capability × Checking: 8
- Reliability × Checking: 8
- Reliability × Algorithm/Method: 3
- Capability × Interface/O-O Messages: 1
- Capability × Function/Class/Object: 1
- Reliability × Assignment/Initialization: 1
- Serviceability × Algorithm/Method: 1
- Serviceability × Assignment/Initialization: 1
- Capability × Relationship: 1

## Alternative Match Cases (Type Changed)

### Mockito-20
- Type shift: Function/Class/Object -> Algorithm/Method.
- Comparison detail: Post-fix primary 'Algorithm/Method' found in pre-fix alternative types
- Prefix reasoning summary: The tests show that when Mockito is asked to create a mock or spy using a constructor, the resulting object does not have the expected state initialized. This indicates a failure in the core capability of the framework to correctly instantiate and initialize objects, which is a structural design issue.
- Postfix reasoning summary: The failure symptoms (null fields in spied/mocked objects) and the nature of the fix (switching to a different instantiator) indicate that the procedure for creating these objects was flawed. This is a classic case of an incorrect algorithmic strategy for object creation.
- Prefix context signal: org.mockitousage.annotation.SpyAnnotationTest::should_spy_inner_class: junit.framework.ComparisonFailure: expected:<[inner] strength> but was:<[null] strength>
- Postfix context signal: org.mockitousage.annotation.SpyAnnotationTest::should_spy_inner_class: junit.framework.ComparisonFailure: expected:<[inner] strength> but was:<[null] strength>

### Mockito-30
- Type shift: Algorithm/Method -> Interface/O-O Messages.
- Comparison detail: Pre-fix primary 'Algorithm/Method' found in post-fix alternative types
- Prefix reasoning summary: The bug is a failure to correctly format a diagnostic message. This is a procedural error in the method responsible for generating the exception message, fitting the Algorithm/Method ODC type as it involves the logic of how the message is constructed from the invocation data.
- Postfix reasoning summary: The failure is an assertion error on the content of an exception message. The fix diff provided in the oracle confirms that the method signature of the reporter was changed to accept an object, which is then used to format the message. This is a clear case of an interface mismatch where the caller (ReturnsSmartNulls) and the callee (Reporter) were not aligned on the required information to fulfill the contract of providing a descriptive error message.
- Prefix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::shouldPrintTheParametersOnSmartNullPointerExceptionMessage: junit.framework.AssertionFailedError: Exception message should include oompa and lumpa, but was:
- Postfix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::shouldPrintTheParametersOnSmartNullPointerExceptionMessage: junit.framework.AssertionFailedError: Exception message should include oompa and lumpa, but was:

### Mockito-32
- Type shift: Assignment/Initialization -> Function/Class/Object.
- Comparison detail: Cross-alternative match: pre-fix 'Assignment/Initialization' is in post-fix alternatives, and post-fix 'Function/Class/Object' is in pre-fix alternatives
- Prefix reasoning summary: The failure is in the error reporting mechanism (assertion message), which relies on the mock's name. Since the name is missing, the mock was not initialized with the provided name.
- Postfix reasoning summary: The bug is a missing capability in the object creation process (naming the spy). The fix adds this capability by using the Mockito settings API. This fits the definition of Function/Class/Object as it involves a design-level capability (naming) that was absent.
- Prefix context signal: org.mockitousage.bugs.SpyShouldHaveNiceNameTest::shouldPrintNiceName: junit.framework.AssertionFailedError: <'
- Postfix context signal: org.mockitousage.bugs.SpyShouldHaveNiceNameTest::shouldPrintNiceName: junit.framework.AssertionFailedError: <'

### Mockito-10
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a classic case of incorrect predicate logic (Checking) where the system validates a condition (serializability) that should not be applied in the current context. The code is missing a check to see if the parent mock was actually configured as serializable before enforcing that requirement on the child mock.
- Postfix reasoning summary: The defect is an incorrect initialization of the `MockSettings` object for deep-stubbed mocks. By unconditionally calling `.serializable()`, the code incorrectly initializes the state of the mock, leading to a validation failure. This is a classic Assignment/Initialization defect where the state (serialization requirement) is set incorrectly.
- Prefix context signal: org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest::should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub: org.mockito.exceptions.base.MockitoException:
- Postfix context signal: org.mockitousage.bugs.DeepStubsWronglyReportsSerializationProblemsTest::should_not_raise_a_mockito_exception_about_serialization_when_accessing_deep_stub: org.mockito.exceptions.base.MockitoException:

### Mockito-12
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The failure is a direct result of missing logic to handle ParameterizedType objects in a reflection-based utility. The code assumes all generic types are simple Classes, which is a validation error.
- Postfix reasoning summary: The bug is a failure to correctly handle the reflection hierarchy for nested generics. The fix implements a conditional check to correctly extract the raw type from a nested ParameterizedType, which is a classic algorithmic/method-level correction.
- Prefix context signal: org.mockito.internal.util.reflection.GenericMasterTest::shouldDealWithNestedGenerics: java.lang.ClassCastException: class sun.reflect.generics.reflectiveObjects.ParameterizedTypeImpl cannot be cast to class java.lang.Class (sun.reflect.generics.reflectiveObjects.ParameterizedTypeImpl and java.lang.Class are in module java.base of loader 'bootstrap')
- Postfix context signal: org.mockito.internal.util.reflection.GenericMasterTest::shouldDealWithNestedGenerics: java.lang.ClassCastException: class sun.reflect.generics.reflectiveObjects.ParameterizedTypeImpl cannot be cast to class java.lang.Class (sun.reflect.generics.reflectiveObjects.ParameterizedTypeImpl and java.lang.Class are in module java.base of loader 'bootstrap')

### Mockito-25
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Post-fix primary 'Algorithm/Method' found in pre-fix alternative types
- Prefix reasoning summary: The bug is caused by missing validation logic to check if a type is mockable before attempting to create a deep stub. This falls under the 'Checking' category as it involves missing parameter/data validation.
- Postfix reasoning summary: The bug is a classic case of an incorrect algorithmic strategy for handling type information in a dynamic proxy/mocking framework. The fix involves changing the method-level computational strategy for mock creation to include generic metadata, which fits the 'Algorithm/Method' ODC type.
- Prefix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsGenericDeepStubsTest::will_return_default_value_on_non_mockable_nested_generic: java.lang.ClassCastException: class org.mockito.internal.creation.jmock.ClassImposterizer$ClassWithSuperclassToWorkAroundCglibBug$$EnhancerByMockitoWithCGLIB$$fdf68caf cannot be cast to class java.lang.String (org.mockito.internal.creation.jmock.ClassImposterizer$ClassWithSuperclassToWorkAroundCglibBug$$EnhancerByMockitoWithCGLIB$$fdf68caf is in unnamed module of loader org.apache.tools.ant.loader.AntClassLoader5 @302e5dfc; java.lang.String is in module java.base of loader 'bootstrap')
- Postfix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsGenericDeepStubsTest::will_return_default_value_on_non_mockable_nested_generic: java.lang.ClassCastException: class org.mockito.internal.creation.jmock.ClassImposterizer$ClassWithSuperclassToWorkAroundCglibBug$$EnhancerByMockitoWithCGLIB$$fdf68caf cannot be cast to class java.lang.String (org.mockito.internal.creation.jmock.ClassImposterizer$ClassWithSuperclassToWorkAroundCglibBug$$EnhancerByMockitoWithCGLIB$$fdf68caf is in unnamed module of loader org.apache.tools.ant.loader.AntClassLoader5 @302e5dfc; java.lang.String is in module java.base of loader 'bootstrap')

### Mockito-26
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The failure is a classic type mismatch in a factory-like method that returns default values for primitives. Since the code fails to return the correct type for 'double', the logic within the method is incomplete.
- Postfix reasoning summary: The bug is a classic initialization error where the wrong type (Integer) was assigned to a map entry intended for a double primitive. This is a local assignment issue that does not require algorithmic changes or structural design changes.
- Prefix context signal: org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')
- Postfix context signal: org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')

### Mockito-27
- Type shift: Algorithm/Method -> Assignment/Initialization.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Assignment/Initialization' is in pre-fix alternatives
- Prefix reasoning summary: The failure occurs specifically after reset() is called. Since reset() is a standard library function, the failure to maintain the listener state during this procedure points to an incorrect implementation of the reset algorithm.
- Postfix reasoning summary: The bug is a classic case of incorrect state initialization. When resetting a mock, the system must preserve the existing configuration (like listeners). The original implementation failed to do this by overwriting the handler with a default one, which is an Assignment/Initialization error.
- Prefix context signal: org.mockitousage.bugs.ListenersLostOnResetMockTest::listener: junit.framework.AssertionFailedError:
- Postfix context signal: org.mockitousage.bugs.ListenersLostOnResetMockTest::listener: junit.framework.AssertionFailedError:

### Mockito-4
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The failure is a classic case of missing validation (Checking) where the code assumes a specific type (String) for a mock's name or representation, but the mock's configuration (custom default answer) causes it to return a different type (Boolean), leading to a runtime exception during error reporting.
- Postfix reasoning summary: The bug is a procedural error in how the Reporter class handles mock objects during error reporting. It assumes that calling toString() on a mock is safe, which is not true when the mock has a custom default answer. This is a local procedural logic error (Algorithm/Method) rather than a design-level capability gap or a simple initialization error.
- Prefix context signal: org.mockito.exceptions.ReporterTest::can_use_print_mock_name_even_when_mock_bogus_default_answer_and_when_reporting_no_more_interaction_wanted_in_order: java.lang.Exception: Unexpected exception, expected<org.mockito.exceptions.verification.VerificationInOrderFailure> but was<java.lang.ClassCastException>
- Postfix context signal: org.mockito.exceptions.ReporterTest::can_use_print_mock_name_even_when_mock_bogus_default_answer_and_when_reporting_no_more_interaction_wanted_in_order: java.lang.Exception: Unexpected exception, expected<org.mockito.exceptions.verification.VerificationInOrderFailure> but was<java.lang.ClassCastException>

### Mockito-6
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Cross-alternative match: pre-fix 'Checking' is in post-fix alternatives, and post-fix 'Algorithm/Method' is in pre-fix alternatives
- Prefix reasoning summary: The bug is a failure to validate input (null) in a conditional check (the matcher's 'matches' method). This is a textbook 'Checking' defect.
- Postfix reasoning summary: The defect is in the implementation of the `anyX()` methods in `org.mockito.Matchers`. The current implementation uses a generic `Any.ANY` matcher, which is logically incorrect for methods intended to match specific types. Replacing this with `InstanceOf` is a local procedural correction to the matcher's logic.
- Prefix context signal: org.mockitousage.matchers.AnyXMatchersAcceptNullsTest::shouldNotAcceptNullInAllAnyPrimitiveWrapperMatchers: junit.framework.ComparisonFailure: expected:<null> but was:<0>
- Postfix context signal: org.mockitousage.matchers.AnyXMatchersAcceptNullsTest::shouldNotAcceptNullInAllAnyPrimitiveWrapperMatchers: junit.framework.ComparisonFailure: expected:<null> but was:<0>

### Mockito-7
- Type shift: Checking -> Algorithm/Method.
- Comparison detail: Pre-fix primary 'Checking' found in post-fix alternative types
- Prefix reasoning summary: The failure is a direct result of an unchecked null value being passed into a method that expects a valid type. This is a classic 'Checking' defect where the predicate logic is missing a null-check guard.
- Postfix reasoning summary: The failure occurs because the metadata extraction logic is incomplete for nested generics. The fix adds a missing step in the algorithm to register type parameters, which is a classic procedural/algorithmic correction.
- Prefix context signal: org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest::discoverDeepMockingOfGenerics: org.mockito.exceptions.base.MockitoException: Raw extraction not supported for : 'null'
- Postfix context signal: org.mockitousage.bugs.deepstubs.DeepStubFailingWhenGenricNestedAsRawTypeTest::discoverDeepMockingOfGenerics: org.mockito.exceptions.base.MockitoException: Raw extraction not supported for : 'null'

### Mockito-8
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The failure is a classic infinite recursion in a recursive algorithm. The fix involves adding a state-tracking mechanism (like a set of visited types) to the method, which is a procedural/algorithmic change.
- Postfix reasoning summary: The defect is a missing guard condition in a recursive resolution process. This fits the 'Checking' category as it involves validating the state (type equality) before proceeding with an operation that would otherwise cause a stack overflow.
- Prefix context signal: org.mockito.internal.util.reflection.GenericMetadataSupportTest::typeVariable_of_self_type: java.lang.StackOverflowError
- Postfix context signal: org.mockito.internal.util.reflection.GenericMetadataSupportTest::typeVariable_of_self_type: java.lang.StackOverflowError

### Mockito-14
- Type shift: Algorithm/Method -> Interface/O-O Messages.
- Comparison detail: Post-fix primary 'Interface/O-O Messages' found in pre-fix alternative types
- Prefix reasoning summary: The failure occurs because Mockito's state machine for verification is not re-entrant or does not handle nested mock calls during the verification phase. This is a procedural logic error in how Mockito tracks the 'verification' state versus the 'invocation' state.
- Postfix reasoning summary: The bug is caused by the lack of association between the verification mode and the mock instance. The fix introduces a wrapper (MockAwareVerificationMode) to pass this context, which is a classic interface/contract issue where the existing signature/contract was insufficient for the required functionality.
- Prefix context signal: org.mockitousage.bugs.VerifyingWithAnExtraCallToADifferentMockTest::shouldAllowVerifyingWhenOtherMockCallIsInTheSameLine: junit.framework.AssertionFailedError:
- Postfix context signal: org.mockitousage.bugs.VerifyingWithAnExtraCallToADifferentMockTest::shouldAllowVerifyingWhenOtherMockCallIsInTheSameLine: junit.framework.AssertionFailedError:

### Mockito-17
- Type shift: Algorithm/Method -> Function/Class/Object.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Function/Class/Object' is in pre-fix alternatives
- Prefix reasoning summary: The failure occurs during serialization of a mock that was explicitly configured to be serializable. The presence of extra interfaces causes the proxy generation to omit the Serializable marker interface, which is a procedural error in the proxy creation algorithm.
- Postfix reasoning summary: The bug report and the provided fix diff confirm that the previous implementation relied on a side-effect (adding an interface) to achieve a capability (serialization). This was insufficient when other interfaces were present, requiring a design change to track the serializable state explicitly.
- Prefix context signal: org.mockitousage.basicapi.MocksSerializationTest::shouldBeSerializeAndHaveExtraInterfaces: java.io.NotSerializableException: org.mockitousage.IMethods$$EnhancerByMockitoWithCGLIB$$7466ec53
- Postfix context signal: org.mockitousage.basicapi.MocksSerializationTest::shouldBeSerializeAndHaveExtraInterfaces: java.io.NotSerializableException: org.mockitousage.IMethods$$EnhancerByMockitoWithCGLIB$$7466ec53

### Mockito-23
- Type shift: Assignment/Initialization -> Relationship.
- Comparison detail: Pre-fix primary 'Assignment/Initialization' found in post-fix alternative types
- Prefix reasoning summary: The failure is a direct consequence of an object (the mock's default answer) not being serializable. This is an initialization/state issue where the object state is not correctly prepared for serialization.
- Postfix reasoning summary: The bug is a failure to maintain the serialization contract of the mock object due to internal state that does not support serialization. This is a relationship issue between the mock's serialization requirement and the internal implementation of the deep stub handler.
- Prefix context signal: org.mockitousage.stubbing.DeepStubsSerializableTest::should_serialize_and_deserialize_mock_created_by_deep_stubs: java.io.NotSerializableException: org.mockito.internal.stubbing.defaultanswers.ReturnsDeepStubs$2
- Postfix context signal: org.mockitousage.stubbing.DeepStubsSerializableTest::should_serialize_and_deserialize_mock_created_by_deep_stubs: java.io.NotSerializableException: org.mockito.internal.stubbing.defaultanswers.ReturnsDeepStubs$2

### Mockito-19
- Type shift: Algorithm/Method -> Checking.
- Comparison detail: Cross-alternative match: pre-fix 'Algorithm/Method' is in post-fix alternatives, and post-fix 'Checking' is in pre-fix alternatives
- Prefix reasoning summary: The bug report and test failure confirm that @InjectMocks does not correctly handle multiple fields of the same type, failing to use the field name as a disambiguator. This is a classic algorithmic error in the selection logic.
- Postfix reasoning summary: The fix adds a check in the NameBasedCandidateFilter to verify if another field exists that matches the mock name and type, which is a classic 'Checking' defect where a validation predicate was missing.
- Prefix context signal: org.mockitousage.annotation.MockInjectionUsingSetterOrPropertyTest::shouldInsertFieldWithCorrectNameWhenMultipleTypesAvailable: junit.framework.AssertionFailedError: Expected: <null> but was: candidate2
- Postfix context signal: org.mockitousage.annotation.MockInjectionUsingSetterOrPropertyTest::shouldInsertFieldWithCorrectNameWhenMultipleTypesAvailable: junit.framework.AssertionFailedError: Expected: <null> but was: candidate2

## Type Changed (No Alternative Overlap)

### Mockito-16
- Type shift: Interface/O-O Messages -> Checking.
- Comparison detail: No match: pre-fix 'Interface/O-O Messages' (Structural) vs post-fix 'Checking' (Control and Data Flow)
- Prefix reasoning summary: The failure occurs because the mock, configured with RETURNS_MOCKS, returns a value during the 'when' call, which interferes with the framework's ability to record the method call as a stubbing target. This is a mismatch in the expected interaction between the 'when' API and the mock's internal handler.
- Postfix reasoning summary: The `MissingMethodInvocationException` occurs because the framework's `mockingProgress` state is not being correctly reset or validated when a mock is created with `RETURNS_MOCKS`. The fix explicitly adds a `resetOngoingStubbing()` call in `MockitoCore.mock` to ensure that the state is clean before the mock is used, which is a validation/checking issue regarding the internal state of the stubbing process.
- Prefix context signal: org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest::shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS: org.mockito.exceptions.misusing.MissingMethodInvocationException:
- Postfix context signal: org.mockitousage.bugs.StubbingMocksThatAreConfiguredToReturnMocksTest::shouldAllowStubbingMocksConfiguredWithRETURNS_MOCKS: org.mockito.exceptions.misusing.MissingMethodInvocationException:

### Mockito-35
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Checking' vs 'Assignment/Initialization')
- Prefix reasoning summary: The failure is a classic case of missing validation or incorrect handling of primitive types during argument matching. The ODC type 'Checking' is appropriate because the fix involves adding a guard or a check to handle the primitive/wrapper conversion safely before proceeding with the matching logic.
- Postfix reasoning summary: The bug is caused by the matcher methods returning null, which is incompatible with primitive types in Java due to auto-unboxing. The fix correctly initializes the return value based on the class type, which is an Assignment/Initialization issue.
- Prefix context signal: org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenIntPassed: java.lang.NullPointerException
- Postfix context signal: org.mockitousage.bugs.NPEWithCertainMatchersTest::shouldNotThrowNPEWhenIntPassed: java.lang.NullPointerException

### Mockito-18
- Type shift: Checking -> Assignment/Initialization.
- Comparison detail: Family match only: both 'Control and Data Flow' but types differ ('Checking' vs 'Assignment/Initialization')
- Prefix reasoning summary: The bug report explicitly requests support for empty Iterables, and the test failure confirms that the current implementation returns null for this type. Adding a check for Iterable to return an empty collection is a validation/predicate logic fix.
- Postfix reasoning summary: The bug report and fix diff confirm that the system was failing to provide a default empty Iterable, returning null instead. This is a classic case of missing initialization for a specific type in a factory-like method.
- Prefix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_empty_iterable: java.lang.NullPointerException
- Postfix context signal: org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_empty_iterable: java.lang.NullPointerException

### Mockito-5
- Type shift: Relationship -> Checking.
- Comparison detail: No match: pre-fix 'Relationship' (Structural) vs post-fix 'Checking' (Control and Data Flow)
- Prefix reasoning summary: The bug is a structural dependency issue where an internal class (VerificationOverTimeImpl) references an external library (JUnit) that is not supposed to be a hard dependency. This violates the architectural constraint of Mockito's independence from JUnit, fitting the 'Relationship' ODC type as it concerns the association between Mockito's internal structures and external dependencies.
- Postfix reasoning summary: The defect is a classic 'Checking' issue where the code logic (the catch block) incorrectly assumes the presence of a specific library (JUnit) for exception handling. By changing the catch block to a more generic 'AssertionError', the dependency is removed, resolving the runtime linkage error.
- Prefix context signal: org.mockitointegration.NoJUnitDependenciesTest::pure_mockito_should_not_depend_JUnit: junit.framework.AssertionFailedError: 'org.mockito.internal.verification.VerificationOverTimeImpl' has some dependency to JUnit
- Postfix context signal: org.mockitointegration.NoJUnitDependenciesTest::pure_mockito_should_not_depend_JUnit: junit.framework.AssertionFailedError: 'org.mockito.internal.verification.VerificationOverTimeImpl' has some dependency to JUnit

## Type Transitions

### Type Changed (Prefix → Postfix)

- Checking -> Algorithm/Method: 5
  - Bugs: Mockito-12, Mockito-25, Mockito-4, Mockito-6, Mockito-7
- Checking -> Assignment/Initialization: 3
  - Bugs: Mockito-10, Mockito-18 (no alt overlap), Mockito-35 (no alt overlap)
- Algorithm/Method -> Interface/O-O Messages: 2
  - Bugs: Mockito-14 (no family match), Mockito-30 (no family match)
- Algorithm/Method -> Checking: 2
  - Bugs: Mockito-19, Mockito-8
- Algorithm/Method -> Assignment/Initialization: 2
  - Bugs: Mockito-26, Mockito-27
- Interface/O-O Messages -> Checking: 1
  - Bugs: Mockito-16 (no alt overlap, no family match)
- Algorithm/Method -> Function/Class/Object: 1
  - Bugs: Mockito-17 (no family match)
- Function/Class/Object -> Algorithm/Method: 1
  - Bugs: Mockito-20 (no family match)
- Assignment/Initialization -> Relationship: 1
  - Bugs: Mockito-23 (no family match)
- Assignment/Initialization -> Function/Class/Object: 1
  - Bugs: Mockito-32 (no family match)
- Relationship -> Checking: 1
  - Bugs: Mockito-5 (no alt overlap, no family match)

### Type Unchanged

- Algorithm/Method -> Algorithm/Method: 10
  - Bugs: Mockito-11, Mockito-13, Mockito-15, Mockito-1, Mockito-21, Mockito-24, Mockito-28, Mockito-31, Mockito-33, Mockito-3
- Checking -> Checking: 8
  - Bugs: Mockito-22, Mockito-29, Mockito-2, Mockito-34, Mockito-36, Mockito-37, Mockito-38, Mockito-9
