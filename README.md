# eHealth Africa

## Senior Coordinator, Data and GIS Analytics Technical Assessment

**Candidate:** Yahaya Umar Muhammad

This repository contains a technical assessment submission demonstrating advanced geospatial analysis, reproducible data engineering workflows, spatial database design, survey data systems, operational decision support, and technical coordination and capability development.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![PostgreSQL/PostGIS](https://img.shields.io/badge/PostgreSQL%20%2F%20PostGIS-Spatial%20data%20platform-336791?logo=postgresql&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-Spatial%20processing-139C5A)
![QGIS](https://img.shields.io/badge/QGIS-Cartography-589632?logo=qgis&logoColor=white)
![Reproducible Research](https://img.shields.io/badge/Reproducible%20Research-Documented%20workflows-4C8BF5)

---

## Contents

- [Assessment Overview](#assessment-overview)
- [Technical Architecture](#technical-architecture)
- [Q1 Campaign Tracking](#q1--campaign-team-tracking-and-coverage-reconciliation)
- [Q3 Digital Form Development](#q3--digital-form-development)
- [Q5 Technical Coordination](#q5--coordinating-delivery-through-the-round)
- [Q6 Capability Development](#q6--building-capability-in-the-counterpart-agency)
- [Technical Stack](#technical-stack)
- [Repository Structure](#repository-structure)
- [Reproducibility Principles](#reproducibility-principles)
- [Data Governance](#data-governance)
- [AI Transparency](#ai-transparency)

---

## Assessment Overview

The paper requires one question from Part 1 (Q1 or Q2), one from Part 2 (Q3 or Q4), and both
compulsory Part 3 questions, which share one scenario:

- Question 5: Coordinating Delivery Through the Round
- Question 6: Building Capability in the Counterpart Agency

This submission is complete on that basis: Q1, Q3, Q5, and Q6 are attempted and finished; Q2 and
Q4 are the un-attempted alternates within their parts, not outstanding work. The connection
between coordination resilience and capability development is a stated expectation of Part 3, not
a separate compulsory question — it is argued directly in the concluding sections of Q5 and Q6.

| Module | Capability Demonstrated | Status |
|---|---|---|
| Q1 | Campaign GPS tracking, settlement reconciliation, spatial statistics | Complete — attempted |
| Q2 | Facility accessibility and spatial database modelling | Not attempted (Part 1 alternate — Q1 chosen) |
| Q3 | Digital survey instrument engineering | Complete — attempted |
| Q4 | Complex survey inference | Not attempted (Part 2 alternate — Q3 chosen) |
| Q5 | Technical coordination and delivery management | Complete — compulsory |
| Q6 | Capability development framework | Complete — compulsory |

---

## Technical Architecture

```text
Operational Data Sources
├── GPS Tracks
├── Settlement Masterlist
├── Administrative Boundaries
└── e-Tally Reports
            ↓
Data Engineering Pipeline
├── Validation
├── Quality Assurance
├── Metadata Tracking
└── Reproducible Processing
            ↓
Spatial Data Platform
└── PostgreSQL + PostGIS
            ↓
Analytics Layer
├── Python
├── GeoPandas
├── Shapely
└── Spatial Statistics
            ↓
Decision Products
├── Maps
├── Reports
└── Operational Briefs
```

---

## Q1 — Campaign Team Tracking and Coverage Reconciliation

Question 1 is designed as an end-to-end operational analytics workflow:

```text
Raw GPS observations
→ spatial ingestion
→ GPS quality assessment
→ settlement attribution
→ coverage reconciliation
→ spatial hotspot analysis
→ decision products
```

Q1 implementation is complete. The workflow retains raw observations, documents quality rules and assumptions, and distinguishes analytical evidence from programme reporting in its decision-support outputs.

A read-only audit on 2026-07-31 found that the supplied GPS track files, despite being named one file per team per day, actually contain 6–21 days of continuous logging each; 85.5% of all 956,702 raw points fall outside their own file's nominal day, and for 66 of 160 team-days two different files both produced GPS fixes during real duty hours on the same real date — physically impossible for one team. Correcting this properly surfaced three further, compounding defects in the QA pipeline (a 1000x unit-conversion bug in the implausible-speed rule, that rule's sequence computations still crossing contaminated files after the first fix, and a stale-flag-accumulation bug that silently re-corrupted two intermediate correction attempts). All four are documented, including the false starts, in `Q1_Campaign_Team_Tracking/technical_decisions.md` (2026-07-31 entries), and the full pipeline was re-run end to end against the final, verified-clean state.

Requirement 5 uses the `baseline_30m` GPS classification for 2,318 non-ambiguous planned settlements (2,179 unvisited and 139 visited). Under binary, row-standardized k=8 nearest-neighbour weights in EPSG:32632, Global Moran's I was 0.020281 (expected I -0.000432; z-score 2.267140; 999-permutation p-value 0.026). This supports positive global autocorrelation in the observed GPS-derived missed-settlement indicator. No Local Moran result survived Benjamini-Hochberg FDR correction; raw local patterns are exploratory screening signals, not confirmed hotspots. The ambiguity-included sensitivity scenario lost significance entirely after the correction (p=0.140), reported plainly rather than smoothed over.

Final Q1 decision products distinguish observed evidence from programme-performance inference. A missing GPS track is not treated as proof of a missed settlement; recommendations state evidence confidence and direct supervisors to verify, inspect devices, reconcile reporting, and confirm repeat visits before mop-up deployment. The corrected GPS-visited rate (5.43%) sits far below e-tally-reported coverage (78.69%, essentially unchanged by these fixes) — a gap wide enough that it is presented as further evidence of GPS-attribution and data-density limitations, not as a literal claim that most settlements were unserved.

---

## Q3 — Digital Form Development

`Household_Questionnaire_HH2026v1.docx` converted to a deployable ODK XLSForm
(`Q3_Digital_Form_Development/form/HH2026_v1.xlsx`), validated with pyxform 4.5.0 against
ODK Validate — conversion output and log committed in `Q3_Digital_Form_Development/conversion/`.

Beyond a faithful digitisation, the submission documents nine defects found in the paper
instrument (an internal contradiction, a missing skip instruction, and unanalysable data among
them — `Q3_Digital_Form_Development/documentation/01_defects_report.md`), a 25-row constraint
register tracing every added rule to its source or to an explicitly stated judgement call, a
sentinel/measurement collision found in the anthropometry questions and fixed by field-splitting
rather than a magic number, a proof (not just a demonstration) that the specimen label's
modulus-11 check digit catches every adjacent-digit transposition, and an honest answer to
whether a self-contained form can detect a duplicate specimen label across nine offline days
(it cannot, in full — the achievable part is implemented, the rest is described as an
architecture, not claimed as done).

---

## Q5 — Coordinating Delivery Through the Round

Part 3 is compulsory and shares one scenario: mid-round resignations, a coverage figure disputed
at national level, a database corrupted by concurrent edits, a partner report due in nine days,
and a counterpart agency waiting on training dates — all at once, on day three of seven.

[Q5_Technical_Coordination/Q5_Response.docx](Q5_Technical_Coordination/Q5_Response.docx) opens
with a "First 24-Hour Response Sequence" table sequenced by risk to live delivery, reversibility,
compounding data damage, reputational exposure, and dependency between actions, then works through
a figure-of-record definition with a categorised root-cause table, a PostGIS-native controlled
editing architecture for the shared spatial database (staging tables, UUID identifiers, feature-
level conflict detection, named-reviewer merge approval, row-level audit history), a blocking-vs-
flagging table for automated data quality rules, a 10-day handover plan for the two departing
analysts, and a delegation structure built on named workstream leads so the coordinator is not the
single point of failure.

---

## Q6 — Building Capability in the Counterpart Agency

The department's own capability assessment found a composite score of 36/100, an objective
knowledge score of 57%, a correlation of 0.11 between self-rated and tested knowledge, and zero of
21 staff with access to QGIS or ArcGIS.

[Q6_Capability_Development/Q6_Response.docx](Q6_Capability_Development/Q6_Response.docx) treats the
software-access finding as the binding constraint on the whole programme, not a footnote — day one
of the five-day course installs QGIS on every participant's own machine, because no curriculum
survives zero take-home tool access. The near-universal stated training demand is read as noise,
not signal, given the self-rating/tested-knowledge correlation, so the course is sequenced from the
objective evidence instead, using a four-level, six-domain observable-behaviour competency
framework (Annex A) rather than a generic beginner/intermediate/advanced scale. Spatial statistics,
remote sensing, web mapping, and automation are explicitly named as *not* taught this round. The
response includes a full stand-alone 90-minute facilitator artefact (Annex B), a 12-item,
demonstrated-capability pre/post assessment instrument scored 0–4 (Annex C), and a 90-day plan
measured by applied output on real departmental work rather than training satisfaction.

Q5 and Q6 close by making the link between them explicit, rather than treating it as a separate
question: Q5's closing section explains that the incident escalated *because* critical knowledge
was concentrated in individuals, documentation was too weak to substitute for them, and delegation
gave no one else the authority to act; Q6's closing section argues that capability building,
reproducible documentation, peer review, and workflow ownership are structural controls against
that same coordination fragility, while stating plainly that they reduce the likelihood of
recurrence rather than eliminate the operational cost of losing key staff.

---

## Technical Stack

| Layer | Technology |
|---|---|
| Programming | Python |
| Spatial Database | PostgreSQL/PostGIS |
| Spatial Processing | GeoPandas, Shapely |
| Data Analysis | Pandas |
| Cartography | QGIS |
| Documentation | Markdown |
| Version Control | Git/GitHub |

---

## Repository Structure

```text
eHealth_Africa_Senior_Coordinator_GIS_Assessment/
├── README.md
├── AI_USE.md
├── environment.yml
├── Candidate_Profile/
├── Candidate_Inputs/
├── Q1_Campaign_Team_Tracking/
├── Q2_Facility_Readiness_Accessibility/
├── Q3_Digital_Form_Development/
├── Q4_Coverage_Survey_Analysis/
├── Q5_Technical_Coordination/
└── Q6_Capability_Development/
```

---

## Reproducibility Principles

### Reproducibility First

- Version-controlled workflows preserve the development history of the submission.
- `environment.yml` specifies the analytical environment.
- Methodology and technical-decision records make assumptions reviewable.
- Processing is designed to run reproducibly from raw data to documented outputs.

### Data Quality by Design

- Raw source data is preserved.
- Validation rules and quality checks are documented.
- Uncertainty is flagged and investigated rather than silently removing records.
- Metadata and provenance are maintained for traceability.

---

## Data Governance

Analysis is organized to support programme decision makers with clear, auditable evidence. Assumptions, data limitations, and uncertainty are communicated explicitly, and outputs are focused on actionable insights rather than unsupported precision.

---

## AI Transparency

AI-assisted work is disclosed in [AI_USE.md](AI_USE.md). AI tools may assist with code scaffolding, debugging, and documentation support; all analytical decisions, assumptions, and technical explanations remain the responsibility of the candidate.
