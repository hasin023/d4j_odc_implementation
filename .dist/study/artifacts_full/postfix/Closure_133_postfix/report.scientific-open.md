# Defects4J ODC Classification Report: Closure-133

- Version: `133b`
- Work directory: `C:\d4j_work\postfix\Closure_133b`
- Generated: `2026-07-26T06:43:36+00:00`

## Failure Summary
- `com.google.javascript.jscomp.parsing.JsDocInfoParserTest::testTextExtents`: java.lang.IllegalStateException: Recorded bad position information

## Suspicious Frames
- `com.google.javascript.rhino.SourcePosition.setPositionInformation` at `SourcePosition.java:87`
- `com.google.javascript.rhino.JSDocInfoBuilder.markText` at `JSDocInfoBuilder.java:172`
- `com.google.javascript.jscomp.parsing.JsDocInfoParser.extractMultilineTextualBlock` at `JsDocInfoParser.java:1503`
- `com.google.javascript.jscomp.parsing.JsDocInfoParser.extractMultilineTextualBlock` at `JsDocInfoParser.java:1379`
- `com.google.javascript.jscomp.parsing.JsDocInfoParser.parse` at `JsDocInfoParser.java:959`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Assignment/Initialization`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is caused by a failure to reset the 'unreadToken' variable in the 'getRemainingJSDocLine' method. This stale state causes the parser to incorrectly calculate the position of tokens in subsequent lines, leading to the 'IllegalStateException' in 'SourcePosition'. This is an Assignment/Initialization defect because the state variable is not being correctly re-initialized/cleared.

## ODC Attribute Mapping (Optional)
- Impact: `Reliability`
