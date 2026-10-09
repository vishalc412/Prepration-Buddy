# Independent client curriculum review

Verdict: **PASS within the content and local-reference scope below.** Final validation executed the rebuilt single-file curriculum and all 16 new Python fixtures. No unresolved correctness blocker found in the reviewed content/runtime paths. Parent browser verification is a separate recorded receipt, not inferred from this validator.

## Scope and observed coverage

Reviewed all 50 client question mechanisms/answers/examples, all 100 client fixed quizzes, all 80 new lesson modules and 16 new reference implementations. Reviewed eight revised JD drills and their 16 follow-up answers. Exact source-to-HTML parity passes for authored Day 14 and Days 15–30 day records, lessons, labs, daily/design answers, client content, JD content and both studio runtime scripts. Embedded lesson/lab/daily/design coverage is 30 days. Six guided study blocks total 240 active minutes per day.

`python3 offline-reference/validate_client_curriculum.py --execute --html`: **PASS**. Each new fixture ran under isolated Python with a fresh temporary working directory and exited zero. No cloud/model call, package installation or user browser storage access was used by this reviewer.

## Correctness findings resolved

- Client routing previously invoked an old renderer without a client route; an independent actual-source Node fixture reproduced the error. Dispatch now includes client and JD routes; client wrapper no longer performs duplicate full rendering.
- A saved zero unsupported-claim count used to become five on rerender. The numeric fallback now preserves zero.
- Day 16 finite inputs could overflow into non-finite outputs. Current forward/oracle validation includes finite-output rejection and explicit overflow assertions.
- Day 24 raw cosine arithmetic produced NaN for identical finite `(1e308, 1e308)` vectors. Per-vector max-absolute scaling, hypot normalization and fsum now produce approximately +1 for identical and −1 for opposite huge vectors. Independently tested these and the larger `(1.7e308, 1.7e308)` case.
- Day 28 accepted matching missing caller/document tenant identities. Current code rejects missing, blank and non-string identities and executes the original None/None negative fixture.
- Client-08 top-k quiz and Day 27 parser/schema quiz had multiple defensible answers. Current wording/distractors remove the ambiguity.

## Semantic review

Mechanisms distinguish Transformer masking/prefill, diffusion noise versus denoiser architecture, MoE routing and gate normalization, selective state recurrence, stationary minima/saddles and binary versus ternary precision. RAG lessons retain trusted identity/ACL scope, source versions/tombstones, separate support/shape checks and explicit answer-versus-claim denominators. Exact vector baselines, approximation recall, embedding-space compatibility, fusion/reranking and word-budget fixtures remain correctly separated from real embedding/model benchmarks. Durable state/replay and financial authorization examples bind trusted context, expected versions, exact approval intent and local transactional receipts; they explicitly avoid external exactly-once claims.

