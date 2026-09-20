# State of the art (2025–2026) for skill-based, memory-durable, spec-driven agentic systems — and what transfers to an always-on trading desk

*Research date: 2026-09-20. ~40 sources fetched; official docs preferred. Sections 1–7 give facts; the final section gives design recommendations tied to sources. Feeds `specs/000-platform/plan.md`, `skills.md`, `memory.md` and ADR-001/002/003.*

## 1. Anthropic Agent Skills

**Open spec (agentskills.io, Dec 2025).** A skill = directory with `SKILL.md` (YAML frontmatter + Markdown) plus optional `scripts/`, `references/`, `assets/`. Frontmatter: `name` (required, ≤64 chars, `a-z0-9-`, no leading/trailing/double hyphens, must match directory name), `description` (required, ≤1024 chars, "what it does and when to use it"), optional `license`, `compatibility` (≤500 chars), `metadata` (string map), `allowed-tools` (space-separated, experimental, e.g. `Bash(git:*) Bash(jq:*) Read`). Validate with `skills-ref validate ./my-skill`. https://agentskills.io/specification , https://github.com/agentskills/agentskills

**Progressive disclosure (three tiers, per spec):** (1) metadata ~100 tokens loaded for all skills at startup; (2) full SKILL.md body (<5000 tokens recommended) loaded on activation; (3) resources loaded only when needed. "Keep your main SKILL.md under 500 lines"; "Keep file references one level deep from SKILL.md."

**Anthropic best practices (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):**
- "The context window is a public good"; "Default assumption: Claude is already very smart" — only add what Claude lacks.
- **Degrees of freedom**: high (prose heuristics) for open tasks; low ("Run exactly this script… Do not modify the command") for fragile/sequenced operations.
- Description in third person, with trigger keywords; name in gerund form (`processing-pdfs`); reserved words `anthropic`/`claude` forbidden.
- Workflows as copyable checklists; **feedback loops** ("Run validator → fix errors → repeat"); **plan-validate-execute** with a machine-verified intermediate file ("changes.json") for batch/destructive/high-stakes ops.
- Scripts: "Prefer scripts for deterministic operations"; "Solve, don't defer"; no "voodoo constants"; state explicitly whether to *execute* or *read* a script; only script output consumes tokens.
- MCP tool refs must be fully qualified `ServerName:tool_name`.
- **Evaluation-driven**: "Create evaluations BEFORE writing extensive documentation"; ≥3 evals; test on Haiku/Sonnet/Opus; eval JSON `{skills, query, files, expected_behavior[]}`.
- Claude A / Claude B iteration loop (author with one instance, test with a fresh one).

