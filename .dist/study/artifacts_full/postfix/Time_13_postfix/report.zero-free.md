# Defects4J ODC Classification Report: Time-13

- Version: `13b`
- Work directory: `C:\d4j_work\postfix\Time_13b`
- Generated: `2026-07-25T14:46:17+00:00`

## Failure Summary
- `org.joda.time.format.TestISOPeriodFormat::testFormatStandard_negative`: junit.framework.ComparisonFailure: expected:<PT[-]0.008S> but was:<PT[]0.008S>

## Suspicious Frames
- `org.joda.time.format.TestISOPeriodFormat.testFormatStandard_negative` at `TestISOPeriodFormat.java:135`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incorrect formatting logic for negative fractional time units`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs when formatting a period containing negative milliseconds that are less than one second (e.g., -100ms). The formatter fails to include the negative sign in the output string (producing 'PT0.100S' instead of 'PT-0.100S'). The fix involves two parts: first, adjusting the buffer size calculation to account for the extra character required by the negative sign in fractional seconds; second, explicitly inserting a '-' character into the buffer when the value is negative but greater than -1 second, ensuring the sign is correctly placed before the fractional part.
