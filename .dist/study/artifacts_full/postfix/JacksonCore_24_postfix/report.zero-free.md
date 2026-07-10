# Defects4J ODC Classification Report: JacksonCore-24

- Version: `24b`
- Work directory: `C:\d4j_work\postfix\JacksonCore_24b`
- Generated: `2026-07-10T18:53:51+00:00`

## Failure Summary
- `com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToLongFailing`: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)
- `com.fasterxml.jackson.core.json.async.AsyncNumberCoercionTest::testToIntFailing`: com.fasterxml.jackson.core.JsonParseException: Numeric value (2147483648) out of range of int
- `com.fasterxml.jackson.core.read.NumberCoercionTest::testToLongFailing`: com.fasterxml.jackson.core.JsonParseException: Numeric value (9223372036854775817) out of range of long (-9223372036854775808 - 9223372036854775807)
- `com.fasterxml.jackson.core.read.NumberCoercionTest::testToIntFailing`: com.fasterxml.jackson.core.JsonParseException: Numeric value (2147483648) out of range of int
- `com.fasterxml.jackson.core.read.NumberOverflowTest::testMaliciousLongOverflow`: com.fasterxml.jackson.core.JsonParseException: Numeric value ([Integer with 199999 digits]) out of range of long
- `com.fasterxml.jackson.core.read.NumberOverflowTest::testSimpleLongOverflow`: com.fasterxml.jackson.core.JsonParseException: Numeric value (-9223372036854775809) out of range of long
- `com.fasterxml.jackson.core.read.NumberOverflowTest::testMaliciousIntOverflow`: com.fasterxml.jackson.core.JsonParseException: Numeric value ([Integer with 199999 digits]) out of range of int
- `com.fasterxml.jackson.core.read.NumberParsingTest::testSimpleLong`: com.fasterxml.jackson.core.JsonParseException: Numeric value (12345678907) out of range of int

## Suspicious Frames
- `com.fasterxml.jackson.core.JsonParser._constructError` at `JsonParser.java:1833`
- `com.fasterxml.jackson.core.base.ParserMinimalBase._reportError` at `ParserMinimalBase.java:704`
- `com.fasterxml.jackson.core.base.ParserMinimalBase.reportOverflowLong` at `ParserMinimalBase.java:582`
- `com.fasterxml.jackson.core.base.ParserMinimalBase.reportOverflowLong` at `ParserMinimalBase.java:577`
- `com.fasterxml.jackson.core.base.ParserBase.convertNumberToLong` at `ParserBase.java:921`
- `com.fasterxml.jackson.core.base.ParserBase.getLongValue` at `ParserBase.java:663`
- `com.fasterxml.jackson.core.testsupport.AsyncReaderWrapper.getLongValue` at `AsyncReaderWrapper.java:57`
- `com.fasterxml.jackson.core.base.ParserBase.convertNumberToInt` at `ParserBase.java:887`
- `com.fasterxml.jackson.core.base.ParserBase.getIntValue` at `ParserBase.java:649`
- `com.fasterxml.jackson.core.testsupport.AsyncReaderWrapper.getIntValue` at `AsyncReaderWrapper.java:56`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Inappropriate Exception Handling`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug was identified as a design flaw where numeric overflow errors during coercion were being reported as generic JsonParseExceptions. The fix involved introducing a more specific exception type, InputCoercionException, which provides better metadata (such as the target type and input token type) to the calling application. The code changes updated the error reporting methods in ParserBase and ParserMinimalBase to utilize this new exception type instead of the generic _reportError method, allowing for better error handling and differentiation between parsing errors and type mismatch/coercion errors.
