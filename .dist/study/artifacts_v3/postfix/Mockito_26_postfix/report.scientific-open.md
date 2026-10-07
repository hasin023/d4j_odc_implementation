# Defects4J ODC Classification Report: Mockito-26

- Version: `26b`
- Work directory: `C:\d4j-work\study-work\postfix\Mockito_26b`
- Generated: `2026-10-07T12:14:42+00:00`

## Failure Summary
- `org.mockito.internal.progress.HandyReturnValuesTest::should_default_values_for_primitive`: java.lang.ClassCastException: class java.lang.Integer cannot be cast to class java.lang.Double (java.lang.Integer and java.lang.Double are in module java.base of loader 'bootstrap')
- `org.mockito.internal.stubbing.defaultanswers.ReturnsEmptyValuesTest::should_return_primitive`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>
- `org.mockito.internal.stubbing.defaultanswers.ReturnsMocksTest::should_return_the_usual_default_values_for_primitives`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>
- `org.mockito.internal.stubbing.defaultanswers.ReturnsSmartNullsTest::should_return_the_usual_default_values_for_primitives`: junit.framework.AssertionFailedError: expected:<0.0> but was:<0>

## Suspicious Frames
- No suspicious stack frames were extracted.

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Assignment/Initialization`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic case of incorrect initialization of a data structure (a Map storing default values for primitives). The fix is a simple correction of the value assigned to the key 'double.class'. This fits the definition of Assignment/Initialization perfectly.

## Scientific Loop

- Turns: `3`
- Termination: `model concluded on its own`
- Loop duration: `11.071s`
- Probe misses: `0`
- Evidence gate: `passed`; conclusions rejected: `1`
- Predicted fix: Change line 66 in org.mockito.internal.util.Primitives from 'primitiveValues.put(double.class, 0);' to 'primitiveValues.put(double.class, 0D);'.

### Turn 1

**Hypothesis.** The bug is caused by an incorrect initialization of the default value for the double primitive type in the Primitives utility class, where an integer 0 is stored instead of a double 0.0D, leading to type mismatch errors during runtime.

**Testing.** `Assignment/Initialization` vs `Algorithm/Method`
**Prediction.** The source code for org.mockito.internal.util.Primitives will show that the map entry for double.class is initialized with an integer 0 instead of a double value.

**Probe.** `source` `org.mockito.internal.util.Primitives`

**Observation.**

```json
{
  "class_name": "org.mockito.internal.util.Primitives",
  "total_lines": 68,
  "legend": "'*' = line executed by the failing test(s) per recorded coverage",
  "content": "      1: /*\n      2:  * Copyright (c) 2007 Mockito contributors\n      3:  * This program is made available under the terms of the MIT License.\n      4:  */\n      5: package org.mockito.internal.util;\n      6: \n      7: import java.util.HashMap;\n      8: import java.util.Map;\n      9: \n     10: @SuppressWarnings(\"unchecked\")\n     11: public class Primitives {\n     12:     \n     13:     public static <T> Class<T> primitiveTypeOf(Class<T> clazz) {\n     14:         if(clazz.isPrimitive()) {\n     15:             return clazz;\n     16:         }\n     17:         return (Class<T>) primitiveTypes.get(clazz);\n     18:     }\n     19: \n     20:     public static boolean isPrimitiveWrapper(Class<?> type) {\n*    21:         return wrapperReturnValues.containsKey(type);\n     22:     }\n     23: \n     24:     public static <T> T primitiveWrapperOf(Class<T> type) {\n     25:         return (T) wrapperReturnValues.get(type);\n     26:     }\n     27: \n     28:     public static <T> T primitiveValueOrNullFor(Class<T> primitiveType) {\n*    29:         return (T) primitiveValues.get(primitiveType);\n     30:     }\n*    31:     private static Map<Class<?>, Class<?>> wrapperTypes = new HashMap<Class<?>, Class<?>>();\n*    32:     private static Map<Class<?>, Class<?>> primitiveTypes = new HashMap<Class<?>, Class<?>>();\n*    33:     private static Map<Class<?>, Object> wrapperReturnValues = new HashMap<Class<?>, Object>();\n*    34:     private static Map<Class<?>, Object> primitiveValues = new HashMap<Class<?>, Object>();\n     35: \n     36:     static {\n*    37:         primitiveTypes.put(Boolean.class, Boolean.TYPE);\n*    38:         primitiveTypes.put(Character.class, Character.TYPE);\n*    39:         primitiveTypes.put(Byte.class, Byte.TYPE);\n*    40:         primitiveTypes.put(Sho
... [truncated — full observation was 3385 chars]
```

_2.618s_

### Turn 2

**Hypothesis.** The bug is caused by an incorrect initialization of the default value for the double primitive type in the Primitives utility class, where an integer 0 is stored instead of a double 0.0D, leading to type mismatch errors during runtime.

**Verdict on previous experiment.** `supported` (quote verified)
> 66:         primitiveValues.put(double.class, 0);

**Testing.** `Assignment/Initialization` vs `Algorithm/Method`
**Prediction.** Changing the initialization of double.class in the primitiveValues map from 0 to 0D will resolve the ClassCastException and assertion failures.

**Conclusion `Assignment/Initialization` rejected by the evidence gate**: predicted_fix is missing — state the concrete code change that would fix the defect

_4.544s_

### Turn 3

**Hypothesis.** The bug is caused by an incorrect initialization of the default value for the double primitive type in the Primitives utility class, where an integer 0 is stored instead of a double 0.0D, leading to type mismatch errors during runtime.

**Verdict on previous experiment.** `supported` (quote verified)
> 66:         primitiveValues.put(double.class, 0);

**Testing.** `Assignment/Initialization` vs `Algorithm/Method`
**Prediction.** Changing the initialization of double.class in the primitiveValues map from 0 to 0D will resolve the ClassCastException and assertion failures.

**Concluded**: `Assignment/Initialization`

_3.909s_
