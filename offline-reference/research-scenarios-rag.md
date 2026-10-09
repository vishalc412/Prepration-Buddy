# RAG, agents and evaluation scenario research

Checked 7 October 2026. Primary sources only. Scenario constraints, corpora, receipts, costs and timings are authored teaching fixtures. The nine bundled programs use Python standard library, run without network/models and make no production certification claim.

## Research findings and tutorial implications

- The original RAG paper combines a learned generator with an external dense retrieval index. This supports teaching retrieval and generation as separate components. Our bundled token-overlap/substring references implement lexical fixtures, **not the paper's neural architecture**, semantic embeddings or measured natural-language quality. [Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401).

- OWASP distinguishes direct and indirect prompt injection and describes risks from untrusted documents reaching connected functions. It recommends least privilege, deterministic output validation, human approval for privileged actions and adversarial testing. Our scenario policy uses authorization before retrieval/tool dispatch and independent trusted approval state; these are exercise design decisions, not a universal injection-prevention guarantee. [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

- NIST's Generative AI Profile is a companion to its voluntary AI Risk Management Framework. Use it to organize responsibilities and evidence across design, deployment and evaluation. Passing local fixtures is not NIST certification or proof of acceptable risk for another use case. [NIST AI 600-1, Generative Artificial Intelligence Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence).

- Ranked-retrieval evaluation needs a cutoff and declared relevance judgments; recall concerns relevant-document coverage, while rank-sensitive metrics assess ordering. The tutorial separately implements Recall@k and first-hit reciprocal rank at k, with unique IDs and a no-answer cohort boundary. Tiny synthetic queries demonstrate arithmetic, not representative search performance. [Stanford/Cambridge Introduction to Information Retrieval: Evaluation of ranked retrieval results](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html).

- LLM-as-a-judge research identifies position, verbosity and self-enhancement biases and limited reasoning ability. The tutorial keeps judges optional, proposes blinded/swapped calibration and does not treat fluent answers or model scores as gate receipts. Study answers and deterministic checks remain usable offline. [Zheng et al., Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685).

- AWS describes ambiguity after a response is lost and the value of explicit caller-intent idempotency identifiers. It also discusses parameter mismatch, late requests and atomicity of the effect plus idempotency record. Our SQLite fixture deliberately has one transactional store; remote actions need independent reconciliation/idempotency and cannot inherit that atomicity claim. [AWS Builders' Library: Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).

- Python's hashing and HMAC modules support content identities and keyed receipt integrity checks. Exercise keys are public fixture values and provide no production signing trust. Receipt validation also checks trusted issuer, executed status, required gate and artifact identity; authentic data can still describe a failed or unrelated operation. [Python hashlib](https://docs.python.org/3/library/hashlib.html), [Python hmac](https://docs.python.org/3/library/hmac.html).

## Local verification boundary

All nine files parsed and executed with Python 3 in a temporary working directory. Reported fixture cohorts: RAG 7 + 7 + 9; Agents 10 + 5 + 8; Evaluation 6 + 14 + 7. Their happy paths and negative cases cover ACL/version/deduplication, stale/quarantined/deleted evidence, claim validation/abstention, exact approval/receipt/drift, durable timeout reconciliation, bounded workflow transitions, ranking denominators, unknown/failed authority gates and all-attempt cost/latency reporting.

These checks establish the supplied fixtures and code paths only. They do not establish real authentication, multi-shard consistency, semantic retrieval quality, OS isolation, Java/.NET migration parity, model quality, live cloud billing or release readiness.

## Scenario inventory

| Track | Executable assignment scenarios | Design/debug scenarios |
|---|---|---|
| RAG | Authorization/versioned citations; incremental index; grounded abstention | Hybrid retrieval/context budget; code-aware chunks; release-bound incident evidence |
| Agents | Exact approval; uncertain-write reconciliation; workflow budgets | Repository injection; independent review/authority; cancellation and resumption |
| Evaluation | Ranked metrics; worst-slice/safety gates; cost/latency | Judge bias; leakage/grouped evaluation; mandatory release gate semantics |

Every scenario includes at least two authored answers of 100+ words, a 120+ word walkthrough, progressive hints, concrete acceptance checks and a changed-constraint follow-up. Exactly the first three scenarios in each track carry executable assignments; the rest remain explicitly design/debug work.