**Claude Code skill runtime (code.claude.com/docs/en/skills).** Locations: enterprise managed, `~/.claude/skills/`, `.claude/skills/`, nested `<subdir>/.claude/skills/`, plugins (`/plugin:skill`). Extra frontmatter: `disable-model-invocation: true` (only user can invoke — recommended for deploy/commit/send-money style skills), `user-invocable: false` (background knowledge only Claude triggers), `paths` (glob-scoped auto-activation), `allowed-tools`/`disallowed-tools`, `context: fork` + `agent:` + `background:` (run in isolated subagent), `model`, `effort`, `hooks` (hooks registered on invocation), `arguments`, `argument-hint`. Substitutions: `$ARGUMENTS`, `$0`, `$name`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`. Dynamic context injection: `` !`gh pr diff` `` runs before render. Permission rules: `Skill(deploy *)` allow/deny; `skillOverrides` in settings. Skill content survives compaction (most recent invocations kept).

**Loading in the Agent SDK**: skills, commands, and CLAUDE.md load from `.claude/` and `~/.claude/` when `setting_sources=["project"]` (Python) / `settingSources: ['project']`; `setting_sources=[]` = SDK-only, no filesystem settings. Plugins (`plugins=[...]`) bundle skills+agents+hooks+MCP by local path. https://code.claude.com/docs/en/agent-sdk/overview , https://code.claude.com/docs/en/agent-sdk/skills

**Managed Agents**: an "Agent" object = model + system prompt + tools + MCP servers + skills; skills also uploadable via the Skills API. https://platform.claude.com/docs/en/managed-agents/overview

**skill-creator**: bundled in `anthropics/skills`; supports create/edit, running evals, benchmarking variance and description-triggering optimisation. https://github.com/anthropics/skills

## 2. Claude Agent SDK (2026) + Claude Code autonomy features

**Positioning**: "Build production AI agents with Claude Code as a library"; Python/TypeScript; other languages drive `claude -p --output-format json`. Managed Agents is a separate hosted product. https://code.claude.com/docs/en/agent-sdk/overview

**`ClaudeAgentOptions` (Python; https://code.claude.com/docs/en/agent-sdk/python):**
- Permissions: `allowed_tools`, `disallowed_tools` (`"Bash(rm *)"` patterns), `permission_mode` ∈ `default|acceptEdits|plan|dontAsk|bypassPermissions|auto`, `can_use_tool` callback → `PermissionResultAllow(updated_input=…)` / `PermissionResultDeny(message, interrupt=True)`.
- Subagents: `agents={name: AgentDefinition(description, prompt, tools, disallowedTools, model, skills, memory∈user|project|local, mcpServers, maxTurns, background, effort, permissionMode)}`. Subagent transcripts persist independently and survive parent compaction.
- Custom in-process tools: `@tool(name, description, input_schema, annotations=ToolAnnotations(readOnlyHint, destructiveHint, idempotentHint, openWorldHint))` + `create_sdk_mcp_server(name, version, tools=[...])`; reference as `mcp__<server>__<tool>`.
- `mcp_servers={...}` (stdio/http/sse/in-process), `hooks={HookEvent: [HookMatcher]}`, `plugins`, `setting_sources`, `system_prompt={"type":"preset","preset":"claude_code","append":…}`, `cwd`, `env`, `sandbox: SandboxSettings`, `enable_file_checkpointing`.
- Cost controls: `max_turns`, `max_budget_usd` (run ends with `error_max_budget_usd`), `effort`, `thinking`; `ResultMessage.total_cost_usd`, `.usage`, `.session_id`.
- Structured output: `output_format={"type":"json_schema","schema":…}` → `structured_output`.
- Sessions: `continue_conversation`, `resume=<id>`, `fork_session`, `resume_session_at`; `ClaudeSDKClient` for in-process multi-turn. Transcripts at `~/.claude/projects/<encoded-cwd>/*.jsonl`; docs' advice: "Don't rely on session resume… capture the results you need… as application state." https://code.claude.com/docs/en/agent-sdk/sessions

**Hooks (https://code.claude.com/docs/en/hooks).** Events: `SessionStart/End`, `UserPromptSubmit`, `PreToolUse` (can block), `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `Stop`, `StopFailure`, `SubagentStart/Stop`, `PreCompact/PostCompact`, `TaskCreated/Completed`, `Notification`, `Elicitation`, etc. Handler types: `command` (stdin JSON; exit 2 = block with stderr reason; JSON `hookSpecificOutput.permissionDecision: allow|deny`, `updatedInput`, `additionalContext`), `http`, `mcp_tool`, `prompt` (single-shot LLM judge, 30 s), `agent` (subagent with Read/Grep/Glob, 60 s). Matchers: tool names, regex, `mcp__server__.*`, `if: "Bash(rm *)"`. Config in settings files or managed policy (cannot be disabled by users). Key doc line: CLAUDE.md is "context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook."

**Headless (https://code.claude.com/docs/en/headless).** `claude -p … --output-format json|stream-json --json-schema … --allowedTools … --permission-mode auto|dontAsk|acceptEdits --permission-prompts none --append-system-prompt … --resume <id> --bare` (skips hooks/skills/MCP/auto-memory/CLAUDE.md discovery; "recommended mode for scripted and SDK calls"). Exit codes: 0 success, 143 on SIGTERM. JSON result includes `total_cost_usd`, `permission_denials`.

**Scheduling.** Three tiers (https://code.claude.com/docs/en/scheduled-tasks): `/loop` in-session; Desktop scheduled tasks; **Routines** (cloud; https://code.claude.com/docs/en/routines) — cron (min 1 h), API fire, GitHub events; fresh clone, no local files. **Managed Agents scheduled deployments** (https://platform.claude.com/docs/en/managed-agents/scheduled-deployments): POSIX cron + IANA timezone, minute granularity, jitter ≤15 % of interval (max 9 min), per-run `budget`, deployment-run records with error types, pause/unpause/archive, webhooks.

**Managed Agents (beta `managed-agents-2026-04-01`)**: Agent / Environment (cloud or self-hosted sandbox) / Session / Events; SSE streaming, steer/interrupt; not ZDR-eligible. Memory stores: workspace-scoped file collections mounted at `/mnt/memory/<slug>/`, `access: read_only|read_write`, ≤8 per session, 100 kB per memory, immutable versions, `content_sha256` optimistic-concurrency updates. Warning in docs: prompt injection can poison a `read_write` store that later sessions trust. https://platform.claude.com/docs/en/managed-agents/memory

**CLAUDE.md + auto-memory (https://code.claude.com/docs/en/memory).** CLAUDE.md hierarchy (managed/user/project/local, `.claude/rules/` path-scoped, AGENTS.md support; "shorter files produce better adherence"). Auto memory: `MEMORY.md` index + topic files with frontmatter `type: user|feedback|project|reference`; first 200 lines / 25 KB of MEMORY.md loaded each session; topic files read on demand. Subagents get their own memory via frontmatter `memory: project` (stored at `~/.claude/agent-memory/<project>/<agent>/`).

**Dynamic workflows**: "A harness for every task" describes Claude writing JS orchestration scripts to spawn subagents with named patterns — classify-and-act, fan-out-and-synthesize, adversarial verification, generate-and-filter, tournament, loop-until-done, model routing — to fight "agentic laziness", "self-preferential bias", and "goal drift". https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code

## 3. Agent memory architectures

**CoALA taxonomy** (Sumers et al., arXiv 2309.02427): working memory (current decision cycle), episodic (past experiences), semantic (world facts), procedural (how-to, in code or weights); internal actions (reason/retrieve/learn) vs external actions; plan-execute-observe loop.

**Anthropic memory tool** (`{"type":"memory_20250818","name":"memory"}`, client-side): commands `view`, `create`, `str_replace`, `insert`, `delete`, `rename` under `/memories`; auto-injected instruction: "ALWAYS VIEW YOUR MEMORY DIRECTORY BEFORE DOING ANYTHING ELSE… ASSUME INTERRUPTION"; pair with context editing (`clear_tool_uses_20250919`, `clear_thinking_20251015`) and server-side compaction. Documented "multisession software development pattern": initializer session creates progress log + feature checklist; each session reads them first, works on one feature, marks complete only after end-to-end verification. https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool

**Effective harnesses for long-running agents** (Anthropic): initializer agent writes `init.sh`, `claude-progress.txt`, a JSON feature list, initial git commit; coding agent each session reads git log + progress file, picks highest-priority incomplete feature, runs an end-to-end smoke test before new work. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

**Letta/MemGPT**: memory blocks edited via `core_memory_append/replace`; tiers core (in-context) / recall / archival; **sleep-time compute** = a separate agent curates the primary agent's memory asynchronously. https://www.letta.com/blog/sleep-time-compute/

**Mem0** (arXiv 2504.19413): extraction+consolidation of facts. **Zep/Graphiti** (arXiv 2501.13956): temporal knowledge graph with bi-temporal validity per fact. **A-MEM** (arXiv 2502.12110): Zettelkasten-style notes with LLM-generated links.

**Evidence on what helps (be skeptical of vendor benchmarks):**
- "Verbatim Chunks Beat Extracted Artifacts" (arXiv 2601.00821, controlled ablation): verbatim chunks beat LLM-extracted facts by 15.9 pts on LoCoMo and 22.0 on LongMemEval-S; "extraction commits to relevance before questions are known"; recommend `chunks ∪ artifacts`, never artifacts alone.
- Reflexion (verbal RL) and Generative Agents (observation stream + periodic reflection + retrieval scored by recency/importance/relevance) remain the reference designs; the transferable idea from RLVR is *verifiable outcome signals feeding the reflection loop*, not weight updates.
- Anthropic context engineering: agents "maintain lightweight identifiers (file paths, URLs, queries)" and fetch just-in-time; structured note-taking outside context; sub-agents return 1–2k-token summaries. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Manus lessons: stable prompt prefix for KV-cache (10× cost difference), mask tools don't remove them, file system as unlimited context, recite `todo.md`, "keep the wrong stuff in", avoid few-shot ruts. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus

## 4. Spec-Driven Development

**GitHub Spec Kit** (github.com/github/spec-kit; v1.0.1 Aug 2026). CLI `specify init <project> --integration <agent>`; commands `/speckit-constitution` (once per project), then `/speckit-specify → /speckit-plan → /speckit-tasks → /speckit-implement → /speckit-converge` per feature. Layout: `.specify/memory/constitution.md`, `specs/###-feature/{spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md, tasks.md}` with `[P]` parallel markers; `[NEEDS CLARIFICATION: …]` markers must be resolved before a spec is complete. Constitution articles: Library-First, CLI Interface, Test-First, Simplicity, Anti-Abstraction, Integration-First. https://github.com/github/spec-kit/blob/main/spec-driven.md

**AWS Kiro** (kiro.dev/docs/specs): `requirements.md` (user stories + EARS acceptance criteria), `design.md`, `tasks.md`. EARS patterns: `WHEN <event> THE SYSTEM SHALL <response>`, `IF <precondition> THEN…`, `WHILE <state>…`, `WHERE <context>…`; one requirement per statement, measurable, error conditions explicit.

**Tessl** (tessl.io): Spec Registry and Tessl Framework (specs live in repo "as long-term memory… pairing with tests to enforce guardrails").

**Writing specs agents implement reliably** (synthesis): EARS-style testable clauses; acceptance scenarios that become tests and eval tasks; explicit non-goals; contracts (schemas) in `contracts/`; clarification markers instead of silent assumptions; constitution for non-negotiables that plan/tasks must cite.

## 5. Harness / context engineering, durability, guardrails, evals, observability

**OpenAI "Harness engineering"** (Feb 2026): ~1M LOC, zero hand-written lines; AGENTS.md as a short map into a `docs/` knowledge base; mechanical enforcement of dependency layers via custom linters/structural tests; agents get telemetry access; "garbage collection" agents fix doc drift. https://developers.openai.com/blog/codex-as-a-platform

**Martin Fowler "Harness engineering"**: guides (feedforward) vs sensors (feedback); computational (deterministic) vs inferential (LLM) sensors; shift cheap checks left. https://martinfowler.com/articles/harness-engineering.html

**Anthropic "Building effective agents"**: workflows (predefined code paths) vs agents (model-directed); patterns prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer; "poka-yoke your tools". **Multi-agent research system**: orchestrator + parallel subagents beat single Opus by 90.2 %; multi-agent uses ~15× chat tokens; "durable execution with error resumption from checkpoints rather than full restarts"; LLM-judge with single 0–1 score + pass/fail was most consistent. https://www.anthropic.com/engineering/multi-agent-research-system

**Durable execution**: Temporal (OpenAI Agents SDK integration GA March 2026; Claude tool-calling cookbook), Inngest, Restate, DBOS (Postgres-backed). Pattern: each LLM call and each tool call = an activity with idempotency key; human approval = durable signal/wait.

**Human-in-the-loop / permissions**: Agent SDK `can_use_tool` + `PermissionRequest` hooks; `--permission-prompts none` for unattended runs. **Policy-as-code**: OPA/Rego (or Cedar) in front of the tool gateway; a probabilistic LLM filter "cannot guarantee absolute compliance" for financial systems (arXiv 2604.01483).

**Sandboxing**: Claude Code `/sandbox` (bubblewrap/Seatbelt); API code execution tool (no network, pandas/numpy/scipy/statsmodels/sklearn preinstalled); E2B Firecracker microVMs.

**Evals** (Anthropic "Demystifying evals for AI agents", Jan 2026): "grade what the agent produced, not the path it took"; check environment state; calibrate LLM judges against humans; pass@k vs pass^k (reliability); evals as CI on every commit/model upgrade; start with 20–50 realistic tasks from real failures. Tools: Braintrust, LangSmith, promptfoo (Claude Agent SDK provider), Langfuse.

**Observability**: OTel GenAI semconv (v1.42.0, June 2026), experimental; spans `invoke_agent` → `chat` → `execute_tool`; attributes `gen_ai.request.model`, `gen_ai.usage.input_tokens/output_tokens`; content capture opt-in. https://opentelemetry.io/blog/2026/genai-observability/

## 6. MCP in 2026

**Zerodha kite-mcp-server** (github.com/zerodha/kite-mcp-server, Go, MIT): tools `login`, quotes/LTP/OHLC/historical/instrument search, profile/margins/holdings/positions, `place_order/modify_order/cancel_order/get_orders/get_trades`, GTT tools. Hosted `https://mcp.kite.trade/mcp` "excludes potentially destructive trading operations"; self-hosted needs `KITE_API_KEY/KITE_API_SECRET`, `APP_MODE=stdio|http|sse|hybrid`, `EXCLUDED_TOOLS="place_order,modify_order,cancel_order"` for read-only instances. It uses a Kite Connect app key — the same credential class as the OAuth login (v1 saw a token collision when two processes shared one key).

**Spec security best practices** (modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices): confused-deputy, token passthrough forbidden, SSRF, session IDs never used for auth, local servers sandboxed, **scope minimisation**. Tool annotations are hints, not enforcement. Tool poisoning via descriptions → pin/allowlist tool descriptions, log every invocation.

**Tools vs skills division**: tools (MCP) = capabilities with schemas, executed by code; skills = procedural knowledge on *how/when* to use tools and scripts, loaded lazily.

## 7. Deterministic control patterns

- **"LLM decides category, code decides numbers"** — the model emits `{ticker, side, thesis, confidence, hold/no-op}`; code computes size/stops/limits and validates against risk rules.
- **Typed structured outputs**: Claude `output_config.format = {type: json_schema, schema}` (constrained decoding; `additionalProperties:false` required; no numeric min/max — validate ranges in Pydantic) and `strict: true` tool schemas; SDK `output_format`; CLI `--json-schema`.
- **Policy-as-code gate** between agent and broker tool, evaluated by code before any order API call; log allow/deny with correlation IDs.
- **Pre-registration by agents**: Vaccaro, "Preregistration for Experiments with AI Agents" (ICML 2026, arXiv 2606.11217); "Mitigating LLM-based p-Hacking by Preregistering" (arXiv 2606.27687). Kinlay (Sept 2026): on zero-alpha synthetic data an agent reported in-sample Sharpe 2.12; "88% of that number is accounted for by two integers — how many backtests the agent ran, and how many of the winners it blended"; log N *and* aggregation depth k; build a zero-alpha calibration surface; commit analysis plans to git before running. https://jonathankinlay.com/2026/09/a-sharpe-of-2-1-from-nothing-the-second-number-your-agent-doesnt-log/
- **Propose-then-verify**: plan-validate-execute; hooks of type `prompt`/`agent` as Stop-time judges; adversarial verification subagents.
- **Cost governance**: `max_budget_usd`, `max_turns`, per-run budgets, prompt caching (stable prefix), model routing, `total_cost_usd` in every result for ledgering.

## Design implications for an agentic trading desk

1. **Two planes, hard boundary.** LLM agents never hold broker write credentials; order execution is a deterministic Python service behind a typed API.
2. **Agents produce a typed proposal, code turns it into orders.** Structured outputs for `{symbol, side, thesis, horizon, confidence, invalidation}`; Pydantic validates ranges; sizing, stops and SEBI limits computed in code.
3. **Policy gate as code, not prompt**, between proposal and execution; every decision logged with a correlation id.
4. **Run Kite MCP read-only for agents** (`EXCLUDED_TOOLS` for all order/GTT writes); the execution service calls Kite Connect directly.
5. **Skills are the desk's procedures.** One skill per role workflow with `scripts/` doing the deterministic parts and `references/` holding gates; SKILL.md <500 lines; money-adjacent skills `disable-model-invocation: true`.
6. **Evaluation-driven skills**: ≥3 eval tasks per skill before writing it; wire into CI.
7. **Enforce with hooks, not CLAUDE.md**: `PreToolUse` command hooks block Bash touching order endpoints, `.env`, or prod DB; `Stop`-time hooks verify a research run wrote a ledger row.
8. **Pre-register every experiment and log N and k**; zero-alpha synthetic calibration run in the research skill.
9. **Memory: file-based, per-entity, verbatim-first**; index ≤200 lines; store extracted "lessons" alongside, never instead of, raw evidence.
10. **Separate read-only reference stores from read-write scratch**; review before promoting a note to reference.
11. **Sleep-time reflection job** nightly: reads logs and ledger, updates per-strategy memory, proposes (not applies) changes, gated.
12. **Durable orchestration for the always-on loop**: each shift as a workflow with retried activities, approval as a durable signal, checkpoints; do not depend on SDK session resume across hosts; persist decisions as application state.
13. **Scheduling choice**: for a Mumbai VM with Postgres, cron/Temporal invoking `claude -p --bare --output-format json --json-schema … --permission-mode dontAsk --permission-prompts none` (or the Agent SDK) is the least-surprise option; log `total_cost_usd` per run.
14. **Spec-driven repo layout**: spec-kit shape; EARS acceptance criteria; acceptance scenarios double as pytest + agent evals.
15. **Orchestrator-worker with clean contexts**: role subagents with tool allowlists, `maxTurns`, cheaper models for screening; ≤2k-token structured summaries; adversarial review.
16. **Context hygiene**: stable system-prompt prefix; context editing; recite plan file; keep failed actions in context.
17. **Sandbox research code**: never on the prod VM's trading process.
18. **Observability from day one**: OTel spans with `gen_ai.*` attributes plus `trade.dossier_id`.
19. **Evals as CI, graded on state**: 20–50 tasks per role from real failures; grade environment state; pass^k for ops tasks.
20. **What to avoid**: sharing broker write scopes with agents; LLM-only compliance filters; storing only distilled memories; unlogged trial counts; relying on CLAUDE.md as a guardrail; multi-agent by default (15× tokens) for tasks a workflow handles.

### Key sources
- Skills spec: https://agentskills.io/specification ; best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices ; Claude Code skills: https://code.claude.com/docs/en/skills
- Agent SDK: https://code.claude.com/docs/en/agent-sdk/overview , /python , /sessions ; hooks: https://code.claude.com/docs/en/hooks ; headless: https://code.claude.com/docs/en/headless ; memory: https://code.claude.com/docs/en/memory ; scheduled tasks: https://code.claude.com/docs/en/scheduled-tasks ; routines: https://code.claude.com/docs/en/routines
- Managed Agents: https://platform.claude.com/docs/en/managed-agents/overview , /scheduled-deployments , /memory
- Memory tool: https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool ; context editing: https://platform.claude.com/docs/en/build-with-claude/context-editing ; structured outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Anthropic engineering: building-effective-agents, effective-context-engineering-for-ai-agents, multi-agent-research-system, effective-harnesses-for-long-running-agents, demystifying-evals-for-ai-agents (https://www.anthropic.com/engineering/)
- Memory research: CoALA arXiv 2309.02427; Mem0 arXiv 2504.19413; Zep arXiv 2501.13956; A-MEM arXiv 2502.12110; Verbatim-chunks arXiv 2601.00821; Letta sleep-time
- SDD: https://github.com/github/spec-kit , https://kiro.dev/docs/specs/ , https://tessl.io
- Harness: https://developers.openai.com/blog/codex-as-a-platform , https://martinfowler.com/articles/harness-engineering.html , https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- Durable execution: https://temporal.io/blog/announcing-openai-agents-sdk-integration , https://docs.temporal.io/ai/cookbook/agentic-loop-tool-call-claude-python
- MCP: https://github.com/zerodha/kite-mcp-server , https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices
- Policy/guardrails: https://arxiv.org/abs/2604.01483 ; sandbox: https://code.claude.com/docs/en/sandboxing
- Evals/observability: https://www.promptfoo.dev/docs/providers/claude-agent-sdk/ , https://opentelemetry.io/blog/2026/genai-observability/
- Pre-registration: https://arxiv.org/abs/2606.11217 , https://jonathankinlay.com/2026/09/a-sharpe-of-2-1-from-nothing-the-second-number-your-agent-doesnt-log/
