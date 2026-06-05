#!/usr/bin/env python3
"""
Tier 4: Rtrvr — MCP-native browser automation with auth session support.

DOM-native AI agents with Chrome Extension for authenticated sessions.
8 MCP tools available. BYOK Gemini = free usage.

Best for:
- Tasks requiring logged-in sessions (use Extension mode)
- MCP-native tool calling
- Cost-sensitive browsing (BYOK Gemini)

Prerequisites:
    npm install -g @rtrvr-ai/cli
    rtrvr auth login --api-key rtrvr_...

Usage:
    python tier4_rtrvr.py
    # Or via Hermes terminal:
    # rtrvr run "extract products" --url https://shop.com --extension --json
"""

import os
import sys
import json
import subprocess
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RTRVR_CLI = "rtrvr"  # Must be in PATH


def check_installed():
    """Verify rtrvr CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            [RTRVR_CLI, "doctor"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print("❌ rtrvr not authenticated. Run: rtrvr auth login --api-key rtrvr_...")
            sys.exit(1)
        print("✓ rtrvr CLI ready")
    except FileNotFoundError:
        print("❌ rtrvr not installed. Run: npm install -g @rtrvr-ai/cli")
        sys.exit(1)


def run_rtrvr(cmd: list[str], timeout: int = 120) -> dict:
    """Run a rtrvr command and parse JSON output."""
    result = subprocess.run(
        [RTRVR_CLI] + cmd,
        capture_output=True, text=True, timeout=timeout
    )

    if result.returncode != 0:
        raise RuntimeError(f"rtrvr failed: {result.stderr}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


# ---------------------------------------------------------------------------
# Pattern 1: Simple Scrape
# ---------------------------------------------------------------------------

def scrape_page(url: str) -> dict:
    """
    Scrape a single page for content. Fast and cheap (5 credits).
    Use this instead of agent mode unless you need multi-step interaction.
    """
    print(f"\n📄 Scraping: {url}")

    result = run_rtrvr(["scrape", "--url", url, "--json"])

    content = result.get("result") or result.get("content") or result
    print(f"  Content length: {len(str(content))} chars")
    return result


# ---------------------------------------------------------------------------
# Pattern 2: AI Agent Task (Multi-Step)
# ---------------------------------------------------------------------------

def run_agent_task(url: str, task: str, use_extension: bool = False) -> dict:
    """
    Execute a multi-step browser task using the AI agent.

    Agent mode costs more credits (5+ per step) but handles:
    - Clicking buttons and links
    - Filling forms
    - Navigating between pages
    - Complex extraction logic

    Args:
        url: Starting URL
        task: Natural language task description
        use_extension: Use Chrome Extension for auth sessions
    """
    print(f"\n🤖 Agent task: {task[:80]}...")
    print(f"  Starting URL: {url}")

    cmd = ["run", task, "--url", url, "--json"]

    if use_extension:
        cmd.append("--extension")
        print("  Mode: Extension (auth sessions)")
    else:
        cmd.append("--cloud")
        print("  Mode: Cloud (managed browser)")

    result = run_rtrvr(cmd, timeout=300)

    output = result.get("result") or result.get("output") or result
    print(f"  Output: {str(output)[:200]}...")
    return result


# ---------------------------------------------------------------------------
# Pattern 3: Batch Processing
# ---------------------------------------------------------------------------

def batch_scrape(urls: list[str]) -> list[dict]:
    """
    Scrape multiple URLs sequentially.
    
    For parallel execution, use Hermes delegate_task with rtrvr in each subagent.
    """
    results = []

    for i, url in enumerate(urls):
        print(f"\n📌 {i+1}/{len(urls)}: {url}")
        try:
            result = scrape_page(url)
            results.append({"url": url, "status": "success", "data": result})
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append({"url": url, "status": "failed", "error": str(e)})

    succeeded = sum(1 for r in results if r["status"] == "success")
    print(f"\n✅ {succeeded}/{len(urls)} URLs scraped")
    return results


# ---------------------------------------------------------------------------
# Pattern 4: Authenticated Session
# ---------------------------------------------------------------------------

def authenticated_scrape(url: str, task: str = None) -> dict:
    """
    Scrape a page that requires login using the Chrome Extension.

    Prerequisites:
    1. Install the Chrome Extension: "Retriever: AI Web Agent"
    2. Sign in with your rtrvr account
    3. Log into the target site in Chrome
    4. The extension will preserve your cookies
    """
    print(f"\n🔐 Authenticated scrape: {url}")

    if task:
        return run_agent_task(url, task, use_extension=True)
    else:
        # Simple scrape in extension mode
        result = run_rtrvr(["scrape", "--url", url, "--extension", "--json"])
        return result


# ---------------------------------------------------------------------------
# Pattern 5: Structured Extraction (Raw MCP Tool)
# ---------------------------------------------------------------------------

def extract_structured(url: str, fields: str) -> dict:
    """
    Extract specific fields from a page using the raw MCP extract tool.

    Args:
        url: Page URL
        fields: Description of what to extract (e.g., "product name, price, rating")

    Returns:
        Structured extraction result
    """
    print(f"\n🔍 Extracting fields from {url}: {fields}")

    result = run_rtrvr([
        "raw", "extract",
        "--param", f"user_input={fields}",
        "--param", f"tab_urls=['{url}']",
    ])

    return result


# ---------------------------------------------------------------------------
# Pattern 6: Multi-Page Crawl
# ---------------------------------------------------------------------------

def crawl_site(start_url: str, task: str, max_pages: int = 10) -> dict:
    """
    Crawl multiple pages starting from a URL.

    Good for: blog archives, product catalogs, paginated lists.
    """
    print(f"\n🕷️ Crawling from {start_url} (max {max_pages} pages)...")

    result = run_rtrvr([
        "raw", "crawl",
        "--param", f"user_input={task}",
        "--param", f"tab_urls=['{start_url}']",
        "--param", f"max_pages={max_pages}",
    ], timeout=600)

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    check_installed()

    # Demo: scrape a page
    result = scrape_page("https://example.com")
    print(f"\n✅ Done: {json.dumps(result, indent=2)[:300]}")

    # Demo: authenticated scrape (requires Extension)
    # result = authenticated_scrape("https://linkedin.com/in/someone")

    # Demo: agent task
    # result = run_agent_task(
    #     "https://example.com/contact",
    #     "Fill out the contact form with name=John, email=john@test.com, message=Hello and submit"
    # )
