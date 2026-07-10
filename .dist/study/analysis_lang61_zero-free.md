# Batch Study Analysis

- Created: `2026-07-10T19:57:08+00:00`
- Total pairs: **61**
- Projects covered: **1**
- Type changed: **46** (75.4%)
- Type unchanged: **15** (24.6%)
- No alternative overlap: **46** (75.4%)
- No family match: **0** (0.0%)
- Family match: **61** (100.0%)

## Alternative Match Cases (Type Changed)

- No qualifying cases found.
## Type Changed (No Alternative Overlap)

### Lang-10
- Type shift: Incorrect Regex Pattern Generation -> Incorrect Regex Generation for Whitespace.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Regex Pattern Generation' vs 'Incorrect Regex Generation for Whitespace')
- Prefix reasoning summary: The FastDateParser implementation incorrectly translates date format patterns into regular expressions. Specifically, it treats whitespace in the format string as a greedy match for any number of whitespace characters (using \s*+), whereas standard Java SimpleDateFormat behavior is more restrictive. This causes the parser to successfully parse input strings that should be considered invalid according to the specified format, leading to discrepancies between FastDateParser and SimpleDateFormat.
- Postfix reasoning summary: The bug report and the fix diff indicate that FastDateParser was incorrectly treating whitespace in format strings as a greedy match for any number of whitespace characters (using \s*+). This caused the parser to successfully parse date strings that should have failed according to the stricter behavior of SimpleDateFormat. The fix involved removing the logic that explicitly converted whitespace characters into the \s*+ regex pattern, ensuring that whitespace is handled according to the standard parsing rules.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormat_ParserTest::testLANG_831: junit.framework.AssertionFailedError: Parsed dates should be equal expected:<null> but was:<Mon Mar 02 21:00:00 PST 1970>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormat_ParserTest::testLANG_831: junit.framework.AssertionFailedError: Parsed dates should be equal expected:<null> but was:<Mon Mar 02 21:00:00 PST 1970>

### Lang-11
- Type shift: Inadequate Exception Handling -> Insufficient Input Validation.
- Comparison detail: Family match only: both 'None' but types differ ('Inadequate Exception Handling' vs 'Insufficient Input Validation')
- Prefix reasoning summary: The code fails to validate input parameters (start and end) before passing them to the underlying Random.nextInt() method. When end <= start, the resulting bound passed to Random.nextInt() is non-positive, causing the Random class to throw an IllegalArgumentException with the message 'n must be positive'. The test expects a more descriptive error message that explicitly mentions 'start' and 'end' to help the user identify the invalid input, but the current implementation allows the generic exception from the Random class to propagate, failing the assertion in the test.
- Postfix reasoning summary: The code failed to validate the relationship between the 'start' and 'end' parameters before passing them to the Random.nextInt() method. When 'end' was less than or equal to 'start', the underlying Random class threw a generic 'bound must be positive' exception, which was misleading to the user. The fix introduces an explicit check to ensure 'end' is greater than 'start' and throws a descriptive IllegalArgumentException, providing clear feedback about the invalid input parameters.
- Prefix context signal: org.apache.commons.lang3.RandomStringUtilsTest::testLANG807: junit.framework.AssertionFailedError: Message (bound must be positive) must contain 'start'
- Postfix context signal: org.apache.commons.lang3.RandomStringUtilsTest::testLANG807: junit.framework.AssertionFailedError: Message (bound must be positive) must contain 'start'

### Lang-20
- Type shift: NullPointerException due to unsafe toString() invocation -> NullPointerException due to unsafe object property access.
- Comparison detail: Family match only: both 'None' but types differ ('NullPointerException due to unsafe toString() invocation' vs 'NullPointerException due to unsafe object property access')
- Prefix reasoning summary: The code in StringUtils.join attempts to calculate the initial capacity of a StringBuilder by calling .toString().length() on the first element of the array (or other elements). If an object in the array returns null from its toString() method, the subsequent call to .length() on that null result triggers a NullPointerException. The implementation assumes that toString() will always return a non-null String, which is not guaranteed by the Java contract.
- Postfix reasoning summary: The code attempted to calculate the initial capacity of a StringBuilder by calling .toString().length() on the first element of an array. If the object's toString() method returned null, the subsequent call to .length() on that null result triggered a NullPointerException. The fix replaces this fragile size estimation logic with a safe, constant-based estimation (noOfItems * 16), which avoids invoking methods on potentially null-returning objects during the initialization phase.
- Prefix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang3.StringUtilsTest::testJoin_ArrayChar: java.lang.NullPointerException

### Lang-22
- Type shift: integer overflow handling error -> Integer overflow in GCD calculation.
- Comparison detail: Family match only: both 'None' but types differ ('integer overflow handling error' vs 'Integer overflow in GCD calculation')
- Prefix reasoning summary: The bug occurs because the greatestCommonDivisor (GCD) calculation fails to correctly handle Integer.MIN_VALUE when it is used as a numerator. In Java, Math.abs(Integer.MIN_VALUE) returns Integer.MIN_VALUE due to two's complement overflow, which causes the GCD algorithm to produce incorrect results or fail to reduce the fraction properly. The failing tests demonstrate that when the numerator is Integer.MIN_VALUE and the denominator is 2, the fraction is not reduced as expected, leading to an assertion failure where the numerator remains Integer.MIN_VALUE instead of being divided by the GCD.
- Postfix reasoning summary: The bug occurs because the `greatestCommonDivisor` method fails to handle `Integer.MIN_VALUE` correctly. When `Integer.MIN_VALUE` is passed, `Math.abs(Integer.MIN_VALUE)` returns `Integer.MIN_VALUE` due to two's complement overflow, which causes the existing logic to incorrectly identify the GCD or fail to reduce the fraction. The fix introduces explicit handling for zero values and `Integer.MIN_VALUE` to prevent this overflow and ensure the GCD is calculated correctly.
- Prefix context signal: org.apache.commons.lang3.math.FractionTest::testReducedFactory_int_int: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>
- Postfix context signal: org.apache.commons.lang3.math.FractionTest::testReducedFactory_int_int: junit.framework.AssertionFailedError: expected:<-1073741824> but was:<-2147483648>

### Lang-23
- Type shift: Inconsistent hashCode implementation -> Missing Override of equals() and hashCode().
- Comparison detail: Family match only: both 'None' but types differ ('Inconsistent hashCode implementation' vs 'Missing Override of equals() and hashCode()')
- Prefix reasoning summary: The class ExtendedMessageFormat extends java.text.MessageFormat but fails to override the equals() and hashCode() methods to account for its own internal state (specifically the registry field). As a result, two instances with different registries are considered equal by the inherited equals() method, and they produce identical hash codes, violating the contract that unequal objects should ideally have different hash codes and that the hashCode must be consistent with equals.
- Postfix reasoning summary: The class ExtendedMessageFormat extends java.text.MessageFormat but introduces new fields (registry and toPattern) that affect the logical equality of the object. The original implementation failed to override equals() and hashCode(), causing instances with different registries or patterns to be considered equal by the default implementation inherited from the superclass or Object. The fix correctly implements these methods to include the new fields in the equality and hash calculation, ensuring that the object's state is properly accounted for.
- Prefix context signal: org.apache.commons.lang3.text.ExtendedMessageFormatTest::testEqualsHashcode: junit.framework.AssertionFailedError: registry, hashcode()
- Postfix context signal: org.apache.commons.lang3.text.ExtendedMessageFormatTest::testEqualsHashcode: junit.framework.AssertionFailedError: registry, hashcode()

### Lang-26
- Type shift: Locale-dependent configuration mismatch -> Locale-dependent configuration omission.
- Comparison detail: Family match only: both 'None' but types differ ('Locale-dependent configuration mismatch' vs 'Locale-dependent configuration omission')
- Prefix reasoning summary: The bug occurs because FastDateFormat fails to correctly apply the locale-specific rules for 'week of year' calculations (specifically firstDayOfWeek and minimalDaysInFirstWeek). While the user provides a locale to the FastDateFormat instance, the internal implementation defaults to system-wide calendar settings rather than deriving these settings from the provided locale, leading to incorrect week numbering when the system locale differs from the requested locale.
- Postfix reasoning summary: The bug occurred because the FastDateFormat class failed to utilize the provided locale when instantiating a GregorianCalendar object during the formatting process. As a result, the calendar defaulted to the system's locale settings for properties like 'firstDayOfWeek' and 'minimalDaysInFirstWeek', leading to incorrect week-of-year calculations when the desired locale differed from the system default. The fix involved passing the stored mLocale instance to the GregorianCalendar constructor, ensuring that locale-specific calendar rules are correctly applied.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang645: junit.framework.ComparisonFailure: expected:<fredag, week [53]> but was:<fredag, week [01]>

