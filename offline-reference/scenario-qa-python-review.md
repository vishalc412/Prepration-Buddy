# Independent Python and framework scenario review

Status: PASS for authored scenario structure, code/reference parity and stated local runtime contracts. Production behavior remains bounded by the explicit limitations below.

## Python and Async Python evidence

- 12 distinct scenarios, 24 authored suggested answers, 36 progressive hints and 6 implementation assignments.
- Six scenarios per track; first three of each track contain executable references; final three are question/design/debug exercises.
- Every answer has at least 100 words; every solution has at least 120 words. Each scenario includes numeric constraints, at least four requirements/acceptance checks, at least two pitfalls and a changed-constraint follow-up.
- JSON/code-on-disk parity and AST parsing passed for every reference.
- All six reference self-tests passed on Python 3.14.7, using only standard-library APIs available in Python 3.11+.
- Checks cover CSV quarantine/accounting/header failure; exact Decimal per-line rounding/replay conflicts/invalid input; stable-key ambiguous retry/permanent rejection/budget exhaustion; bounded worker/queue accounting/expected and unexpected failures/external cancellation; timeout versus external cancellation/resource release; same-key coalescing/cancelled waiter/capacity/failure retry/shutdown/new-work rejection.
- Large-input memory, production throughput, durable distributed idempotency, real external side effects and semantic model quality are explicitly outside execution evidence.

## Framework source and runtime review

Nine framework reference self-tests passed independently using `/private/tmp/principal-scenario-validation/bin/python` (Python 3.12 runtime). They cover FastAPI validation/tenant identity, SQLite replay/restart, lifespan work bounds; Django tenant-scoped ORM, atomic order/outbox, N+1 query budget; Flask app isolation, bounded uploads, signed webhook replay.

Resolved findings:

1. Malformed non-ASCII webhook signature now fails strict 64-character ASCII-hex validation and returns 401. Independently re-ran the original `é` reproduction and all webhook assertions.
2. Django outbox receipt now says transaction-committed. Assignment limits explicitly state in-memory SQLite commit/rollback and constraint evidence, with no process-crash/restart durability claim. Durable outbox is the design target; restart durability remains an implementation follow-up.

Framework JSON final checks passed: 18 distinct scenarios; six per framework with exactly first three executable; all authored-answer/solution minimums; embedded file parity; complete main-command files; the FastAPI jobs helper is bundled. Every assignment bundles the full tested requirements file, and every package pin matches the isolated runtime. All nine reference self-tests passed again after repairs. Initial dependency setup can require internet or a wheel cache; static HTML teaching remains independent. Current Starlette emitted a TestClient/httpx deprecation warning; tests still passed, and limits disclose it.

Source review confirms trusted fixture identities rather than caller tenant headers; tenant-qualified status/ORM lookups; changed-payload replay conflicts; database uniqueness/check boundaries; raw-byte signatures and freshness; bounded upload paths; explicit separation of volatile lifespan jobs from durable delivery. Concurrency, production database contention, actual OIDC/CSRF integration, remote effects, model quality and deployment throughput were not certified by these tests. Browser integration belongs to parent verification.
