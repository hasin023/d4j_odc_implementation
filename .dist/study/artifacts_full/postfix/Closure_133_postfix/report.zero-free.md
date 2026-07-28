# Defects4J ODC Classification Report: Closure-133

- Version: `133b`
- Work directory: `C:\d4j_work\postfix\Closure_133b`
- Generated: `2026-07-26T07:25:14+00:00`

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
- ODC Type: `State inconsistency in parser`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs because the JSDoc parser fails to reset its internal state ('unreadToken') after consuming a line of JSDoc content. When the parser encounters specific JSDoc structures, the stale token state causes the parser to miscalculate the character positions of the text, leading to an IllegalStateException when the recorded end position is less than the start position. The fix involves explicitly resetting the 'unreadToken' state to 'NO_UNREAD_TOKEN' within the 'getRemainingJSDocLine' method, ensuring that subsequent parsing operations start from a clean state.
