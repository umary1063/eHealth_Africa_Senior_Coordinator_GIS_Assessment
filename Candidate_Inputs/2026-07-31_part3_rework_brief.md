# Part 3 Rework Brief — 2026-07-31

Candidate-authored content specification directing the rework of Q5 and Q6, and the creation of
Q7, in this repository. Reproduced verbatim (content only — the delivery wrapper was a bash
heredoc invoking `codex exec --full-auto`, which was not executed; Claude Sonnet 5, in Claude
Code, carried out the rework directly against this same brief instead — see [AI_USE.md](../AI_USE.md)).

This file is the record of what the candidate specified versus what the model drafted: every
structural choice named here (the PostGIS-native editing architecture in preference to GeoGig,
the 24-hour response table, the six-domain/four-level competency framework, the 0–4 scoring
scale, the day-by-day course table, the 90-day plan table, and the Q7 argument and its stated
limits) originates in this brief, not in unprompted model output.

---

Work directly on these files:

- eHA_Technical_Assessment_questions(1).docx
- Q5_Response.docx
- Q6_Response.docx

Create or overwrite:

- Q5_Response.docx
- Q6_Response.docx
- Q7_Response.docx

Do not produce a review report first. Rework the documents directly.

SOURCE OF TRUTH

Read the assessment scenario, every direct requirement under Questions 5 and 6, and the "WHAT WE ARE LOOKING FOR" statement in Part 3.

The central argument that must run through the revised work is:

Capability development, reproducible documentation, shared ownership, cross-training, and institutional workflows are structural controls against coordination fragility. The resignation of two analysts is an immediate staffing event, but the fact that delivery is threatened reveals that critical knowledge, access, procedures, and decision authority were concentrated in individuals. The counterpart agency's capability weakness is the same institutional problem in another organisation.

GENERAL REQUIREMENTS

1. Rewrite Questions 5 and 6 to a stronger senior-coordinator standard.
2. Preserve the candidate's core reasoning where it is sound, but improve clarity, operational realism, defensibility, and direct alignment with the assessment.
3. Write in plain professional English suitable for a Nigerian public-health and government-partner context.
4. Avoid generic management language, inflated claims, repetition, and academic phrasing.
5. Every direct question must be answered explicitly.
6. Make the answers defensible in a 45-minute technical walkthrough.
7. Do not invent facts, assessment results, organisations, tools, or campaign procedures not supported by the scenario.
8. Keep Question 5 within three pages.
9. Keep Question 6 within six pages excluding annexes.
10. Use concise paragraphs, tables where they improve scanning, and clear section headings.
11. Do not add citations unless already supported by the assessment material.
12. Do not include drafting notes, comments, tracked changes, or placeholders in the final documents.

DOCUMENT DESIGN

Apply consistent professional formatting across all three documents.

Use an eHealth Africa-inspired visual style:

- Primary heading colour: dark eHA blue, approximately RGB 0, 92, 153 or hex #005C99.
- Secondary accent colour: lighter blue, approximately RGB 38, 132, 181 or hex #2684B5.
- Body text: black or very dark grey.
- Use blue only for headings, table headers, section dividers, and restrained emphasis.
- Do not overdecorate.
- Use a clean professional font such as Aptos, Arial, or Calibri.
- Body text: approximately 10.5 or 11 pt.
- Main title: approximately 16–18 pt.
- Section headings: approximately 12–14 pt.
- Use consistent paragraph spacing.
- Use page numbers in the footer.
- Include the candidate name and question title in a restrained header.
- Ensure tables do not split awkwardly across pages.
- Repeat table header rows where a table continues.
- Keep margins suitable for the stated page limits.
- Remove excessive blank space.
- Ensure the documents remain readable when printed in black and white.

QUESTION 5 — COORDINATING DELIVERY THROUGH THE ROUND

Rewrite the answer around the six direct requirements.

Open with a concise framing paragraph explaining that the first 24 hours are sequenced according to:

- risk to live delivery;
- reversibility;
- compounding data damage;
- reputational exposure;
- dependency between actions.

Add a prominent table titled:

"First 24-Hour Response Sequence"

Use columns similar to:

- Time window
- Action
- Lead
- Immediate output
- Reason for sequence

The sequence must cover at least:

0–1 hour:
- activate incident coordination;
- acknowledge the state discrepancy;
- preserve evidence;
- place controlled restrictions on settlement-layer editing rather than blindly shutting down all campaign operations.

