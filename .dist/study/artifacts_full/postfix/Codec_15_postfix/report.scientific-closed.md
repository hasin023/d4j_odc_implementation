# Defects4J ODC Classification Report: Codec-15

- Version: `15b`
- Work directory: `C:\d4j_work\postfix\Codec_15b`
- Generated: `2026-07-10T18:49:33+00:00`

## Failure Summary
- `org.apache.commons.codec.language.SoundexTest::testHWRuleEx1`: junit.framework.AssertionFailedError: expected:<Y3[3]0> but was:<Y3[0]0>

## Suspicious Frames
- `org.apache.commons.codec.language.SoundexTest.testHWRuleEx1` at `SoundexTest.java:232`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Soundex.getMappingCode`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug report and the failing test case 'yhwdyt' indicate that the HW rule implementation is too restrictive. The fix (as seen in the provided diff) replaces the fixed-depth check with a loop that correctly traverses backwards to find the last non-H/W character, confirming the defect is an algorithmic/methodological error.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Impact: `Capability`
