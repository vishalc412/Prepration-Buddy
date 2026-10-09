# Independent scenario integration review

7 October 2026. Reviewed `scenario-studio.js`, `offline-teacher.js`, `simple-ui.js` and `embed_content.py`, with targeted checks of base state normalization and delegated input handling in `index.html`. No shared implementation sources edited.

## Repaired finding: independently rechecked

**P2 stale imported completion marker — fixed.** `scenarioStatus` now requires completion marker **and** current `scenarioVerified(s)`. Legacy verification count applies the same conjunction; the focused `simple-ui.js` list delegates status to repaired function and no longer displays a separate unguarded verification counter. Fresh VM reproduction with marker `yes` and blank code/evidence/checks returned `{verified:false,status:'Ready to start'}`. Adding nonempty code, evidence and all acceptance checks returned “Verification recorded.” Repair addresses the reported import inconsistency without treating declarations as authenticated execution proof.

Initial scenario repair and both subsequent cockpit/import repairs are independently confirmed by focused source and VM checks. No unresolved concrete blocker found in the reviewed paths. Browser validation remains separate.

## Checks and boundaries

- **Draft preservation:** scenario answers, code, evidence, checks and notes use existing version-1 maps. Generic input handler saves field value before later scenario handler invalidates completion. Scenario filtering, selection and new four-step pane changes do not clear drafts. VM empty-track fixture preserved saved answer while returning zero matches/current undefined.
- **Filtering/empty state:** combined track/kind/level/query/day predicates are bounded local filters. Empty result renders explicit no-match state; clear filters preserves stored work. Selected scenario falls back to first filtered result without rewriting old selection.
- **Study/Practice:** in-question suggested answers require an attempt plus explicit Compare in Practice and are available in Study. VM confirmed no-attempt Practice question reference hidden. Worked solution remains available directly before an attempt, as do deliberate answer-library references. This follows the existing study-library philosophy but is not strict closed-book enforcement; clarify if a stricter Practice contract is desired.
- **Completion invalidation:** code edits clear acceptance checks and completion; evidence/check edits clear completion. Assignment verification is explicitly a learner declaration, not automated code execution. Answer/twist changes do not invalidate code-verification state because they are not its prerequisites.
- **Offline boundary:** scenario filtering/search/hints and downloads use embedded data, Blob URLs and local state. No remote model, dynamic import or network request appears in scenario engine. Official-source and video links are optional external navigation. `learningLinks` renders ordinary HTTPS links and encoded topic-search links, not remote iframes or embeds; all 18 resource subjects currently contain HTTPS URLs.
- **HTML injection boundary:** learner text reaches `esc`; code blocks and source labels/URLs are escaped. Payload bundler converts `<` to `\u003c` and escapes Unicode line separators before inline script insertion. Tested draft `<script>alert(1)</script>` becomes escaped text. All sources in the 18 authored RAG/Agents/Evaluation scenarios are HTTPS. This checks known rendering paths; it is not a general XSS certification.
- **Bundling/state integration:** embed script asserts 48 unique scenarios, 24 assignments and flat filenames before writing HTML. Scenario dispatch is included in patched renderer; state key/version unchanged. Base input completion clearing receives NaN for scenario keys, but currently only deletes `done[NaN]` and does not interfere with scenario keys.

## Focused UI crossflow recheck

- Four scenario panes (`context`, `discuss`, `build`, `review`) rendered under VM fixture stubs with saved draft maps intact. Context includes optional constraints; adding `maximum 4 workers` fixture rendered that constraint. Download brief handler includes matching `CONSTRAINTS` section.
- `scenario-open-reference` handles absent details in Understand/Answer/Build by switching saved step to Review, rendering and then opening/scrolling reference details. VM event reproduction confirmed saved Review step and open reference. This repairs the cross-pane null-element hazard from moving the reference into Review.
- New scenario Discussion reuses original attempted-answer Compare gating and saved IDs. Build retains code/check/evidence map attributes so existing invalidation handlers still apply. Review preserves changed-constraint response and source/reference downloads.
- All six teacher panes rendered under fixture stubs; day/module/stage IDs remain compatible with existing handlers. Step/day/module controls persist existing notes; previous/next routes still lead to daily assessment. Actual DOM focus, scroll and timing behavior require browser checks.
- Resource wrappers append links into existing detail bodies while preserving base answer/module/lab content. Optional missing resource category returns empty links. Curated resource links do not alter offline content dependence or dispatch authority.
- Focused navigation runs after prior renderer and changes only navigation/crumb display. Existing sidebar/input/save handling remains in prior chain. More-tools expansion lives in notes and does not erase work.

## Reference content execution

18 authored scenarios meet track/assignment/depth schema. Nine Python standard-library programs parsed and executed in temporary working directory; all fixture cohorts passed: RAG 7/7/9, Agents 10/5/8, Evaluation 6/14/7. JSON code equals downloadable file bytes. Each reference states lexical/synthetic/simulated limits and does not claim real model quality or deployment.

## Remaining verification

