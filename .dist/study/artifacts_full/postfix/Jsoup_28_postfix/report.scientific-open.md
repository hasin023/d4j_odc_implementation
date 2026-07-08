# Defects4J ODC Classification Report: Jsoup-28

- Version: `28b`
- Work directory: `C:\d4j_work\postfix\Jsoup_28b`
- Generated: `2026-07-08T16:58:29+00:00`

## Failure Summary
- `org.jsoup.nodes.EntitiesTest::unescape`: junit.framework.AssertionFailedError: expected:<Hello &<> ® Å [&angst] π π 新 there &! ¾ © ...> but was:<Hello &<> ® Å [Å] π π 新 there &! ¾ © ...>
- `org.jsoup.nodes.EntitiesTest::noSpuriousDecodes`: junit.framework.AssertionFailedError: expected:<...tp://www.foo.com?a=1[&num_rooms=1&children=0&int]=VA&b=2> but was:<...tp://www.foo.com?a=1[#_rooms=1&children=0∫]=VA&b=2>
- `org.jsoup.parser.AttributeParseTest::moreAttributeUnescapes`: junit.framework.AssertionFailedError: expected:<...23&mid-size=true&ok=[&wr]> but was:<...23&mid-size=true&ok=[≀]>
- `org.jsoup.parser.AttributeParseTest::strictAttributeUnescapes`: junit.framework.AssertionFailedError: expected:<?foo=bar[&mid]&lt=true> but was:<?foo=bar[∣]&lt=true>
- `org.jsoup.parser.HtmlParserTest::doesNotFindShortestMatchingEntity`: junit.framework.AssertionFailedError: expected:<One [&amp;clubsuit]e; ♣> but was:<One [♣]e; ♣>
- `org.jsoup.parser.HtmlParserTest::relaxedBaseEntityMatchAndStrictExtendedMatch`: junit.framework.AssertionFailedError: expected:<&amp; &quot; &reg; &[amp;icy &amp;hopf] &icy; &hopf;> but was:<&amp; &quot; &reg; &[icy; &hopf;] &icy; &hopf;>

## Suspicious Frames
- `org.jsoup.nodes.EntitiesTest.unescape` at `EntitiesTest.java:27`
- `org.jsoup.nodes.EntitiesTest.noSpuriousDecodes` at `EntitiesTest.java:65`
- `org.jsoup.parser.AttributeParseTest.moreAttributeUnescapes` at `AttributeParseTest.java:67`
- `org.jsoup.parser.AttributeParseTest.strictAttributeUnescapes` at `AttributeParseTest.java:60`
- `org.jsoup.parser.HtmlParserTest.doesNotFindShortestMatchingEntity` at `HtmlParserTest.java:729`
- `org.jsoup.parser.HtmlParserTest.relaxedBaseEntityMatchAndStrictExtendedMatch` at `HtmlParserTest.java:737`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug is a classic case of an incorrect algorithmic strategy for parsing. The regex-based `unescape` method is too greedy and lacks the context-awareness (like checking for valid entity names or the required semicolon) needed to distinguish between actual HTML entities and plain text that happens to contain an ampersand. The fix replaces this with a proper `Tokeniser` implementation, which is a change to the computational strategy/procedure.
