# Defects4J ODC Classification Report: Jsoup-12

- Version: `12b`
- Work directory: `C:\d4j_work\postfix\Jsoup_12b`
- Generated: `2026-07-08T16:47:46+00:00`

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
- Confidence: `0.95`
- Needs Human Review: `False`

The bug occurs because the CSS selector parser uses a simple 'consumeToAny' approach when encountering combinators, which fails to account for nested structures like attribute selectors containing special characters (e.g., '[class~=x|y]'). When a combinator is present, the parser prematurely stops consuming the sub-query at the first character that matches a combinator or a special symbol, leading to an incomplete and invalid query string. The fix introduces a 'consumeSubQuery' method that correctly handles balanced brackets and parentheses, ensuring that complex attribute selectors are parsed as a single unit rather than being broken apart by the tokenizer.
