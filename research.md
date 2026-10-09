# Principal AI/ML and AI Modernization: primary-source research

Research checked 7 October 2026. Scope: practical preparation for the supplied role profile and a 14-day study sprint. Primary sources establish technical behavior and documented tool capabilities. They do **not** establish this employer's question distribution, interviewer preferences, hiring threshold, or probability of passing. Day ordering, readiness checks, and practice formats below are curriculum recommendations, not company interview predictions. No candidate experience is assumed, and no pass is guaranteed.

## Implementation scope clarified by the learner

Hands-on code is Python and Java only. .NET, middleware, database and other ecosystem changes are tool targets orchestrated by Python adapters or AI-assisted plugins. The learner must defend tool capabilities, identity, scoped execution, behavior parity, failure handling and receipts; no C# coding curriculum is required. This scope supersedes any earlier suggestion of direct .NET coding.

## 1. Evaluate the system before optimizing the model

Scikit-learn documents leakage as using information unavailable at prediction time. Split before fitting preprocessing; fit scalers, imputers and feature selectors inside training folds; transform validation and production inputs consistently. A pipeline makes this boundary easier to preserve, including during cross-validation. A pipeline cannot repair an invalid target or a feature containing future information. [Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).

Cross-validation must reflect the deployment unit. Repeated customer, patient or repository observations require group-aware splitting; future forecasting needs a temporal split. Repeated tuning against a test set contaminates the estimate even if individual training runs never fit on that set. Stratification preserves approximate class proportions but can hide some variability; fold standard deviation is not automatically a confidence interval. [Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html).

**Curriculum recommendation:** start with a deliberately flawed churn or defect-risk notebook. Ask the learner to identify the prediction timestamp, target maturity, duplicate entities, sampling mechanism, fold construction and baseline. Require a written split justification before accepting any score. A compelling principal-level explanation connects each boundary to production behavior rather than listing metric names.

## 2. Keep ranking, probability and business decisions separate

A well-calibrated classifier associates predicted probabilities with observed event frequencies. Reliability diagrams compare bin-average predictions and outcomes. Calibration fitting requires data independent of model fitting; `CalibratedClassifierCV` supports cross-validated calibration. Brier score and log loss reflect more than calibration alone, so a lower aggregate score is not proof that reliability improved. Small calibration sets make flexible calibration methods risky. [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html).

Changing a threshold can change decisions without changing fitted model coefficients. The default 0.5 probability threshold need not maximize the task's utility. Tuning the cutoff on the same data used to fit the estimator can overfit. [Threshold example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_tuned_decision_threshold.html), [Cost-sensitive threshold tuning](https://scikit-learn.org/stable/auto_examples/model_selection/plot_cost_sensitive_learning.html).

**Curriculum recommendation:** use a threshold slider over a fixed synthetic probability table. Show confusion matrix, precision, recall, review capacity and expected cost. Label values as illustrative. Ask which metric changes if base rate shifts and why ranking quality alone does not decide action policy. A useful answer names false-positive and false-negative costs and explains how validation chooses the threshold.

## 3. Make the PyTorch training loop explainable

PyTorch's documented optimization sequence includes prediction, loss, gradient reset, backpropagation and parameter update. Gradients accumulate unless cleared; intentional gradient accumulation needs an explicit plan. Training and validation loops differ in mode and gradient recording. [Optimization tutorial](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html).