### Lang-28
- Type shift: Unicode supplementary character handling error -> Incorrect character encoding handling.
- Comparison detail: Family match only: both 'None' but types differ ('Unicode supplementary character handling error' vs 'Incorrect character encoding handling')
- Prefix reasoning summary: The failing test demonstrates that the NumericEntityUnescaper fails to correctly process a numeric entity representing a supplementary character (code point > 0xFFFF). The error message shows that the unescaper produced a single character (U+0C22) instead of the expected surrogate pair (U+D803 U+DC22). This indicates that the unescaper logic is likely treating the numeric entity as a standard 16-bit character rather than correctly converting the code point into a surrogate pair, which is required for characters outside the Basic Multilingual Plane in Java.
- Postfix reasoning summary: The bug occurs because the NumericEntityUnescaper was treating all numeric entities as single 16-bit characters. When encountering supplementary characters (Unicode code points above 0xFFFF), which require two 16-bit characters (a surrogate pair) in Java, the original code failed to correctly convert the integer entity value into the appropriate surrogate pair. The fix introduces logic to check if the entity value exceeds 0xFFFF and, if so, uses Character.toChars() to correctly write the surrogate pair to the output stream.
- Prefix context signal: org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>
- Postfix context signal: org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testSupplementaryUnescaping: junit.framework.ComparisonFailure: Failed to unescape numeric entities supplementary characters expected:<[𐰢]> but was:<[ఢ]>

### Lang-29
- Type shift: Type Mismatch / Incorrect Return Type -> Incorrect Return Type Declaration.
- Comparison detail: Family match only: both 'None' but types differ ('Type Mismatch / Incorrect Return Type' vs 'Incorrect Return Type Declaration')
- Prefix reasoning summary: The failing test indicates an assertion error where the expected value is an integer (0) but the actual value returned by the method is a floating-point number (0.0). This suggests that the implementation of SystemUtils.toJavaVersionInt is incorrectly returning a float or double type instead of an integer, causing a type mismatch during the equality check in the test suite.
- Postfix reasoning summary: The method 'toJavaVersionInt' was declared to return a 'float' instead of an 'int'. This caused the method to return a floating-point representation (e.g., 0.0) when an integer was expected, leading to assertion failures in the test suite where 'assertEquals(0, ...)' was used. The fix involved changing the return type signature from 'float' to 'int', which correctly aligns the implementation with the method's intended purpose and name.
- Prefix context signal: org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>
- Postfix context signal: org.apache.commons.lang3.SystemUtilsTest::testJavaVersionAsInt: junit.framework.AssertionFailedError: expected:<0> but was:<0.0>

### Lang-30
- Type shift: Unicode supplementary character handling error -> Unicode Supplementary Character Handling Error.
- Comparison detail: Family match only: both 'None' but types differ ('Unicode supplementary character handling error' vs 'Unicode Supplementary Character Handling Error')
- Prefix reasoning summary: The StringUtils methods (such as containsAny, containsNone, and indexOfAny) are failing to correctly process Unicode supplementary characters (characters outside the Basic Multilingual Plane, represented as surrogate pairs in Java). The evidence shows that while standard JRE methods like String.indexOf() handle these surrogate pairs correctly, the custom implementations in StringUtils treat the high and low surrogates as individual characters, leading to incorrect matching logic when searching for or excluding these characters.
- Postfix reasoning summary: The code failed to correctly process Unicode supplementary characters (which are represented as surrogate pairs in Java). The original implementation treated each 16-bit char in a surrogate pair as an independent character, leading to incorrect matching logic when searching for or excluding these characters. The fix introduces checks using Character.isHighSurrogate(ch) to ensure that when a high surrogate is encountered, the subsequent low surrogate is also considered as part of the same character unit, preventing partial or incorrect matches.
- Prefix context signal: org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_CharArrayWithSupplementaryChars: junit.framework.AssertionFailedError: expected:<true> but was:<false>
- Postfix context signal: org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsNone_CharArrayWithSupplementaryChars: junit.framework.AssertionFailedError: expected:<true> but was:<false>

### Lang-32
- Type shift: Resource Leak (ThreadLocal) -> Resource Leak / Improper ThreadLocal Lifecycle Management.
- Comparison detail: Family match only: both 'None' but types differ ('Resource Leak (ThreadLocal)' vs 'Resource Leak / Improper ThreadLocal Lifecycle Management')
- Prefix reasoning summary: The test failure indicates that the registry used by HashCodeBuilder to track objects during reflection-based hashCode calculation is not being cleared after execution. The registry, which is likely implemented using a ThreadLocal, persists across method calls. Because the registry is not properly cleaned up (unregistered) after the hashCode calculation completes, it remains in a non-null state (containing an empty collection or references), causing the assertion 'assertNull(HashCodeBuilder.getRegistry())' to fail. This confirms that the internal state management for tracking object cycles is leaking.
- Postfix reasoning summary: The bug involves the improper management of a ThreadLocal variable used to track object cycles during hash code calculation. In the buggy version, the ThreadLocal was initialized with a default value (an empty HashSet), meaning it would persist for the lifetime of the thread. In containerized environments like web servers, this causes memory leaks because the ThreadLocal holds references to classes loaded by the web application's classloader, preventing garbage collection upon application undeployment. The fix ensures the ThreadLocal is only initialized when needed and explicitly removed when the registry becomes empty, preventing the accumulation of stale references.
- Prefix context signal: org.apache.commons.lang3.builder.HashCodeBuilderTest::testReflectionObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: []
- Postfix context signal: org.apache.commons.lang3.builder.HashCodeBuilderTest::testReflectionObjectCycle: junit.framework.AssertionFailedError: Expected: <null> but was: []

### Lang-37
- Type shift: Type safety violation in array concatenation -> Inadequate Exception Handling.
- Comparison detail: Family match only: both 'None' but types differ ('Type safety violation in array concatenation' vs 'Inadequate Exception Handling')
- Prefix reasoning summary: The method ArrayUtils.addAll uses the component type of the first array (array1) to create a new array for the result. When the second array (array2) contains elements that are not assignable to the component type of the first array, System.arraycopy throws an ArrayStoreException. The implementation fails to validate that the elements of the second array are compatible with the type of the destination array before attempting the copy operation.
- Postfix reasoning summary: The method ArrayUtils.addAll attempts to perform an array copy using System.arraycopy without validating that the component types of the two input arrays are compatible. When incompatible types are provided (e.g., attempting to copy a Long[] into an Integer[]), the JVM throws an ArrayStoreException, which is a low-level runtime exception that does not clearly communicate the nature of the failure to the API user. The fix introduces a try-catch block around the array copy operation to catch the ArrayStoreException, verify the type incompatibility, and rethrow a more descriptive IllegalArgumentException, which is the expected behavior for an API utility method.
- Prefix context signal: org.apache.commons.lang3.ArrayUtilsAddTest::testJira567: java.lang.ArrayStoreException: arraycopy: type mismatch: can not copy java.lang.Long[] into java.lang.Integer[]
- Postfix context signal: org.apache.commons.lang3.ArrayUtilsAddTest::testJira567: java.lang.ArrayStoreException: arraycopy: type mismatch: can not copy java.lang.Long[] into java.lang.Integer[]

### Lang-38
- Type shift: Calendar state inconsistency -> Lazy initialization failure in Calendar API.
- Comparison detail: Family match only: both 'None' but types differ ('Calendar state inconsistency' vs 'Lazy initialization failure in Calendar API')
- Prefix reasoning summary: The issue arises because the GregorianCalendar object's internal fields are not synchronized with its time zone when the calendar is modified via set() methods without a subsequent call to getTime() or getTimeInMillis(). FastDateFormat relies on the calendar's internal state to perform formatting. When the time zone is changed or the calendar is initialized in a specific way, the internal time fields may remain stale relative to the new time zone, leading to incorrect output during formatting. The bug report confirms that calling cal.getTime() forces the calendar to recompute its internal fields, resolving the discrepancy.
- Postfix reasoning summary: The issue stems from the Java Calendar API's internal state management. When a Calendar object is modified (e.g., setting fields), the internal time representation is not always immediately recalculated. If a TimeZone is changed on such a 'dirty' Calendar object, the internal fields may become inconsistent with the new timezone. The fix involves calling calendar.getTime() before cloning and modifying the timezone, which forces the Calendar to synchronize its internal fields and resolve the state inconsistency.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang538: junit.framework.ComparisonFailure: dateTime expected:<2009-10-16T[16]:42:16.000Z> but was:<2009-10-16T[08]:42:16.000Z>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormatTest::testLang538: junit.framework.ComparisonFailure: dateTime expected:<2009-10-16T[16]:42:16.000Z> but was:<2009-10-16T[08]:42:16.000Z>

### Lang-3
- Type shift: Incorrect Type Inference Logic -> Incorrect Type Inference / Precision Loss.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Type Inference Logic' vs 'Incorrect Type Inference / Precision Loss')
- Prefix reasoning summary: The method NumberUtils.createNumber attempts to parse numeric strings by checking for specific types in a fixed order. The evidence indicates that the implementation incorrectly prioritizes the 'Float' type for all floating-point numbers. When a string represents a number that exceeds the range or precision of a Float (such as the value '3.40282354e+38'), the logic fails to correctly identify it as a Double or BigDecimal, leading to truncation or incorrect type instantiation. The failing test confirms that the method returns a type other than the expected Double for a value that is clearly outside the range of a Float.
- Postfix reasoning summary: The method 'createNumber' was designed to convert strings to the smallest possible numeric type. However, it incorrectly attempted to parse all floating-point strings as 'Float' first. Because 'Float' has lower precision than 'Double' or 'BigDecimal', many numbers were being truncated or rounded during the initial 'Float' conversion attempt, leading to precision loss. The fix introduces logic to check the number of decimal places before attempting to parse as 'Float' or 'Double', ensuring that numbers requiring higher precision are not prematurely forced into a 'Float' type.
- Prefix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testStringCreateNumberEnsureNoPrecisionLoss: junit.framework.AssertionFailedError
- Postfix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testStringCreateNumberEnsureNoPrecisionLoss: junit.framework.AssertionFailedError

