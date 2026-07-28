# InsuraMind AI - Architecture

This describes what's actually implemented in this repo, not just the
original spec - where something in the spec was ambiguous or where I made
a call, it's noted here.

## Layers

```
frontend/   -> plain HTML/JS, talks to the backend over REST
backend/    -> FastAPI app: routers -> services -> models -> Postgres
agents/     -> CrewAI crews + PydanticAI agents, called only from
               backend/app/services/agent_service.py
guardrails/ -> pure Python safety checks, called from both backend
               services and agents/
rag/        -> chunking, embeddings, retrieval - used by vector_db/indexer.py
               and by agents/tools/rag_tool.py
vector_db/  -> Chroma client + the four knowledge base collections
database/   -> init.sql (runs once on first Postgres boot) + Faker seed script
```

## Why agents/guardrails/rag/vector_db aren't inside backend/

The original directory tree has them as siblings of `backend/`, not
children of it. Rather than restructure that, `docker-compose.yml` mounts
each of them into the backend container at the filesystem root
(`/agents`, `/guardrails`, `/rag`, `/vector_db`) and sets
`PYTHONPATH=/:/app`, so `import agents.orchestrator` works from
`backend/app/services/agent_service.py` without those folders needing to
physically live inside `backend/`.

## Two decisions that weren't specified in the original brief

**Vector DB: Chroma, not Pinecone.** The spec listed both as if
interchangeable. Pinecone is a managed cloud service; using it would mean
sending policy/medical embeddings to a third party, which contradicts the
spec's own reasoning for using local open-weight LLMs in the first place
(no third-party data transmission). Chroma runs self-hosted and is the
consistent choice given that reasoning.

**LLM serving: Ollama, running Llama 3 by default.** The spec named three
model options (Llama 3, Qwen 2.5, DeepSeek) without saying how any of them
get served. Ollama is the simplest way to run any of them locally with an
OpenAI-compatible API, which both CrewAI's `LLM` class and PydanticAI's
`OpenAIModel` can talk to. Swap `OLLAMA_MODEL` in `.env` to change models.

## Request flow for a claim

1. Customer submits a claim (`POST /api/v1/claims`) - saved straight to
   Postgres, no AI involved yet.
2. Customer uploads supporting documents
   (`POST /api/v1/claims/{id}/documents`) - each one runs through either
   `cv_service.assess_damage` (vehicle photos) or
   `ocr_service.check_document_quality` (everything else) immediately,
   synchronously, and the result gets appended to the claim's
   `processing_history`.
3. An agent calls `POST /api/v1/claims/{id}/run-analysis`, which runs
   both the claim adjudication crew and the fraud investigation crew via
   `agent_service.process_claim_with_agents`, and checks
   `guardrails/output_guard.requires_human_review`.
4. A human agent makes the actual call via
   `POST /api/v1/claims/{id}/decision`. No agent or crew in this system
   has write access to approve or reject a claim on its own - that's
   deliberate, see `guardrails/execution_guard.py`'s read-only DB
   restriction on agent tools.

## Not yet built

Being upfront about the gap between "designed" and "wired into an
endpoint":

- `agents/pydantic_agents/policy_recommender.py` and `kyc_verifier.py`
  aren't called from any API endpoint yet - `agent_service.py` has
  functions ready for both (`get_policy_recommendation`,
  `verify_customer_kyc`), they just need routes added, e.g. under
  `policies.py` and `customers.py`.
- The vector DB collections start empty - `vector_db/indexer.py` reads
  `.txt` files from `data/raw/policy_terms/` etc, but no actual policy
  wording or regulatory text is bundled with this repo. Drop real
  documents in those folders and run `python -m vector_db.indexer`.

## What was actually tested vs. what wasn't

See the root README's verification table - short version: everything
that's pure Python (guardrails, risk scoring) was actually executed and
two real bugs were caught and fixed that way. Everything that needs
FastAPI, SQLAlchemy, CrewAI, PydanticAI, TensorFlow, or a live Postgres
couldn't be executed in the sandbox this was built in - written correctly
against my knowledge of those APIs, but genuinely untested.
