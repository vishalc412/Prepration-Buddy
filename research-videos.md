# Optional video and online-reference catalog

Reviewed: 7 October 2026. Catalog: `offline-reference/resources.json`.

## Verification boundary

18 distinct `youtube.com/watch?v=...` links cover all 18 subjects. Identity checks used indexed YouTube title/creator metadata and, where available, publisher or creator pages linking the exact video. Some direct YouTube fetches returned bot/cache errors; this review does not certify playback in every region, every lesson in a long course, transcript accuracy or current framework compatibility. No durations or timecodes were invented. Duration words occurring in a video title are part of the identified title.

The catalog is authored guidance, not a course-quality benchmark or interview guarantee. Videos and documentation are optional external links. They need internet only when opened. Bundled explanations, questions, hints, quizzes, references and JavaScript interactions remain local; no iframe, autoplay or remote fetch is needed to render them.

## Identified videos

| Subject | Identified video / creator | Identity evidence |
|---|---|---|
| python | [Watch python topic video](https://www.youtube.com/watch?v=rfscVS0vtbw) — freeCodeCamp.org / Mike Dane | [YouTube title/uploader metadata; publisher learning-resource listing](https://www.freecodecamp.org/news/the-best-way-to-learn-python-python-programming-tutorial-for-beginners/) |
| async | [Watch async topic video](https://www.youtube.com/watch?v=K56nNuBEd0c) — Socratica | [YouTube creator/title metadata](https://www.youtube.com/watch?v=K56nNuBEd0c) |
| fastapi | [Watch fastapi topic video](https://www.youtube.com/watch?v=0sOvCWFmrtA) — freeCodeCamp.org / Sanjeev Thiyagarajan | [Publisher article identifies instructor and course](https://www.freecodecamp.org/news/creating-apis-with-python-free-19-hour-course) |
| django | [Watch django topic video](https://www.youtube.com/watch?v=PtQiiknWUcI) — Traversy Media / Dennis Ivy | [Publisher-owned repository links the exact tutorial ID](https://github.com/Traversy-Media/StudyBud) |
| flask | [Watch flask topic video](https://www.youtube.com/watch?v=Z1RJmh_OqeA) — freeCodeCamp.org / Coding with Jake | [YouTube uploader/title metadata](https://www.youtube.com/watch?v=Z1RJmh_OqeA) |
| statistics | [Watch statistics topic video](https://www.youtube.com/watch?v=vikkiwjQqfU) — StatQuest with Josh Starmer | [Creator video index and YouTube title metadata](https://statquest.org/video_index.html) |
| ml | [Watch ml topic video](https://www.youtube.com/watch?v=i_LwzRVP7bg) — freeCodeCamp.org / Kylie Ying | [Publisher article identifies instructor and embeds exact video ID](https://www.freecodecamp.org/news/machine-learning-for-everybody) |
| pytorch | [Watch pytorch topic video](https://www.youtube.com/watch?v=V_xro1bcAuA) — freeCodeCamp.org / Daniel Bourke | [Instructor publisher article links exact course ID](https://www.freecodecamp.org/news/learn-pytorch-for-deep-learning-in-day/) |
| transformers | [Watch transformers topic video](https://www.youtube.com/watch?v=kCc8FmEb1nY) — Andrej Karpathy | [YouTube creator/title metadata](https://www.youtube.com/watch?v=kCc8FmEb1nY) |
| llm | [Watch llm topic video](https://www.youtube.com/watch?v=7xTGNNLPyMI) — Andrej Karpathy | [YouTube creator/title metadata](https://www.youtube.com/watch?v=7xTGNNLPyMI) |
| rag | [Watch rag topic video](https://www.youtube.com/watch?v=sVcwVQRHIc8) — freeCodeCamp.org / Lance Martin | [YouTube uploader/title metadata](https://www.youtube.com/watch?v=sVcwVQRHIc8) |
| agents | [Watch agents topic video](https://www.youtube.com/watch?v=LP5OCa20Zpg) — Anthropic | [YouTube creator/title/description metadata](https://www.youtube.com/watch?v=LP5OCa20Zpg) |
| mlops | [Watch mlops topic video](https://www.youtube.com/watch?v=-dJPoLm_gtE) — freeCodeCamp.org | [Publisher article links exact course ID](https://www.freecodecamp.org/news/mlops-course-learn-to-build-machine-learning-production-grade-projects/) |
| cloud | [Watch cloud topic video](https://www.youtube.com/watch?v=7HKot-brXFE) — freeCodeCamp.org / Andrew Brown | [Publisher article links current titled course ID](https://www.freecodecamp.org/news/aws-certified-cloud-practitioner-study-course-pass-the-exam-with-this-free-13-hour-course/) |
| security | [Watch security topic video](https://www.youtube.com/watch?v=dq5jD_qE1Cg) — Vandana Verma | [YouTube creator/title metadata and creator series announcement](https://www.linkedin.com/posts/vandana-verma_owasp-top-10-for-llm03-supply-chain-vulnerabilities-activity-7366457628773842945-4z-s) |
| java | [Watch java topic video](https://www.youtube.com/watch?v=eIrMbAQSU34) — Programming with Mosh | [Named course resource identifies creator and topic](https://www.freecodecamp.org/news/learn-java-free-java-courses-for-beginners) |
| leadership | [Watch leadership topic video](https://www.youtube.com/watch?v=jMpCF0Z623s) — Continuous Delivery / Dave Farley | [YouTube title/description identifies Dave Farley and channel](https://www.youtube.com/watch?v=jMpCF0Z623s) |
| evaluation | [Watch evaluation topic video](https://www.youtube.com/watch?v=7EcznH0-of8) — DeepLearning.AI / Weights & Biases workshop | [YouTube title/description plus first-party workshop announcement](https://www.linkedin.com/posts/deeplearningai_join-us-on-august-15-for-an-exclusive-webinar-activity-7093606606382252032-TCjO) |

## Current primary references

Documentation links below were opened during this review. Use installed-version documentation for executable work, especially older FastAPI, Django, Flask, LangChain, PyTorch and MLOps videos. Framework reference assignments include tested dependency pins; that is separate from upstream latest documentation. LangChain retrieval/RAG links currently resolve into Deep Agents documentation, so this catalog uses those resolved URLs and labels their current scope explicitly.

- python: [Python official tutorial](https://docs.python.org/3/tutorial/).
- async: [asyncio tasks, cancellation and timeouts](https://docs.python.org/3/library/asyncio-task.html).
- fastapi: [FastAPI tutorial and user guide](https://fastapi.tiangolo.com/tutorial/).
- django: [Django 5.2 official tutorial](https://docs.djangoproject.com/en/5.2/intro/tutorial01/).
- flask: [Flask stable official tutorial](https://flask.palletsprojects.com/en/stable/tutorial/).
- statistics: [NIST/SEMATECH statistical methods handbook](https://www.itl.nist.gov/div898/handbook/).
- ml: [scikit-learn preprocessing and leakage pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).
- pytorch: [PyTorch Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro.html).
- transformers: [Hugging Face LLM course: transformer models](https://huggingface.co/learn/llm-course/chapter1/1).
- llm: [Claude prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview).
- rag: [LangChain retrieval concepts and current APIs](https://docs.langchain.com/oss/python/deepagents/retrieval).
- agents: [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
- mlops: [MLflow machine-learning documentation](https://mlflow.org/docs/latest/ml/).
- cloud: [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html).
- security: [OWASP Gen AI security risk catalog](https://genai.owasp.org/llm-top-10/).
- java: [Oracle JDK 25 Migration Guide](https://docs.oracle.com/en/java/javase/25/migrate/index.html).
- leadership: [Google SRE: Organizational Change Management](https://sre.google/workbook/organizational-change/).
- evaluation: [Ragas evaluation metric overview](https://docs.ragas.io/en/stable/concepts/metrics/overview/).

## Teaching use

Choose one topic relevant to the current lesson, watch selectively, then close the video and explain the mechanism from memory. Implement or debug the bundled scenario and compare against its authored checks. Allocate viewing within guided-learning time; do not consume all six daily hours with passive video. Skip beginner refreshers when baseline evidence already shows mastery.

ML video contains some TensorFlow material; bundled implementation scope remains Python, Java, scikit-learn and PyTorch. RAG or agent videos can call remote models; bundled deterministic fixtures do not require them and do not claim semantic generation quality. The statistics video focuses on population estimates, Java video is a language refresher and leadership video is a technical-team discussion; their topic notes do not pretend each covers an entire subject.

All 14 curriculum days and eight scenario tracks map explicitly to catalog subjects. Parent integration attaches the mapped optional resources to individual learning views; this memo verifies the catalog, not browser-link rendering.
