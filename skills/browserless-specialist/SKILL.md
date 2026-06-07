---
name: browserless-specialist
description: Use Browserless for hosted Chromium, Puppeteer, Playwright, or CDP-based browser automation. Use when the task needs browser infrastructure rather than a natural-language web agent.
---

# Browserless Specialist

## Use For

- Hosted Chromium infrastructure.
- REST scrape/screenshot/function APIs.
- Puppeteer/Playwright/CDP workflows.
- Workloads where you bring the automation logic.

## Do Not Use For

- Natural-language agent tasks unless another layer supplies the agent logic.
- Full desktop workflows.
- Advanced anti-bot tasks without proof.

## Required Env

- `BROWSERLESS_TOKEN`
- Optional: `BROWSERLESS_BASE_URL`

## Super Browser Adapter

The adapter calls Browserless REST:

1. `POST /scrape?token=...`
2. Sends the target `url` and `body` selector.
3. Writes `browserless-output.json`.

Use Browserless when the task needs hosted browser infrastructure. It is not a natural-language agent by itself.

If `BROWSERLESS_BASE_URL` is set, Super Browser validates it before sending `BROWSERLESS_TOKEN`. Loopback HTTP is allowed for local self-hosted Browserless, but private-network/link-local endpoints and insecure remote HTTP require explicit override env vars.

Before submitting a target URL to Browserless, Super Browser resolves public-looking hostnames locally. If DNS points to loopback, private-network, or link-local addresses, execution returns `provider_url_resolved_target_scope` and does not call the Browserless REST API. Treat that as a non-resumable safety stop; create a new run or replan for the intended target scope.

## Verification

- Contract-tested with fake Browserless scrape responses.
- Live-gated by `BROWSERLESS_TOKEN`.
- Keep anti-bot claims evaluating unless BrowserQL or unblock-specific live tests pass.

Docs:

- https://docs.browserless.io/rest-apis/intro
- https://docs.browserless.io/rest-apis/screenshot
- https://docs.browserless.io/mcp/rest-api-tools
- https://docs.browserless.io/browserql/start
