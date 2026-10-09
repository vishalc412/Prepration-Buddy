# Practical implementation plan and acceptance contract

8 October 2026. Four bounded vertical slices connect the revised JD to runnable Python/Java practice. This is the design contract; implementation and execution receipts belong to the assigned workers and parent. Proposed paths and PASS criteria below are not completion claims. Coverage is in `offline-reference/jd-coverage.json`. Existing guided days remain four hours; practical cases replace selected build/defend blocks or form optional separate sessions, not hidden extra mandatory hours.

Every case needs: problem and measurable acceptance; architecture/data flow; exact implemented boundary; a first-attempt assignment; worked implementation; negative tests; runnable commands; returned artifacts; limitations; and follow-up design questions with answers. Downloads preserve the complete multi-file structure. The browser saves learner drafts and evidence but does not execute Python or Java. A checked box is a learner declaration, not authenticated execution proof.

## case-modernization — Python-orchestrated Java modernization

Problem: a supplied Java fixture needs a deliberately supported modernization slice, with a reviewed change and behavioral parity. Python inventories only the allowed fixture root, records source revision/digest and parses declared build/dependency metadata. Analysis distinguishes observed metadata from supplied policy/advisory inputs; no guessed current versions or CVEs. A deterministic rule produces a bounded preview patch. Compilation and behavior assertions produce receipts tied to the exact reviewed input and output. Approval permits the declared local fixture change only after gates pass. A report explains evidence and untested boundaries.

Acceptance:

1. Happy path inventories the declared fixture, produces a reviewable change, compiles actual Java and runs documented behavior assertions.
2. Original and changed fixtures retain the specified behavior; the report lists the covered cases and actual runtime/compiler used. Compiler target comparison on one runtime is labeled accordingly.
3. Out-of-root paths, unexpected files, unsupported target/configuration and malformed dependency input fail closed.
4. Changed source or preview digest after review invalidates apply. A gate receipt for another artifact, failed gate or altered payload cannot authorize it.
5. A compile/test failure reports failure and prevents local apply; cancellation/timeout has an explicit bounded outcome.
6. Temporary files/processes are cleaned and unrelated user repositories remain untouched. No Git commit, push, package installation, cloud deployment or arbitrary fixture build script executes.

Evidence: worker command/result plus source fingerprints; report and gate artifacts; parent integration receipt. Primary anchors: day12 and `jd-accelerators`, `jd-context`, `jd-delivery-leadership`; agents-01/evaluation-06. Implement only the supported fixture transform. OpenRewrite, CVE/license scanners, cross-JDK source/runtime migration, .NET and real cloud release remain optional external extensions. The prototype is deterministic engineering automation, not a live LLM or general semantic modernization engine.

## case-mcp — Real stdio client/server subset

Problem: a client must discover and invoke narrow modernization tools/resources through an actual separate server process, with valid wire contracts and failure handling. Implement a declared subset pinned to **2025-11-25**: initialize/version agreement, initialized notification, tools/list/tools/call and resources/list/resources/read. The worked client validates JSON-RPC correlation/outcome and structured tool content. The server keeps stdout for newline-delimited protocol only, logs to stderr and exposes no arbitrary shell or filesystem operation. Client timeout/cleanup must end the fixture process predictably.

Acceptance:

1. A real launched client/server exchange initializes and returns the pinned revision; supported tools/resources are discovered and used.
2. Valid calls produce schema-valid structured content; domain errors use declared tool-error outcomes, while malformed methods/params use JSON-RPC errors.
3. Unsupported revision, request before required initialization, unknown tool/resource, malformed JSON, oversized message and invalid fields are handled without crash or unauthorized effect.
4. Request IDs correlate replies; protocol stdout remains parseable even while stderr contains logs. Client checks isError rather than treating a result envelope as success.
5. Trusted fixture identity/allowed roots constrain the operation; model-supplied fields cannot create grants. Do not label fixture identity OAuth.
6. The harness closes streams and terminates the subprocess on completion/error/timeout, retaining a sanitized transcript or assertions without secrets.

Evidence: real subprocess integration assertions, revision declaration and error fixtures. Anchors: `jd-mcp-contract`, `jd-mcp-security`, days8/9/29. **2026-07-28 current core is a design/compatibility extension, not implemented by this legacy subset.** Streamable HTTP, authorization-server discovery, PKCE, audience-validated OAuth, external SDK/client conformance and remote secure deployment remain unimplemented optional integrations. Claim only the actual tested subset; protocol version pinning is not a general conformance certification.