1–3 hours:
- assign separate leads for database integrity and coverage reconciliation;
- capture database snapshots, logs, affected records, and source files;
- identify whether the duplicate issue could affect the reported coverage figure.

2–4 hours:
- issue a factual holding update to national stakeholders;
- state that a discrepancy exists;
- state its known magnitude where available;
- state that reconciliation is underway;
- avoid endorsing either figure prematurely.

3–8 hours:
- reconcile definitions, denominators, reporting cut-off, geography, source records, duplicate influence, and late submissions;
- document the root-cause decision tree.

4–10 hours:
- begin structured handover with the two departing analysts;
- protect tacit operational knowledge, credentials, scripts, local contacts, pending issues, undocumented workarounds, and state-specific risks.

8–16 hours:
- establish temporary state coverage;
- reassign responsibilities;
- confirm decision rights and escalation thresholds;
- protect the daily EOC product.

16–24 hours:
- publish a reconciled figure if defensible;
- otherwise publish a clearly labelled provisional figure with uncertainty and next update time;
- confirm partner-report recovery plan;
- acknowledge the counterpart training request without committing prematurely.

State clearly what is deliberately not done first:

- no immediate deletion of duplicate records;
- no rollback before preserving evidence;
- no premature declaration that the state or central figure is correct;
- no personal takeover of every technical task;
- no immediate commitment to training dates before resource implications are understood.

For the authoritative coverage figure:

- define a controlled, reproducible figure-of-record process;
- make clear that "authoritative" means governed and reproducible, not automatically correct;
- specify the agreed denominator, geographic unit, reporting cut-off, source hierarchy, validation status, and version;
- show how the state figure and central pipeline are reconciled;
- include a short root-cause table if space permits.

The root-cause assessment should consider:

- denominator mismatch;
- different settlement masterlists;
- reporting cut-off differences;
- late or duplicate submissions;
- duplicate settlement records;
- aggregation or join errors;
- geographic misclassification;
- manual spreadsheet changes;
- state-side transcription errors;
- pipeline defects.

Communication while the cause is unknown must distinguish:

What can be claimed:
- a discrepancy exists;
- the figures being compared;
- the scope of the reconciliation;
- the time of the next update;
- whether operational decisions should be paused or treated cautiously.

What cannot yet be claimed:
- which side is wrong;
- whether the database duplication caused the discrepancy;
- whether campaign performance changed;
- whether any person or team is responsible.

For concurrent spatial editing:

Use a practical architecture the candidate can defend. Prefer:

- PostgreSQL/PostGIS as the authoritative database;
- controlled role-based editing;
- immutable UUID primary keys;
- database constraints;
- staging or branch tables for proposed edits;
- row-level audit history;
- transaction-based merges;
- conflict detection based on feature ID, geometry, attributes, timestamps, and editor;
- automated pre-merge validation;
- named reviewer approval for conflicts.

Do not depend entirely on GeoGig unless the document explains its operational fit and maintainability. A PostGIS-native controlled editing workflow is acceptable and may be easier to defend.

Explain:

- unique identifier strategy;
- prevention of duplicate creation;
- conflict detection;
- conflict resolution;
- versioning;
- rollback;
- audit trail;
- offline or intermittent connectivity considerations;
- merge approval.

For data-quality controls, use a two-column or three-column table separating:

Blocking rules:
- missing or duplicate UUID;
- invalid geometry;
- invalid CRS;
- broken foreign key;
- exact duplicate;
- required attribute missing;
- impossible coordinate;
- unauthorised schema change.

Review flags:
- near-duplicate settlement;
- large geometry movement;
- settlement outside declared ward;
- unusual population change;
- name similarity;
- edit outside expected campaign window;
- two users modifying the same feature;
- possible boundary mismatch.

Explain why objective structural errors block submission, while plausible field corrections are flagged for human review.

For the handover:

Make clear that ten days is not used for a generic knowledge dump.

Protect first:

- active campaign responsibilities;
- current unresolved incidents;
- scripts and workflows;
- credentials and access ownership;
- state and LGA contacts;
- local escalation routes;
- undocumented exceptions;
- data-quality risks;
- daily product production steps;
- partner-report inputs.

Use:

- structured handover checklist;
- paired shadowing;
- recorded walkthroughs where permitted;
- shared documentation;
- transfer of ownership;
- rehearsal by the receiving analyst;
- sign-off on critical tasks.

