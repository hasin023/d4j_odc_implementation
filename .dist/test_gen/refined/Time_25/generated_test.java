package org.joda.time;

import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class LLMGeneratedTest {

    @Test
    public void testDateTimeZone_getOffsetFromLocal_AmbiguousDST() {
        // The bug report states: "The behaviour during DST overlaps is now defined 
        // to always return the earlier instant which is normally known as daylight or summer time."
        // In the case of America/Los_Angeles on 2009-11-01, the overlap is between 
        // 01:00 and 02:00. The earlier instant is the one in Daylight Time (-07:00).
        
        DateTimeZone zone = DateTimeZone.forID("America/Los_Angeles");
        
        // Constructing a DateTime at 1:30 AM on the day of the fall transition.
        // The constructor uses getOffsetFromLocal internally.
        // The fix ensures that for an ambiguous time, the earlier offset (Daylight, -07:00) is chosen.
        DateTime dt = new DateTime(2009, 11, 1, 1, 30, 0, 0, zone);
        
        // The fixed behavior is to return the earlier instant (Daylight, -07:00).
        // The bug was that it was returning the later instant (-08:00).
        // -07:00 is -25200000 ms.
        // Note: The offset is -07:00, which is -25200000 ms.
        assertEquals("Should return the offset for the earlier (Daylight) instant (-07:00)", 
                     -25200000, zone.getOffsetFromLocal(dt.getMillis()));
        assertEquals("2009-11-01T01:30:00.000-07:00", dt.toString());
    }
}