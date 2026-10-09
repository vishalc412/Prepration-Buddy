# Framework scenario research and execution evidence

Research checked 7 October 2026. Sources are framework-owned documentation. The eighteen case studies and business numbers are authored teaching fixtures, not claims about an actual employer or provider. Python implementation only; Java appears as an existing consumer or modernization boundary.

## FastAPI

- Pydantic request models supply request-body validation and documented schemas. The quote assignment adds strict integer quantities, bounds and forbidden extra fields; these are explicit application choices. [Request bodies](https://fastapi.tiangolo.com/tutorial/body/).
- Dependency injection supplies a replaceable authentication/policy seam. A trusted token-to-principal map is suitable for deterministic local fixtures, but does not establish production OIDC verification. [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/).
- Application lifespan owns startup and cleanup. Loop-bound queues and tasks in the reference are created there, then cancelled and awaited on exit. [Lifespan](https://fastapi.tiangolo.com/advanced/events/).
- Yield-dependency cleanup changed across FastAPI versions. Current documentation describes `Depends(scope="function")` support introduced in 0.121.0 and request-scope cleanup after the response; streaming resource ownership must be checked against the installed version. [Advanced dependencies](https://fastapi.tiangolo.com/advanced/advanced-dependencies/), [yield scopes](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/).
- TestClient supports direct application testing without a listening socket. Context-manager usage in the bounded worker assignment exercises lifespan entry/exit. [Testing](https://fastapi.tiangolo.com/tutorial/testing/).

## Django 5.2

- `transaction.atomic` groups database changes for commit or rollback. Catch database errors outside the atomic block rather than continuing queries within a broken transaction. [Transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/).
- `on_commit` runs callbacks after successful commit; a failed callback does not reverse that commit. It cannot replace a durable outbox row. Django `TestCase` wraps tests in transactions, so callback tests need `captureOnCommitCallbacks` or a transaction-aware alternative. [Transactions and callback tests](https://docs.djangoproject.com/en/5.2/topics/db/transactions/).
- Database `UniqueConstraint` and `CheckConstraint` express invariants across writers. The local outbox fixture tests tenant/request uniqueness and positive quantity. [Constraints](https://docs.djangoproject.com/en/5.2/ref/models/constraints/).
- `select_related` fits single-valued relations; `prefetch_related` supports collection-oriented loading through separate batched queries. Serialization must be included when measuring lazy QuerySet evaluation. [QuerySets](https://docs.djangoproject.com/en/5.2/ref/models/querysets/).
- Django Client exercises view behavior without running a server. Tenant-scoped reads and writes are application policy, not automatic consequences of authentication. [Testing tools](https://docs.djangoproject.com/en/5.2/topics/testing/tools/).

## Flask 3.1

- Application factories allow independent instances and configurations. Blueprint code accesses the active application through `current_app` during requests; import-time mutable stores undermine isolation. [Factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/).
- `MAX_CONTENT_LENGTH` limits request size. The upload example additionally limits the file read, validates text and ignores client filenames for storage naming. These checks do not constitute malware scanning or complex-parser sandboxing. [Uploads](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/).
- `test_client` supplies request/response testing without a live server. Each assignment checks persisted/local state as well as HTTP status. [Testing](https://flask.palletsprojects.com/en/stable/testing/).

## Executed references and limits

All nine scripts passed self-tests in isolated Python 3.12 environment. Tested versions: FastAPI 0.142.2, Django 5.2.18, Flask 3.1.3, httpx 0.28.1 and Pydantic 2.13.5. Every assignment embeds the complete transitive freeze as `requirements-tested.txt`; download all files into one exercise directory. Initial dependency installation needs packages or an available wheel cache. Static HTML content, hints, suggested answers and downloads remain network-independent.

FastAPI tests emitted a Starlette deprecation warning recommending `httpx2`; the pinned combination passed. This records current execution evidence, not a promise of future compatibility.

Verified contracts: quote validation/tenant scope, SQLite replay/restart, bounded cooperative workers/cancellation, Django tenant writes, atomic rollback/constraints, ORM query count 51→1, Flask app isolation, bounded text uploads and webhook signatures/replay. Independent review exposed a non-ASCII signature `TypeError`; strict ASCII-hex validation and negative fixtures now reject it with 401.

The Django outbox uses in-memory SQLite: it proves transaction commit/rollback and constraints, not process-crash durability. FastAPI jobs and Flask webhook use temporary file databases and recreated app instances; they prove that app-boundary replay persists, not arbitrary external-effect exactly-once execution. No real identity provider, broker, model, payment vendor, production database concurrency, deployed egress, or production load was exercised. WSGI capacity, migration, cache, token and SSRF scenarios supply explicit design/evidence plans rather than claiming those environments were tested.
