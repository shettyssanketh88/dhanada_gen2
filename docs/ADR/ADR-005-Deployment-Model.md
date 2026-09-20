# ADR-005 — Deployment model (retained from v1)

## Status
Accepted by inheritance (2026-09-20).

## Decision
Docker Compose on one Mumbai VM with a whitelisted static IP; native PostgreSQL; images built by GitHub Actions on tags and pulled from ghcr.io; encrypted backups off-box; two environments (paper, live) on the same VM with separate databases and accounts. Source never lives on the VM; the Git object database never lives on OneDrive (it is at `~/git-repos/dhanada-v2.git`).

## Rationale
Nothing in v1's failures was caused by this model; it is cheap and SEBI-compatible (static IP). Kubernetes remains deferred.