### Lang-40
- Type shift: Locale-sensitive case conversion -> Locale-sensitive case conversion error.
- Comparison detail: Family match only: both 'None' but types differ ('Locale-sensitive case conversion' vs 'Locale-sensitive case conversion error')
- Prefix reasoning summary: The bug occurs because the code uses locale-sensitive string case conversion methods (like String.toUpperCase() or String.toLowerCase()) for case-insensitive comparisons. In certain locales, such as Turkish, character mappings differ from the standard Unicode expectations (e.g., 'i' to 'I' mapping). The failing test demonstrates that the character 'ß' (German sharp S) is being incorrectly treated as equivalent to 'SS' in a case-insensitive comparison, which is a known issue when locale-dependent case folding is applied inappropriately.
- Postfix reasoning summary: The original implementation of StringUtils.containsIgnoreCase used String.toUpperCase() to perform case-insensitive comparisons. Because String.toUpperCase() is locale-sensitive, it produces different results depending on the default locale of the JVM (e.g., the Turkish locale treats 'i' differently). This causes the method to behave inconsistently across different environments. The fix replaces the locale-dependent conversion with String.regionMatches(true, ...), which performs a locale-independent, case-insensitive comparison, ensuring consistent behavior regardless of the system locale.
- Prefix context signal: org.apache.commons.lang.StringUtilsEqualsIndexOfTest::testContainsIgnoreCase_LocaleIndependence: junit.framework.AssertionFailedError: en: 0 ß SS
- Postfix context signal: org.apache.commons.lang.StringUtilsEqualsIndexOfTest::testContainsIgnoreCase_LocaleIndependence: junit.framework.AssertionFailedError: en: 0 ß SS

### Lang-49
- Type shift: Incorrect Logic in Fraction Reduction -> Incorrect logic for handling zero-numerator fractions.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Logic in Fraction Reduction' vs 'Incorrect logic for handling zero-numerator fractions')
- Prefix reasoning summary: The test case fails because the Fraction.reduce() method does not correctly normalize fractions where the numerator is zero. When the numerator is 0, the denominator should be reduced to 1 to represent the canonical form of zero (0/1). The failing test shows that for a fraction like 0/100, the reduce() method returns a fraction with a denominator of 100 instead of 1, indicating that the reduction logic fails to handle the zero-numerator case correctly.
- Postfix reasoning summary: The bug occurs because the `reduce()` method in the `Fraction` class fails to correctly handle fractions where the numerator is zero. When the numerator is zero, the greatest common divisor (GCD) calculation logic is bypassed or handled incorrectly, leading to a fraction that retains its original denominator (e.g., 0/100) instead of being reduced to the canonical form (0/1). The fix introduces an explicit check for a zero numerator, ensuring that such fractions are correctly returned as the canonical zero fraction.
- Prefix context signal: org.apache.commons.lang.math.FractionTest::testReduce: junit.framework.AssertionFailedError: expected:<1> but was:<100>
- Postfix context signal: org.apache.commons.lang.math.FractionTest::testReduce: junit.framework.AssertionFailedError: expected:<1> but was:<100>

### Lang-50
- Type shift: caching inconsistency due to stale locale dependency -> caching inconsistency due to improper key generation.
- Comparison detail: Family match only: both 'None' but types differ ('caching inconsistency due to stale locale dependency' vs 'caching inconsistency due to improper key generation')
- Prefix reasoning summary: The FastDateFormat class uses a caching mechanism (likely a HashMap) to store instances based on parameters, including the locale. When a locale is not explicitly provided, the implementation defaults to the current system locale. However, the cache key generation logic fails to account for subsequent changes to the default system locale. Consequently, when the default locale is updated, the cache returns a previously instantiated object that was created with the old locale, leading to the observed mismatch in the test cases.
- Postfix reasoning summary: The bug occurs because the caching mechanism for FastDateFormat instances used a key that did not consistently include the Locale. When the locale was null, it was omitted from the cache key, but the instance was created using the default locale at that time. If the default locale changed later, the cache would return an instance created with the old default locale instead of the new one, because the key did not account for the dependency on the default locale. The fix ensures that the locale is always included in the cache key, defaulting to the current system locale if null, thereby preventing stale cache hits.
- Prefix context signal: org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateInstance: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>
- Postfix context signal: org.apache.commons.lang.time.FastDateFormatTest::test_changeDefault_Locale_DateInstance: junit.framework.AssertionFailedError: expected same:<de_DE> was not:<en_US>

### Lang-53
- Type shift: incorrect rounding logic -> logic error in rounding algorithm.
- Comparison detail: Family match only: both 'None' but types differ ('incorrect rounding logic' vs 'logic error in rounding algorithm')
- Prefix reasoning summary: The DateUtils.round() method is failing to correctly round time units (minutes/seconds) because the internal implementation likely resets or incorrectly calculates the field values during the rounding process. The test case shows that when rounding 08:08:50 to the nearest minute, the result is 08:01:00 instead of the expected 08:09:00, indicating that the logic is incorrectly clearing or miscalculating the minute field instead of performing a proper round-up operation.
- Postfix reasoning summary: The bug is caused by incorrect placement of closing braces in the `modify` method of `DateUtils`. In the buggy version, the `if (field == Calendar.SECOND)` and `if (field == Calendar.MINUTE)` checks were nested inside the `if (!round || millisecs < 500)` and `if (!done && (!round || seconds < 30))` blocks respectively. This meant that if the rounding condition (e.g., milliseconds < 500) was false, the code would skip the check to see if it should stop rounding at that field, leading to incorrect truncation or rounding behavior. The fix correctly moves these field checks outside the conditional blocks so that the `done` flag is set regardless of whether the rounding threshold was met.
- Prefix context signal: org.apache.commons.lang.time.DateUtilsTest::testRoundLang346: junit.framework.AssertionFailedError: Minute Round Up Failed expected:<Mon Jul 02 08:09:00 PDT 2007> but was:<Mon Jul 02 08:01:00 PDT 2007>
- Postfix context signal: org.apache.commons.lang.time.DateUtilsTest::testRoundLang346: junit.framework.AssertionFailedError: Minute Round Up Failed expected:<Mon Jul 02 08:09:00 PDT 2007> but was:<Mon Jul 02 08:01:00 PDT 2007>

