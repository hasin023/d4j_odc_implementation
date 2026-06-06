package org.joda.time.format;

import org.junit.Test;
import org.joda.time.Period;
import static org.junit.Assert.assertEquals;

public class LLMGeneratedTest {

    @Test
    public void testBug64() {
        // The bug report states that ISOPeriodFormat.standard() behaves differently 
        // than a manually constructed builder that mimics it.
        // Specifically, parsing "PT1003199059S" fails in the buggy version.
        
        PeriodFormatter pfmt = new PeriodFormatterBuilder()
            .appendLiteral("P")
            .appendYears()
            .appendSuffix("Y")
            .appendMonths()
            .appendSuffix("M")
            .appendWeeks()
            .appendSuffix("W")
            .appendDays()
            .appendSuffix("D")
            .appendSeparatorIfFieldsAfter("T")
            .appendHours()
            .appendSuffix("H")
            .appendMinutes()
            .appendSuffix("M")
            .appendSecondsWithOptionalMillis()
            .appendSuffix("S")
            .toFormatter();

        // This string represents a large number of seconds that caused the parser to fail
        String periodStr = "PT1003199059S";
        
        // This should parse successfully without throwing an IllegalArgumentException
        Period p = pfmt.parsePeriod(periodStr);
        
        assertEquals(1003199059, p.getSeconds());
    }
}