---
name: orgo-specialist
description: Use Orgo for full desktop/computer automation when browser-only tools are not enough. Use for OS apps, multi-window workflows, files plus browser, terminal work, screenshots, or computer-use fallback.
---

# Orgo Specialist

## Use For

- Full desktop tasks.
- Browser plus files plus terminal workflows.
- Installing or running desktop apps.
- Computer-use fallback when browser automation cannot solve the job.

## Do Not Use For

- Simple page extraction.
- Raw HTTP.
- High-volume cheap scraping.
- Tasks that can run in local Playwright or Browserbase.

## Required Env

- `ORGO_API_KEY`
- `ORGO_COMPUTER_ID`
- Optional: `ORGO_API_BASE`
- Optional: `ORGO_MODEL`

## Super Browser Adapter

The runtime uses Orgo's computer-use API against an explicit existing computer:

- `POST /api/v1/chat/completions` or `POST /v1/chat/completions` with `computer_id`, `model`, and task messages
- `GET /computers/{id}/screenshot`

It does not create new computers automatically because that can spend money unexpectedly. Create or select a computer in Orgo first, then set `ORGO_COMPUTER_ID`.

Provider request failures and screenshot failures must be returned as structured failed attempts with saved output evidence when available. Treat missing screenshot evidence as a verification failure, not as a successful desktop run.

If `ORGO_API_BASE` is set, Super Browser validates it before sending `ORGO_API_KEY`. Loopback HTTP is allowed for local testing, but private-network/link-local endpoints and insecure remote HTTP require explicit override env vars.

## Verification

Require desktop screenshots, provider output logs, uploaded/downloaded file checks, and cleanup confirmation. The local contract tests cover successful chat+screenshot capture, failed computer-use requests, and failed screenshot requests.

Docs:
- https://docs.orgo.ai/quickstart
- https://docs.orgo.ai/api-reference/introduction
