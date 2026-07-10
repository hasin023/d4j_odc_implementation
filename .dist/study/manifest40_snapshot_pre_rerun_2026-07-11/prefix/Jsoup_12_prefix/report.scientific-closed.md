# Defects4J ODC Classification Report: Jsoup-12

- Version: `12b`
- Work directory: `C:\d4j_work\prefix\Jsoup_12b`
- Generated: `2026-07-08T17:05:47+00:00`

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
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Checking`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The code snippet for 'findElements' shows it only checks for '#', '.', and various pseudo-selectors. It does not check for '['. When a query like 'table[class~=x|y]' is processed, the parser reaches the attribute part, but 'findElements' doesn't know how to handle '[', leading to the 'unhandled' exception.

## ODC Attribute Mapping (Optional)
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Recovery/Exception`
- Inferred Impact: `Reliability`
