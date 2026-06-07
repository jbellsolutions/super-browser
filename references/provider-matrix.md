# Super Browser Provider Matrix

This matrix is the source of truth for planner and specialist decisions. Mark provider behavior as `verified`, `claimed`, `evaluating`, or `untested`; do not treat vendor claims as proof.

| Provider | Status | Best for | Do not use when | Required or optional env |
| --- | --- | --- | --- | --- |
| Local Playwright | verified-local | Deterministic browser tests, screenshots, known selectors, fixture sites, low-cost extraction | Advanced anti-bot, personal logged-in Chrome sessions, full desktop apps | none; requires Playwright Python package and Chromium runtime |
| Browserbase + Stagehand | implemented-live-gated | Cloud browser sessions, contexts, proxies, natural-language observe/act/extract | Raw HTTP, full desktop, anti-bot flows where Browser Use has better proof | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| Browser Use Cloud | implemented-live-gated | Hardened cloud browser, anti-bot workflows, profiles, recordings, live URLs | Cheap raw HTTP, local deterministic tests | `BROWSER_USE_API_KEY` |
| Rtrvr | implemented-live-gated | Logged-in local Chrome/extension sessions, OAuth/cookie state, MCP-native browsing | High-volume tasks where credits get expensive, no local profile available | `RTRVR_API_KEY`, optional `GEMINI_API_KEY` |
| Orgo | implemented-live-gated | Full computer/desktop automation, browser plus files plus terminal, multi-window workflows | Browser-only or raw HTTP tasks | `ORGO_API_KEY`, `ORGO_COMPUTER_ID` |
| Airtop | implemented-live-gated | Cloud sessions, page-query extraction, no-code/browser-agent workflows, scheduled GTM, webhook-driven automations | MCP-native local workflows without a wrapper, untested anti-bot claims, high-volume use before cost is measured | `AIRTOP_API_KEY` |
| Decodo Raw HTTP | verified-pattern | Supplied `http://` or `https://` API endpoints, JSON endpoints, optional residential proxy fetches, cheap bulk data | Missing endpoint, browser rendering, advanced headless detection, personal logged-in sessions | optional `DECODO_PROXY` for residential proxy routing |
| Hyperbrowser | implemented-live-gated | REST scrape jobs, cloud browser automation to test, scale workflows | Production until live tests pass for the target workflow | `HYPERBROWSER_API_KEY` |
| Steel | implemented-live-gated | Playwright CDP control of Steel cloud browser sessions, agent browser infrastructure | Raw HTTP endpoints, full desktop work, production before live task proof | `STEEL_API_KEY` |
| Browserless | implemented-live-gated | Hosted Chromium REST scrape, Puppeteer/Playwright/CDP infrastructure | Natural-language agent tasks without another agent layer, full desktop | `BROWSERLESS_TOKEN` |

## Provider Selection Notes

- Prefer Playwright first only when the site is ordinary and the workflow is deterministic.
- Treat local Playwright as ready only when `super-browser doctor` reports `ready_local` and `browser_runtime_available=true`; a package-only install without Chromium is `runtime_missing`.
- Prefer Browserbase/Stagehand for general cloud browser work where contexts, sessions, and natural-language actions matter.
- Prefer Browser Use when the task mentions Cloudflare, Meta, LinkedIn, PerimeterX, DataDome, CAPTCHA, or repeated prior bot failures.
- Prefer Rtrvr when the key requirement is an existing logged-in local browser session.
- Prefer Orgo only when a browser is not enough.
- Prefer Decodo only when no browser rendering is required and the task supplies a concrete HTTP endpoint.
- Direct Decodo/raw HTTP can run without `DECODO_PROXY`; set `DECODO_PROXY` only when residential proxy routing is required.
- Keep Hyperbrowser, Steel, Browserless, and Airtop behind live tests until task-specific reliability is proven.
- Treat `raw_http_redirect_target_scope`, `raw_http_resolved_target_scope`, `provider_url_resolved_target_scope`, and `browser_request_target_scope` as non-resumable safety stops. Replan for the intended target scope instead of retrying the same public-web run.
- Raw HTTP, URL-capable remote/desktop providers, and Playwright-backed browser guards resolve public-looking hostnames before continuing and block DNS results that point at loopback, private-network, or link-local addresses, plus unresolved public hosts that cannot be verified locally.
- Optional provider API/CDP base overrides are validated before credentials are sent. Loopback HTTP/WS is allowed for self-hosted local providers; private-network/link-local endpoints and insecure remote HTTP/WS require explicit override env vars.

## Implemented Adapter Notes

- Browserbase uses the official Python `browserbase` package to create a session with a bounded provider-native timeout, then Playwright CDP to capture title, text, screenshot, and session metadata.
- Browser Use uses `browser_use_sdk.v3.AsyncBrowserUse().run(...)` and writes the returned SDK payload to `browser-use-output.json`.
- Rtrvr uses `rtrvr run "<task>" --target auto --json --no-stream` when the CLI is installed. If the CLI is unavailable, it calls `POST https://api.rtrvr.ai/agent` with `input`, `urls`, and `target`. CLI/HTTP output is saved and checked for explicit failure payloads.
- Orgo uses an explicit existing `ORGO_COMPUTER_ID`, submits the desktop task through Orgo computer-use chat completions, and requests a screenshot. It does not create new computers by default because that can spend money unexpectedly, and missing screenshot evidence is a failed provider attempt.
- Airtop creates a session, opens a window, runs page-query, writes `airtop-output.json`, and terminates the session.
- Hyperbrowser calls REST `/scrape`, polls `/scrape/{jobId}/status`, fetches `/scrape/{jobId}` after completion, and writes `hyperbrowser-output.json`.
- Steel connects through Playwright CDP to `connect.steel.dev`, captures screenshot/text/metadata, and writes local artifacts.
- Browserless calls REST `/scrape?token=...` and writes `browserless-output.json`.
- Every adapter returns a structured `blocked` result with docs and missing env vars instead of failing silently when setup is incomplete.
- JSON-backed adapters and Rtrvr CLI/HTTP output handling mark explicit provider errors, nested provider-result errors, failed statuses, unfinished statuses after polling, and `success=false` responses as failed attempts with saved output evidence instead of treating any API response as success.
- Playwright-backed adapters install a request target-scope guard before navigation. Local Playwright, Browserbase CDP, and Steel CDP block browser redirects or subresources into loopback, private-network, link-local, or local-file targets unless the run was planned for that same target scope.
