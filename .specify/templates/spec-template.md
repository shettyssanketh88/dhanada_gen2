# Feature NNN — <Title>

| Field | Value |
|---|---|
| Feature id | `NNN-<name>` |
| Phase / task | `<phase.task>` in `specs/000-platform/tasks.md` |
| Parent requirements | DH2-… |
| Status | draft · clarifying · ready · implementing · done |
| Companion docs | which of `000-platform/*.md` govern this feature |

## 1. Purpose
One paragraph: what this feature lets the firm do and which v1 failure or platform requirement it serves (`docs/lessons-from-v1.md`).

## 2. Scope
In scope / out of scope. Which roles (agents) and which code components are touched. State explicitly which decisions remain agentic and which actions are deterministic (constitution I and VI).

## 3. Requirements (EARS)
- **DH2-<AREA>-<nnn>.1** WHEN … THE SYSTEM SHALL …
- **DH2-<AREA>-<nnn>.2** WHILE … THE SYSTEM SHALL …
- **DH2-<AREA>-<nnn>.3** IF … THEN THE SYSTEM SHALL …

## 4. Acceptance scenarios
- **F1** Given … When … Then …
- **F2** …

## 5. Contracts and data
Pydantic models / JSON schemas added or changed (`contracts/`), tables and migrations, events on the firm bus, tools exposed (name, scope, read/write, reason enums).

## 6. Rails and compliance touchpoints
Which rails this feature evaluates or must respect; which rule-catalogue rows (A*/B*) apply; what the Compliance Officers pre-clear.

## 7. Clarifications
- [NEEDS CLARIFICATION: …] — owner, due before tasks are written.

## 8. Non-goals
