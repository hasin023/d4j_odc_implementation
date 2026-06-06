package org.joda.time.format;

import org.junit.Test;
import org.joda.time.Period;
import static org.junit.Assert.assertEquals;

public class LLMGeneratedTest {

    @Test
    public void testBug64() {
        // The bug was that the manual builder construction of the formatter
        // was failing to parse large values in the seconds field because the 
        // internal parser logic for the seconds field was not correctly 
        // handling the sequence of fields when using appendSecondsWithOptionalMillis().
        
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

        // The input "PT1003199059S" represents 1003199059 seconds.
        // The bug was that the parser would throw an IllegalArgumentException 
        // because it failed to parse the large integer value correctly.
        String periodStr = "PT1003199059S";
        
        Period p = pfmt.parsePeriod(periodStr);
        
        // Verify that the parser now correctly identifies the seconds field.
        // 1003199059 seconds is the expected value.
        assertEquals(1003199059, p.getSeconds());
    }
}