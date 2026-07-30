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
- [Technical Stack](#technical-stack)
- [Repository Structure](#repository-structure)
- [Reproducibility Principles](#reproducibility-principles)
- [Data Governance](#data-governance)
- [AI Transparency](#ai-transparency)

---

## Assessment Overview

| Module | Capability Demonstrated | Status |
|---|---|---|
| Q1 | Campaign GPS tracking, settlement reconciliation, spatial statistics | In Development |
| Q2 | Facility accessibility and spatial database modelling | Planned |
| Q3 | Digital survey instrument engineering | Planned |
| Q4 | Complex survey inference | Planned |
| Q5 | Technical coordination and delivery management | Planned |
| Q6 | Capability development framework | Planned |

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

Implementation is underway. The work will retain raw observations, document quality rules and assumptions, and distinguish analytical evidence from programme reporting before producing decision-support outputs.

Requirement 5 uses the `baseline_30m` GPS classification for 2,382 non-ambiguous planned settlements (2,168 unvisited and 214 visited). Under binary, row-standardized k=8 nearest-neighbour weights in EPSG:32632, Global Moran's I was 0.046612 (expected I -0.000420; z-score 4.821064; 999-permutation p-value 0.001). This supports positive global autocorrelation in the observed GPS-derived missed-settlement indicator. No Local Moran result survived Benjamini-Hochberg FDR correction; raw local patterns are exploratory screening signals, not confirmed hotspots.

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
