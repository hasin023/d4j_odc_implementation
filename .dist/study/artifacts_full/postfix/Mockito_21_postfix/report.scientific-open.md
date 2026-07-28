# Defects4J ODC Classification Report: Mockito-21

- Version: `21b`
- Work directory: `C:\d4j_work\postfix\Mockito_21b`
- Generated: `2026-07-25T12:45:19+00:00`

## Failure Summary
- `org.mockito.internal.creation.instance.ConstructorInstantiatorTest::creates_instances_of_inner_classes`: org.mockito.internal.creation.instance.InstantationException: Unable to create mock instance of 'SomeInnerClass'.

## Suspicious Frames
- No suspicious stack frames were extracted.

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a procedural error in how the constructor is selected. The original implementation used a rigid lookup that failed to account for inheritance in the outer class instance. This is a classic algorithmic/method-level defect in the instantiation logic.

## ODC Attribute Mapping (Optional)
- Impact: `Capability`
