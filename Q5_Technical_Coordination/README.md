# Question 5: Coordinating Delivery Through the Round

Compulsory, Part 3, maximum 3 pages.

**[Q5_Response.docx](Q5_Response.docx)** is the full response, covering the six required
components against a "First 24-Hour Response Sequence" table (activation → evidence capture →
holding statement → root-cause work → handover start → interim coverage → reconciled or
provisional figure), followed by: the figure-of-record definition and a categorised root-cause
table (scope/definition, timing, data engineering, human reporting); a PostGIS-native controlled
editing architecture for the shared spatial database (staging tables, UUID identifiers, feature-
level conflict detection, named-reviewer merge approval, row-level history for versioning and
rollback, offline sync) rather than a dependency on an external versioning product; a blocking-
vs-flagging table for automated data quality rules; a 10-day handover plan for the two departing
analysts distinguishing what is protected first from what is knowingly accepted as incomplete;
and a delegation structure built on named workstream leads and supervision by exception, so the
coordinator is not the single point of failure. Closes by explaining that the incident escalated
because critical knowledge was concentrated in individuals, documentation was too weak to
substitute for them, and delegation gave no one else the authority to act — the structural
argument carried forward into [Question 6](../Q6_Capability_Development/Q6_Response.docx).
