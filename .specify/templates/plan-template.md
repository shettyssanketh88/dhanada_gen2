# Plan — NNN <Title>

## Approach
How the requirements are met; alternatives considered; ADRs cited or created.

## Modules
| Path | Responsibility | Tests |
|---|---|---|

## Contracts
Models, schemas, tool signatures (typed; agent outputs carry reasoning; validation = type + rails + consistency only).

## Data model and migrations

## Runtime (if roles are involved)
Role definitions touched, skills, memory scopes, budgets, hooks, evals.

## Structural checks
no LLM import under `engine/`; read-only tool registries where required; hooks; spec lint.

## Test plan
Unit (floors), integration (PostgreSQL), fault injection, evals, scenarios → test ids.

## Risks and rollback
