# Defects4J ODC Classification Report: Jsoup-28

- Version: `28b`
- Work directory: `.dist\study\work\postfix\Jsoup_28b`
- Generated: `2026-04-21T12:32:36+00:00`

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
- Target: `Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The defect is a procedural error in how the parser identifies and processes HTML entities. The original implementation used an incorrect algorithmic strategy (regex matching) that caused false positives. The fix involves implementing a more robust parsing algorithm (tokenization) to correctly identify valid entities, which is a classic Algorithm/Method correction.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Recovery/Exception, Test Variation`
- Inferred Impact: `Reliability`
