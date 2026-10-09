# Independent practical case review

Verdict: **PASS for the four local prototype cases, source/download integrity and mapped coverage contracts.** Four independent entrypoints exited zero. All 22 source/config files match authored case JSON; embedded HTML case/coverage/runtime parity and all four ZIP round-trips pass. No unresolved implementation blocker found within the declared local scope. Broader production guarantees remain explicitly outside that scope.

Final HTML: 1,964,659 bytes, SHA-256 `403cd4c6e9f89163d4eaccc70434c53740fbfacfdc6c0318010544d4e6116065`. Full independent receipts and per-file fingerprints: `output/practical-validation.json`.

## What independently executed

| Case | Observed execution | Scope |
|---|---|---|
| Modernization | 8 unittest methods pass; actual Java compile/runtime gates exercise 43 behavior checks | Exact audited PricePolicy fixture, owned temporary workspace, source/input/patch-bound approval and in-process replay |
| MCP | Separate client/server subprocesses exchange JSON-RPC; lifecycle/schema/path/role/error negatives pass | Read-only legacy 2025-11-25 subset, trusted launcher fixture role; no HTTP/OAuth/current-revision conformance |
| Enterprise | Actual Spring Boot → FastAPI loopback HTTP, scoped evidence, strict output enums, rejected writes, concurrent duplicates, persisted replay, restart and outage | Prepared Python packages, JDK and cached offline Maven; temporary SQLite ends with 3 tickets/3 commands/3 pending outbox rows |
| Evaluation | Tenant-filtered lexical retrieval, support/security/cost gates, undefined all-abstain denominators, SQL traces and pilot arithmetic | Synthetic candidate outputs/labels/timings/prices; no live model quality or causal adoption result |

`python3 offline-reference/validate_practical_cases.py --execute` ran all four from JSON-provided files copied into separate temporary directories. Framework dependencies were already prepared; Maven ran with `-o`. Only the enterprise harness opened loopback HTTP sockets. No model, bank, cloud service, learner storage, real repository mutation, Git commit or package provisioning was used. These receipts describe independent reviewer execution; case execution summaries describe the reference author's runs. Neither marks a learner's implementation complete.

## Integrity and coverage

Validator checks exact case IDs, substantive explanations, assignments, follow-ups, hints, primary source provenance shape, linked day bounds, safe nested archive names, duplicate paths, Python syntax/imports and exact code/download inventory. It checks all 154 unique coverage rows (45 revised JD requirements, 15 modernization patterns, 22 ML clusters, 72 platform topics), 17 gap rows and references to actual days, JD lessons, scenarios, client questions, lab files and cases. Degree/professional-experience rows correctly remain credential requirements with no invented course day. .NET remains adapter planning; TensorFlow, production cloud operation and actual platform integrations remain external/design/experience boundaries where appropriate.

`--html --zip` independently checked final payload/runtime parity, executed the exact practicalZip JavaScript function in Node, then read each archive with Python zipfile. All CRC checks, nested file lists and UTF-8 source bytes match: modernization 9 files, MCP 2, enterprise 10, evaluation 1. No archive extraction or learner browser storage access was needed.

## Findings resolved

