# eHealth Africa

## Senior Coordinator, Data and GIS Analytics Technical Assessment

**Candidate:** Yahaya Umar Muhammad

This repository contains the technical assessment submission for the Senior Coordinator, Data and GIS Analytics role. It is organized to demonstrate advanced geospatial analysis, reproducible data engineering workflows, spatial database design, survey data systems, technical coordination, and capability development.

## Assessment Overview

| Component | Focus |
|---|---|
| Q1 | Campaign Team Tracking and Coverage Reconciliation |
| Q2 | Facility Readiness and Spatial Accessibility |
| Q3 | Digital Survey Instrument Development |
| Q4 | Complex Survey Analysis |
| Q5 | Technical Coordination |
| Q6 | Capability Development |

## Technical Architecture

The assessment is structured around reproducible Python analytical pipelines and a PostgreSQL/PostGIS spatial database. GeoPandas and Shapely support spatial processing, while QGIS is used for cartographic production. Workflows, assumptions, data handling, and technical decisions are documented alongside the relevant assessment component so that results can be reviewed and reproduced.

## Q1 Highlight

Question 1 examines how raw field operations data becomes a decision-ready coverage product:

```text
Raw operational data
        ↓
Spatial ingestion
        ↓
Quality assurance
        ↓
Settlement attribution
        ↓
Coverage reconciliation
        ↓
Decision products
```

## Repository Structure

```text
.
├── README.md
├── AI_USE.md
├── environment.yml
├── Candidate_Profile/
│   └── Yahaya_Umar_Muhammad.md
├── Q1_Campaign_Team_Tracking/
│   ├── data/
│   ├── database/
│   ├── notebooks/
│   ├── outputs/
│   ├── src/
│   ├── tests/
│   ├── methodology.md
│   ├── technical_decisions.md
│   └── data_dictionary.md
├── Q2_Facility_Readiness_Accessibility/
├── Q3_Digital_Form_Development/
├── Q4_Coverage_Survey_Analysis/
├── Q5_Technical_Coordination/
└── Q6_Capability_Development/
```

## Reproducibility

- `environment.yml` defines the project environment.
- Each component records its workflow, assumptions, and technical decisions.
- Tests support validation of processing logic as the assessment is developed.
- Data dictionaries and provenance documentation make source data and derived products traceable.

## AI Transparency

Use of AI assistance is disclosed in [AI_USE.md](AI_USE.md), including the tools used and their purpose.
