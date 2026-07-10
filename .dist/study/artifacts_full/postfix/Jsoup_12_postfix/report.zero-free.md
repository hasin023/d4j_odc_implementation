# Defects4J ODC Classification Report: Jsoup-12

- Version: `12b`
- Work directory: `C:\d4j_work\postfix\Jsoup_12b`
- Generated: `2026-07-10T18:54:12+00:00`

## Failure Summary
- `org.jsoup.select.SelectorTest::testByAttributeRegexCombined`: org.jsoup.select.Selector$SelectorParseException: Could not parse query '=x|y]': unexpected token at '=x|y]'

## Suspicious Frames
- `org.jsoup.select.Selector.findElements` at `Selector.java:187`
- `org.jsoup.select.Selector.select` at `Selector.java:113`
- `org.jsoup.select.Selector.select` at `Selector.java:84`
- `org.jsoup.select.Selector.combinator` at `Selector.java:149`
- `org.jsoup.select.Selector.select` at `Selector.java:126`
- `org.jsoup.nodes.Element.select` at `Element.java:199`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Incorrect Tokenization/Parsing Logic`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs because the CSS selector parser uses a simple 'consumeToAny' approach when processing sub-queries after a combinator. This approach fails to account for nested structures like attribute selectors containing brackets (e.g., [attr~=x|y]) or parentheses, causing the parser to prematurely terminate the sub-query at the first occurrence of a character that might be part of a combinator or a special token. The fix introduces a 'consumeSubQuery' method that correctly balances brackets and parentheses, ensuring the entire sub-query is captured as a single unit before the next combinator is processed.
