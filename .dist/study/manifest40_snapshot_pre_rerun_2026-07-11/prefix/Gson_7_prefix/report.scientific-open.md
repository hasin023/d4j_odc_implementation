# Defects4J ODC Classification Report: Gson-7

- Version: `7b`
- Work directory: `C:\d4j_work\prefix\Gson_7b`
- Generated: `2026-07-08T16:55:57+00:00`

## Failure Summary
- `com.google.gson.functional.MapTest::testMapDeserializationWithUnquotedLongKeys`: com.google.gson.JsonSyntaxException: java.lang.IllegalStateException: Expected a long but was STRING at line 1 column 2 path $.
- `com.google.gson.functional.MapTest::testMapDeserializationWithUnquotedIntegerKeys`: com.google.gson.JsonSyntaxException: java.lang.IllegalStateException: Expected an int but was STRING at line 1 column 2 path $.
- `com.google.gson.stream.JsonReaderTest::testPeekingUnquotedStringsPrefixedWithIntegers`: java.lang.IllegalStateException: Expected an int but was STRING at line 1 column 2 path $[0]

## Suspicious Frames
- `com.google.gson.Gson.fromJson` at `Gson.java:892`
- `com.google.gson.Gson.fromJson` at `Gson.java:845`
- `com.google.gson.Gson.fromJson` at `Gson.java:794`
- `com.google.gson.stream.JsonReader.nextLong` at `JsonReader.java:966`
- `com.google.gson.internal.bind.TypeAdapters$11.read` at `TypeAdapters.java:325`
- `com.google.gson.internal.bind.TypeAdapters$11.read` at `TypeAdapters.java:317`
- `com.google.gson.internal.bind.TypeAdapterRuntimeTypeWrapper.read` at `TypeAdapterRuntimeTypeWrapper.java:40`
- `com.google.gson.internal.bind.MapTypeAdapterFactory$Adapter.read` at `MapTypeAdapterFactory.java:186`
- `com.google.gson.internal.bind.MapTypeAdapterFactory$Adapter.read` at `MapTypeAdapterFactory.java:145`
- `com.google.gson.Gson.fromJson` at `Gson.java:880`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The failure occurs because the parser encounters an unquoted token (e.g., an integer key in a map) and the logic in JsonReader.nextInt()/nextLong() does not include PEEKED_UNQUOTED in the conditional branch that attempts to parse the value. This is a missing validation/handling case for a specific token type.
