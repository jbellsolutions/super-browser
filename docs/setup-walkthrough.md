# Setup walkthrough — share this with a new teammate

Repo: [https://github.com/jbellsolutions/super-browser](https://github.com/jbellsolutions/super-browser)

Give an agent this prompt:

> Install Super Browser from `https://github.com/jbellsolutions/super-browser`. Run `./scripts/super-browser setup`, follow every step, install skills and MCP, run doctor, then use `super-browser-orchestrator` for browser tasks. Never paste API keys into chat — use `.env` locally.

Machine-readable steps (same content as this doc):

```bash
./scripts/super-browser setup
./scripts/super-browser setup --client cursor   # optional: tailor commands
```

MCP equivalent: `setup_walkthrough` with optional `client`.

---

## Step 1 — Clone

```bash
git clone https://github.com/jbellsolutions/super-browser.git
cd super-browser
```

## Step 2 — Install Python package + Chromium

```bash
python3 -m pip install -e ".[playwright,mcp]"
python3 -m playwright install chromium
```

Playwright is the free local lane. MCP extras enable the JSON tool server.

## Step 3 — Point the runtime at this checkout

```bash
export SUPER_BROWSER_REPO_ROOT="$(pwd)"
```

Add that line to your shell profile if you want it permanent.

## Step 4 — Create `.env` from the template

```bash
cp .env.example .env
```

Edit `.env` locally. **Do not commit `.env` and do not paste secrets into chat.**

## Step 5 — Get API keys (signup links)

| Provider | Env var | Sign up | What it unlocks |
| --- | --- | --- | --- |
| Browser Use Cloud | `BROWSER_USE_API_KEY` | [cloud.browser-use.com](https://cloud.browser-use.com/) | Anti-bot cloud browser, profiles, recordings |
| Hyperbrowser | `HYPERBROWSER_API_KEY` | [hyperbrowser.ai](https://www.hyperbrowser.ai/) | Cloud scrape jobs at scale |
| Airtop | `AIRTOP_API_KEY` | [airtop.ai](https://www.airtop.ai/) | Cloud sessions, page-query, GTM workflows |
| Steel | `STEEL_API_KEY` | [steel.dev](https://steel.dev/) | Hosted Chromium over Playwright CDP |
| Orgo | `ORGO_API_KEY` | [orgo.ai](https://orgo.ai/) | Full desktop / computer-use VMs |
| Decodo (optional) | `DECODO_PROXY` | [decodo.com](https://decodo.com/) | Residential proxy for raw HTTP |

Local Playwright and direct raw HTTP work **without** paid keys.

Check what's still missing:

```bash
./scripts/super-browser env-checklist
./scripts/super-browser doctor
```

## Step 6 — Install skills

**Cursor**

```bash
./scripts/super-browser install-skill --target ~/.cursor/skills --force
```

**Codex**

```bash
./scripts/super-browser install-skill --target ~/.codex/skills --force
```

**Claude Code** — enable `.claude-plugin/plugin.json` in the plugin picker, or copy skills the same way:

```bash
./scripts/super-browser install-skill --target ~/.claude/skills --force
```

## Step 7 — Wire MCP

**Cursor**

```bash
./scripts/super-browser init-mcp --path ~/.cursor/mcp.json --merge --cwd "$(pwd)"
```

**Codex**

```bash
./scripts/super-browser init-mcp --path ~/.codex/mcp.json --merge --cwd "$(pwd)"
```

Restart the IDE so MCP loads `super-browser`.

**Claude Code plugin** — `.mcp.json` ships with the repo; set `SUPER_BROWSER_REPO_ROOT` and enable the plugin.

## Step 8 — Smoke test (no paid keys)

```bash
./scripts/super-browser live-test --provider local
./scripts/super-browser live-test --provider fixtures
```

## Step 9 — Certify cloud providers (after keys)

```bash
./scripts/super-browser live-test --provider all
./scripts/super-browser production-readiness
```

`production-readiness` stays **blocked** until each provider you care about has live-test evidence. That is expected before keys are configured.

## Step 10 — Use the orchestrator

Tell your agent:

> Use the **super-browser-orchestrator** skill. Plan with `plan_browser_task` or `super-browser plan`. Stop for approval on external writes. Verify with `verify_browser_run` before claiming success.

## Optional — Slack daemon

See [slack-agent-setup.md](slack-agent-setup.md) for Socket Mode tokens and `super-browser agent`.

## Full repo verify (maintainers)

```bash
./scripts/verify-super-browser
```