State what can be accepted as incomplete:

- cosmetic documentation;
- historical files with no operational relevance;
- personal working preferences;
- low-risk backlog items.

For delegation:

- assign named workstream leads;
- define decision rights;
- define escalation thresholds;
- use daily short coordination checkpoints;
- supervise through automated controls, peer review, exception reports, and sampled quality checks;
- avoid personally reviewing every edit and every output.

End Question 5 with a concise paragraph connecting the incident to structural fragility:

The immediate response contains the crisis, but the deeper lesson is that delivery should not depend on knowledge held by two individuals. Documentation, cross-training, version-controlled workflows, shared ownership, and demonstrated backup capability are required to prevent recurrence.

QUESTION 6 — BUILDING CAPABILITY IN THE COUNTERPART AGENCY

Rewrite the answer around all seven direct requirements.

Section 1: Interpret the evidence

Explain:

- mean composite score of 36/100 indicates weak applied capability;
- mean objective score of 57% indicates partial knowledge but inconsistent practical performance;
- correlation of 0.11 means confidence cannot be used as a reliable proxy for competence;
- near-universal demand across all topics is not sufficient for curriculum prioritisation;
- individual self-ratings should not be used publicly to rank or embarrass staff;
- first-day facilitation should establish psychological safety without hiding the evidence;
- baseline findings should be presented in aggregate;
- individual results should be private;
- practical demonstration should determine grouping and support.

State clearly that zero software access is the binding constraint.

Explain that:

- training without continued tool access will decay;
- QGIS installation, device readiness, permissions, sample data, storage, and technical support must be resolved before or at course start;
- software access alone is insufficient without practice, supervision, and real work;
- QGIS is preferred because it is free, open source, and maintainable;
- any department IT restrictions or reimaging policies must be addressed.

Section 2: Competency framework

Create a compact table with operational levels.

Use four levels with observable behaviours:

1. Assisted execution
2. Independent standard execution
3. Adaptive execution
4. Review and workflow ownership

Apply the levels across domains such as:

- data handling and quality assurance;
- reproducible documentation;
- cartography;
- basic spatial analysis;
- communication of results;
- workflow ownership and peer review.

Avoid generic beginner/intermediate/advanced language.

Each level must be observable and assessable.

Section 3: Five-day course

Create a detailed table with columns:

- Day/session
- Learning outcome
- Cognitive level
- Practical exercise
- Dataset
- Duration
- Delivery method

The course must include approximately 75–80% hands-on work.

Use this sequence:

Day 1:
- baseline practical assessment;
- QGIS installation and environment setup;
- file types, layers, CRS, attribute tables;
- opening and checking a real departmental dataset.

Day 2:
- data cleaning;
- validation;
- duplicate detection;
- coordinate checks;
- documenting a reproducible cleaning workflow.

Day 3:
- cartography;
- classification;
- symbology;
- labels;
- layout;
- projection;
- production of a decision-ready map.

Day 4:
- basic spatial analysis;
- joins;
- buffers or proximity;
- interpreting results;
- stating limitations;
- producing a short technical output.

Day 5:
- independent capstone;
- peer review;
- communication to a non-technical manager;
- post-assessment;
- individual development actions;
- launch of the 90-day application plan.

Every session must state:

- learning outcome;
- practical task;
- dataset;
- duration;
- instructional method.

Section 4: What is not taught

Explicitly exclude:

- spatial statistics;
- remote sensing;
- web mapping;
- Python or R automation;
- advanced database administration;
- machine learning;
- advanced network analysis.

Explain that these are deferred because:

- the cohort has not yet demonstrated foundational capability;
- the five-day window is limited;
- software access and reproducibility are more urgent;
- shallow exposure would not transfer into reliable work.

State the conditions for a later Phase 2.

Section 5: Full 90-minute session

Retain and improve the session:

"From a Messy Settlement List to a Documented, Reproducible Workflow"

Include:

- facilitator guide with timings;
- participant brief;
- dataset specification;
- expected outputs;
- model answer;
- scoring guide;
- common errors;
- facilitator interventions;
- materials required;
- completion criteria.

Ensure the dataset is realistic for Nigerian administrative and public-health data.

Use defects such as:

- inconsistent LGA and ward names;
- duplicate records;
- transposed coordinates;
- points outside Nigeria;
- missing values;
- sentinel value confusion;
- unexpected population values;
- inconsistent column names.

Do not silently delete records.

