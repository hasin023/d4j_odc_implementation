# Defects4J ODC Classification Report: Jsoup-28

- Version: `28b`
- Work directory: `C:\d4j_work\prefix\Jsoup_28b`
- Generated: `2026-07-08T16:51:09+00:00`

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
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Algorithm/Method`
- Family: `Control and Data Flow`
- Target: `Code`
- Confidence: `0.9`
- Needs Human Review: `False`

The issue is a flaw in the entity decoding procedure itself. It is not a missing guard (Checking) or a wrong initialization (Assignment/Initialization), but rather an incorrect algorithmic strategy for identifying and replacing entities in the input string. The fix requires changing the logic that determines what constitutes a valid entity to be decoded.

## ODC Attribute Mapping (Optional)
- Qualifier: `Incorrect`
- Age: `Base`
- Source: `Developed In-House`
- Inferred Activity: `Unit Test`
- Inferred Triggers: `Test Variation`
- Inferred Impact: `Reliability`