Parent-owned browser checks must establish actual desktop/mobile layout, offline load, event behavior, search caret/focus, download contents, refresh persistence and Study/Practice controls. Node VM and source review do not establish those UI outcomes or certify reference code safe for arbitrary repositories.

## Final cockpit and import review

Additional read-only scope: current `cockpit.js`, `cockpit.css`, refreshed `simple-ui.js`, inline state import/normalization and timer dispatcher. No shared sources edited.

**P2 fractional imported routing indices — repaired and independently rechecked.** Original reproduction accepted `day:1.5` and `teacher-stage-1:"0.5"`, causing undefined course/block indexing and rendering `TypeError`. Current inline `normalize` truncates day before clamping; actual `teacherStage` and `teacherModule` truncate before their bounded clamps. Re-executing the original import reproduction now returns day 1 and stage 0 with valid course/block entries. Additional actual teacher helpers with `.5`, `2.9`, negative, `Infinity`, `NaN` and `999` note values return integers; focused teacher rendering succeeds across this fixture matrix. Import truncation repairs the identified renderer failure without asserting that arbitrary imported progress is authenticated.

**P2 Challenge Recall answer exposure — repaired and independently rechecked.** Focused Recall now calls `teacherRecallSupport`: Study permits references immediately, Challenge requires nonempty current answer. A later input listener updates the existing support container after the base answer-save listener. Targeted source VM checks pass for empty Challenge hidden, attempted Challenge unlocked, cleared attempt hidden again through the input event, and empty Study reference available. Deliberate library/search/solution references remain accessible by the documented review policy; this is not strict examination security.

**Recorded teacher step visibility — independently rechecked.** Recorded completion now adds a checkmark to the step name plus `recorded complete` in its small label. A `teacher-complete-7-0:"yes"` fixture renders `Recall ✓` and the explicit status. This remains a learner declaration; the timer does not establish learning or test execution.

Other final source observations:

- Cockpit mode buttons write existing `notes.studyMode` and render without resetting answers/code/evidence. Native selector is hidden from keyboard/accessibility tree, and focus returns to selected custom button.
- Focus session uses existing timer counter and interval. Start/pause/reset update rendered state; target change pauses and clears elapsed counter. Observer disconnects before reconnecting to current dial, avoiding accumulation across renders. Current CSS and timer observer both use `--focus-progress`, resolving the previously assigned variable mismatch. Typography and actual dial rendering require browser visual proof.
- Stopwatch elapsed ticks are transient, not exported progress or execution receipts; tab throttling/reload behavior is not certified by source review. Timer never marks skill or assignment completion.
- One-pane scenario routing preserves existing state IDs, Study/Practice Compare gate, code invalidation and reference-open fallback. Search-result scenario links explicitly select target, clear stale filters/day and open Answer pane.
- Resource wrappers keep original escaped content; source catalog currently uses HTTPS links and no iframes/fetches. Optional links require internet; authored curriculum remains embedded.
- Parent-reported browser/reference receipts were noted as supplied coordination evidence, not independently re-executed by this reviewer. Final browser behavior, keyboard layout and CSS repairs still require parent's final checks.

Final targeted recheck executed 7 October 2026 using `/private/tmp/review_import_indices.js` and `/private/tmp/review_final_guided_vm.js`. The latter includes current focused UI source plus DOM/content stubs; it is an event/rendering regression harness, not a browser or visual test. Shared implementation files remained untouched by this reviewer.

## User correction: Home mode feedback and requested app name

Read-only focused review on 7 October 2026. Before the parent change, actual cockpit mode listener changed `notes.studyMode`, saved, rendered, and restored focus; existing Recall/scenario answer gates consumed that state. Targeted VM execution recorded one save, one render, one focus, and preserved answer/code/evidence drafts. However, actual cockpit Home HTML was byte-identical in Study and Challenge because its final `overviewView` had no mode-dependent content. The perceived no-op was a visible Home feedback gap; no listener/persistence failure was demonstrated.

Parent repair independently rechecked with current source: Home now displays `STUDY / GUIDED LEARNING` or `CHALLENGE / ATTEMPT FIRST`, different explanatory text and a mode-specific primary CTA. Challenge's `drive-start-challenge` pauses and clears the timer, selects practice mode, sets the current day's teacher stage to Recall (`0`), saves and routes to Teacher. Starting from saved Example stage `2`, targeted event execution selected Recall and preserved all answer/code/evidence maps. Switching mode emits a clear feedback toast. Study retains existing teacher continuation behavior. The exact requested spelling/case `Prepration Buddy (OFFline and AI)` appears in document title and Home identity text.

Evidence: `/private/tmp/review_mode_home.js` reproduced original mechanism; `/private/tmp/review_mode_home_fixed.js` passed current mode-specific Home, Challenge Recall routing, timer reset, draft preservation, feedback and exact name checks. These are source/VM assertions with DOM stubs; parent browser tests establish visible styling, actual clicks, refresh persistence and device layout. No shared source edited by this reviewer.