Section 6: Pre/post assessment

Use the same practical assessment at baseline and endline.

Measure demonstrated capability, not confidence.

Use observable tasks and a consistent rubric.

A suitable scoring system is:

- 0: cannot complete;
- 1: completes with substantial prompting;
- 2: completes with minor prompting;
- 3: completes correctly and independently;
- 4: completes independently and explains or checks the result.

Include tasks across:

- loading data;
- identifying CRS;
- detecting invalid records;
- correcting and documenting a record;
- producing a reproducible log;
- choosing classification;
- choosing projection;
- creating a complete map layout;
- running a join or buffer;
- interpreting limitations;
- peer-reviewing an output;
- communicating results.

Explain comparability, assessor calibration, timing, and pass thresholds.

Section 7: Ninety-day plan

Create a table covering:

- period;
- activity;
- owner;
- evidence;
- success measure.

Use phases such as:

Days 0–14:
- confirm software access;
- resolve IT restrictions;
- assign mentors;
- identify real departmental workflows;
- publish templates and SOPs.

Days 15–30:
- first supervised departmental assignment;
- weekly office hours;
- review against competency framework.

Days 31–60:
- second assignment with less support;
- peer review;
- documentation audit;
- identify emerging internal champions.

Days 61–90:
- independent capstone on real work;
- reassessment;
- review of retained skills;
- assign workflow ownership;
- identify Phase 2 candidates.

Capability transfer must be measured through:

- independently completed real tasks;
- reproducible logs;
- reviewed outputs;
- reduced correction rates;
- successful peer review;
- continuity during absence;
- work delivered without external rescue.

Do not use attendance, satisfaction, or certificates as the primary success measure.

End Question 6 by linking capability building to institutional resilience:

The programme is not only a training intervention. It is a mechanism for distributing knowledge, documenting workflows, creating backup capability, and reducing dependence on individual experts.

QUESTION 7 — CONNECTING COORDINATION RESILIENCE AND CAPABILITY DEVELOPMENT

Create a separate response titled:

Question 7 — Connecting Coordination Resilience and Capability Development

Target length: 500–700 words.

Make the argument directly.

Cover:

1. The two resignations are an immediate staffing problem, but the delivery threat reveals a pre-existing institutional design problem.
2. Critical knowledge, access, local relationships, procedures, and decision authority were concentrated in a small number of people.
3. Emergency handover is necessary but reactive.
4. Structural resilience comes from:
   - documented SOPs;
   - reproducible workflows;
   - shared repositories;
   - version control;
   - audit trails;
   - cross-training;
   - role rotation;
   - peer review;
   - backup ownership;
   - observable competency standards.
5. The counterpart agency faces the same problem at institutional scale:
   - dependence on external experts;
   - weak access to tools;
   - limited demonstrated practical capability;
   - weak reproducible documentation.
6. Question 6 addresses that risk by transferring work into institutional routines and real departmental practice.
7. Documentation alone is insufficient if staff cannot understand, execute, adapt, and review the process.
8. Training alone is insufficient if the process remains undocumented and person-dependent.
9. Capability and documentation must reinforce one another.
10. The goal is not to make every staff member interchangeable.
11. The goal is to remove avoidable single points of failure while retaining specialist expertise and accountability.
12. Capability building cannot eliminate the operational effect of two resignations.
13. Throughput, contextual knowledge, and relationships may still decline.
14. Recruitment and workload adjustment may still be required.
15. The defensible claim is that institutional capability reduces the likelihood that normal staff movement becomes a delivery failure.

End with this conclusion in substance, but improve the wording:

The controls in Question 5 contain the immediate incident. The competency framework, practical learning, reproducible documentation, peer review, and ninety-day application plan in Question 6 reduce the likelihood of recurrence. Together they shift delivery from dependence on particular individuals toward accountable institutional capability.

FINAL CHECKS

Before saving:

- verify every direct requirement in Questions 5 and 6 has a visible answer;
- verify the Part 3 structural connection is explicit;
- verify Question 5 remains within three pages;
- verify Question 6 remains within six pages excluding annexes;
- verify Question 7 is concise and non-repetitive;
- verify tables fit the page;
- verify headings use the blue theme consistently;
- verify no unsupported factual claims were added;
- verify no tracked changes or comments remain;
- verify the Word files open correctly;
- report only:
  - files created or modified;
  - page count of each;
  - major structural changes;
  - any requirement that could not be satisfied.
