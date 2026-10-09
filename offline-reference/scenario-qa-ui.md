# Independent scenario UI review

Review date: 7 October 2026. Scope: usability, state preservation, answer access, completion invalidation, navigation and mobile semantics. Reviewer did not edit shared UI code or learner storage. Source review is not a screen-reader or WCAG certification; parent owns isolated browser/visual checks.

## Findings and repair evidence

1. **P2 — Numeric constraints hidden; repaired.** Original scenario detail and downloaded brief omitted `s.constraints`. The new Understand step renders the list and the brief now includes a CONSTRAINTS section. A focused Node rendering assertion confirmed an authored numeric constraint appears in the simplified detail output.
2. **P2 — Restored completion contradicted evidence; repaired.** `scenarioStatus` and original verification statistics now require the completion declaration and `scenarioVerified(s)`. A focused execution fixture restored only the declaration and observed `Ready to start`; after adding code, evidence and all checks, it observed `Verification recorded`. Editing code then removed checks and the declaration.
3. **P1 — Worked solution crashed outside Review; repaired.** The staged UI originally rendered reference details only in Review while showing the solution button everywhere. Executing the click handler reproduced `TypeError: Cannot set properties of null (setting 'open')`. The repaired handler changes to Review and rerenders before querying the reference. Focused event-handler fixtures passed from Understand, Answer and Build. Phase persistence was subsequently added by parent and is included in the browser verification boundary.
4. **P2 — Resource/index discovery gap; reported to parent.** Scenario cards in the answer library and raw teacher-search result details bypass the resource-wrapped answer functions. Those cards initially lacked watch/read links; the library's generic studio link also did not select the referenced case. Parent owns resource attachment and case-specific routing repairs. Check the final integrated browser path before declaring every content surface has topic resources.

## Source paths already checked

- Typed answer, twist, code and evidence drafts use existing synchronous `data-map` input persistence. Scenario selection, hint reveal, filtering and navigation call render only after input events have saved current text. No source-level draft-loss mechanism found in these paths.
- Code edits clear all scenario acceptance checks and the completion declaration. Evidence/check edits clear the declaration. The completion button requires nonempty code, nonempty evidence and all checks.
- Study mode makes answers available without an attempt; Practice mode requires a nonempty attempt and Compare. Clearing a Practice answer hides its support and clears the review flag.
- Search keeps its own focus and caret after render. Track/kind/level changes and hint reveal rerender their triggering controls; keyboard focus restoration needs browser verification.
- Selection falls back to the first filtered scenario. Empty results show an explanation and keep Clear filters available. All scenario selection controls have `aria-pressed`; filter controls have labels; draft fields have explicit labels.
- Answer/reference details preserve open state through captured toggle events. Downloaded Python text comes from embedded authored files; no network/model call is introduced by reference reveal.

## Simplified UI source review

Reviewed `offline-reference/simple-ui.js` after creation. Four primary destinations are Home, Learn, Practice and Review. Existing tools remain inside native keyboard-operable details/summary navigation; active secondary views open that drawer. Existing `go` focuses the main application, and scenario phase selection focuses the active case section with tabindex -1.

Practice now shows one phase at a time: Understand, Answer, Build/Design and Review. Phase changes persist before render, while drafts continue using the existing synchronous input handlers. No source-level loss of typed draft data found through phase switches, case selection or hint rerenders. Advanced filters retain stored values and Clear filters remains visible when no rows match. The render chooses the first matching case if the stored selection is excluded.

Optional resources are plain external anchors, with no embedded video, dynamic fetch or model dependency. Their labels explain that links need online access while built-in teaching stays offline. Modules, baseline/daily/final answers, lab solutions, designs and active scenarios receive subject links through wrapper functions.

Mobile source styles use wrapping case-step buttons, a single-column scenario layout below 1050px, three-column lesson steps below 1150px and one-column help cards below 760px. This is source-level intent, not visual proof. Parent isolated browser checks should cover measured overflow, draft persistence, reference opening from all phases, filter emptiness, Study/Practice answer access, verification invalidation and keyboard focus after rerenders. Search explicitly restores caret; filter/hint controls may still require focus restoration to avoid restarting keyboard traversal.
