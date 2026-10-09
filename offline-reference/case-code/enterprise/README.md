# Enterprise case: Spring Boot gateway and FastAPI evidence service

This is an executed two-process HTTP application, with a deterministic offline provider fixture. It does not call an LLM, bank or cloud. It demonstrates request/response boundaries, tenant-scoped evidence, validated classification, durable local commands and recovery after a Python process restart. It does not claim semantic retrieval quality, production identity, complete prompt-injection detection or exactly-once external delivery.

## Setup and complete local CI command

Save every shipped file together. Tested with Python 3.12, JDK 23.0.2, Maven 3.9.9, Spring Boot 3.4.4 and the exact Python package versions in requirements-tested.txt. Java sources target Java 17. Initial framework dependencies must already be cached or provisioned once; the tutorial itself has no such runtime dependency.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-tested.txt
.venv/bin/python integration_test.py --offline-maven
```

The last command is the complete local CI gate. It compiles the actual Spring Boot application, starts both services on temporary loopback ports, runs positive and negative HTTP assertions, exercises concurrent duplicate requests, stops/restarts Python against the same file-backed database and deletes its temporary project/data afterward. It has a 180-second Maven build timeout and bounded server readiness deadlines. For a fully offline first setup, provision an approved wheel directory and use `pip install --no-index --find-links /path/to/wheels -r requirements-tested.txt`; Maven also needs its complete cached artifact/plugin closure. The cached build route uses the explicitly pinned maven-dependency-plugin 3.7.0. A missing cache is an initial setup limitation, not a reason to claim offline execution passed.

If Maven dependencies are not cached, run the following once when dependency provisioning is allowed, then repeat the offline gate:

```sh
mvn -q compile org.apache.maven.plugins:maven-dependency-plugin:3.7.0:build-classpath -Dmdep.outputFile=classpath.txt
```

## Explore the application manually

Terminal one starts Python. The `demo.sqlite3` path is explicit, and this command creates it in your selected working directory:

```sh
.venv/bin/python python_service.py --port 9091 --db demo.sqlite3
```

Terminal two compiles and launches Java without an executable-jar packaging plugin:

```sh
mvn -o -q compile org.apache.maven.plugins:maven-dependency-plugin:3.7.0:build-classpath -Dmdep.outputFile=classpath.txt
PYTHON_BASE=http://127.0.0.1:9091 java -cp "target/classes:$(cat classpath.txt)" bootcampcase.EnterpriseGateway --server.port=9090 --server.address=127.0.0.1
```

Request an evidence answer:

```sh
curl -sS http://127.0.0.1:9090/api/assist -H 'Authorization: Bearer token-acme-editor' -H 'Content-Type: application/json' -d '{"question":"refunds final sale","ticket_text":"My refund invoice needs help."}'
```

Save an idempotent ticket by calling `/api/tickets` with the same JSON plus `Idempotency-Key: case-1`. Retrying that exact payload returns its recorded ticket ID. Changing the payload under that key returns409. `/api/tickets/{ticket_id}` reads only within the authenticated tenant, returning404 outside that scope. Fixed tokens are fixture credentials: acme editor is alice, acme viewer is eve, bravo editor is bob. A caller-supplied tenant header is ignored, and a tenant body field fails the extra-field contract. Do not use these tokens as real authentication.

## Read the mechanism before changing it

Java verifies a demo principal and write role, bounds the input bytes, accepts JSON content type and calls only the configured loopback origin. That origin comes from server configuration, never from caller text. A four-second HttpRequest timeout bounds request/response availability, and readNBytes caps response materialization by size. The subsequent InputStream body read has no separately enforced total deadline and can stall after headers; adding and testing a body-read deadline is an explicit production extension. This reference does not claim an end-to-end response-time guarantee. Java checks that the Python response is a JSON object, while Python remains the authoritative schema/business boundary. Replace fixtures with real verified identity, service authentication, contract schemas and transport security before production.

Python's dependency derives actor, tenant and role from its own trusted fixture mapping. Pydantic rejects unknown fields, wrong types and unsupported provider category/urgency enums. A malformed provider result produces502 before any ticket is written. Retrieval scores token overlap against SQL rows selected with a parameterized tenant predicate. The answer is a complete literal evidence excerpt and carries source/version citations; no relevant eligible evidence produces `no_answer` with an empty answer/citation list. Those are mechanical guarantees, not an LLM factuality benchmark. Text saying “switch tenant” or “execute SQL” remains classification data; no tool exists that converts that text into authority.

For writes, the canonical hash includes trusted actor/tenant, schema version and the complete validated request. The first idempotency lookup supports cheap accepted replays. After inference, `BEGIN IMMEDIATE` repeats the lookup under the write transaction, so concurrent requests cannot both create tickets for one tenant/key. Ticket, command and pending `ticket.created` outbox rows commit together. Outbox work is not dispatched in this reference: it demonstrates a recoverable pending event, not exactly-once remote execution. The restart test proves local file-backed process recovery, not host-loss durability, power-loss guarantees or a replicated database.

## Failure timeline and assignment

Predict each outcome before opening the integration assertions. At timeT0, a viewer attempts a write: both Java and direct Python reject403, with zero rows. AtT1, malformed/invalid-enum provider output returns502 and still writes nothing. AtT2, an editor creates a ticket and all three rows commit. AtT3, its response is retried: the stored result is reused. AtT4, a changed request under the same key returns409. AtT5, six concurrent identical submissions converge on one ticket. AtT6, Python is unavailable: Java returns502, without pretending a write succeeded. AtT7, Python restarts with the same file and returns the original accepted result. Extend this timeline with an injected crash between individual SQL statements and prove rollback using a new test; this additional crash point is an assignment, not an executed claim.

Rebuild one route from the contracts without copying its implementation, add an unseen enum and unknown JSON field, and defend why neither can bypass validation. Add a second acme editor and decide whether idempotency keys should be actor-scoped or tenant-scoped; implement your chosen contract and its collision test. Replace lexical retrieval only after establishing reviewed evidence-recall/support cases, keeping tenant filtering and citation provenance unchanged. A real model adapter must handle refusal, incomplete output, timeouts and shape failures; its quality is a separate evaluation gate.

## Optional container and Kubernetes design exercise

Dockerfile.python, Dockerfile.java and deployment-exercise.yaml are authored teaching artifacts; no Docker image was built and no cluster deployment was executed. The two containers share one Pod's network namespace, so Java's allowed loopback origin can reach Python. Only the Java service port is published. Python's probe executes inside its container because Python binds127.0.0.1. A single replica, Recreate strategy and PVC represent the local SQLite constraint; evaluate volume/backup/recovery behavior rather than assuming multi-replica scaling. Resource values are placeholders for measurement, and image names in the manifest deliberately require replacement. Image tags in the Dockerfiles are not immutable digest pins.

Before a real deployment, replace fixed-token identity with verified caller and service identities, apply ingress/network policy and secret management, define audit retention, replace or operationally validate storage, resolve image digests and establish backups/reconciliation. An HTTP health endpoint confirms process readiness only; it is not a security or semantic-quality certification. The local CI gate above remains the executed evidence boundary.