`model.eval()` changes behavior of modules such as dropout and batch normalization. It does **not** disable autograd. `torch.no_grad()` and inference mode control gradient recording independently of module evaluation mode. Inference mode has stronger restrictions on later autograd use of tensors created there. [Autograd mechanics](https://docs.pytorch.org/docs/stable/notes/autograd).

**Curriculum recommendation:** learner must annotate every line of a small training loop, identify tensor shapes and loss expectations, and explain stale gradients, wrong label dtype, train/eval confusion and device mismatch. Require a tiny-batch overfit diagnostic, validation monitoring, and a checkpoint containing enough state to resume deliberately. Distinguish a code example printed in HTML from code actually executed in Python. Neither a screenshot nor a decreasing training loss proves generalization.

## 4. Understand transformers, adaptation and retrieval

The original Transformer architecture uses attention rather than recurrence or convolution for sequence transduction. Scaled dot-product attention forms scores from queries and keys and weights values; positional information supplies sequence order. Architecture basics should precede tool-specific configuration. [Original Transformer paper](https://arxiv.org/abs/1706.03762).

LoRA freezes base weights and learns low-rank update matrices, reducing trainable parameters. Rank and target modules affect adaptation capacity; fewer trainable parameters do not remove dataset, evaluation or deployment responsibilities. Adapter and base-model compatibility still matter. [Hugging Face PEFT LoRA reference](https://github.com/huggingface/peft/blob/main/docs/source/package_reference/lora.md).

RAG conditions generation on externally retrieved passages. Changing the index can refresh available knowledge without retraining the generator. Retrieval does not guarantee the correct passage or faithful generation. [Transformers RAG documentation](https://huggingface.co/docs/transformers/en/model_doc/rag).

**Curriculum recommendation:** teach prompt-only, retrieval, adaptation and combined approaches as choices driven by measured failure. Fresh, permissioned knowledge suggests retrieval; stable output behavior may justify supervised adaptation; neither should be selected merely because it is fashionable. Ask for labeled examples and baseline comparisons before authorizing fine-tuning. This decision rule is curriculum synthesis, not a claim that RAG always beats fine-tuning.

## 5. Diagnose retrieval and generation separately

Microsoft's RAG evaluator documentation distinguishes document-retrieval quality from answer quality. Labeled relevance judgments enable ranking evaluation such as NDCG. Groundedness checks alignment with supplied context; relevance asks whether the response addresses the query; completeness compares critical content with expected information. A response can be grounded yet incomplete, and a relevant-sounding answer can be unsupported. [RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators).

End-to-end RAG evaluation needs granular retrieval/search measurements alongside final-response measurements. LLM responses and model-based judges can vary; repeated evaluation and ranges are more meaningful than presenting a single sample as deterministic proof. [RAG evaluation phase](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-llm-evaluation-phase).

**Curriculum recommendation:** build a frozen evaluation set with normal queries, ambiguous questions, missing answers, contradictory versions and unauthorized documents. Compare chunking, retrieval and reranking one change at a time. Measure retrieval recall, ranking quality, supported citations, answer correctness, abstention and latency separately. State who labels relevance and adjudicates disputed answers. LLM-judge output is evidence to calibrate against human judgments, not objective truth.

## 6. Bound agent authority outside the model

OWASP identifies direct and indirect prompt injection, including instructions hidden in retrieved or tool-provided content. RAG and fine-tuning do not fully eliminate this vulnerability. [Prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

Excessive agency arises when unexpected or manipulated model output can trigger harmful actions. OWASP recommends minimizing functionality, permissions and autonomy, using granular tools, enforcing authorization downstream, and requiring human approval for high-impact actions. A generic shell or unconstrained write capability expands the damage available to a compromised reasoning step. [Excessive agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/).

**Curriculum recommendation:** draw separate trust boundaries for user, retrieved document, model, tool gateway, executor and data store. Explain maximum steps, wall-clock deadline, spend limit, cancellation, typed arguments, identity-aware authorization, idempotency and observable failures. A prompt that says “do not exfiltrate” does not replace a permission check. Test a poisoned document that requests an unrelated outbound action and verify that the execution boundary rejects it.

## 7. Choose cloud services by control needs

AWS positions Bedrock as a managed platform for foundation-model applications and agents, while SageMaker AI offers stronger control over custom model training, deployment and infrastructure. These paths can be combined; the choice is about workload and operational control rather than a universal winner. [AWS decision guide](https://docs.aws.amazon.com/decision-guides/latest/decision-guides/bedrock-or-sagemaker.html).

AWS knowledge-base evaluation requires a service role granting access to selected model invocation, retrieval and evaluation data. Authentication alone is insufficient: the trust relationship and allowed resource actions must both be correct. [Bedrock evaluation role requirements](https://docs.aws.amazon.com/bedrock/latest/userguide/rag-eval-service-roles.html).

**Curriculum recommendation:** candidate should choose a provider based on organization constraints, data residency, networking, identity, model control, operational burden and measured latency/throughput. Avoid memorizing a cross-cloud table as if services were interchangeable. Regional availability, preview status, permissions and integration limits require fresh checks before an implementation. No price or model-ranking claim is necessary to explain these tradeoffs well.

## 8. Explain keyless identity and tenant isolation

Azure AI Search supports system-assigned or user-assigned managed identities for outbound access. Assigning appropriate roles allows connections without embedding secrets; firewall and supported-scenario constraints still apply. Managed identity authenticates a workload, while role assignments authorize operations. [Search managed identities](https://learn.microsoft.com/en-us/azure/search/search-how-to-managed-identities).

Google recommends Workload Identity Federation for suitable external workloads instead of long-lived service-account keys. Federated identities can receive resource access or impersonate service accounts, obtaining short-lived credentials. [Google workload identities](https://docs.cloud.google.com/iam/docs/workload-identities), [Federation overview](https://docs.cloud.google.com/iam/docs/workload-identity-federation).

**Curriculum recommendation:** trace identity from end user to application to retrieval and tool execution. Require tenant/document authorization before context reaches the model, including cache and trace access. Distinguish service-agent identity from end-user permissions. Explain why private networking does not itself establish authorization and why a service account able to read all documents does not grant every user permission to receive them.

## 9. Prefer semantic transforms for mechanical Java changes

OpenRewrite's lossless semantic trees preserve formatting and carry type information, enabling matching beyond raw text. Recipes operate on these structured representations. [Lossless semantic trees](https://docs.openrewrite.org/concepts-and-explanations/lossless-semantic-trees).

Its Maven plugin provides `rewrite:discover`, `rewrite:dryRun` and `rewrite:run`. Dry-run produces a proposed diff without applying source edits; run applies selected recipes locally. Recipe discovery and pinned configuration make the proposed transformation reviewable. [Maven plugin documentation](https://docs.openrewrite.org/reference/rewrite-maven-plugin).

**Curriculum recommendation:** inventory dependencies and runtime assumptions, pin the tool and recipe set, preview changes, review diff, compile, run parity tests and examine behavior. Use deterministic recipes for repetitive supported changes; use an LLM for bounded explanations or proposed custom changes subject to gates. Neither a semantic transform nor successful compilation proves preservation of transactions, security, time handling or serialization. Check current artifact repository and licensing guidance before copying installation commands.

## 10. Update the .NET modernization lesson

Microsoft explicitly marks .NET Upgrade Assistant deprecated and recommends GitHub Copilot modernization. Its migration guidance still emphasizes assessment and testing. Do not teach the old CLI as the unquestioned current default. Tool availability and supported project types must be checked in the selected development environment. [Upgrade Assistant overview](https://learn.microsoft.com/en-us/dotnet/core/porting/upgrade-assistant-overview).

GitHub documents that Copilot review may miss problems or produce false positives, particularly for complex changes; human review remains necessary. AI review comments need validation before editing. [Responsible use of Copilot agents](https://docs.github.com/en/copilot/responsible-use/agents).

**Curriculum recommendation:** teach migration as assessment, scope, parity contract, narrow change, build/test gates and rollout. Compare generated recommendations with dependency support, API changes and measured behavior. Preserve user authorization over commits and deployment even if a modernization tool's default workflow commits changes. Candidate should discuss AI assistance with review and evidence, not claim the assistant guarantees a complete or secure migration.

## 11. Make reproducibility and promotion explicit

MLflow Tracking records runs with parameters, metrics, code-related metadata and artifacts. Tracking a score is different from having enough data, environment and configuration information to reproduce it. [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/).

The Model Registry manages named models, versions, aliases and tags. Registry workflow documentation describes database-backed storage requirements for a self-hosted registry. Aliases support resolving an intended version without embedding a version number in every caller. [Model Registry workflows](https://www.mlflow.org/docs/latest/ml/model-registry/workflow/).

MLflow tracing captures intermediate inputs, outputs and metadata, helping locate retriever or tool failures; it supports redaction and sampling controls. [Tracing documentation](https://mlflow.org/docs/latest/llms/tracing/).

**Curriculum recommendation:** require dataset/split identity, dependency pins, prompt and retriever configuration, evaluation records, model version and rollback reference. Promotion criteria should cover quality, safety, resource limits and operational readiness. Logs may contain sensitive text, so retention and access decisions belong in the architecture. Drift alerting should trigger diagnosis rather than automatic retraining on unreviewed data.

## 12. Turn governance into release evidence

NIST AI RMF organizes risk work around Govern, Map, Measure and Manage. Its Generative AI Profile provides suggested actions for generative AI risks; it is a risk-management resource, not proof that a system passed a technical test. [AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/), [Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf).

**Curriculum recommendation:** connect each framework label to an artifact: named owner and policy; intended use and affected users; evaluation and adversarial-test evidence; release decision, incident response and rollback. Use OWASP for concrete attack scenarios and NIST for lifecycle ownership. Avoid a framework-name checklist without tests or owners. For modernization, specify which existing behavior must remain equivalent, which behavior intentionally changes, and how both cases are verified.

## 13. Teaching design for the interactive tutorial

These recommendations synthesize the sources above; they are not sourced claims about the employer. Each study day should contain a compact explanation, worked example, bounded exercise, failure drill and observable exit criterion. A learner should alternate building with explaining: code fluency, architecture rationale and business translation test different capabilities.

Keep the 30-question baseline diagnostic closed: no prefilled answer keys or automatic claims of correctness for subjective answers. Use self-ratings, notes and optional review rubric after attempting a response. Label training quizzes separately. Progress means completed practice artifacts, not hours spent reading. Flashcards support recall but do not substitute for coding or defending a design.

Suggested sprint emphasis: days 1–3 on leakage-safe ML and PyTorch; days 4–6 on transformers, RAG and evaluation; days 7–8 on bounded agents and cloud identity; days 9–11 on modernization and MLOps; days 12–14 on integrated architecture, timed coding and mock interviews. Reorder after the learner's baseline. A 14-day sprint can improve readiness but cannot establish principal-level production experience.

A useful final capstone combines a permissioned modernization assistant, a retrieval evaluation set, one previewed deterministic transform, independently reviewed code changes, quality gates and rollback plan. Ask the learner to explain failure handling, ownership and release criteria in five minutes, then defend one disputed tradeoff. Record unproven claims honestly: proposed design, local demonstration and deployed production evidence are different states.
