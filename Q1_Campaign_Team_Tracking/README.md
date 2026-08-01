# 🗺️ Question 1: Campaign Team Tracking and Coverage Reconciliation

## 🎯 Purpose

A five-day house-to-house vaccination campaign supplied GPS tracker logs, a list of planned villages, daily tally reports, and administrative boundaries. This component turns those raw, messy inputs into a reliable answer to one question: **which villages actually got visited, and how does that compare to what was reported?**

## ❓ The problem

GPS logs, the settlement list, tally reports, and administrative boundaries each tell part of the story — and each has gaps. The work here checks the GPS data for quality problems, works out which planned settlements were actually visited, compares that against what teams reported, and flags areas that may need a follow-up visit.

## ⚙️ Pipeline

```text
Raw GPS data
    → spatial database
    → quality checks
    → match points to settlements
    → compare to tally reports
    → cluster analysis
    → maps & decision brief
```

## 📚 Documentation

- 📖 [Methodology](methodology.md) — the approach and the assumptions behind it
- 🧾 [Technical decisions](technical_decisions.md) — every material design choice and why it was made
- 📇 [Data dictionary](data_dictionary.md) — what every source and derived dataset actually contains

## 📊 Results

Quality flags are used as screening signals, not automatic deletions — a flagged GPS point stays available for review rather than silently disappearing. Settlement visits are checked under a primary scenario and two sensitivity scenarios, since GPS proximity is evidence of a visit, not proof of service delivery.

### 🐛 A real defect, found and fixed (2026-07-31)

A routine check found the GPS files were secretly wrong: although each file was meant to hold one team's tracks for one day, the files actually contained 6–21 days of continuous logging each. For 66 of 160 team-days, two different files showed the same team in two places at once during real duty hours — physically impossible. Fixing that properly uncovered three more linked bugs (a 1000× unit-conversion error, leftover cross-file contamination in the same rule, and a bug where old wrong flags never cleared between re-runs). All four are documented in full in [`technical_decisions.md`](technical_decisions.md), including the two wrong "final" numbers reported along the way, because a live walkthrough is exactly the setting where "why did this number change three times" deserves a real answer. Every number below is from the final, fully-corrected pipeline run, checked to match between the database and every output file.

### ✅ Headline numbers

| Metric | Result |
|---|---|
| 🏘️ Settlements visited (30 m baseline) | **139** |
| 🏘️ Settlements visited (60 m sensitivity) | 171 (more ambiguous cases too) |
| 🏘️ Settlements visited (urban accuracy-aware) | 142 |
| 📡 GPS-confirmed coverage | **5.43%** |
| 📝 Tally-reported coverage | 78.69% |
| ⚠️ Gap between the two | 73.26 percentage points |

That gap is too large to be genuine under-delivery — a tally system reporting 78.69% next to a real 5.43% physical coverage rate isn't plausible. The decision brief treats this as strong evidence of a data problem, not proof that most villages went unserved, and recommends rapid verification before any mop-up round.

### 📍 Cluster analysis (Requirement 5)

The missed-settlement pattern clusters together more than random chance would explain (Global Moran's I = 0.020281, p = 0.026, using each settlement's 8 nearest neighbours). But once that's corrected for testing thousands of small areas individually, no single local area stays significant — so the local patterns guide *where to look*, not confirmed hotspots. See [the method note](docs/missed_settlement_cluster_method.md) for the full statistical detail.

The primary analysis covers 2,318 clearly-classified settlements (2,179 unvisited, 139 visited), using projected coordinates, 999 random permutations, and the Benjamini-Hochberg correction for multiple testing.

## 🚨 Decision products (Requirement 6)

The A3 map and Incident Manager brief turn the evidence above into cautious, actionable recommendations. **A missing GPS track is never treated as proof a settlement was missed** — every recommendation states how confident the evidence is, and prioritizes verification, device checks, and repeat-visit confirmation before any mop-up deployment or performance judgement.
