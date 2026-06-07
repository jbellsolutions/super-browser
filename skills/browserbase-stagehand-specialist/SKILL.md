---
name: browserbase-stagehand-specialist
description: Use Browserbase and Stagehand for cloud browser sessions, contexts, proxies, and natural-language browser automation. Use for general cloud browser work, persisted contexts, scalable browsing, and agent-friendly observe/act/extract workflows.
---

# Browserbase + Stagehand Specialist

## Use For

- General cloud browser sessions.
- Persisted auth with Browserbase Contexts.
- Stagehand-style `observe`, `act`, and `extract` workflows.
- Screenshots, sessions, proxies, and cloud isolation.

## Do Not Use For

- Advanced anti-bot sites when Browser Use has proven better.
- Raw HTTP endpoints where Decodo is cheaper.
- Full desktop tasks needing OS-level apps or files.

## Required Env

- `BROWSERBASE_API_KEY`
- `BROWSERBASE_PROJECT_ID`
- Optional `BROWSERBASE_CONTEXT_ID` for persisted context sessions.

## Super Browser Adapter

The runtime uses the official Python `browserbase` package to create a session, then connects through Playwright CDP. It captures title, text, screenshot, metadata, and the Browserbase session recording URL. The adapter passes a provider-native session timeout derived from Super Browser `timeout_seconds`, clamped to Browserbase's documented 60-second minimum and 21,600-second maximum, so cloud sessions do not run on only the project default. Install with:

```bash
python3 -m pip install browserbase playwright
```

Before creating a Browserbase session, Super Browser resolves public-looking target hostnames locally. If DNS points to loopback, private-network, or link-local addresses, execution returns `provider_url_resolved_target_scope` and does not create the session. The CDP path also installs Super Browser's request target-scope guard before navigation. Browser redirects or subresources into `loopback`, `private_network`, `link_local`, or `local_file` from a different planned scope return a `browser_request_target_scope` blocked result rather than page artifacts. Treat both as non-resumable safety stops; create a new run or replan for the intended target scope.

## Docs

- Browserbase MCP: https://docs.browserbase.com/integrations/mcp/introduction
- Stagehand agent: https://docs.stagehand.dev/v3/basics/agent
