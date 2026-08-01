<div align="center">

# 🌍 eHealth Africa
### Senior Coordinator, Data and GIS Analytics — Technical Assessment

**Candidate:** Yahaya Umar Muhammad

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![PostgreSQL/PostGIS](https://img.shields.io/badge/PostgreSQL%20%2F%20PostGIS-Spatial%20database-336791?logo=postgresql&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-Spatial%20processing-139C5A?logo=pandas&logoColor=white)
![QGIS](https://img.shields.io/badge/QGIS-Cartography-589632?logo=qgis&logoColor=white)
![ODK](https://img.shields.io/badge/ODK-Digital%20forms-D22B2B)
![Status](https://img.shields.io/badge/Submission-Complete-2EA44F)

</div>

---

## 👋 What this is

A national vaccination campaign generated messy GPS tracks, a paper survey needed to become a phone-based digital form, and a coordinator has to keep a distributed team and a partner agency's training programme both on track at once. This repository is one candidate's answer to four of those problems — real code, real data, and honest write-ups of what went wrong along the way and how it got fixed.

## 📋 What was attempted

The assessment asks for one question from Part 1, one from Part 2, and both compulsory Part 3 questions. Q2 and Q4 are the alternates that were **not** chosen — not missing work.

| # | Question | What it covers | Status |
|---|---|---|---|
| 🗺️ **Q1** | Campaign Team Tracking & Coverage Reconciliation | Turning messy GPS tracks into "which villages got visited" | ✅ Complete |
| 🏥 Q2 | Facility Readiness & Accessibility | *(alternate — not attempted, Q1 chosen instead)* | ⬜ Not attempted |
| 📱 **Q3** | Digital Form Development | Paper survey → phone-based ODK form for 120 field enumerators | ✅ Complete |
| 📊 Q4 | Coverage Survey Analysis | *(alternate — not attempted, Q3 chosen instead)* | ⬜ Not attempted |
| 🧭 **Q5** | Coordinating Delivery Through the Round | Crisis management: staff loss, data conflicts, a live campaign | ✅ Complete (compulsory) |
| 🎓 **Q6** | Building Capability in the Counterpart Agency | Designing a 5-day GIS training course from real test results | ✅ Complete (compulsory) |

Q5 and Q6 share one scenario. The assessment expects candidates to connect coordination and capability-building as one theme, not treat them as separate — so that link is made directly in the closing section of each response.

---

## 🗺️ Q1 — Campaign Team Tracking & Coverage Reconciliation

```text
Raw GPS points  →  quality checks  →  match to villages  →  compare to tally  →  cluster map  →  decision brief
```

**The pipeline is complete** — it keeps every raw GPS point, writes down every rule and threshold used, and never mistakes a data problem for proof that a village was skipped.

🔍 **The interesting part:** a routine check found the GPS files were secretly wrong. They were meant to be one file per team per day, but actually held 6–21 days of continuous logging each — over 85% of the 956,702 raw points fell outside the day their filename claimed. Fixing that properly uncovered three more linked bugs (a 1000× unit-conversion error, a leftover data-contamination bug, and a bug where old wrong flags never cleared between re-runs). All four are documented in full — including the two wrong "final" numbers reported along the way — in [`technical_decisions.md`](Q1_Campaign_Team_Tracking/technical_decisions.md).

**The headline result:** GPS confirms only 5.43% of villages visited, against 78.69% reported in the tally system. That gap is too large to be real under-performance — the write-up treats it as a data-completeness problem and tells the Incident Manager to verify before acting on either number.

📄 Full response: [`Q1_Technical_Response.docx`](Q1_Campaign_Team_Tracking/docs/Q1_Technical_Response.docx)

---

## 📱 Q3 — Digital Form Development

The supplied paper questionnaire (`Household_Questionnaire_HH2026v1.docx`) converts cleanly into a real, deployable ODK form ([`HH2026_v1.xlsx`](Q3_Digital_Form_Development/form/HH2026_v1.xlsx)), tested on two live platforms — not just a clean conversion check.

Beyond digitising it, the submission:
- 🐛 Names **9 real defects** in the paper form itself (a contradiction, a missing skip instruction, unanalysable data) and says for each whether it was fixed or escalated to the ministry
- 📋 Traces every validation rule to its source in a **29-row constraint register** — no rule without a reason
- 🔢 **Proves**, not just demonstrates, that the specimen-label check digit catches every possible mistyped label
- 🔐 Gives an honest answer on cross-device duplicate detection: a form alone can't fully guarantee it — implemented what's achievable, tested the rest ([**ODK Entities**](Q3_Digital_Form_Development/documentation/05_duplicate_label_detection.md)) live against a real ODK Central server

📄 Full response: [`Q3_Response.docx`](Q3_Digital_Form_Development/Q3_Response.docx)

---

## 🧭 Q5 — Coordinating Delivery Through the Round

Day 3 of a 7-day campaign, four things land at once: two analysts resign, a coverage figure is disputed nationally, the shared database gets corrupted by two people editing at the same time, and a partner report and a training-date request are both waiting.

[`Q5_Response.docx`](Q5_Technical_Coordination/Q5_Response.docx) covers, in order: the first 24 hours and why in that sequence, how to publish one trustworthy figure while the cause is still unknown, a real technical design for conflict-free concurrent database editing (staging tables, unique IDs, named-reviewer conflict resolution, full audit history), which data-quality rules should block a change versus just flag it for review, a 10-day handover plan for the departing analysts, and how to delegate so the coordinator isn't the bottleneck.

---

## 🎓 Q6 — Building Capability in the Counterpart Agency

A real capability test of 21 staff found a composite score of 36/100, a knowledge score of 57%, almost no relationship between how confident people felt and what they could actually do, and **zero** of 21 staff with access to QGIS or ArcGIS.

[`Q6_Response.docx`](Q6_Capability_Development/Q6_Response.docx) treats that last finding as the constraint the whole course lives or dies on — day one installs QGIS on every machine. Since confidence didn't predict skill, the course is built from the test results, not from what people said they wanted, using a 4-level, 6-domain framework with observable behaviours instead of a vague beginner/intermediate/advanced scale. It states plainly what's *not* taught this round (spatial statistics, remote sensing, automation), includes one full 90-minute session written out end to end, a scored pre/post practical test, and a 90-day plan measured by real work produced, not attendance.

**The Q5↔Q6 link:** both responses close by naming the same underlying weakness — knowledge concentrated in individuals with no backup is what turns ordinary staff movement into a crisis (Q5) and what the training programme exists to prevent (Q6).

---

## 🧰 Technical Stack

| Layer | Tools |
|---|---|
| 🐍 Language | Python |
| 🗄️ Spatial database | PostgreSQL / PostGIS |
| 🌐 Spatial processing | GeoPandas, Shapely |
| 📊 Data analysis | Pandas |
| 🗺️ Cartography | QGIS |
| 📱 Digital forms | ODK (pyxform, Collect, Central) |
| 📝 Documentation | Markdown |
| 🔀 Version control | Git / GitHub |

## 📁 Repository Structure

<details>
<summary>Click to expand</summary>

```text
eHealth_Africa_Senior_Coordinator_GIS_Assessment/
├── README.md
├── AI_USE.md
├── environment.yml
├── Candidate_Profile/
├── Candidate_Inputs/
├── Q1_Campaign_Team_Tracking/     ✅ attempted
├── Q2_Facility_Readiness_Accessibility/   ⬜ alternate, not attempted
├── Q3_Digital_Form_Development/   ✅ attempted
├── Q4_Coverage_Survey_Analysis/   ⬜ alternate, not attempted
├── Q5_Technical_Coordination/     ✅ compulsory
└── Q6_Capability_Development/     ✅ compulsory
```

</details>

## ♻️ Reproducibility

- **Nothing is hand-edited.** Every output can be regenerated from raw data using the code in this repo.
- **Raw data is never overwritten.** Quality problems get flagged, not silently deleted.
- **Every threshold has a stated reason** — a named source, or an explicit "this is my judgement."
- `environment.yml` pins the exact environment needed to reproduce every result.

## 🔎 Data Governance

Every output is built to help a real decision-maker, not just to look sophisticated. Assumptions and uncertainty are stated plainly rather than hidden behind precision the data doesn't actually support.

## 🤖 AI Transparency

AI-assisted work is disclosed in full in [`AI_USE.md`](AI_USE.md), including corrections the candidate made along the way. Every analytical decision, assumption, and technical explanation remains the candidate's own responsibility.
