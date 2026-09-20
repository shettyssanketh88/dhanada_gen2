# ADR-003 — Memory storage: PostgreSQL truth, git-backed markdown projection, no embeddings in v2.0

## Status
Proposed (2026-09-20).

## Context
Per-trade, per-role memory with outcome embargo and versioning is required (spec DH2-MEM-*). Options: Managed Agents memory stores; vector databases; plain files; PostgreSQL.

## Decision
- Dossiers, sections, evidence, memory items and retrieval logs live in **PostgreSQL** (versioned rows, `known_at`, hash chain).
- Role, desk and ops memory are **git-backed markdown** (`memory/`) mirrored into PostgreSQL for search; agents read them as files and write through tools that enforce scope.
- Retrieval uses PostgreSQL full-text search (BM25-like ranking) plus recency decay; deterministic and auditable. Embeddings (pgvector) are deferred until recall is shown to be insufficient (Phase 5.2).
- Lessons are stored with verbatim evidence links (arXiv 2601.00821); status `hypothesis|validated|retired`; only validated lessons reach trading prompts.

## Consequences
- Point-in-time reads and embargo are SQL predicates, testable.
- No external memory service; backups are the existing DB + git.