### Lang-61
- Type shift: Off-by-one error in array manipulation -> incorrect boundary condition in search algorithm.
- Comparison detail: Family match only: both 'None' but types differ ('Off-by-one error in array manipulation' vs 'incorrect boundary condition in search algorithm')
- Prefix reasoning summary: The bug occurs in the `deleteImpl` method of `StrBuilder`, which is called by `deleteAll`. The `System.arraycopy` call at line 1114 uses `size - endIndex` as the length parameter. When `endIndex` is equal to `size` (i.e., deleting until the end of the buffer), the length becomes 0, which is valid. However, the logic fails to account for cases where the internal state or index calculations in `deleteAll` lead to an invalid range or incorrect buffer shifting, resulting in an `ArrayIndexOutOfBoundsException` or incorrect string state. The stack trace confirms that `System.arraycopy` is receiving invalid parameters, specifically a negative length in some scenarios, indicating that the index arithmetic is flawed.
- Postfix reasoning summary: The bug occurs because the indexOf method in StrBuilder was searching the entire underlying character buffer, including 'junk' data beyond the current valid size of the string. This caused the method to return incorrect indices (finding matches in the buffer's tail) and subsequently caused ArrayIndexOutOfBoundsException in methods like deleteImpl and replaceImpl, which relied on these incorrect indices to perform array operations. The fix correctly limits the search range to the current valid size of the string.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testIndexOfLang294: junit.framework.AssertionFailedError: expected:<-1> but was:<6>
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testIndexOfLang294: junit.framework.AssertionFailedError: expected:<-1> but was:<6>

### Lang-62
- Type shift: Integer overflow handling error -> Integer overflow / Unchecked range validation.
- Comparison detail: Family match only: both 'None' but types differ ('Integer overflow handling error' vs 'Integer overflow / Unchecked range validation')
- Prefix reasoning summary: The code fails to correctly handle numeric character references that exceed the maximum value of a Java char (0xFFFF). When the unescape logic encounters a numeric entity like '&#12345678;', it attempts to parse the number and cast it to a character. Because 12345678 is significantly larger than 65535, the cast results in an incorrect character representation (truncation), whereas the specification requires that invalid or out-of-range numeric entities should be treated as literal text rather than being converted to an incorrect character.
- Postfix reasoning summary: The code failed to validate that the parsed numeric value of an XML entity reference fits within the range of a valid Java character (0xFFFF). When an entity like '&#12345678;' was provided, the parser attempted to convert the large integer into a character, resulting in an incorrect character representation or overflow behavior. The fix introduces a check to ensure the parsed integer does not exceed 0xFFFF, treating values outside this range as invalid entities, which correctly preserves the original string as expected.
- Prefix context signal: org.apache.commons.lang.EntitiesTest::testNumberOverflow: junit.framework.ComparisonFailure: expected:<[&#12345678;]> but was:<[慎]>
- Postfix context signal: org.apache.commons.lang.EntitiesTest::testNumberOverflow: junit.framework.ComparisonFailure: expected:<[&#12345678;]> but was:<[慎]>

### Lang-63
- Type shift: Incorrect Date Arithmetic Logic -> Incorrect Calendar Arithmetic Logic.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Date Arithmetic Logic' vs 'Incorrect Calendar Arithmetic Logic')
- Prefix reasoning summary: The test case demonstrates that DurationFormatUtils.formatPeriod fails to correctly calculate the difference in months between two dates when the start date is at the end of a year (December 31st). The resulting value of -2 indicates that the internal logic for calculating the duration period is incorrectly handling the transition between years or the month subtraction, leading to an invalid negative result instead of the expected positive duration.
- Postfix reasoning summary: The bug was caused by an incorrect implementation of duration calculation between two dates. Specifically, the code used a hardcoded 'days += 31' logic when handling negative day differences, which failed to account for the varying number of days in different months. Additionally, the 'reduceAndCorrect' method was performing redundant and flawed adjustments to the calendar fields, leading to incorrect results (e.g., negative values). The fix involved replacing the hardcoded addition with dynamic calendar manipulation using 'getActualMaximum(Calendar.DAY_OF_MONTH)' and removing the faulty 'reduceAndCorrect' helper method entirely.
- Prefix context signal: org.apache.commons.lang.time.DurationFormatUtilsTest::testJiraLang281: junit.framework.ComparisonFailure: expected:<[09]> but was:<[-2]>
- Postfix context signal: org.apache.commons.lang.time.DurationFormatUtilsTest::testJiraLang281: junit.framework.ComparisonFailure: expected:<[09]> but was:<[-2]>

### Lang-64
- Type shift: Inadequate Type Safety in Comparison Logic -> Type safety violation in comparison logic.
- Comparison detail: Family match only: both 'None' but types differ ('Inadequate Type Safety in Comparison Logic' vs 'Type safety violation in comparison logic')
- Prefix reasoning summary: The ValuedEnum.compareTo method fails to verify that the object being compared is of the same class as the current instance. Because it only compares the underlying integer values, it incorrectly returns 0 (indicating equality) when comparing two different subclasses of ValuedEnum that happen to share the same integer value. The test case expects a ClassCastException when comparing different Enum types, but the implementation proceeds to compare the values, causing the assertion to fail.
- Postfix reasoning summary: The bug exists because the compareTo method in ValuedEnum performed a direct subtraction of integer values without verifying that the objects being compared belonged to the same class. This allowed two different enum types that happened to share the same integer value to be considered equal, violating type safety. The fix introduces a class check to ensure that only instances of the same enum class (or compatible classes loaded by different classloaders) are compared, throwing a ClassCastException otherwise.
- Prefix context signal: org.apache.commons.lang.enums.ValuedEnumTest::testCompareTo_otherEnumType: junit.framework.AssertionFailedError
- Postfix context signal: org.apache.commons.lang.enums.ValuedEnumTest::testCompareTo_otherEnumType: junit.framework.AssertionFailedError

### Lang-7
- Type shift: Inconsistent Exception Handling -> Inconsistent Error Handling.
- Comparison detail: Family match only: both 'None' but types differ ('Inconsistent Exception Handling' vs 'Inconsistent Error Handling')
- Prefix reasoning summary: The code in NumberUtils.createNumber is designed to handle numeric string parsing. The bug report and test failure indicate that when the input string contains a double negative sign ('--'), the method returns null instead of throwing a NumberFormatException as expected by the API contract and the test case. This inconsistency violates the expected behavior for invalid numeric inputs, which should consistently result in an exception rather than a null return value.
- Postfix reasoning summary: The code contained a special check for a leading '--' in the input string within the 'createNumber' method, which returned 'null' instead of throwing an exception. This behavior was inconsistent with the method's contract and the behavior of other parsing methods in the class, which are expected to throw a 'NumberFormatException' for invalid input. The fix involved removing this inconsistent check from 'createNumber' and moving the validation logic to 'createBigDecimal', where it now correctly throws a 'NumberFormatException' when such an invalid pattern is encountered.
- Prefix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: junit.framework.AssertionFailedError: Expected NumberFormatException
- Postfix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: junit.framework.AssertionFailedError: Expected NumberFormatException

### Lang-9
- Type shift: Incorrect Input Validation / Parsing Logic -> Improper Input Validation.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Input Validation / Parsing Logic' vs 'Improper Input Validation')
- Prefix reasoning summary: The FastDateParser fails to correctly handle unterminated quotes in date format strings. When provided with an invalid format like "'d'd'", the parser should throw an exception because the quote is not properly closed. Instead, the parser incorrectly interprets the format and successfully parses the input string, leading to a mismatch with the expected behavior of SimpleDateFormat. The evidence shows that the test case expects a failure (shouldFail = true), but the parser returns a valid date object, indicating that the internal state machine or regex generation logic for the parser does not validate the integrity of quoted sections.
- Postfix reasoning summary: The bug occurs because the FastDateParser fails to validate that the entire format string has been consumed during the parsing process. When an unterminated quote is present in the format string, the parser ignores the trailing invalid characters instead of throwing an exception, leading to incorrect successful parses. The fix introduces a check using the pattern matcher's region boundaries to ensure that the entire input pattern has been processed, throwing an IllegalArgumentException if any part of the pattern remains unparsed.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormat_ParserTest::testLANG_832: junit.framework.AssertionFailedError: Parsed dates should be equal expected:<null> but was:<Fri Jan 02 21:00:00 PST 1970>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormat_ParserTest::testLANG_832: junit.framework.AssertionFailedError: Parsed dates should be equal expected:<null> but was:<Fri Jan 02 21:00:00 PST 1970>

### Lang-12
- Type shift: Incorrect Array Index Calculation -> Input Validation Error.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Array Index Calculation' vs 'Input Validation Error')
- Prefix reasoning summary: The code in RandomStringUtils.random() calculates an index for the 'chars' array using 'random.nextInt(gap) + start'. This logic assumes that the range defined by 'start' and 'gap' (which is 'end - start') maps directly to valid indices within the provided 'chars' array. However, when 'chars' is provided, the method should select a random index within the bounds of the array itself, rather than using the 'start' and 'gap' parameters which are intended for character range generation. Consequently, the calculated index frequently exceeds the array's length, triggering an ArrayIndexOutOfBoundsException.
- Postfix reasoning summary: The code failed to validate the input parameters 'start' and 'end' when provided with a character array, and it did not handle the case where the provided character array was empty. This led to an ArrayIndexOutOfBoundsException because the logic calculated an index based on 'start' and 'gap' (end - start) without ensuring these values were within the bounds of the provided array. The fix introduces explicit checks for empty arrays and correctly initializes 'end' to the array length when it is not provided, preventing invalid index calculations.
- Prefix context signal: org.apache.commons.lang3.RandomStringUtilsTest::testExceptions: java.lang.ArrayIndexOutOfBoundsException: Index 304389849 out of bounds for length 0
- Postfix context signal: org.apache.commons.lang3.RandomStringUtilsTest::testExceptions: java.lang.ArrayIndexOutOfBoundsException: Index 1490277398 out of bounds for length 0

### Lang-13
- Type shift: Incomplete ClassLoader resolution logic -> Incomplete Class Resolution Logic.
- Comparison detail: Family match only: both 'None' but types differ ('Incomplete ClassLoader resolution logic' vs 'Incomplete Class Resolution Logic')
- Prefix reasoning summary: The ClassLoaderAwareObjectInputStream class overrides the resolveClass method to attempt class loading using a specific class loader and then the thread's context class loader. However, it fails to handle primitive types (like int.class) because it does not delegate to the super.resolveClass() method when both custom class loading attempts fail. The standard ObjectInputStream implementation includes internal logic to resolve primitive class names, which is bypassed by this custom implementation, leading to a ClassNotFoundException when serializing/deserializing primitive class objects.
- Postfix reasoning summary: The bug occurs because the custom 'ClassLoaderAwareObjectInputStream' overrides 'resolveClass' to handle class loading but fails to account for primitive types (e.g., 'int.class', 'void.class'). When the standard 'Class.forName' calls fail to resolve these primitive names, the implementation throws a 'ClassNotFoundException' instead of checking a registry of primitive types, which is the standard behavior required for Java serialization to function correctly with primitive class objects.
- Prefix context signal: org.apache.commons.lang3.SerializationUtilsTest::testPrimitiveTypeClassSerialization: org.apache.commons.lang3.SerializationException: ClassNotFoundException while reading cloned object data
- Postfix context signal: org.apache.commons.lang3.SerializationUtilsTest::testPrimitiveTypeClassSerialization: org.apache.commons.lang3.SerializationException: ClassNotFoundException while reading cloned object data

### Lang-14
- Type shift: Incorrect API usage (contract violation) -> Incorrect API usage / Contract violation.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect API usage (contract violation)' vs 'Incorrect API usage / Contract violation')
- Prefix reasoning summary: The StringUtils.equals(CharSequence, CharSequence) method incorrectly relies on the CharSequence.equals(Object) method to determine equality. According to the Java documentation, the CharSequence interface does not define the contract for equals(), meaning that two different implementations of CharSequence representing the same character sequence may return false when compared using equals(). The failing test demonstrates this by comparing a String to a StringBuilder, which fails because StringBuilder does not override Object.equals() to perform content-based equality checks.
- Postfix reasoning summary: The bug stems from the fact that the CharSequence interface does not guarantee that the equals() method will return true for objects representing the same sequence of characters, as it does not refine the general contract of Object.equals(). The original implementation of StringUtils.equals(CharSequence, CharSequence) relied on calling cs1.equals(cs2), which fails when comparing different implementations of CharSequence (e.g., a String and a StringBuilder). The fix correctly replaces the reliance on the unreliable equals() method with a character-by-character comparison using CharSequenceUtils.regionMatches().
- Prefix context signal: org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testEquals: junit.framework.AssertionFailedError
- Postfix context signal: org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testEquals: junit.framework.AssertionFailedError

### Lang-15
- Type shift: Incorrect Type Variable Resolution -> incorrect type variable resolution logic.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Type Variable Resolution' vs 'incorrect type variable resolution logic')
- Prefix reasoning summary: The issue lies in the TypeUtils.getTypeArguments implementation, which fails to correctly resolve type arguments when a class implements an interface with specific type parameters while also defining its own type variables. The logic incorrectly ignores the class hierarchy when it encounters its own type variables, leading to an empty map of type arguments instead of the expected mappings. This is confirmed by the failing test case where Other<T> implements This<String, T>, and the utility fails to identify the mapping for the type parameters of This.
- Postfix reasoning summary: The defect stems from an overly restrictive condition in the TypeUtils.getTypeArguments method that prematurely terminates the traversal of the class hierarchy when encountering classes with type parameters. By checking 'cls.getTypeParameters().length > 0' as a termination condition, the algorithm failed to correctly map type arguments for classes that implement interfaces with specific type assignments (e.g., 'Other<T> implements This<String, T>'). The fix removes this incorrect condition and introduces 'unrollVariableAssignments' to properly resolve type variables across the hierarchy, ensuring that the mapping between the subclass and the target interface is correctly captured.
- Prefix context signal: org.apache.commons.lang3.reflect.TypeUtilsTest::testGetTypeArguments: junit.framework.AssertionFailedError: expected:<2> but was:<0>
- Postfix context signal: org.apache.commons.lang3.reflect.TypeUtilsTest::testGetTypeArguments: junit.framework.AssertionFailedError: expected:<2> but was:<0>

### Lang-19
- Type shift: IndexOutOfBoundsException due to missing bounds check -> IndexOutOfBoundsException due to improper boundary checking.
- Comparison detail: Family match only: both 'None' but types differ ('IndexOutOfBoundsException due to missing bounds check' vs 'IndexOutOfBoundsException due to improper boundary checking')
- Prefix reasoning summary: The NumericEntityUnescaper class attempts to parse numeric entities from a string. When it encounters an entity that does not end with a semicolon, the while loop at line 54 continues to increment the 'end' index until it reaches the end of the string or finds a semicolon. Because there is no check to ensure 'end' remains within the bounds of the input string, the code attempts to access characters beyond the string's length, resulting in a StringIndexOutOfBoundsException. This occurs both when accessing the character at 'start' (line 44) and when iterating through the string to find the end of the entity (line 54).
- Postfix reasoning summary: The code attempted to access characters in a CharSequence using index-based lookups without verifying if the index was within the bounds of the string. Specifically, the loop condition 'input.charAt(end) != ';'' assumed that a semicolon would always be present before the end of the string, leading to an out-of-bounds access when the input string ended prematurely (e.g., '&#03'). The fix introduced explicit boundary checks (end < seqEnd) and replaced the unsafe character lookup with a validation loop that checks for valid numeric/hexadecimal characters, preventing the code from reading past the end of the input.
- Prefix context signal: org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testUnfinishedEntity: java.lang.StringIndexOutOfBoundsException: String index out of range: 19
- Postfix context signal: org.apache.commons.lang3.text.translate.NumericEntityUnescaperTest::testUnfinishedEntity: java.lang.StringIndexOutOfBoundsException: String index out of range: 19

### Lang-1
- Type shift: Integer overflow due to improper type selection -> Integer overflow due to incorrect numeric type selection.
- Comparison detail: Family match only: both 'None' but types differ ('Integer overflow due to improper type selection' vs 'Integer overflow due to incorrect numeric type selection')
- Prefix reasoning summary: The code in NumberUtils.createNumber() incorrectly assumes that any hexadecimal number with 8 or fewer digits must be an Integer. When a hex string like '0x80000000' is passed, it is treated as an Integer. However, '0x80000000' represents 2147483648, which exceeds the maximum value of a signed 32-bit integer (2147483647). Because Integer.decode() is used, it throws a NumberFormatException when the value is out of the range of a signed integer, even though it fits perfectly within a Long.
- Postfix reasoning summary: The code incorrectly assumed that any hexadecimal string with 8 or fewer digits could be safely parsed as a signed 32-bit Integer. In Java, the hex value 0x80000000 represents a value that exceeds the maximum positive range of a signed 32-bit integer (Integer.MAX_VALUE is 0x7FFFFFFF). When the code attempted to parse such values using Integer.decode(), it triggered a NumberFormatException. The fix introduces logic to correctly identify when a hex string requires a larger container (Long or BigInteger) by checking the number of significant digits and the value of the leading digit, while also accounting for leading zeros.
- Prefix context signal: org.apache.commons.lang3.math.NumberUtilsTest::TestLang747: java.lang.NumberFormatException: For input string: "80000000"
- Postfix context signal: org.apache.commons.lang3.math.NumberUtilsTest::TestLang747: java.lang.NumberFormatException: For input string: "80000000"

### Lang-21
- Type shift: Incorrect Field Comparison -> incorrect field usage in date comparison.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect Field Comparison' vs 'incorrect field usage in date comparison')
- Prefix reasoning summary: The method DateUtils.isSameLocalTime is intended to compare whether two Calendar objects represent the same local time. The bug report and the failing test indicate that the implementation incorrectly uses Calendar.HOUR (which is 12-hour format) instead of Calendar.HOUR_OF_DAY (which is 24-hour format). This causes the method to return true for times that are 12 hours apart (e.g., 4 AM and 4 PM), leading to the assertion failure in the test case.
- Postfix reasoning summary: The method DateUtils.isSameLocalTime was intended to compare two Calendar objects for equality in local time. However, it used the Calendar.HOUR field, which represents the 12-hour clock (0-11), instead of the Calendar.HOUR_OF_DAY field, which represents the 24-hour clock (0-23). This caused the method to incorrectly return true for times that were 12 hours apart (e.g., 4:00 AM and 4:00 PM). The fix correctly updates the field to HOUR_OF_DAY to ensure accurate 24-hour time comparison.
- Prefix context signal: org.apache.commons.lang3.time.DateUtilsTest::testIsSameLocalTime_Cal: junit.framework.AssertionFailedError: LANG-677
- Postfix context signal: org.apache.commons.lang3.time.DateUtilsTest::testIsSameLocalTime_Cal: junit.framework.AssertionFailedError: LANG-677

### Lang-27
- Type shift: IndexOutOfBoundsException due to improper string slicing -> Improper Input Validation.
- Comparison detail: Family match only: both 'None' but types differ ('IndexOutOfBoundsException due to improper string slicing' vs 'Improper Input Validation')
- Prefix reasoning summary: The code in NumberUtils.createNumber attempts to perform a substring operation using an index (expPos) that is calculated based on the presence of an exponent character. When a string like '1eE' is provided, the logic fails to validate the bounds of the string before calling substring, leading to a StringIndexOutOfBoundsException. The code assumes that if an exponent character exists, the substring operation will be valid, but it does not account for cases where the index might be invalid or the string structure is malformed.
- Postfix reasoning summary: The code fails to validate the position of the exponent character ('e' or 'E') relative to the string length before performing substring operations. When an invalid string like '1eE' is provided, the logic incorrectly assumes the exponent position is valid, leading to a StringIndexOutOfBoundsException when attempting to extract substrings. The fix introduces explicit checks to ensure the exponent position is within the bounds of the string, throwing a NumberFormatException instead of crashing.
- Prefix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: java.lang.StringIndexOutOfBoundsException: begin 0, end 4, length 3
- Postfix context signal: org.apache.commons.lang3.math.NumberUtilsTest::testCreateNumber: java.lang.StringIndexOutOfBoundsException: begin 0, end 4, length 3

### Lang-31
- Type shift: Unicode supplementary character handling error -> Unicode Supplementary Character Handling Error.
- Comparison detail: Family match only: both 'None' but types differ ('Unicode supplementary character handling error' vs 'Unicode Supplementary Character Handling Error')
- Prefix reasoning summary: The StringUtils.containsAny method fails to correctly handle Unicode supplementary characters (characters outside the Basic Multilingual Plane, represented as surrogate pairs in Java). The evidence shows that while standard JRE methods like String.indexOf correctly identify that two different supplementary characters do not match, the custom implementation of containsAny incorrectly returns true. This indicates that the logic within containsAny likely iterates over or compares characters as individual 16-bit char units rather than treating surrogate pairs as single code points, leading to false positive matches when partial surrogate components overlap.
- Postfix reasoning summary: The bug occurs because the `StringUtils.containsAny` method treats Unicode supplementary characters (which are represented as surrogate pairs in Java) as individual 16-bit characters. When comparing strings, the algorithm incorrectly matches a high surrogate character in isolation, leading to false positives. The fix introduces logic to check if a matched character is a high surrogate and, if so, verifies that the subsequent low surrogate also matches, ensuring the entire supplementary character is treated as a single unit.
- Prefix context signal: org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars: junit.framework.AssertionFailedError: expected:<false> but was:<true>
- Postfix context signal: org.apache.commons.lang3.StringUtilsEqualsIndexOfTest::testContainsAnyCharArrayWithSupplementaryChars: junit.framework.AssertionFailedError: expected:<false> but was:<true>

### Lang-35
- Type shift: Type safety violation / Incorrect return type -> Missing Input Validation.
- Comparison detail: Family match only: both 'None' but types differ ('Type safety violation / Incorrect return type' vs 'Missing Input Validation')
- Prefix reasoning summary: The ArrayUtils.add method is designed to return an array of the same type as the input array. When both the input array and the element to be added are null, the method cannot infer the component type of the array to be created. Consequently, it defaults to creating an Object[] array. When the caller expects a specific type (e.g., String[]), the JVM throws a ClassCastException because an Object[] cannot be cast to a String[]. The bug report correctly identifies that this scenario should be handled by throwing an IllegalArgumentException rather than returning an incompatible array type.
- Postfix reasoning summary: The bug occurs because the ArrayUtils.add methods fail to handle the case where both the input array and the element to be added are null. In this scenario, the method cannot infer the correct component type for the resulting array, defaulting to Object.class. This leads to a ClassCastException when the caller expects a specific array type (e.g., String[]). The fix introduces an explicit check to throw an IllegalArgumentException when both arguments are null, preventing the creation of an incorrectly typed array.
- Prefix context signal: org.apache.commons.lang3.ArrayUtilsAddTest::testLANG571: java.lang.ClassCastException: class [Ljava.lang.Object; cannot be cast to class [Ljava.lang.String; ([Ljava.lang.Object; and [Ljava.lang.String; are in module java.base of loader 'bootstrap')
- Postfix context signal: org.apache.commons.lang3.ArrayUtilsAddTest::testLANG571: java.lang.ClassCastException: class [Ljava.lang.Object; cannot be cast to class [Ljava.lang.String; ([Ljava.lang.Object; and [Ljava.lang.String; are in module java.base of loader 'bootstrap')

### Lang-41
- Type shift: incorrect array class name handling -> improper handling of array class name encoding.
- Comparison detail: Family match only: both 'None' but types differ ('incorrect array class name handling' vs 'improper handling of array class name encoding')
- Prefix reasoning summary: The ClassUtils utility methods for retrieving class names (getShortClassName and getPackageName) fail to correctly handle array types. The evidence shows that when processing array classes, the implementation incorrectly includes internal JVM representation characters (like the semicolon suffix or the '[L' prefix) in the returned string, rather than stripping them to provide a human-readable class name as expected by the test cases.
- Postfix reasoning summary: The bug occurs because the ClassUtils methods were treating array class names (which follow the JVM internal format like '[Ljava.lang.String;') as standard class names. The code failed to strip the JVM-specific array prefixes ('[') and object type markers ('L' and ';') before attempting to extract the package or short class name. This resulted in the inclusion of these internal characters in the output, causing the observed test failures where 'String[]' was returned as 'String;' and package names were incorrectly prefixed with '[L'.
- Prefix context signal: org.apache.commons.lang.ClassUtilsTest::test_getShortClassName_Class: junit.framework.ComparisonFailure: expected:<String[[]]> but was:<String[;]>
- Postfix context signal: org.apache.commons.lang.ClassUtilsTest::test_getShortClassName_Class: junit.framework.ComparisonFailure: expected:<String[[]]> but was:<String[;]>

### Lang-44
- Type shift: Unchecked String Index Access -> Unchecked input length leading to index out of bounds.
- Comparison detail: Family match only: both 'None' but types differ ('Unchecked String Index Access' vs 'Unchecked input length leading to index out of bounds')
- Prefix reasoning summary: The code attempts to access the character at index 0 of the 'numeric' string using 'numeric.charAt(0)' without verifying that the string is not empty. When 'NumberUtils.createNumber' is called with a single-character input like 'l' or 'L', the 'numeric' variable becomes an empty string (via 'val.substring(0, val.length() - 1)'), causing 'charAt(0)' to throw a 'StringIndexOutOfBoundsException'.
- Postfix reasoning summary: The code attempts to access the first character of a string (numeric.charAt(0)) without verifying that the string has a non-zero length. When the input string is just a single character like 'L' or 'l', the logic that strips the last character results in an empty string. Calling charAt(0) on an empty string triggers a StringIndexOutOfBoundsException. The fix adds a guard clause to check if the string length is 1 and if the character is not a digit, throwing a NumberFormatException instead of proceeding to invalid operations.
- Prefix context signal: org.apache.commons.lang.NumberUtilsTest::testLang457: java.lang.StringIndexOutOfBoundsException: String index out of range: 0
- Postfix context signal: org.apache.commons.lang.NumberUtilsTest::testLang457: java.lang.StringIndexOutOfBoundsException: String index out of range: 0

### Lang-46
- Type shift: Incorrect character escaping logic -> Incorrect logic implementation (unnecessary character escaping).
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect character escaping logic' vs 'Incorrect logic implementation (unnecessary character escaping)')
- Prefix reasoning summary: The bug report and the failing test case indicate that the StringEscapeUtils.escapeJava method is incorrectly escaping the forward slash ('/') character. In Java, the forward slash is not a character that requires escaping in string literals. The implementation of escapeJava is performing an unnecessary transformation, which violates the expected behavior of producing a valid Java string representation without extraneous escape sequences.
- Postfix reasoning summary: The code was incorrectly escaping the forward slash ('/') character in the escapeJava method. According to Java string literal rules, the forward slash does not require escaping. The fix involved introducing a boolean flag 'escapeForwardSlash' to the internal helper method 'escapeJavaStyleString' to conditionally control whether the forward slash is escaped, ensuring it is only escaped for JavaScript (where it is often desired to avoid </script> tags) but not for Java.
- Prefix context signal: org.apache.commons.lang.StringEscapeUtilsTest::testEscapeJavaWithSlash: junit.framework.ComparisonFailure: expected:<...tring with a slash ([]/) in it> but was:<...tring with a slash ([\]/) in it>
- Postfix context signal: org.apache.commons.lang.StringEscapeUtilsTest::testEscapeJavaWithSlash: junit.framework.ComparisonFailure: expected:<...tring with a slash ([]/) in it> but was:<...tring with a slash ([\]/) in it>

### Lang-4
- Type shift: Inappropriate use of CharSequence as Map key -> Inappropriate use of mutable/non-standard CharSequence as Map key.
- Comparison detail: Family match only: both 'None' but types differ ('Inappropriate use of CharSequence as Map key' vs 'Inappropriate use of mutable/non-standard CharSequence as Map key')
- Prefix reasoning summary: The LookupTranslator uses a HashMap with CharSequence keys. According to the CharSequence contract, equality and hash codes are not guaranteed to be consistent across different implementations (e.g., String vs. StringBuffer vs. CharBuffer). When a non-String implementation like StringBuffer is passed to the translate method, the lookup fails because the map cannot find the key, even if the content is identical to a String key already in the map. This results in the translator failing to perform the expected substitution, leading to zero codepoints being consumed.
- Postfix reasoning summary: The LookupTranslator used a HashMap with CharSequence keys. Because CharSequence implementations (like StringBuffer or CharBuffer) do not guarantee consistent equals() and hashCode() behavior, and specifically because CharBuffer explicitly states it is not equal to other types, lookups in the map failed when the input type did not match the key type stored in the map. The fix involved converting all keys to String, which provides a stable and consistent contract for equality and hashing, ensuring that any CharSequence representation of the same text correctly matches the map entry.
- Prefix context signal: org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>
- Postfix context signal: org.apache.commons.lang3.text.translate.LookupTranslatorTest::testLang882: junit.framework.AssertionFailedError: Incorrect codepoint consumption expected:<3> but was:<0>

### Lang-51
- Type shift: Missing break statement in switch-case -> Missing break or return statement in switch-case.
- Comparison detail: Family match only: both 'None' but types differ ('Missing break statement in switch-case' vs 'Missing break or return statement in switch-case')
- Prefix reasoning summary: The method BooleanUtils.toBoolean() processes strings of different lengths using a switch statement. When the input string has a length of 3 (e.g., 'tru'), the code enters the case 3 block. Because there is no 'break' statement at the end of the case 3 block, the execution flow falls through into the case 4 block. The case 4 block then attempts to access the character at index 3 (str.charAt(3)), which is out of bounds for a string of length 3, resulting in a StringIndexOutOfBoundsException.
- Postfix reasoning summary: The code contains a switch-case block where 'case 3' lacks a termination statement (like 'return false' or 'break'). Consequently, when the input string has a length of 3, the execution flow falls through into 'case 4'. Inside 'case 4', the code attempts to access characters at index 3 (e.g., str.charAt(3)), which triggers a StringIndexOutOfBoundsException for strings of length 3. The fix adds a 'return false' statement at the end of 'case 3' to prevent this fall-through behavior.
- Prefix context signal: org.apache.commons.lang.BooleanUtilsTest::test_toBoolean_String: java.lang.StringIndexOutOfBoundsException: String index out of range: 3
- Postfix context signal: org.apache.commons.lang.BooleanUtilsTest::test_toBoolean_String: java.lang.StringIndexOutOfBoundsException: String index out of range: 3

### Lang-56
- Type shift: Missing Serialization Implementation -> Missing Serialization Support.
- Comparison detail: Family match only: both 'None' but types differ ('Missing Serialization Implementation' vs 'Missing Serialization Support')
- Prefix reasoning summary: The test case fails with a NotSerializableException when attempting to serialize a FastDateFormat object. The stack trace indicates that the internal class PaddedNumberField, which is part of the FastDateFormat object's state (specifically within the mRules collection), does not implement the Serializable interface. As a result, the Java serialization mechanism cannot process the object graph, leading to the reported exception.
- Postfix reasoning summary: The class FastDateFormat contains non-serializable fields (mRules and mMaxLengthEstimate) that are not marked as transient. When an instance of FastDateFormat is serialized, the Java serialization mechanism attempts to serialize these fields, leading to a NotSerializableException because the underlying Rule objects do not implement Serializable. The fix involves marking these fields as transient and implementing a readObject method to re-initialize them upon deserialization, ensuring the object state is correctly restored without requiring the non-serializable fields to be part of the serialized stream.
- Prefix context signal: org.apache.commons.lang.time.FastDateFormatTest::testLang303: org.apache.commons.lang.SerializationException: java.io.NotSerializableException: org.apache.commons.lang.time.FastDateFormat$PaddedNumberField
- Postfix context signal: org.apache.commons.lang.time.FastDateFormatTest::testLang303: org.apache.commons.lang.SerializationException: java.io.NotSerializableException: org.apache.commons.lang.time.FastDateFormat$PaddedNumberField

### Lang-57
- Type shift: Uninitialized static field -> Uninitialized static field access.
- Comparison detail: Family match only: both 'None' but types differ ('Uninitialized static field' vs 'Uninitialized static field access')
- Prefix reasoning summary: The class LocaleUtils uses a static field 'cAvailableLocaleSet' which is intended to store a set of available locales. The stack trace indicates a NullPointerException at line 223, where this field is accessed. The bug report confirms that this field is not initialized in the class, and it only gets populated when the 'availableLocaleSet()' method is called. If 'isAvailableLocale()' is invoked before 'availableLocaleSet()', the uninitialized field causes a NullPointerException.
- Postfix reasoning summary: The code attempted to access a static field 'cAvailableLocaleSet' directly within the 'isAvailableLocale' method. This field was intended to be lazily initialized by the 'availableLocaleSet()' method. If 'isAvailableLocale' was called before 'availableLocaleSet()', the field remained null, resulting in a NullPointerException. The fix replaces the direct field access with a call to the initialization method, ensuring the set is properly populated before use.
- Prefix context signal: org.apache.commons.lang.LocaleUtilsTest::testAvailableLocaleSet: java.lang.NullPointerException
- Postfix context signal: org.apache.commons.lang.LocaleUtilsTest::testAvailableLocaleSet: java.lang.NullPointerException

### Lang-59
- Type shift: incorrect parameter usage in string manipulation -> Incorrect parameter usage in array copy operation.
- Comparison detail: Family match only: both 'None' but types differ ('incorrect parameter usage in string manipulation' vs 'Incorrect parameter usage in array copy operation')
- Prefix reasoning summary: The method appendFixedWidthPadRight attempts to copy characters from a string into a buffer. When the string length exceeds the specified width, the code incorrectly uses the full length of the string (strLen) as the end index for the getChars method, rather than the specified width. This causes an attempt to copy more characters than the buffer has been allocated for or than the logic intends to append, leading to a StringIndexOutOfBoundsException.
- Postfix reasoning summary: The code intended to copy a fixed-width portion of a string into a buffer. When the string length exceeded the specified width, the code incorrectly used the full string length as the end index for the 'getChars' method instead of the specified width. This caused an attempt to copy more characters than the allocated buffer space allowed, leading to an ArrayIndexOutOfBoundsException.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderAppendInsertTest::testLang299: java.lang.StringIndexOutOfBoundsException: offset 0, count 3, length 1
- Postfix context signal: org.apache.commons.lang.text.StrBuilderAppendInsertTest::testLang299: java.lang.StringIndexOutOfBoundsException: offset 0, count 3, length 1

### Lang-5
- Type shift: Input validation logic error -> Incomplete Input Validation Logic.
- Comparison detail: Family match only: both 'None' but types differ ('Input validation logic error' vs 'Incomplete Input Validation Logic')
- Prefix reasoning summary: The LocaleUtils.toLocale method is designed to parse locale strings, but it contains overly restrictive validation logic that assumes all valid locale strings must start with two lowercase letters representing the language. The code explicitly checks if the first two characters are lowercase and throws an IllegalArgumentException if they are not. This prevents the method from correctly parsing valid locale strings that start with an underscore (indicating a missing language component), which is a standard format according to the Java Locale documentation.
- Postfix reasoning summary: The LocaleUtils.toLocale method was designed to parse locale strings, but it strictly enforced that the first two characters must be lowercase letters (representing a language code). This implementation failed to account for valid locale strings that start with an underscore, which occur when the language component is missing but a country or variant is present (e.g., '_GB'). The fix introduces a specific branch to handle strings starting with an underscore, correctly validating the subsequent country and variant components, thereby aligning the method's behavior with the standard Locale.toString() output format.
- Prefix context signal: org.apache.commons.lang3.LocaleUtilsTest::testLang865: java.lang.IllegalArgumentException: Invalid locale format: _GB
- Postfix context signal: org.apache.commons.lang3.LocaleUtilsTest::testLang865: java.lang.IllegalArgumentException: Invalid locale format: _GB

### Lang-60
- Type shift: Off-by-one boundary condition error -> Off-by-one boundary error.
- Comparison detail: Family match only: both 'None' but types differ ('Off-by-one boundary condition error' vs 'Off-by-one boundary error')
- Prefix reasoning summary: The bug report and test failure indicate that the StrBuilder class incorrectly references the internal buffer's length (thisBuf.length) instead of the actual logical size of the string (size) when performing search operations like contains() or indexOf(). This causes the methods to scan beyond the valid data stored in the buffer, leading to incorrect results when the buffer capacity exceeds the current string length.
- Postfix reasoning summary: The StrBuilder class maintains an internal character buffer that may be larger than the actual string content stored within it. The methods 'contains(char)' and 'indexOf(char, int)' were incorrectly iterating over the entire length of the underlying buffer ('thisBuf.length') instead of the current logical size of the string ('this.size'). This caused the methods to scan stale or uninitialized data beyond the valid string content, leading to incorrect results when the character being searched for existed in the unused portion of the buffer.
- Prefix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string
- Postfix context signal: org.apache.commons.lang.text.StrBuilderTest::testLang295: junit.framework.AssertionFailedError: The contains(char) method is looking beyond the end of the string

### Lang-65
- Type shift: Timezone-unaware calendar manipulation -> side-effect-induced state corruption.
- Comparison detail: Family match only: both 'None' but types differ ('Timezone-unaware calendar manipulation' vs 'side-effect-induced state corruption')
- Prefix reasoning summary: The bug occurs because the DateUtils.truncate method performs calendar field modifications that trigger a recalculation of the underlying time in milliseconds. When this happens during a Daylight Saving Time (DST) transition (like the transition from MDT to MST), the Calendar object may incorrectly shift the time by an hour because it re-evaluates the offset based on the modified fields without properly preserving the original timezone context or absolute time.
- Postfix reasoning summary: The bug occurs because the Calendar.set() method in Java has side effects, specifically resetting internal fields like DST_OFFSET even when the value being set is identical to the current value. In the context of DateUtils.truncate, this causes the calendar to shift time zones (e.g., from MDT to MST) during truncation operations, leading to incorrect results. The fix avoids these problematic Calendar.set calls by performing manual arithmetic on the underlying time (milliseconds) and only updating the Calendar object when a change is actually required, thereby preventing the unintended side effects of the Calendar API.
- Prefix context signal: org.apache.commons.lang.time.DateUtilsTest::testTruncateLang59: junit.framework.AssertionFailedError: Truncate Calendar.SECOND expected:<Sun Oct 31 01:02:03 MDT 2004> but was:<Sun Oct 31 01:02:03 MST 2004>
- Postfix context signal: org.apache.commons.lang.time.DateUtilsTest::testTruncateLang59: junit.framework.AssertionFailedError: Truncate Calendar.SECOND expected:<Sun Oct 31 01:02:03 MDT 2004> but was:<Sun Oct 31 01:02:03 MST 2004>

### Lang-6
- Type shift: Off-by-one error in surrogate pair handling -> Off-by-one index calculation error.
- Comparison detail: Family match only: both 'None' but types differ ('Off-by-one error in surrogate pair handling' vs 'Off-by-one index calculation error')
- Prefix reasoning summary: The code in CharSequenceTranslator.java attempts to iterate through a CharSequence by manually advancing the position index. When a surrogate pair is encountered, the code correctly identifies the codepoint but then incorrectly increments the position index by the length of the character count of the codepoint. Because the loop logic already handles the character advancement for the surrogate pair via the 'consumed' variable or the default character writing logic, the additional increment at line 95 causes the index to skip past the end of the string, resulting in a StringIndexOutOfBoundsException when the loop condition is checked again.
- Postfix reasoning summary: The code iterates through a CharSequence to translate characters. When a translator does not consume a character (returns 0), the loop attempts to advance the position pointer. The original code used 'pos' as the index for 'Character.codePointAt(input, pos)' inside a loop that was intended to iterate based on the number of consumed characters. However, the logic was flawed because it was using the global 'pos' variable instead of the local loop index 'pt' to determine the character count, leading to an incorrect index calculation that eventually exceeded the string length, causing a StringIndexOutOfBoundsException.
- Prefix context signal: org.apache.commons.lang3.StringUtilsTest::testEscapeSurrogatePairs: java.lang.StringIndexOutOfBoundsException: index 2,length 2
- Postfix context signal: org.apache.commons.lang3.StringUtilsTest::testEscapeSurrogatePairs: java.lang.StringIndexOutOfBoundsException: index 2,length 2

### Lang-8
- Type shift: Incorrect TimeZone context usage in formatting -> Incorrect TimeZone Context Usage.
- Comparison detail: Family match only: both 'None' but types differ ('Incorrect TimeZone context usage in formatting' vs 'Incorrect TimeZone Context Usage')
- Prefix reasoning summary: The bug occurs because the FastDateFormat formatter, when processing the 'z' (timezone name) pattern, incorrectly uses the formatter's internal default timezone instead of the timezone associated with the Calendar object being formatted. As described in the bug report and confirmed by the failing tests, the formatter correctly adjusts the time for the Calendar's timezone but fails to retrieve the corresponding timezone display name, defaulting to the system's local timezone instead. This is a regression where the logic for retrieving the timezone name was decoupled from the dynamic Calendar context.
- Postfix reasoning summary: The bug occurred because the TimeZoneNameRule class was using a cached TimeZone instance (associated with the FastDateFormat object) instead of dynamically retrieving the TimeZone from the Calendar object provided during the formatting process. This caused the 'z' pattern to always output the timezone name of the system default or the formatter's initial configuration, ignoring the specific timezone set on the Calendar instance being formatted. The fix involved modifying the appendTo method to extract the TimeZone directly from the provided Calendar object, ensuring the output correctly reflects the Calendar's timezone.
- Prefix context signal: org.apache.commons.lang3.time.FastDateFormat_PrinterTest::testCalendarTimezoneRespected: junit.framework.AssertionFailedError: expected:<7:57PM [IC]T> but was:<7:57PM [PS]T>
- Postfix context signal: org.apache.commons.lang3.time.FastDateFormat_PrinterTest::testCalendarTimezoneRespected: junit.framework.AssertionFailedError: expected:<8:00PM [IC]T> but was:<8:00PM [PS]T>

## Type Transitions

### Type Changed (Prefix → Postfix)

- Unicode supplementary character handling error -> Unicode Supplementary Character Handling Error: 2
  - Bugs: Lang-30 (no alt overlap), Lang-31 (no alt overlap)
- Incorrect Regex Pattern Generation -> Incorrect Regex Generation for Whitespace: 1
  - Bugs: Lang-10 (no alt overlap)
- Inadequate Exception Handling -> Insufficient Input Validation: 1
  - Bugs: Lang-11 (no alt overlap)
- Incorrect Array Index Calculation -> Input Validation Error: 1
  - Bugs: Lang-12 (no alt overlap)
- Incomplete ClassLoader resolution logic -> Incomplete Class Resolution Logic: 1
  - Bugs: Lang-13 (no alt overlap)
- Incorrect API usage (contract violation) -> Incorrect API usage / Contract violation: 1
  - Bugs: Lang-14 (no alt overlap)
- Incorrect Type Variable Resolution -> incorrect type variable resolution logic: 1
  - Bugs: Lang-15 (no alt overlap)
- IndexOutOfBoundsException due to missing bounds check -> IndexOutOfBoundsException due to improper boundary checking: 1
  - Bugs: Lang-19 (no alt overlap)
- Integer overflow due to improper type selection -> Integer overflow due to incorrect numeric type selection: 1
  - Bugs: Lang-1 (no alt overlap)
- NullPointerException due to unsafe toString() invocation -> NullPointerException due to unsafe object property access: 1
  - Bugs: Lang-20 (no alt overlap)
- Incorrect Field Comparison -> incorrect field usage in date comparison: 1
  - Bugs: Lang-21 (no alt overlap)
- integer overflow handling error -> Integer overflow in GCD calculation: 1
  - Bugs: Lang-22 (no alt overlap)
- Inconsistent hashCode implementation -> Missing Override of equals() and hashCode(): 1
  - Bugs: Lang-23 (no alt overlap)
- Locale-dependent configuration mismatch -> Locale-dependent configuration omission: 1
  - Bugs: Lang-26 (no alt overlap)
- IndexOutOfBoundsException due to improper string slicing -> Improper Input Validation: 1
  - Bugs: Lang-27 (no alt overlap)
- Unicode supplementary character handling error -> Incorrect character encoding handling: 1
  - Bugs: Lang-28 (no alt overlap)
- Type Mismatch / Incorrect Return Type -> Incorrect Return Type Declaration: 1
  - Bugs: Lang-29 (no alt overlap)
- Resource Leak (ThreadLocal) -> Resource Leak / Improper ThreadLocal Lifecycle Management: 1
  - Bugs: Lang-32 (no alt overlap)
- Type safety violation / Incorrect return type -> Missing Input Validation: 1
  - Bugs: Lang-35 (no alt overlap)
- Type safety violation in array concatenation -> Inadequate Exception Handling: 1
  - Bugs: Lang-37 (no alt overlap)
- Calendar state inconsistency -> Lazy initialization failure in Calendar API: 1
  - Bugs: Lang-38 (no alt overlap)
- Incorrect Type Inference Logic -> Incorrect Type Inference / Precision Loss: 1
  - Bugs: Lang-3 (no alt overlap)
- Locale-sensitive case conversion -> Locale-sensitive case conversion error: 1
  - Bugs: Lang-40 (no alt overlap)
- incorrect array class name handling -> improper handling of array class name encoding: 1
  - Bugs: Lang-41 (no alt overlap)
- Unchecked String Index Access -> Unchecked input length leading to index out of bounds: 1
  - Bugs: Lang-44 (no alt overlap)
- Incorrect character escaping logic -> Incorrect logic implementation (unnecessary character escaping): 1
  - Bugs: Lang-46 (no alt overlap)
- Incorrect Logic in Fraction Reduction -> Incorrect logic for handling zero-numerator fractions: 1
  - Bugs: Lang-49 (no alt overlap)
- Inappropriate use of CharSequence as Map key -> Inappropriate use of mutable/non-standard CharSequence as Map key: 1
  - Bugs: Lang-4 (no alt overlap)
- caching inconsistency due to stale locale dependency -> caching inconsistency due to improper key generation: 1
  - Bugs: Lang-50 (no alt overlap)
- Missing break statement in switch-case -> Missing break or return statement in switch-case: 1
  - Bugs: Lang-51 (no alt overlap)
- incorrect rounding logic -> logic error in rounding algorithm: 1
  - Bugs: Lang-53 (no alt overlap)
- Missing Serialization Implementation -> Missing Serialization Support: 1
  - Bugs: Lang-56 (no alt overlap)
- Uninitialized static field -> Uninitialized static field access: 1
  - Bugs: Lang-57 (no alt overlap)
- incorrect parameter usage in string manipulation -> Incorrect parameter usage in array copy operation: 1
  - Bugs: Lang-59 (no alt overlap)
- Input validation logic error -> Incomplete Input Validation Logic: 1
  - Bugs: Lang-5 (no alt overlap)
- Off-by-one boundary condition error -> Off-by-one boundary error: 1
  - Bugs: Lang-60 (no alt overlap)
- Off-by-one error in array manipulation -> incorrect boundary condition in search algorithm: 1
  - Bugs: Lang-61 (no alt overlap)
- Integer overflow handling error -> Integer overflow / Unchecked range validation: 1
  - Bugs: Lang-62 (no alt overlap)
- Incorrect Date Arithmetic Logic -> Incorrect Calendar Arithmetic Logic: 1
  - Bugs: Lang-63 (no alt overlap)
- Inadequate Type Safety in Comparison Logic -> Type safety violation in comparison logic: 1
  - Bugs: Lang-64 (no alt overlap)
- Timezone-unaware calendar manipulation -> side-effect-induced state corruption: 1
  - Bugs: Lang-65 (no alt overlap)
- Off-by-one error in surrogate pair handling -> Off-by-one index calculation error: 1
  - Bugs: Lang-6 (no alt overlap)
- Inconsistent Exception Handling -> Inconsistent Error Handling: 1
  - Bugs: Lang-7 (no alt overlap)
- Incorrect TimeZone context usage in formatting -> Incorrect TimeZone Context Usage: 1
  - Bugs: Lang-8 (no alt overlap)
- Incorrect Input Validation / Parsing Logic -> Improper Input Validation: 1
  - Bugs: Lang-9 (no alt overlap)

### Type Unchanged

- Null Pointer Dereference -> Null Pointer Dereference: 3
  - Bugs: Lang-33, Lang-39, Lang-47
- Input validation logic error -> Input validation logic error: 2
  - Bugs: Lang-36, Lang-54
- Incomplete Input Validation -> Incomplete Input Validation: 1
  - Bugs: Lang-16
- Incorrect loop iteration logic for Unicode supplementary characters -> Incorrect loop iteration logic for Unicode supplementary characters: 1
  - Bugs: Lang-17
- incorrect validation logic -> incorrect validation logic: 1
  - Bugs: Lang-24
- Resource Leak (ThreadLocal) -> Resource Leak (ThreadLocal): 1
  - Bugs: Lang-34
- Unicode surrogate pair handling error -> Unicode surrogate pair handling error: 1
  - Bugs: Lang-42
- infinite loop -> infinite loop: 1
  - Bugs: Lang-43
- Input validation error -> Input validation error: 1
  - Bugs: Lang-45
- Incomplete character escaping -> Incomplete character escaping: 1
  - Bugs: Lang-52
- Incorrect State Transition Logic -> Incorrect State Transition Logic: 1
  - Bugs: Lang-55
- incorrect input validation logic -> incorrect input validation logic: 1
  - Bugs: Lang-58
