# Defects4J ODC Classification Report: Mockito-21

- Version: `21b`
- Work directory: `C:\d4j_work\prefix\Mockito_21b`
- Generated: `2026-07-25T12:45:12+00:00`

## Failure Summary
- `org.mockito.internal.creation.instance.ConstructorInstantiatorTest::creates_instances_of_inner_classes`: org.mockito.internal.creation.instance.InstantationException: Unable to create mock instance of 'SomeInnerClass'.

## Suspicious Frames
- No suspicious stack frames were extracted.

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The bug is in the logic of the ConstructorInstantiator. It fails to correctly identify the constructor signature for inner classes, which includes the outer class instance. This is a procedural/algorithmic flaw in how the class handles instantiation.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
