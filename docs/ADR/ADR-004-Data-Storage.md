# ADR-004 — Data storage: Parquet + DuckDB for research, PostgreSQL for transactions

## Status
Proposed (2026-09-20).

## Context
v1 held 12.9M one-minute bars in PostgreSQL; research queries hit statement timeouts and index pitfalls (docs/lessons-from-v1.md, edge-phase0 notes). Research needs columnar scans; trading needs transactions.

## Decision
- Bars and research datasets: **Parquet** partitioned by interval/symbol/month, queried with **DuckDB**; immutable `data_snapshots` for reproducible trials.
- Everything transactional (orders, fills, positions, dossiers, ledger, memory, runtime): **PostgreSQL 16**, native on the VM.
- v1 data is imported once (export → Parquet); no re-download.

## Consequences
- Research sandboxes mount Parquet read-only.
- Backups: Postgres dumps + Parquet sync, both `age`-encrypted (v1 ADR-005 model retained).