## case-enterprise — Java API and Python integration

Problem: a Java-owned application admits a tenant-scoped assessment job, stores state and returns a clear contract; Python consumes the API or performs a bounded analysis step. Use a real loopback HTTP exchange with actual Java compilation/execution. Keep controller/handler, service policy and repository/state responsibilities distinct even when dependency-free code is selected. Explicit statuses distinguish admission from completion. Fixed fixture tokens map to trusted tenant/principal context; untrusted body tenant cannot become authority. Show a browser/frontend contract and a TypeScript bridge assignment separately.

Acceptance:

1. Python starts or connects to the local Java server, submits a valid request, observes admitted/pending and retrieves a completed bounded result.
2. Missing/unknown credential, foreign task access, mismatched tenant, unknown enum, malformed/oversized payload and unsupported methods yield declared outcomes.
3. Same scoped replay key with exact intent returns the original result; changed intent under that key fails. A new key does not bypass a consumed authorization/approval policy.
4. A worker failure produces failed state rather than success; reported artifact identity matches the accepted task. Deterministic contention/version checks prevent a stale overwrite if state mutation is implemented.
5. If SQLite/outbox/restart durability is implemented, demonstrate atomic rollback and reopen/recovery with receipts. If storage is in memory, state that clearly and leave durability as a design extension rather than asserting it.
6. Listener binds loopback, has explicit time/request/resource limits and is shut down after the test. No production credentials, external API calls, cloud resource creation or package installation are required.

Evidence: actual HTTP requests/responses, negative assertions, Java compiler/runtime metadata and Python test result. Anchors: `jd-java-fullstack`, `jd-cloud-operation`, fastapi-01/02 and days9/12/29. A JDK HttpServer prototype is **not Spring Boot**, and fixture tokens are **not OIDC**. Spring controller/service/repository transactions, runtime JSON validation in an actual frontend, production TLS, distributed storage and Kubernetes/cloud operation remain separately scoped integrations. The supplied TypeScript bridge does not certify JS/TS professional proficiency.

## case-evaluation — Evaluation, tracing and pilot gate

Problem: an accelerator change appears cheaper but may lose critical quality. Build a Python local evaluation harness over explicit tasks, labels, candidate outputs and trace records. Evaluate retrieval/support correctness, scope failures, schema failures, abstentions and critical vetoes separately. Use paired task IDs so a candidate cannot omit hard cases. Calculate declared attempt/cost/latency statistics and cost per accepted task with defined denominators; source units are illustrative unless actually measured.

Acceptance:

1. Baseline/candidate task IDs and labels must align; duplicates, missing tasks, wrong tenant and malformed metric records reject the report.
2. An aggregate improvement cannot override a failed critical authorization/quality gate. Expected unsupported/missing evidence blocks the decision or requires explicit abstention.
3. Metrics include numerator, denominator and slices; zero denominators yield a declared unavailable state rather than a fabricated rate.
4. Retries count toward resource/cost totals. Distinguish supplied latency/cost values from measured execution and actual provider bills/tokens.
5. Trace records connect accepted task, stages, outcome and evidence identifiers without raw secrets. Missing required stages/receipts cannot become success through a model summary.
6. The adoption scorecard declares baseline/cohort/task-mix assumptions and expand/revise/stop rules. Illustrative data cannot establish causal productivity gains or a real team pilot.

Evidence: executable arithmetic/contract/critical-gate assertions and a generated local report. Anchors: `jd-evaluation`, `jd-delivery-leadership`, evaluation-01/02/03/06, days9/22/23/28. Fixed-output labels are not live LLM benchmarking; lexical evidence is not a genuine embedding model; a local trace is not a production OpenTelemetry collector; fixture prices are not current API rates.

## Integration and final boundary

Each worker supplies a reproducible run receipt and source fingerprints before coverage changes from planned to runnable local. Parent builds the case UI, multi-file downloads and navigation, then verifies offline startup, every case/link, saved learner drafts and rendering at narrow/wide widths. Final report lists actual accepted checks and unresolved optional integrations. No local receipt establishes cloud operation, security certification, professional tenure, degree, production adoption or a guaranteed hiring outcome.
