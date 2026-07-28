# Defects4J ODC Classification Report: Mockito-21

- Version: `21b`
- Work directory: `C:\d4j_work\postfix\Mockito_21b`
- Generated: `2026-07-25T14:49:43+00:00`

## Failure Summary
- `org.mockito.internal.creation.instance.ConstructorInstantiatorTest::creates_instances_of_inner_classes`: org.mockito.internal.creation.instance.InstantationException: Unable to create mock instance of 'SomeInnerClass'.

## Suspicious Frames
- No suspicious stack frames were extracted.

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Inflexible Constructor Selection Logic`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The original implementation of 'ConstructorInstantiator' was hardcoded to look for a constructor matching the exact class of the outer instance. This failed when the inner class constructor expected a superclass or interface of the provided outer instance, or when the constructor signature did not match the expected type hierarchy. The fix replaces this rigid lookup with a more robust 'paramsMatch' mechanism that iterates through available constructors and verifies parameter compatibility using 'isInstance', allowing for polymorphic constructor injection.
