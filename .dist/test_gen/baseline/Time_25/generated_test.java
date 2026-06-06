package org.joda.time;

import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class LLMGeneratedTest {

    @Test
    public void testDateTimeZone_getOffsetFromLocal_AmbiguousDST() {
        // America/Los_Angeles in 2009:
        // DST ended on Nov 1, 2009 at 2:00 AM.
        // 1:30 AM occurred twice: once at UTC-7 and once at UTC-8.
        // The bug report states that Joda-Time should return the earlier instant (the one with the larger offset, -07:00).
        
        DateTimeZone zone = DateTimeZone.forID("America/Los_Angeles");
        
        // 2009-11-01T01:30:00 is ambiguous.
        // The expected behavior is to return the earlier instant (Daylight time, -07:00).
        // 1:30 AM -07:00 is 08:30 AM UTC.
        // 1:30 AM -08:00 is 09:30 AM UTC.
        
        long localMillis = new DateTime(2009, 11, 1, 1, 30, 0, 0, DateTimeZone.UTC).getMillis();
        int offset = zone.getOffsetFromLocal(localMillis);
        
        // The offset for the earlier instant (Daylight) is -07:00 (-25,200,000 ms)
        assertEquals("Should return the offset for the earlier (Daylight) instant", -25200000, offset);
    }
}