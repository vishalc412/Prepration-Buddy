# Independent curated-video review

Verdict: **PASS within the checks below**. No unresolved content or runtime blocker found. This does not certify playback availability, captions, regional access, every tutorial code line, teaching quality or interview success.

Reviewer edited only `offline-reference/validate_videos.py` and this report. Checks do not access learner browser storage, play/download media, provision packages or call models.

## Executed reviewer checks

- `python3 offline-reference/validate_videos.py --self-test`: **13 URL boundary cases and 7 merge/metadata rejection cases PASS**. Invalid domains, insecure schemes, search/channel/embed URLs, short or duplicate video IDs, conflicting query identity, missing playlist identity, credentials, lost merge fields, boolean days, unverifiable status and empty evidence are rejected.
- `python3 offline-reference/validate_videos.py --html`: **45 authored records, 45 unique direct destinations, 30/30 day mappings, source-to-HTML metadata parity and exact runtime inclusion PASS**. No duplicate destination merges were necessary; aliases and union preservation are exercised by meaningful synthetic merge fixtures.
- Isolated Node executes the actual guidance/card/JD/case renderer source against the embedded data: **226 outputs, 2,171 anchors, zero active YouTube search anchors, zero missing focused panels and zero video/media embeds**. Outputs include all 155 lesson modules, 50 client questions, 8 JD drills, 4 cases, 8 framework/scenario tracks and the library. All 155 compact teacher-sidebar companions also render one selected canonical destination with no search or embed. These are reviewer renderer checks, not browser interaction proof.
- Runtime source contains no fetch, streaming network client, iframe, thumbnail load or model call. Video save/review controls use video note keys. They do not update lesson mastery or scores. Publisher-derived Moderne title labels remain visibly disclosed rather than presented as retrieved exact video display titles.

## Content and provenance review

Each entry supplies creator/title attribution, a viewing question, a distinct practical task, source evidence and limitations. Provider examples can require online services, but the assigned local follow-up uses code, fixed fixtures or a design/teach-back. These authored follow-ups are not misrepresented as exercises supplied by the recordings. Long courses are selective references within existing learning time, not an extra mandatory course per tagged day.

Reviewer independently inspected first-party publisher/creator evidence for the [freeCodeCamp API course](https://www.freecodecamp.org/news/creating-apis-with-python-free-19-hour-course/), [StatQuest index](https://statquest.org/video_index.html), [Karpathy creator repository](https://github.com/karpathy/nn-zero-to-hero), [Moderne demo](https://www.moderne.ai/downloads/running-your-first-recipe-on-the-moderne-platform-video), [Stanford MoE/inference schedule](https://cs336.stanford.edu/spring2025/index.html), [Mamba coauthor discussion](https://www.cognitiverevolution.ai/the-state-space-model-revolution-with-albert-gu/), [Pinecone HNSW tutorial](https://www.pinecone.io/learn/series/faiss/hnsw/), [Neo4j graph lesson](https://neo4j.com/videos/going-meta-a-series-on-graphs-semantics-and-knowledge/), [OWASP FinBot learning page](https://genai.owasp.org/learning/agentic-ai-capture-the-flag-ctf-finbot-demo-goal-manipulation/) and accompanying reviewed publisher/presenter repositories. Allowlisted GitHub and LinkedIn entries are scoped to reviewed paths. A hostname/schema check alone is not proof of every publication's identity.

MoE uses a dedicated Stanford lecture; sparse activation is correctly separated from total model storage and communication costs. Mamba uses a coauthor discussion with state and inference chapters, correctly labeled a discussion rather than a coding course. The [Microsoft historical talk](https://www.microsoft.com/en-us/research/video/ai-forum-2023-future-of-foundation-models/) names BitNet, but predates b1.58. Its caution explicitly records the focused implementation-video gap. Generic quantization content is not mislabeled as BitNet. FinBot is an attack demonstration and is not claimed to teach complete payment controls or banking compliance. Neo4j basic inference is not claimed to be a complete OWL 2 reasoner.

Resolved findings: initial HTML omitted later exact title/uploader corrections for MITCBMM, CoreWeave and the LLMOps Bootcamp title; the final build matches both frozen shards. An older security-series memo attached an unrelated LLM03 supply-chain announcement to `dq5jD_qE1Cg`. The current researcher indexed receipt identifies the exact LLM01 prompt-injection title/creator; reviewer independently opened the [creator article](https://www.linkedin.com/pulse/prompt-injection-owasp-top-10-llm-vandana-verma-hppcc), corroborating title, author and date. Reviewer's direct YouTube page retrieval was unavailable. Publication identity/topic corroboration remains distinct from playback.

## Verification boundary and artifact identity

The final local UI remains usable without optional online links. No availability or fabricated numeric quality score is inferred from index or oEmbed metadata. The source researcher checked the complete identity/topic catalog; this reviewer independently checked selected publication provenance, metadata integrity, topical limits and rendered offline mechanisms. Parent browser receipt `output/video-browser-validation.json` is separately observed PASS against the same final artifact SHA256: all 45 library entries, 30 day views, 50 client questions, 8 JD drills, 4 cases, saved/reviewed filters, backup/import/reload, three viewports (1440/847/390), zero runtime errors and zero remote/offline requests. It reports no missing track or lesson mapping and preserves learner storage through an isolated context. These browser actions were executed by the parent, not by this reviewer. Parent focused receipt `output/video-gate-validation.json` is separately observed PASS: marking a video reviewed does not unlock client answers, case reference gates remain effective, teacher sidebar guidance stays compact, zero runtime errors and learner storage untouched. No pending review check remains.

Artifact: `index.html`, **2,036,349 bytes**, SHA256 `b4e76dec8d2822c4c09f8814be871abd9deb5b775ad4463823e6e5b9e9ca6e1b`.

Source fingerprints:

- `video-foundations.json`: `561de5bc96e3016387efa228a7766aba617394eb72a9343bd37380d633b41e1c`
- `video-advanced.json`: `6020cd2d8c8f6256d501f5a50551c682d90a4e3fa83effefc4d9e97b9a92ffb2`
- `video-studio.js`: `91e2018ad39a84140c5cb4cdc6d8af82384a2dd1eadf98c2583bac48c9183036`
