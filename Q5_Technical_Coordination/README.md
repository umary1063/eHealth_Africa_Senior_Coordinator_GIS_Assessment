# 🧭 Question 5: Coordinating Delivery Through the Round

*Compulsory, Part 3, maximum 3 pages.*

Day 3 of a 7-day campaign, four things land at once: two analysts resign, a coverage figure is disputed at national level, the shared database gets corrupted by two people editing at the same time, and a partner report and a counterpart's training-date request are both waiting.

**📄 [`Q5_Response.docx`](Q5_Response.docx)** covers all six required parts:

- ⏱️ A **first 24-hour sequence** (activate → capture evidence → holding statement → find the root cause → start the handover → cover the vacated states → publish a figure), and why in that order
- 🔍 How to publish **one trustworthy figure** while the cause is still unknown, plus a categorised root-cause checklist (scope, timing, data engineering, human reporting)
- 🗄️ A real **technical design** for editing a shared spatial database without conflicts — staging tables, unique IDs, conflict detection, named-reviewer approval, full version history, offline sync — built natively in PostGIS rather than depending on an external tool
- 🚦 Which **data-quality rules** should block a change outright versus just flag it for review
- 🤝 A **10-day handover plan** for the two departing analysts — what gets protected first, what's knowingly accepted as incomplete
- 👥 A **delegation structure** with named workstream leads, so the coordinator isn't the single point of failure

It closes on the real cause of the crisis: knowledge concentrated in individuals, documentation too weak to fill the gap, and no one else with the authority to act — the same argument carried forward into [Question 6](../Q6_Capability_Development/Q6_Response.docx).