- Enterprise card ID initially differed from its mapped coverage references. Author aligned it to `case-enterprise`, and all mapped links now resolve.
- Enterprise README claimed its request timeout plus size-limited read prevented indefinite waiting. Source at `case-code/enterprise/EnterpriseGateway.java:46` and `:63` uses ofInputStream before later readNBytes. The [JDK streaming-body contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.net.http/java/net/http/HttpResponse.BodyHandlers.html#ofInputStream()) does not make body materialization complete when the response object arrives. Author corrected `case-code/enterprise/README.md:48` and the case limits: post-header reads have no enforced total body deadline, which remains a production extension. No stalled-body integration test or full timing guarantee is claimed.

## Review boundaries

The modernization graph is lexical class-reference candidates with explicit gaps, not resolved Java calls. One-file replacement is atomic within its fixture; approval/replay state is process-local and does not claim restart, hostile-process race or multi-file safety. MCP annotations do not enforce authority; the actual server role/path policy does. Evaluation checks authored claim annotations, not unrestricted semantic truth. Enterprise fixed tokens and keyword classification are test fixtures; its local SQL outbox has no external dispatcher or exactly-once remote effect. Containers/Kubernetes manifests are authored designs, unbuilt and undeployed. Initial framework setup needs an approved package/artifact cache for completely offline provisioning; the static tutorial itself remains locally bundled. Python/Java execution requires a local runtime outside the browser.

Schema/length checks and mapping links do not certify professional proficiency, production operation or interview success. AST guards/temp directories are not an OS sandbox. Parent owns browser interaction/keyboard/viewport/offline/storage and downloaded-browser ZIP tests; those results are separate from this independent execution/source review.

## Current source fingerprints

| File | SHA-256 |
|---|---|
| case-modernization/fixtures/after/BehaviorProbe.java | 5b300d99b0028793ba73579032dd7895f5bcc2a5ccd0ba52c13fa1226ecfa70d |
| case-modernization/fixtures/after/InvoiceService.java | 455438c2368d0e616763e15ba0060d424ac8f166fa95d8f0fa5fe4f7ccbce919 |
| case-modernization/fixtures/after/PricePolicy.java | 6fe0938b694cb986d68ee5e0801ee99c519dff75e16ac229d99660823b2318e0 |
| case-modernization/fixtures/after/ReceiptApi.java | c3b077a742b1746c9159902174ff207a6e2a5aec606efd21b42ea7bd8c48dbcd |
| case-modernization/fixtures/before/BehaviorProbe.java | 5b300d99b0028793ba73579032dd7895f5bcc2a5ccd0ba52c13fa1226ecfa70d |
| case-modernization/fixtures/before/InvoiceService.java | 455438c2368d0e616763e15ba0060d424ac8f166fa95d8f0fa5fe4f7ccbce919 |
| case-modernization/fixtures/before/PricePolicy.java | 80fac5c4f2cbdbb53262bd25f2fbdd95b451cf475889d7254cc6c06d5b0ead02 |
| case-modernization/fixtures/before/ReceiptApi.java | c3b077a742b1746c9159902174ff207a6e2a5aec606efd21b42ea7bd8c48dbcd |
| case-modernization/modernization_case.py | 51d107cc1de895ff06018be7070c82145abb267624c92d2ccb602c87a730fa1b |
| case-mcp/client.py | 19fdb0991efdb4054bff097c39bc6577ece3eb96accec3e3a20af5b0e09442d8 |
| case-mcp/server.py | 6f7e65a0c6cf3d5ca5964aa658c7fc0618ab6d01723dc652ff410360650f3a24 |
| case-enterprise/README.md | 4bf4c5435e38eb303b1b5fd9a4cef4ca26194a46c5e73010c322fa4a4cebb0b2 |
| case-enterprise/pom.xml | 3b91b191df26f984c47e7e308443478842126710fc6c335374c562260108a9b4 |
| case-enterprise/EnterpriseGateway.java | 47a986246b2068006cbe6b195d7bc888336b9d9bee17b8f779587091a1fa5a2d |
| case-enterprise/python_service.py | 28f623a052b60e59403cee8df069b9466d3549f3db8952770b438d5b16412f1d |
| case-enterprise/seed_sources.json | d212b91ec2fa65431b0036e8729c25841105478c63e786e795d820c22114af0e |
| case-enterprise/requirements-tested.txt | 744a4e51ac762d306dd0e7c3d66e122dbee294fc5c466d354bf4c0f02e75a5c7 |
| case-enterprise/integration_test.py | 9e933e70cfc73136f3b07a716c0b286d6153a7babcd1d976181212747260ea6b |
| case-enterprise/Dockerfile.python | ccc501ba16b9831dd9ea9c7300a8f7f3441382c30afdc4c69b447ea46ddbb251 |
| case-enterprise/Dockerfile.java | bbd4cd48bfea5a3995b4fc00bf0d5f32035c63e40502442a3d9bb8933a6c2655 |
| case-enterprise/deployment-exercise.yaml | 91074d0e2e0402a332b7452ce3a56b614cbf3e89cc28cee42e9ea872ef1e2861 |
| case-evaluation/evaluate.py | 48be32e91ee927cb49d80c55293c0c66abb68f297159744415ce1be75a4be319 |
