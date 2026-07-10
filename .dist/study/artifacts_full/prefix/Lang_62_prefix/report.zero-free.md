# Defects4J ODC Classification Report: Lang-62

- Version: `62b`
- Work directory: `C:\d4j_work\prefix\Lang_62b`
- Generated: `2026-07-10T19:30:22+00:00`

## Failure Summary
- `org.apache.commons.lang.EntitiesTest::testNumberOverflow`: junit.framework.ComparisonFailure: expected:<[&#12345678;]> but was:<[慎]>

## Suspicious Frames
- `org.apache.commons.lang.EntitiesTest.doTestUnescapeEntity` at `EntitiesTest.java:101`
- `org.apache.commons.lang.EntitiesTest.testNumberOverflow` at `EntitiesTest.java:201`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Integer overflow handling error`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The code fails to correctly handle numeric character references that exceed the maximum value of a Java char (0xFFFF). When the unescape logic encounters a numeric entity like '&#12345678;', it attempts to parse the number and cast it to a character. Because 12345678 is significantly larger than 65535, the cast results in an incorrect character representation (truncation), whereas the specification requires that invalid or out-of-range numeric entities should be treated as literal text rather than being converted to an incorrect character.
