# Agent quickstart — drop in the GitHub link

Repo: [https://github.com/jbellsolutions/super-browser](https://github.com/jbellsolutions/super-browser)

Give an agent this one-liner:

> Clone `https://github.com/jbellsolutions/super-browser`, run `./scripts/super-browser setup`, follow each step (skills, MCP, `.env` keys), run `doctor`, then use the `super-browser-orchestrator` skill for all browser and computer automation. Plan before execute; stop for approval on external writes.

Step-by-step guide with signup links: [setup-walkthrough.md](setup-walkthrough.md). Machine-readable: `./scripts/super-browser setup` or MCP `setup_walkthrough`.

## What you get

| Surface | Purpose |
| --- | --- |
| **Plugin** (`.claude-plugin/` or `.codex-plugin/`) | Skills + MCP in one package for Claude Code / Codex |
| **Skills** (`skills/`) | Orchestrator, planner, verifier, provider specialists |
| **MCP** (`mcp/super-browser-server`) | JSON tools: plan, run, approve, profiles, fleet |
| **Python CLI** (`super-browser`) | Same runtime without MCP — scripts and humans |

There is no separate HTTP API. Agents use **MCP tools** or the **CLI** (stdout JSON).

## Fastest path (Claude Code / Codex plugin)

```bash
git clone https://github.com/jbellsolutions/super-browser.git
cd super-browser
export SUPER_BROWSER_REPO_ROOT="$(pwd)"
pip install -e ".[playwright,mcp]" && playwright install chromium
cp .env.example .env   # fill keys locally — never commit .env
./scripts/super-browser doctor
```

Point your agent client at `.claude-plugin/plugin.json` or `.codex-plugin/plugin.json`. The plugin loads `skills/` and `.mcp.json` automatically.

## Fastest path (Cursor / any MCP client)

```bash
git clone https://github.com/jbellsolutions/super-browser.git
cd super-browser
pip install -e ".[playwright,mcp]" && playwright install chromium
./scripts/super-browser install-skill --target ~/.cursor/skills --force
./scripts/super-browser init-mcp --path ~/.cursor/mcp.json --merge --cwd "$(pwd)"
```

Restart Cursor so MCP picks up `super-browser`.

## Fastest path (copy bundle only — no git checkout)

```bash
./scripts/super-browser install-skill --target ~/.codex/skills --force
```

Run from a cloned repo, or from `pip install super-browser` (uses packaged `share/super-browser` assets).

## Natural-language examples (after setup)

| You say | Agent does |
| --- | --- |
| "Extract product names from https://example.com" | `plan` → `run` on cheapest provider (usually Playwright) |
| "Read my dashboard using profile `ig-account-1`" | `profiles` + `run --profile ig-account-1` |
| "Post a LinkedIn comment" | `run` → stops at `awaiting_approval` → you `approve` with reason |
| "Run the same read on 5 accounts" | `run --fleet 5 --profile base-acct` |
| "Fetch this JSON endpoint cheaply" | Routes to `decodo-http` when goal implies raw HTTP |

## Skill to invoke

**`super-browser-orchestrator`** — owns plan → approval → execute → verify.

Supporting skills: `super-browser-planner`, `super-browser-verifier`, `publishing-safety-specialist`, and per-provider specialists (`playwright-specialist`, `steel-specialist`, etc.).

## Verify before you trust it

```bash
./scripts/verify-super-browser
```

## Printing Press CLI (separate artifact)

The in-repo **Python CLI** ships with the plugin. A **Printing Press Go CLI** (installable binary + MCP) is a planned second distribution channel — see `docs/printing-press-cli.md`. Until that is published, use the Python CLI or MCP tools above.

## Slack ingress (optional)

See `docs/slack-agent-setup.md` for token setup, then:

```bash
pip install slack-bolt
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
./scripts/super-browser agent
```
