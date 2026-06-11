from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from .provider_signup import PROVIDER_SIGNUP
from .setup_helpers import discover_repo_root, is_super_browser_root


def launch_setup(*, client: str | None = None) -> dict[str, Any]:
    from .env_checklist import environment_checklist
    root = discover_repo_root()
    repo_path = str(root) if root else None
    python = sys.executable
    has_playwright_pkg = _module_available("playwright")
    chromium_hint = "playwright install chromium" if has_playwright_pkg else 'pip install -e ".[playwright]" && playwright install chromium'

    steps = [
        {
            "step": 1,
            "title": "Clone the repo",
            "natural_language": "Clone https://github.com/jbellsolutions/super-browser and cd into it.",
            "commands": [
                "git clone https://github.com/jbellsolutions/super-browser.git",
                "cd super-browser",
            ],
            "done": bool(repo_path and is_super_browser_root(repo_path)),
        },
        {
            "step": 2,
            "title": "Install Python package + local browser",
            "natural_language": "Install Super Browser with Playwright and MCP support, then install Chromium.",
            "commands": [
                f'{python} -m pip install -e ".[playwright,mcp]"',
                f"{python} -m playwright install chromium",
            ],
            "done": has_playwright_pkg,
        },
        {
            "step": 3,
            "title": "Point runtime at this checkout",
            "natural_language": "Set SUPER_BROWSER_REPO_ROOT so MCP resources and skills resolve correctly.",
            "commands": [
                'export SUPER_BROWSER_REPO_ROOT="$(pwd)"',
            ],
            "env": {"SUPER_BROWSER_REPO_ROOT": repo_path},
            "done": bool(os.environ.get("SUPER_BROWSER_REPO_ROOT") or repo_path),
        },
        {
            "step": 4,
            "title": "Copy env template",
            "natural_language": "Copy .env.example to .env and add API keys locally — never paste secrets into chat.",
            "commands": [
                "cp .env.example .env",
            ],
            "done": (root / ".env").exists() if root else False,
        },
        {
            "step": 5,
            "title": "Install skills for your agent",
            "natural_language": "Copy the skill bundle into your agent's skills directory.",
            "commands": _install_skill_commands(client),
            "done": None,
        },
        {
            "step": 6,
            "title": "Wire MCP",
            "natural_language": "Merge Super Browser into your MCP config, then restart the IDE.",
            "commands": _init_mcp_commands(client, repo_path),
            "done": None,
        },
        {
            "step": 7,
            "title": "Run doctor",
            "natural_language": "Check which providers are ready and which keys are still missing.",
            "commands": ["./scripts/super-browser doctor"],
            "done": None,
        },
        {
            "step": 8,
            "title": "Smoke test (no paid keys)",
            "natural_language": "Run local fixture tests to prove routing, safety gates, and artifacts work.",
            "commands": [
                "./scripts/super-browser live-test --provider local",
                "./scripts/super-browser live-test --provider fixtures",
            ],
            "done": None,
        },
        {
            "step": 9,
            "title": "Certify cloud providers (after keys)",
            "natural_language": "Run live tests per provider to collect production evidence.",
            "commands": [
                "./scripts/super-browser live-test --provider all",
                "./scripts/super-browser production-readiness",
            ],
            "done": None,
        },
        {
            "step": 10,
            "title": "Use the orchestrator skill",
            "natural_language": "Tell your agent to use skill super-browser-orchestrator for every browser or computer task.",
            "agent_prompt": (
                "Use the super-browser-orchestrator skill. Plan with plan_browser_task or "
                "`super-browser plan`, stop for approval on external writes, verify before claiming success."
            ),
            "done": None,
        },
    ]

    return {
        "type": "super_browser_setup_walkthrough",
        "repo": "https://github.com/jbellsolutions/super-browser",
        "docs": {
            "quickstart": "docs/agent-quickstart.md",
            "walkthrough": "docs/setup-walkthrough.md",
            "slack": "docs/slack-agent-setup.md",
        },
        "repo_root": repo_path,
        "client_hint": client,
        "provider_signup": list(PROVIDER_SIGNUP.values()),
        "env_checklist": environment_checklist(),
        "steps": steps,
        "one_liner_for_agent": (
            "Clone https://github.com/jbellsolutions/super-browser, run `./scripts/super-browser setup`, "
            "follow each step, install skills + MCP, run doctor, then use super-browser-orchestrator."
        ),
    }


def _install_skill_commands(client: str | None) -> list[str]:
    targets = {
        "cursor": "~/.cursor/skills",
        "codex": "~/.codex/skills",
        "claude": "~/.claude/skills",
    }
    if client and client in targets:
        return [f'./scripts/super-browser install-skill --target {targets[client]} --force']
    return [
        "./scripts/super-browser install-skill --target ~/.cursor/skills --force",
        "./scripts/super-browser install-skill --target ~/.codex/skills --force",
        "./scripts/super-browser install-skill --target ~/.claude/skills --force",
    ]


def _init_mcp_commands(client: str | None, repo_path: str | None) -> list[str]:
    cwd = '"$(pwd)"' if repo_path else "/path/to/super-browser"
    paths = {
        "cursor": f"~/.cursor/mcp.json",
        "codex": "~/.codex/mcp.json",
    }
    if client and client in paths:
        return [f"./scripts/super-browser init-mcp --path {paths[client]} --merge --cwd {cwd}"]
    return [
        f"./scripts/super-browser init-mcp --path ~/.cursor/mcp.json --merge --cwd {cwd}",
        f"./scripts/super-browser init-mcp --path ~/.codex/mcp.json --merge --cwd {cwd}",
    ]


def _module_available(name: str) -> bool:
    try:
        import importlib.util

        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False
