# ADR-005 — Deployment model (retained from v1)

## Status
Accepted by inheritance (2026-09-20).

## Decision
Docker Compose on one **Hostinger KVM VPS** (the Principal's provider; Mumbai region; static IPv4 whitelisted with Zerodha; Tailscale installed on the VPS for owner access — Hostinger KVM exposes `/dev/net/tun`, and Tailscale falls back to DERP relays if the Hostinger firewall blocks UDP 41641); native PostgreSQL; images built by GitHub Actions on tags and pulled from ghcr.io; encrypted backups off-box; two environments (paper, live) on the same VM with separate databases and accounts. Source never lives on the VM; the Git object database never lives on OneDrive (it is at `~/git-repos/dhanada-v2.git`).

## Rationale
Nothing in v1's failures was caused by this model; it is cheap and SEBI-compatible (static IP). Kubernetes remains deferred.
