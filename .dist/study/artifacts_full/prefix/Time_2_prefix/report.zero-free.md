# Defects4J ODC Classification Report: Time-2

- Version: `2b`
- Work directory: `C:\d4j_work\prefix\Time_2b`
- Generated: `2026-07-10T18:54:51+00:00`

## Failure Summary
- `org.joda.time.TestPartial_Basics::testWith_baseAndArgHaveNoRange`: java.lang.IllegalArgumentException: Types array must not contain duplicate: era and year

## Suspicious Frames
- `org.joda.time.Partial.<init>` at `Partial.java:225`
- `org.joda.time.Partial.with` at `Partial.java:466`

## ODC Result
- **Evidence Mode**: ✅ Pre-fix only
- ODC Type: `Incorrect validation logic for partial date-time fields`
- Family: `None`
- Target: `Design/Code`
- Confidence: `0.95`
- Needs Human Review: `False`

The code in Partial.java enforces that fields must be ordered from largest to smallest duration. When comparing two fields with the same duration (e.g., both having null range duration types), the code incorrectly assumes they are duplicates and throws an IllegalArgumentException. In the case of 'era' and 'year', both have null range duration types, but they are distinct fields that should be allowed to coexist in a Partial object. The validation logic fails to distinguish between actual duplicate field types and different field types that happen to share the same (null) range duration.
