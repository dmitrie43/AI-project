# Hybrid retrieval — short note (Week 5E deliverable)

## When keyword (BM25)

Use for exact tokens: Wi‑Fi SSIDs, ticket IDs, error codes, API names.  
Example: query `CorpWiFi` → lexical match beats a vague semantic guess.

## When vector

Use for natural-language paraphrase.  
Example: “I cannot reach the company network from home” → `vpn-reset.md` without sharing many keywords.

## When hybrid (default)

Users ask both ways. Run BM25 + dense, fuse with **RRF** (rank-based), return top-k.  
Do not average raw BM25 and cosine — scales differ.

In this repo: `search_hybrid()` in `app/retrieval/hybrid.py`.

## Why retrieval before the LLM (RAG)

Internal Assistant must answer from **our** runbooks, with **citations**.  
Retrieve first → put chunks in context → generate. Less hallucination, updatable docs, auditable sources.

## RAG ≠ fine-tune

| RAG | Fine-tune |
|-----|-----------|
| Swap/reindex docs | Change model weights |
| Fast fact updates | Slow/costly; bad for weekly wiki edits |
| Right default for internal docs pilot | Later, only if style/domain needs it |

## Later (not this week)

Chunk size/overlap, dedicated reranker, Qdrant/pgvector filters, multi-tenant ACL — weeks 7–10 / JD gap work.
