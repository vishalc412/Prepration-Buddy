# Independent offline curriculum QA

Historical review of the 7 October 14-day/six-hour edition. Schedule and coverage counts below are superseded by the 8 October 30-day/four-hour client-curriculum review in `output/client-curriculum-review.md`. They are not current acceptance evidence.

Verdict: **PASS for reviewed offline content, repaired reference mechanisms and static integration.** Review performed 7 October 2026. Only this report was written; source files and browser storage were not changed.

## Corrected mechanisms — verified

- **Day 11 trusted approval/receipt binding fixed.** `offline-reference/day11_adversarial.py:19` compares each request field against independent `TRUSTED_REVIEWED_ARTIFACT`; lines 25–31 require trusted issuer, executed status, approved artifact and valid signature. Independent tests reject equal attacker-chosen hashes, valid-signature failed receipts and valid-signature wrong-artifact receipts. Built-in harness now passes 15/15 negative fixtures. Request identity still represents a toy authenticated context; production authentication and OS isolation remain explicitly outside this example.
- **Day 14 failed/unknown critical boundaries block readiness.** `offline-reference/day14_assessment.py:24` records failures, lines 25–27 flag unknown names as unresolved, and line 37 requires no failures or unresolved boundaries. Independent complete fixture passes only with all 17 scores/evidence and four known passed boundaries. Added unknown boundary with failed, unassessed or passed state blocks readiness. Built-in tests also cover every missing or failed known boundary. Revision allocation remains exactly 360 minutes.
- Corrected downloadable Day 11 and Day 14 code equals corresponding `labs.json` file code. Final HTML rechecked after parent reembedding: all three JSON objects and teaching engine match source; all 16 embedded reference files match downloadable code.

## Smaller corrections — verified resolved

- Lab library now derives a filtered `labs` list and uses the same list for matching count and rendering in `offline-reference/offline-teacher.js` and embedded HTML.
- `index.html:293` rejects boolean, whitespace-only, absent, nonfinite and out-of-range imported scores. Executed exact extracted validator through Node: 10 invalid fixture values rejected, six numeric/numeric-string valid fixtures accepted. No browser storage used.
- `README.md:7`–11 describes default Study mode, local teacher, six active hours and optional external coaching.

## Passed static checks

- Embedded `OFFLINE.answers`, `OFFLINE.lessons`, `OFFLINE.labs` equal their local JSON source data exactly.
- Every embedded reference file equals its downloadable local source: 16 files across 14 labs.
- Answer coverage: 30 baseline, 70 daily (five per day), 14 designs and 12 final rounds = 126 interview/design answers.
- Detailed lesson coverage: 70 modules across Days 1–13; every module has three quiz options, an in-range integer answer and three hints = 70 quizzes and 210 progressive module hints. Day 14 uses final simulation and assessment.
- Six teaching blocks total 360 active minutes: 30 + 75 + 45 + 105 + 60 + 45. Fourteen days total 84 planned active hours.
- No required fetch, XHR, WebSocket, EventSource, remote script, dynamic import or external stylesheet found in workbook. Favicon is inline data. Source links are optional further reading. Python tokenizer path explicitly requests `local_files_only=True`.
- Implementation scope remains Python and Java. .NET appears as a target ecosystem handled through Python adapters and dry-run plans; no C# curriculum or fabricated .NET migration success.
- Hints/search/quiz feedback explicitly identify prewritten or deterministic behavior. Essay/code scores remain self-assessed. No semantic essay grading, hiring guarantee or execution proof inferred from reading/checking boxes.
- Reviewed numerical teaching examples: Bayes alert prevalence, absolute/relative change, FP/FN costs, attention matrix dimensions, KV cache memory, LoRA parameter count, token budgets, Little’s law and error budget calculations are consistent with stated assumptions.
- Source-sensitive facts remain bounded: capability mapping avoids asserting current cloud availability/prices; OpenRewrite described as semantic-tree tooling, not universal behavior proof; NIST AI RMF categories do not claim compliance certification.
- Reference lab limits identify synthetic model data, lexical retrieval, mock gateway quality, architecture-only cloud plan, same-installed-JDK compiler target comparison and untested deployment boundaries.

## Execution evidence and limits

Executed standard-library entrypoints using their local fixtures: Day 7 retrieval, Day 8 workflow (temporary directory), Day 9 lineage, Day 10 quota simulator, Day 11 adversarial tests, Day 13 capacity and Day 14 assessment. All built-in assertions passed. Independent counterexamples originally exposed failures absent from the built-in assertions. Corrected Day 11/14 now reject those counterexamples and include expanded regression fixtures.

No live browser tests performed by this reviewer. No external repository, cloud API or model API accessed. No package installation attempted. NumPy/Pandas, scikit-learn, Torch, FastAPI, Transformers/local tokenizers, gateway process timing and actual Java compile/run require separate execution reports; this review does not certify them. Parent agent owns integration/browser validation.
