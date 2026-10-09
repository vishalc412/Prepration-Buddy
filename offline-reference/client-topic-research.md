# Client interview topics: verified primary-source notes

Purpose: support the supplied interview questions with accurate explanations and practical offline exercises. This document records research, not evidence that the candidate used these technologies in production. The original buggy snippets and insurance architecture diagram were not supplied; any replacement example must be labeled an illustrative fixture, not a diagnosis of those originals. No company interview probability or passing guarantee is inferred.

Primary sources were opened during this research session. Stable papers describe their original architectures; current library documentation describes particular implementations and can change. Pin package versions before publishing exact executable examples. For OpenAI product behavior, the artifact directory had no package manifest or SDK source, and `importlib.util.find_spec("openai")` in the current Python interpreter returned no installed package; official documentation was therefore used as the fallback. No live API invocation or hosted model benchmark was performed.

## 1. Transformer encoder, decoder and prompt prefill

The original Transformer is an encoder–decoder sequence model. The encoder computes source representations with self-attention and feed-forward layers. The decoder uses causal self-attention over target tokens and cross-attention over encoder outputs. In cross-attention, queries come from decoder representations while keys and values come from encoder outputs. Causal masking prevents access to future target positions. Scaled dot-product attention is `softmax(QKᵀ / sqrt(d_k))V`; positional information, residual connections and normalization are also important. [Original Transformer paper, §§3.1–3.5](https://arxiv.org/html/1706.03762v7).

Decoder-only text generation does not introduce a separate encoder merely because it reads a prompt. Prompt processing initializes the sequence state and, when enabled, KV cache; autoregressive decoding extends it. The same causal model performs both phases. Encoder-only, decoder-only and encoder–decoder are distinct architectural choices, not synonymous with input, processing and output. [Transformers text generation](https://huggingface.co/docs/transformers/en/llm_tutorial), [KV cache strategies](https://huggingface.co/docs/transformers/en/kv_cache).

**Offline exercise:** show causal and unrestricted attention masks over five positions. Compute toy attention with fixed matrices. State explicitly that this demonstrates masking and weighted aggregation, not a trained language model or meaningful semantic understanding.

## 2. Diffusion process versus encoder–decoder network shape

DDPM defines a forward process that gradually corrupts data with noise and a learned reverse process used for generation. The model predicts denoising-related quantities conditioned on the noisy state and timestep; a sampler iteratively updates that state. Calling this simply an “encoder that understands a prompt and decoder that generates an image” loses the mechanism. [DDPM paper](https://arxiv.org/abs/2006.11239).

A particular text-to-image pipeline may contain several separate networks. Stable Diffusion's documented pipeline includes a text encoder, latent VAE, denoising U-Net and scheduler. The VAE handles image/latent conversion, the text encoder handles conditioning, and the denoiser is repeatedly called by the sampling process. [Diffusers Stable Diffusion pipeline](https://huggingface.co/docs/diffusers/en/api/pipelines/stable_diffusion/text2img).

A U-Net has contracting and expanding paths, but diffusion is not defined by U-Net geometry. Diffusion Transformers replace that backbone with a transformer operating over latent patches. [DiT paper](https://arxiv.org/abs/2212.09748).

**Offline exercise:** fixed noisy vectors and a deliberately simple update rule illustrate timesteps. Label it an arithmetic denoising demonstration; it does not train DDPM, produce a valid diffusion benchmark or prove that generated content is correct.

## 3. Mixture of Experts: learned routing and sparse computation

In sparse MoE, a router computes scores from a token representation and selects experts. Experts typically replace some dense feed-forward computation; they are not necessarily entire independent language models. Switch Transformer uses top-1 routing, whereas other MoE variants select multiple experts and combine their outputs. Router parameters are learned. There is no general requirement that an expert correspond to a human label such as finance, insurance or coding. [Switch Transformer paper, §2](https://arxiv.org/html/2101.03961v3).

Distinguish total parameters from parameters active per token. Sparse activation can reduce arithmetic relative to using every expert, but weights, inter-device communication, expert capacity and load balance still affect deployment. Routing is not free and does not guarantee cheaper or faster service in every workload. The cited paper discusses capacity overflow and balancing loss; its benchmark claims apply to its experiments, not every MoE model.

**Offline exercise:** use fixed router logits and top-k selection to show which small expert functions run. Explain that hand-written logits are a fixture. A rules-based business router is useful software but is not evidence of training an MoE network.

## 4. Mamba and selective state spaces

Original Mamba makes state-space parameters input-dependent so the model can selectively preserve or discard information as it processes a sequence. Its hardware-aware scan implementation enables linear sequence-length scaling for the stated architecture. Original Mamba uses selective SSM blocks rather than ordinary Transformer attention. [Mamba paper](https://arxiv.org/abs/2312.00752), [Authors' implementation](https://github.com/state-spaces/mamba).

An intuitive recurrence is `h_t = A_t h_(t−1) + B_t x_t`, with an output derived from state and input; this is explanatory shorthand, not the full discretization or Mamba block. Attention explicitly mixes token representations through query/key interactions; selective state models propagate a compressed state with input-dependent dynamics. Both can model sequences. Hybrid models can combine mechanisms, so “all models called Mamba contain no attention” is too broad.

**Offline exercise:** a scalar recurrence with changing gates demonstrates selective retention. It does not reproduce the trained Mamba architecture, kernels, context quality or claimed throughput. No universal conclusion that Mamba beats attention is supported; benchmark candidate implementations under actual sequence lengths and hardware.

## 5. Local minima, saddles and failed optimization

A local minimum is no worse than nearby points; a global minimum is no worse than every point in the domain. A saddle has directions with opposing behavior. At the origin, `f(x,y)=x²−y²` has zero gradient and Hessian `diag(2,−2)`, so it is a saddle, not a minimum. A zero gradient alone does not establish a minimum. High-dimensional saddle regions can slow nonconvex optimization and resemble being trapped at a minimum. [Dauphin et al., saddle-point research](https://arxiv.org/abs/1406.2572).

**Teaching recommendation:** first check gradients, learning rate, data, loss definition and tensor shapes before announcing “local minimum.” Inspect training versus validation behavior and attempt a tiny-batch overfit test. Momentum, stochasticity or changing learning rate can alter the trajectory, but none provides a general guarantee of reaching the global optimum of arbitrary neural-network training.

**Offline exercise:** compare a convex quadratic, a double-well one-dimensional function and the saddle above. A two-dimensional plotted path is an intuition aid; it does not characterize the geometry of a real model with millions of parameters.

## 6. BitNet: binary weights versus b1.58 ternary weights

Original BitNet introduces BitLinear for training binary-weight Transformer models from scratch. BitNet b1.58 instead uses ternary weight values `{-1,0,+1}`. They are related proposals, not identical representations. [Original BitNet paper](https://arxiv.org/abs/2310.11453), [BitNet b1.58 paper](https://arxiv.org/abs/2402.17764).

The name 1.58 reflects `log₂(3) ≈ 1.585` bits of information for three equally distinguishable states. That arithmetic is not a claim that every tensor, checkpoint field or device allocation occupies exactly 1.58 bits per parameter. Activations, scales, embeddings, optimizer states and physical packing affect total resource use. These papers discuss training designed around low-precision weights; merely rounding an arbitrary pretrained model is not evidence that it becomes a trained BitNet model.

**Offline exercise:** map toy scalars to binary or ternary values and compute reconstruction error. Explain that this is a quantization illustration, not the complete BitLinear operation, quantization-aware training procedure, inference kernel or measured memory saving. Evaluate accuracy, quality, compatibility, throughput and memory rather than repeating the paper title as a universal deployment result.

## 7. ANN, exact search, HNSW and IVF

Approximate nearest-neighbor search trades completeness of nearest-neighbor recovery for resource use. Establish an exact baseline such as Faiss `IndexFlatL2` or `IndexFlatIP`. For cosine similarity, normalize vectors consistently before inner-product search; metric mismatch changes what “nearest” means. [Faiss index reference](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes).

HNSW is graph-based: `M` controls graph connectivity, `efConstruction` affects construction exploration and `efSearch` affects query exploration. IVF assigns vectors to coarse-quantizer lists; `nlist` sets partition count and `nprobe` controls how many lists are visited per query. IVF generally requires quantizer training on representative vectors. Raising exploration commonly improves recall at greater work, but the actual curve requires measurement. [Faiss IVF API](https://faiss.ai/cpp_api/struct/structfaiss_1_1IndexIVF.html), [Faiss tuning examples](https://github.com/facebookresearch/faiss/wiki/Indexing-1M-vectors).

**Offline exercise:** compare approximate returned IDs with exact top-k using `|approx ∩ exact|/k`, explicitly defining tie handling. Tiny fixtures can test arithmetic and parameter wiring; they cannot establish production latency, scale or index superiority. ANN recall against an exact vector baseline is separate from relevance recall against human-labeled documents.

## 8. RDF, OWL, SPARQL, Cypher and GQL

RDF is a graph data model of subject–predicate–object triples. In RDF 1.1, subjects are IRIs or blank nodes, predicates are IRIs, and objects can also be literals. Turtle is a serialization, not a query language. [W3C RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/).

OWL expresses ontologies with formal semantics, including classes and properties. It uses open-world reasoning: absence of a fact need not mean false. Domain/range axioms can support inference; they should not be casually presented as database input-validation constraints. SHACL separately provides RDF shape validation and reports constraint results. [W3C OWL 2 Primer](https://www.w3.org/TR/owl2-primer/), [W3C SHACL](https://www.w3.org/TR/shacl/).

SPARQL queries RDF graphs and datasets. Cypher is a declarative property-graph query language. GQL is standardized as ISO/IEC 39075:2024; it is not GraphQL, and vendor conformance and extensions still matter. The names do not make all queries portable. [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/), [Cypher introduction](https://neo4j.com/docs/cypher-manual/current/introduction/), [ISO GQL](https://www.iso.org/standard/76120.html), [Cypher/GQL conformance](https://neo4j.com/docs/cypher-manual/5/appendix/gql-conformance/).

**Offline exercise:** show the same small entity relationship as RDF triples and a property graph. A Python list-filter demonstration is not a SPARQL engine or Cypher execution. Use real libraries/databases when claiming executed queries. Keep generated queries parameterized and enforce authorization in the executor.

## 9. Model choice and hallucination evaluation

Model selection is empirical: compare candidates on the same representative inputs and keep the smallest resource setting that meets the required quality bar. Model family alone does not settle context support, tool behavior, output constraints or operational suitability. [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection).

Evaluation should match the task, include real edge cases, and compare against clear criteria. Human judgments and LLM judges have costs and limitations; automated grading should be calibrated against expert labels rather than treated as inherently authoritative. [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices).

OpenAI's hallucination research identifies training/evaluation incentives favoring guesses over uncertainty as one mechanism for plausible false statements. This is a research argument, not a claim that hallucinations have one exclusive cause or a solved universal fix. Evaluate incorrect assertions, abstentions and coverage separately. [OpenAI hallucination research](https://openai.com/index/why-language-models-hallucinate/).

**Offline exercise:** use a fixed set with known facts, missing answers, conflicting sources and unsupported citations. Report simulated results as fixture results. Retrieval quality, citation support and factual correctness are distinct checks; valid citations can still be irrelevant or fail to support the associated claim.

## 10. Structured output and response envelopes

OpenAI Structured Outputs constrains generation to a supported JSON Schema subset. This differs from asking for JSON in prose or using a mode that guarantees only JSON syntax. Schema-supported successful generation does not establish truth, permitted access or valid business action. Handle refusal and incomplete responses explicitly before consuming the payload. Unsupported schema constraints can fail at the API boundary. [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs).

The Responses API output array can include items other than a text message. Do not assume `output[0].content[0].text` exists. SDK helpers such as `output_text` aggregate text where available; absence of text is a state to handle, not permission to invent an answer. Chat Completions and Responses have different envelopes. [OpenAI text generation guide](https://developers.openai.com/api/docs/guides/text).

Python `json.loads` parses JSON into Python values; it is not automatically a JSON Schema validator. Python's default JSON behavior also permits non-finite values unless configured otherwise. [Python JSON documentation](https://docs.python.org/3/library/json.html).

**Offline exercise:** separate envelope checks, decoding, structural validation, business rules and evidence checks. A hand-written shape checker validates only its implemented constraints; do not label it a full JSON Schema implementation.

## 11. Tokenization, context budget and truncation

Tiktoken is a BPE tokenizer. Tokens are not words, characters or bytes; the encoding must match the target model when available. Tool definitions, conversation structure, retrieved context and modality handling may affect request accounting beyond raw text. [OpenAI tiktoken repository](https://github.com/openai/tiktoken), [OpenAI token counting](https://developers.openai.com/api/docs/guides/token-counting).

Reasoning models can consume generated tokens that do not appear as visible answer text. Reaching `max_output_tokens` can yield `status="incomplete"` and `incomplete_details.reason="max_output_tokens"`, even before a visible answer appears. Budgeting only desired answer length is therefore insufficient. Context-window and output limits depend on the selected model snapshot. [OpenAI reasoning guide](https://developers.openai.com/api/docs/guides/reasoning).

**Teaching recommendation:** reserve output/reasoning capacity first, then allocate instructions, user input, history and selected evidence. Use relevance selection, deduplication and summarized history rather than blind truncation that may remove source identifiers or constraints. Preserve mandatory instructions and authorization context. A character-count heuristic is an estimate, not exact token accounting. Offline tokenizer examples need installed packages and cached tokenizer data; first-use downloads must not be disguised as fully offline execution.

## 12. Production workflow state and side effects

LangGraph checkpointers store state and use `thread_id` to identify checkpoint history. Persistence enables continuation but does not itself authorize access to a thread. An in-memory checkpointer does not demonstrate recovery after process loss. [LangGraph checkpoint reference](https://reference.langchain.com/python/langgraph.checkpoint/memory).

Retries can duplicate side effects unless the downstream operation is idempotent. Caller-provided request identifiers can distinguish a retry from a new intent; deduplication must bind the identifier to the intended operation. Retry limits, backoff and jitter reduce amplification during failures. [AWS idempotent API design](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), [AWS retry bounds](https://docs.aws.amazon.com/wellarchitected/2024-06-27/framework/rel_mitigate_interaction_failure_limit_retries.html).

OWASP recommends limiting agent functionality, permissions and autonomy, with downstream authorization and human approval for high-impact actions. [OWASP Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/).

**Teaching recommendation:** require authenticated ownership of tenant/thread state, explicit approval bound to a concrete action, expiry and replay controls, bounded tool execution and cancellation. Approval from the model itself is not a human decision. Offline examples can test decision-state transitions and duplicate-request handling; they cannot certify distributed exactly-once effects, cloud IAM or a deployed security boundary.

## 13. Evidence rules for the tutorial

Use three explicit labels: **conceptual demonstration**, **locally executed fixture**, and **production evidence required**. Only use the second when the documented command actually ran and its assertions passed. A deterministic mock can verify parsing and control flow without verifying model quality or service availability. A teaching diagram can illustrate an architecture without claiming to reproduce the missing insurance diagram.

For missing buggy snippets, provide a representative broken example and corrected version with a precise test. State that it is illustrative and list what the original would need for diagnosis: source, dependency versions, error output, input and expected behavior. For a missing deployment, provide an evidence checklist with measurable acceptance criteria rather than a story claiming production success.

Principal-level explanations should identify mechanism, boundary, tradeoff, failure mode and verification method. Repeating a definition is insufficient; inventing deployment experience is unacceptable. Sources above support the mechanisms. Exercise selection and interview-answer structure are teaching recommendations, not verified employer scoring rules.
