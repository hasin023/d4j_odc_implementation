# Defects4J ODC Classification Report: Mockito-21

- Version: `21b`
- Work directory: `C:\d4j_work\prefix\Mockito_21b`
- Generated: `2026-07-25T12:52:41+00:00`

## Failure Summary
- `org.mockito.internal.creation.instance.ConstructorInstantiatorTest::creates_instances_of_inner_classes`: org.mockito.internal.creation.instance.InstantationException: Unable to create mock instance of 'SomeInnerClass'.

## Suspicious Frames
- No suspicious stack frames were extracted.

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.8`
- Needs Human Review: `False`

The issue is a failure in the procedural logic responsible for instantiating inner classes. The 'ConstructorInstantiator' is unable to correctly associate the provided outer instance with the inner class, which is a procedural/algorithmic failure in how the constructor parameters are resolved. It is not a missing check (Checking), a wrong constant (Assignment), or a design-level capability omission (Function/Class/Object), but rather an incorrect implementation of the instantiation algorithm for inner classes.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
