# Super Browser

**The agent plugin that picks the right browser backend — then proves the run worked.**

Super Browser is a drop-in skill pack, CLI, and MCP server for Claude Code, Codex, Cursor, and any MCP client. Describe a task in natural language; Super Browser classifies it, deliberates on provider choice (3–5 loops), routes to the cheapest backend that can do the job, gates risky writes for human approval, and saves artifacts plus a verification report.

**Repo:** [github.com/jbellsolutions/super-browser](https://github.com/jbellsolutions/super-browser)

---

## Hey, here's how this works

You (or your agent) get a **browser/computer job** in plain English — extract a page, log into a dashboard, scrape behind anti-bot, post a comment, or fetch a JSON API. Super Browser does not make you pick Hyperbrowser vs Steel vs Playwright up front.

1. **Plan** — `./scripts/super-browser setup` on first use, then `plan` (or MCP `plan_browser_task`). The planner runs **3 deliberation loops** for simple jobs and **5** when multiple cloud providers could work. You get a `council_report` with provider order, cost estimate, and `deliberation_complete`.
2. **Approve** — Posts, DMs, purchases, CRM changes, and credential-bearing work stop at `awaiting_approval` until a human approves with a reason. Draft-only tasks that explicitly say *do not publish* can proceed without approval.
3. **Execute** — Primary provider runs first; fallbacks try the next option if needed. Artifacts land under `.super-browser/`.
4. **Verify** — `verify` checks run reports, policy guards, and artifact integrity before anyone claims success.

**Your setup in one pass:**

```bash
git clone https://github.com/jbellsolutions/super-browser.git && cd super-browser
./scripts/super-browser setup          # prints welcome + step-by-step JSON (same as this doc)
cp .env.example .env                   # add API keys locally — never commit .env
pip install -e ".[playwright,mcp]" && playwright install chromium
export SUPER_BROWSER_REPO_ROOT="$(pwd)"
./scripts/super-browser install-skill --target ~/.cursor/skills --force   # or ~/.codex/skills / ~/.claude/skills
./scripts/super-browser init-mcp --path ~/.cursor/mcp.json --merge --cwd "$(pwd)"
./scripts/super-browser doctor
```

**Tell your agent (paste this after cloning):**

> Read the Super Browser repo README. Run `./scripts/super-browser setup` and follow every step. Use the **super-browser-orchestrator** skill for all browser/computer tasks. Always **plan** before **run**. Do not execute until `deliberation_complete` is true. Stop for approval on external writes. Never paste API keys into chat — use `.env`.

Human walkthrough: [docs/setup-walkthrough.md](docs/setup-walkthrough.md) · Agent cheat sheet: [docs/agent-quickstart.md](docs/agent-quickstart.md)

---

## Start here (60 seconds)

If you already know the flow:

```bash
git clone https://github.com/jbellsolutions/super-browser.git && cd super-browser
./scripts/super-browser setup
cp .env.example .env
pip install -e ".[playwright,mcp]" && playwright install chromium
./scripts/super-browser doctor
```

---

## What you get

| Piece | What it does |
| --- | --- |
| **Orchestrator + specialist skills** | Classify tasks, deliberate on providers, gate publishing, verify results |
| **`super-browser` CLI** | Plan, run, approve, resume, verify — JSON in/out for scripts |
| **MCP server** | Same runtime as tools (`setup_walkthrough`, `plan_browser_task`, `run_browser_task`, …) |
| **Codex / Claude plugins** | `.codex-plugin/` and `.claude-plugin/` bundle skills + MCP |
| **Durable runs** | SQLite store, artifacts, `run-report.json`, handoff for another agent |
| **Weekly provider intel** | `scripts/weekly-provider-intelligence.py` + GitHub Action (changelog sync) |

![Super Browser plugin architecture](docs/plugin-architecture.svg)

---

## Supported providers (current lineup)

Capability picks the provider; **rank** is only the cost tie-breaker when several can do the job.

| Rank | Provider | Best for | Adapter |
| --- | --- | --- | --- |
| **1** | **Playwright** (local) | Deterministic tests, screenshots, cheap extraction | live |
| **1** | **Browser Use** | Anti-bot, profiles, hardened cloud Chromium | live |
| **2** | **Hyperbrowser** | Cloud scrape jobs, geo proxy, scale automation | live |
| **2** | **Airtop** | Cloud sessions, page-query, GTM / webhook workflows | live |
| **2** | **Browserbase** | Stagehand, Model Gateway BYOK, hosted agents | **docs-only** ([audit](references/providers/browserbase-capability-audit.md)) |
| **3** | **Steel** | Hosted Chromium via Playwright CDP | live |
| **4** | **Orgo** | Full desktop — files, terminal, multi-window | live |
| **Lane** | **Decodo HTTP** | Raw `http(s)://` endpoints + optional residential proxy | live |

Per-provider SSOT: [references/providers/](references/providers/) · Combos: [references/combo-playbook.md](references/combo-playbook.md) · Full matrix: [references/provider-matrix.md](references/provider-matrix.md) · Routing: [references/routing-playbook.md](references/routing-playbook.md)

![Provider escalation stack](docs/architecture.svg)

---

## How a run works

```mermaid
flowchart LR
  A[Task] --> B[Deliberate + plan]
  B --> C{Write risk?}
  C -->|Yes| D[Approval gate]
  C -->|No| E[Execute]
  D --> E
  E --> F[Primary + fallbacks]
  F --> G[Verify artifacts]
```

1. **Deliberate + plan** — 3–5 loops: classify → redundancy filter → env/live evidence → task shape → simplest-tool challenge. Output: `council_report` with `deliberation_complete`, `execution_pattern`, optional `combo_steps`.
2. **Approve** — external writes and credential use stop until approved.
3. **Execute** — primary provider, then fallbacks; timeouts and target-scope guards enforced in code.
4. **Verify** — artifacts hashed, run report checked, policy summarized for handoff.

Safety: [references/security-and-approval-policy.md](references/security-and-approval-policy.md)

---

## Example commands

```bash
# Read-only extraction (local first)
super-browser plan --goal "Extract product names from https://example.com"

# Force 5 deliberation loops
super-browser plan --goal "Bypass Cloudflare on https://shop.example.com" --deliberation-rounds 5

# Cheap raw HTTP
super-browser run --goal "Fetch JSON" --url "https://example.com/data.json" \
  --allow-provider decodo-http --max-cost-usd 0.01

# Draft without publishing (still plan first)
super-browser run --goal "Draft a LinkedIn comment but do not publish"

# After approval
super-browser approve <run-id> --by "you" --reason "approved exact text" --execute
super-browser verify <run-id>
```

Install the skill bundle elsewhere:

```bash
./scripts/super-browser install-skill --target ~/.codex/skills --force
./scripts/super-browser init-mcp --path ~/.cursor/mcp.json --merge
```

---

## MCP tools (high level)

`setup_walkthrough` · `plan_browser_task` · `run_browser_task` · `resume_browser_run` · `get_browser_run` · `handoff_browser_run` · `list_browser_runs` · `verify_browser_run` · `approve_browser_run` · `deny_browser_run` · `list_browser_providers` · `browser_doctor` · `production_readiness` · `env_checklist` · `bundle_manifest` · `run_browser_live_tests` · `install_super_browser_skill` · `init_super_browser_mcp`

`setup_walkthrough` returns a `welcome` string plus numbered steps — use it as the first message when someone drops this repo link into an agent.

Read-only docs via MCP resources: provider matrix, routing playbook, combo playbook, provider SSOT index, Browserbase capability audit, and each specialist skill.

---

## Production checklist

```bash
./scripts/verify-super-browser      # full local gate (tests + doctor + fixtures)
super-browser production-readiness
super-browser env-checklist
super-browser live-test --provider all   # needs API keys in .env
```

Cloud providers stay **evaluating** until live tests pass for your workflow class. See [references/live-test-matrix.md](references/live-test-matrix.md).

Weekly changelog sync (dry run locally):

```bash
python scripts/weekly-provider-intelligence.py
python scripts/weekly-provider-intelligence.py --apply --verify   # writes cache + SSOT stamps
```

---

## Install options

| Client | Path |
| --- | --- |
| **Codex** | `.codex-plugin/plugin.json` — set `SUPER_BROWSER_REPO_ROOT` to this repo |
| **Claude Code** | `.claude-plugin/plugin.json` — same env var |
| **Cursor / Hermes** | `install-skill` + merge `.mcp.json` into your MCP config |
| **Python only** | `pip install -e .` or `pip install -e ".[all-providers]"` |

Optional extras: `.[playwright]`, `.[browser-use]`, `.[mcp]`, `.[all-providers]`.

---

## Docs map

| Doc | Use when |
| --- | --- |
| [setup-walkthrough.md](docs/setup-walkthrough.md) | Onboarding humans or agents step by step |
| [agent-quickstart.md](docs/agent-quickstart.md) | Drop-in GitHub link for another agent |
| [slack-agent-setup.md](docs/slack-agent-setup.md) | Slack / agent-os integration |
| [provider-matrix.md](references/provider-matrix.md) | Provider capabilities and env vars |
| [routing-playbook.md](references/routing-playbook.md) | How routing and fallbacks work |
| [combo-playbook.md](references/combo-playbook.md) | When to combine providers vs one tool |
| [providers/browserbase-capability-audit.md](references/providers/browserbase-capability-audit.md) | Browserbase adapter ship criteria |
| [security-and-approval-policy.md](references/security-and-approval-policy.md) | Approval, target scope, redaction |

Older research notes under `docs/research-*.md` are **historical**. Use the provider matrix and `references/providers/` for the current lineup.

---

## Development

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
./scripts/verify-super-browser
```

Run store defaults to `.super-browser/` (override with `SUPER_BROWSER_STATE_DIR`).

---

MIT · [AI Integraterz](https://github.com/jbellsolutions)
