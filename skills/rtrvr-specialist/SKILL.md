---
name: rtrvr-specialist
description: Use Rtrvr for authenticated browsing through a local Chrome extension, logged-in sessions, and MCP-native browser automation. Use when the task depends on an existing user profile or OAuth/cookie state.
---

# Rtrvr Specialist

## Use For

- Existing logged-in Chrome sessions.
- OAuth/cookie state that should stay local.
- Authenticated research, extraction, or controlled browser actions.
- MCP-native workflows when Rtrvr is already installed.

## Do Not Use For

- High-volume jobs where Rtrvr credits become expensive.
- Work where no local extension/profile is available.
- Advanced anti-bot cases where Browser Use is proven better.

## Required Env

- `RTRVR_API_KEY`
- `GEMINI_API_KEY` when using BYOK mode.
- Optional: `RTRVR_API_BASE`

## Super Browser Adapter

The runtime uses `rtrvr run "<task>" --target auto --json --no-stream` when the CLI is installed. If the CLI is unavailable, it calls `POST https://api.rtrvr.ai/agent` with `input`, `urls`, and `target`.

CLI and HTTP output is saved to `rtrvr-output.json` and checked before the attempt is marked complete. Explicit provider errors, failed statuses, unfinished statuses, and `success=false` are failed attempts, even when the CLI exits 0 or the HTTP request returns 200.

If `RTRVR_API_BASE` is set, Super Browser validates it before sending `RTRVR_API_KEY`. Loopback HTTP is allowed for local testing, but private-network/link-local endpoints and insecure remote HTTP require explicit override env vars.

Before dispatching a target URL to Rtrvr CLI or HTTP, Super Browser resolves public-looking hostnames locally. If DNS points to loopback, private-network, or link-local addresses, execution returns `provider_url_resolved_target_scope` and does not start the CLI or API request. Treat that as a non-resumable safety stop; create a new run or replan for the intended target scope.

Docs: https://www.rtrvr.ai/docs/cli