JD drills cover maintained accelerators, MCP revision/transport/result contracts, audience-bound authorization, coding context evaluation, Java/Python integration, the visible JS/TS proficiency gap, telemetry/cost denominators, cloud operations, secure delivery and measurable adoption. Proposed work and synthetic outcomes stay labeled. Independent spot verification used the official [MCP current revision](https://modelcontextprotocol.io/specification/2026-07-28), [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization), [security guidance](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices), [Spring transaction documentation](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html), [DORA metrics](https://dora.dev/guides/dora-metrics/) and [SLSA provenance](https://slsa.dev/spec/v1.2/provenance). Those sources support the reviewed revision/authorization, transaction, delivery-measurement and provenance distinctions.

## Verification limits

Length/schema checks do not prove learning effectiveness or factual accuracy; semantic review is independent and human-readable. URL allowlists establish primary-source provenance shape, not every page's availability. Self-assessed explanations/JD checklists do not grade actual implementations, and the browser does not execute Python/Java. New references use standard-library fixtures with synthetic data; unchanged framework suites were not rerun. No live SDK/provider, real tokenizer, actual ANN engine, trained model, deployment, distributed recovery, external financial effect or hiring outcome is certified. Static AST guards and temporary working directories are not an OS security sandbox. Parent browser tests own keyboard, responsive layout, offline interaction, challenge gates and import/storage evidence.

## Final receipt

After the CSS badge-wrapping adjustment, independently reran `python3 offline-reference/validate_client_curriculum.py --html`: **PASS**, including authored payload/runtime parity. Final `index.html`: 1,679,455 bytes, SHA-256 `b5919a9c91318bdef601f051e1db5c48f3357325686703e2a760e48453922f7c`. No reference code changed, so the executed fixture fingerprints below remain current.

Read the separate parent-owned browser receipt, `output/playwright/client-curriculum-verification.json`: **PASS**, 0 runtime errors and 0 remote requests. It records all 30×6 teaching panes, 50×3 client panes, eight JD drills, challenge/hint/check flows, old and new backup persistence, offline single-file startup and 1440/847/390 layouts. It reports learner storage untouched. Its artifact hash exactly matches the independently hashed final HTML above. This browser execution was performed by the parent; this reviewer independently checked the receipt and matching artifact identity.

```json
{
  "status": "PASS",
  "client_questions": 50,
  "client_checks": 100,
  "jd_drills": 8,
  "jd_followups": 16,
  "client_followups": 100,
  "extended_days": 16,
  "extended_modules": 80,
  "extended_labs": 16,
  "daily_minutes": 240,
  "executed_fixtures": 16,
  "embedded_parity": "PASS"
}
```

Fixture source fingerprints:

| Day | File | Exit | SHA-256 |
|---|---|---:|---|
| 15 | day15_foundations.py | 0 | 586a1c6b5c7757fdf1fe2bd61f3b2a307e1d8bc3a2b1540e5ac5d332e3116fa5 |
| 16 | day16_foundations.py | 0 | 7dcbc30f9fc5e2870d58d9bf0602b5f5c25ad96794a81c4423726aca35b56b9f |
| 17 | day17_foundations.py | 0 | 3a994a1c46430fbb24c338a20336484083e861d51541f69daf6cc6d83e311479 |
| 18 | day18_foundations.py | 0 | f94f32af9a4a8cee4f820d6128f9c6ecb175530fb9a5799705a01227a021487a |
| 19 | day19_foundations.py | 0 | ce2651b22d9487f3ac67d5baf2c2d9d262c64b29a6998aec2239e19374958b2e |
| 20 | day20_foundations.py | 0 | d733f4938ccb2323c66e5005892728853265f4933d0361dc7a3b7658cd799539 |
| 21 | day21_scoped_rag.py | 0 | 02dc3f2dd5aeb43ec4788a5aec5bdccbc6a225bbfb4cddab6cbb44dd545a8a8e |
| 22 | day22_hallucination_metrics.py | 0 | dfbde2234346c657fe19d86a4e3a84cc132c255384c6e0fa93c0569da397bb30 |
| 23 | day23_model_selection.py | 0 | fb44983813cf2a25583fa852c2458b6dd21e628e7732d22d051552077b95435e |
| 24 | day24_vector_baselines.py | 0 | 1c18555aaecba84550d37c328725fde34130a623cb9642e3950c74b21a57fedb |
| 25 | day25_hybrid_chunking.py | 0 | 419242862e4b008335356780d5e2606b5f05ad44f740649b91df7a7e1267caee |
| 26 | day26_graph_boundaries.py | 0 | 4e3f1012421dc2e54857ac7c4e1a25972874a82b32638091bf3da2abd01d621c |
| 27 | day27_ticket_contract.py | 0 | 64dd4dec8566a3e8acec5e91207a9eec99bb2f543266bc3b298dae307e884234 |
| 28 | day28_budget_selection.py | 0 | 1c9e88cbcc03198d0638d0e755b1d1763d0c87fba6d8845929acf8e38ab43752 |
| 29 | day29_durable_state.py | 0 | be68d86618edee7af963e3bd76aaf48b25b908b8613c954873688c6f9a5b109d |
| 30 | day30_financial_gate.py | 0 | d2b4936d8bb56f158a3fd9e06f63a9695958a28299dc1f8422805bdc955e7477 |

Final contrast-only refinement: the parent reran the full browser suite and static HTML validation after changing selected Client/JD card text contrast. Independently read both updated PASS receipts (`output/playwright/client-curriculum-verification.json`, `output/client-curriculum-static-final.json`) and verified the browser receipt exactly matches the current final HTML hash and byte count above. Reference source fingerprints remain unchanged.
