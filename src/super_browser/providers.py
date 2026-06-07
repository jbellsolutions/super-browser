from __future__ import annotations

import os
import shutil
import importlib.util

from .live_evidence import load_live_test_evidence
from .models import ProviderCapability
from .redaction import redact_text


def _has_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


SUPPORTED_LIVE_WORKFLOW_CLASSES = {
    "decodo-http": ["raw_http_direct", "external_write_gate"],
    "playwright": ["local_browser_fixture", "external_write_gate"],
    "rtrvr": ["authenticated_read", "external_write_gate"],
    "orgo": ["desktop_read", "external_write_gate"],
}
DEFAULT_REMOTE_LIVE_WORKFLOW_CLASSES = ["general_read", "external_write_gate"]

PROVIDERS: dict[str, ProviderCapability] = {
    "playwright": ProviderCapability(
        name="playwright",
        display_name="Local Playwright",
        stability="stable",
        cost_band="free",
        env_vars=[],
        docs_url="https://playwright.dev/python/",
        best_for=["deterministic local browser control", "testing", "simple extraction", "known selectors"],
        avoid_when=["advanced anti-bot is present", "a logged-in personal Chrome session is required"],
        supports_long_running=True,
    ),
    "browserbase-stagehand": ProviderCapability(
        name="browserbase-stagehand",
        display_name="Browserbase + Stagehand",
        stability="stable",
        cost_band="variable",
        env_vars=["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID"],
        docs_url="https://docs.browserbase.com/integrations/mcp/introduction",
        best_for=["cloud browser sessions", "contexts", "general web workflows", "natural-language actions"],
        avoid_when=["the site has proven advanced bot detection and Browser Use is available"],
        supports_auth=True,
        supports_long_running=True,
    ),
    "browser-use": ProviderCapability(
        name="browser-use",
        display_name="Browser Use Cloud",
        stability="stable",
        cost_band="variable",
        env_vars=["BROWSER_USE_API_KEY"],
        docs_url="https://docs.browser-use.com/cloud/guides/mcp-server",
        best_for=["anti-bot sites", "complex cloud browser tasks", "recordings", "profiles"],
        avoid_when=["a free local deterministic test is enough", "the job is raw HTTP only"],
        supports_auth=True,
        supports_anti_bot=True,
        supports_long_running=True,
    ),
    "rtrvr": ProviderCapability(
        name="rtrvr",
        display_name="Rtrvr",
        stability="stable",
        cost_band="variable",
        env_vars=["RTRVR_API_KEY"],
        docs_url="https://www.rtrvr.ai/docs/cli",
        best_for=["logged-in local Chrome sessions", "extension-based authenticated browsing", "MCP-native browser tasks"],
        avoid_when=["no local Chrome profile is available", "high-volume work would be cheaper in another backend"],
        supports_auth=True,
    ),
    "orgo": ProviderCapability(
        name="orgo",
        display_name="Orgo Computer",
        stability="stable",
        cost_band="medium",
        env_vars=["ORGO_API_KEY", "ORGO_COMPUTER_ID"],
        docs_url="https://docs.orgo.ai/api-reference/introduction",
        best_for=["full desktop workflows", "multi-window work", "files plus browser", "computer-use fallback"],
        avoid_when=["a browser-only API can complete the task cheaply"],
        supports_desktop=True,
        supports_long_running=True,
    ),
    "airtop": ProviderCapability(
        name="airtop",
        display_name="Airtop",
        stability="evaluating",
        cost_band="medium",
        env_vars=["AIRTOP_API_KEY"],
        docs_url="https://docs.airtop.ai/api-reference/airtop-api/sessions/create",
        best_for=["cloud sessions", "page-query extraction", "business-user GTM agents", "webhook-driven automations"],
        avoid_when=["you need a local open-source runtime", "the task must be MCP-native without a wrapper", "a free local browser is enough"],
        supports_auth=True,
        supports_long_running=True,
    ),
    "decodo-http": ProviderCapability(
        name="decodo-http",
        display_name="Decodo Raw HTTP",
        stability="stable",
        cost_band="low",
        env_vars=["DECODO_PROXY"],
        docs_url="https://decodo.com/",
        best_for=["raw HTTP", "API endpoints", "cheap residential proxy fetches", "bulk data where browser rendering is unnecessary"],
        avoid_when=["the site requires real browser rendering", "headless browser fingerprinting is the blocker"],
        supports_raw_http=True,
    ),
    "hyperbrowser": ProviderCapability(
        name="hyperbrowser",
        display_name="Hyperbrowser",
        stability="evaluating",
        cost_band="variable",
        env_vars=["HYPERBROWSER_API_KEY"],
        docs_url="https://www.hyperbrowser.ai/docs/home",
        best_for=["cloud browser automation to evaluate", "scale-oriented browser workflows"],
        avoid_when=["the workflow has not passed live tests yet"],
        supports_auth=True,
        supports_long_running=True,
    ),
    "steel": ProviderCapability(
        name="steel",
        display_name="Steel",
        stability="evaluating",
        cost_band="variable",
        env_vars=["STEEL_API_KEY"],
        docs_url="https://docs.steel.dev/",
        best_for=["cloud browser sessions to evaluate", "agent-friendly browser infrastructure"],
        avoid_when=["the workflow has not passed live tests yet"],
        supports_auth=True,
        supports_long_running=True,
    ),
    "browserless": ProviderCapability(
        name="browserless",
        display_name="Browserless",
        stability="evaluating",
        cost_band="variable",
        env_vars=["BROWSERLESS_TOKEN"],
        docs_url="https://docs.browserless.io/",
        best_for=["hosted browserless/chromium infrastructure", "Puppeteer or Playwright CDP control"],
        avoid_when=["natural-language agent actions are needed without building them"],
        supports_long_running=True,
    ),
}


def list_providers() -> list[dict]:
    from .costs import provider_cost_floor_usd

    rows = []
    for provider in PROVIDERS.values():
        row = provider.to_dict()
        row["cost_floor_usd"] = provider_cost_floor_usd(provider.name)
        rows.append(row)
    return rows


def provider_readiness() -> list[dict]:
    rows = []
    for provider in PROVIDERS.values():
        missing = [name for name in provider.env_vars if not os.environ.get(name)]
        cli = None
        if provider.name == "rtrvr":
            cli = bool(shutil.which("rtrvr"))
        elif provider.name == "playwright":
            cli = bool(shutil.which("playwright"))
        package = None
        if provider.name == "playwright":
            package = _has_module("playwright.sync_api")
        elif provider.name == "browserbase-stagehand":
            package = _has_module("browserbase") and _has_module("playwright.sync_api")
        elif provider.name == "browser-use":
            package = _has_module("browser_use_sdk")
        elif provider.name == "orgo":
            package = True
        elif provider.name in {"airtop", "hyperbrowser", "browserless"}:
            package = True
        elif provider.name == "steel":
            package = _has_module("playwright.sync_api")
        browser_runtime_available = None
        browser_runtime_error = None
        if provider.name == "playwright" and package:
            browser_runtime_available, browser_runtime_error = _playwright_runtime_available()
        required_missing = list(missing)
        optional_missing: list[str] = []
        if provider.name == "decodo-http":
            # Direct raw HTTP works without Decodo. DECODO_PROXY only gates residential proxy routing.
            optional_missing = missing
            required_missing = []
        supported_live_workflow_classes = _supported_live_workflow_classes(provider.name)
        latest_live_test = load_live_test_evidence(provider.name)
        certified_workflow_classes = _certified_workflow_classes(latest_live_test, supported_live_workflow_classes, provider.name)
        stale_certified_workflow_classes = _stale_certified_workflow_classes(latest_live_test, supported_live_workflow_classes, provider.name)
        ignored_unsupported_evidence_workflow_classes = _ignored_unsupported_evidence_workflow_classes(
            latest_live_test,
            supported_live_workflow_classes,
            provider.name,
        )
        ignored_provider_mismatch_evidence_workflow_classes = _ignored_provider_mismatch_evidence_workflow_classes(latest_live_test, provider.name)
        readiness_status = _readiness_status(
            provider.name,
            provider.stability,
            required_missing,
            optional_missing,
            package,
            browser_runtime_available,
            certified_workflow_classes,
            stale_certified_workflow_classes,
        )
        production_ready_scope = _production_ready_scope(readiness_status, certified_workflow_classes)
        if readiness_status == "ready_local":
            uncertified_workflow_classes = []
        else:
            uncertified_workflow_classes = [
                workflow_class for workflow_class in supported_live_workflow_classes if workflow_class not in certified_workflow_classes
            ]
        usable_now = readiness_status in {
            "ready_local",
            "live_test_passed",
            "live_test_stale",
            "usable_direct_http_no_proxy",
            "configured_live_test_recommended",
            "configured_live_test_required",
        }
        production_ready = production_ready_scope != "none"
        production_blockers = _production_blockers(
            provider.name,
            readiness_status,
            required_missing,
            optional_missing,
            uncertified_workflow_classes,
            ignored_unsupported_evidence_workflow_classes,
            ignored_provider_mismatch_evidence_workflow_classes,
        )
        rows.append(
            {
                "name": provider.name,
                "display_name": provider.display_name,
                "stability": provider.stability,
                "cost_band": provider.cost_band,
                "cost_floor_usd": _provider_cost_floor(provider.name),
                "missing_env": missing,
                "missing_required_env": required_missing,
                "missing_optional_env": optional_missing,
                "configured": not required_missing and (package is not False) and (browser_runtime_available is not False),
                "usable_now": usable_now,
                "production_ready": production_ready,
                "production_ready_scope": production_ready_scope,
                "certified_workflow_classes": certified_workflow_classes,
                "stale_certified_workflow_classes": stale_certified_workflow_classes,
                "supported_live_workflow_classes": supported_live_workflow_classes,
                "uncertified_workflow_classes": uncertified_workflow_classes,
                "ignored_unsupported_evidence_workflow_classes": ignored_unsupported_evidence_workflow_classes,
                "ignored_provider_mismatch_evidence_workflow_classes": ignored_provider_mismatch_evidence_workflow_classes,
                "requires_live_test_before_production": bool(
                    not production_ready
                    and not required_missing
                    and package is not False
                    and provider.name != "playwright"
                    and supported_live_workflow_classes
                ),
                "requires_live_test_before_broader_production": bool(production_ready and uncertified_workflow_classes),
                "production_blockers": production_blockers,
                "readiness_status": readiness_status,
                "ready": usable_now,
                "cli_available": cli,
                "python_package_available": package,
                "browser_runtime_available": browser_runtime_available,
                "browser_runtime_error": browser_runtime_error,
                "docs_url": provider.docs_url,
                "production_gate": _production_gate(provider.name, readiness_status, certified_workflow_classes),
                "next_action": _next_action(provider.name, readiness_status, required_missing, optional_missing, certified_workflow_classes),
                "latest_live_test": latest_live_test,
            }
        )
    return rows


def _provider_cost_floor(provider_name: str) -> float:
    from .costs import provider_cost_floor_usd

    return provider_cost_floor_usd(provider_name)


def _playwright_runtime_available() -> tuple[bool, str | None]:
    try:
        sync_api = importlib.import_module("playwright.sync_api")
        sync_playwright = getattr(sync_api, "sync_playwright")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                return True, None
            finally:
                try:
                    browser.close()
                except Exception:
                    pass
    except Exception as exc:  # pragma: no cover - environment-specific details
        return False, redact_text(str(exc))


def _readiness_status(
    provider_name: str,
    stability: str,
    missing_required_env: list[str],
    missing_optional_env: list[str],
    package: bool | None,
    browser_runtime_available: bool | None,
    certified_workflow_classes: list[str],
    stale_certified_workflow_classes: list[str],
) -> str:
    if missing_required_env:
        return "missing_env"
    if package is False:
        return "package_missing"
    if provider_name == "playwright" and browser_runtime_available is False:
        return "runtime_missing"
    if provider_name == "playwright":
        return "ready_local"
    if certified_workflow_classes:
        return "live_test_passed"
    if stale_certified_workflow_classes:
        return "live_test_stale"
    if provider_name == "decodo-http" and missing_optional_env:
        return "usable_direct_http_no_proxy"
    if stability == "evaluating":
        return "configured_live_test_required"
    return "configured_live_test_recommended"


def _certified_workflow_classes(latest_live_test: dict | None, supported_workflow_classes: list[str], provider_name: str) -> list[str]:
    return _evidence_classes_by_freshness(latest_live_test, supported_workflow_classes, provider_name, fresh=True)


def _stale_certified_workflow_classes(latest_live_test: dict | None, supported_workflow_classes: list[str], provider_name: str) -> list[str]:
    return _evidence_classes_by_freshness(latest_live_test, supported_workflow_classes, provider_name, fresh=False)


def _evidence_classes_by_freshness(
    latest_live_test: dict | None,
    supported_workflow_classes: list[str],
    provider_name: str,
    fresh: bool,
) -> list[str]:
    if not latest_live_test:
        return []
    supported = set(supported_workflow_classes)
    classes: list[str] = []
    for record in _evidence_workflow_records(latest_live_test):
        workflow_class = str(record.get("workflow_class") or "")
        if workflow_class not in supported:
            continue
        if not _evidence_record_provider_matches(record, provider_name):
            continue
        if record.get("status") != "passed":
            continue
        record_fresh = record.get("fresh")
        if record_fresh is None:
            record_fresh = latest_live_test.get("fresh")
        if bool(record_fresh) == fresh:
            classes.append(workflow_class)
    return _dedupe_workflow_classes(classes)


def _ignored_unsupported_evidence_workflow_classes(
    latest_live_test: dict | None,
    supported_workflow_classes: list[str],
    provider_name: str,
) -> list[str]:
    if not latest_live_test:
        return []
    supported = set(supported_workflow_classes)
    return _dedupe_workflow_classes(
        [
            str(record.get("workflow_class"))
            for record in _evidence_workflow_records(latest_live_test)
            if _evidence_record_provider_matches(record, provider_name) and str(record.get("workflow_class") or "") not in supported
        ]
    )


def _ignored_provider_mismatch_evidence_workflow_classes(latest_live_test: dict | None, provider_name: str) -> list[str]:
    if not latest_live_test:
        return []
    top_provider = latest_live_test.get("provider")
    if top_provider and str(top_provider) != provider_name:
        return _evidence_claimed_workflow_classes(latest_live_test)
    return _dedupe_workflow_classes(
        [
            str(record.get("workflow_class"))
            for record in _evidence_workflow_records(latest_live_test)
            if not _evidence_record_provider_matches(record, provider_name)
        ]
    )


def _evidence_workflow_records(latest_live_test: dict | None) -> list[dict]:
    if not latest_live_test:
        return []
    raw_records = latest_live_test.get("latest_by_workflow_class")
    records: list[dict] = []
    if isinstance(raw_records, dict):
        for key, item in raw_records.items():
            if not isinstance(item, dict):
                continue
            record = dict(item)
            record["workflow_class"] = str(record.get("workflow_class") or key)
            records.append(record)
    if records:
        return records
    workflow_class = latest_live_test.get("workflow_class")
    if workflow_class:
        record = dict(latest_live_test)
        record["workflow_class"] = str(workflow_class)
        return [record]
    return []


def _evidence_claimed_workflow_classes(latest_live_test: dict | None) -> list[str]:
    if not latest_live_test:
        return []
    classes = [str(record.get("workflow_class")) for record in _evidence_workflow_records(latest_live_test) if record.get("workflow_class")]
    for key in ("certified_workflow_classes", "stale_certified_workflow_classes"):
        values = latest_live_test.get(key)
        if isinstance(values, list):
            classes.extend(str(item) for item in values)
    if latest_live_test.get("workflow_class"):
        classes.append(str(latest_live_test["workflow_class"]))
    return _dedupe_workflow_classes(classes)


def _evidence_record_provider_matches(record: dict, provider_name: str) -> bool:
    return record.get("provider") == provider_name


def _dedupe_workflow_classes(workflow_classes: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for workflow_class in workflow_classes:
        if workflow_class in seen:
            continue
        seen.add(workflow_class)
        deduped.append(workflow_class)
    return deduped


def _supported_live_workflow_classes(provider_name: str) -> list[str]:
    if provider_name in SUPPORTED_LIVE_WORKFLOW_CLASSES:
        return list(SUPPORTED_LIVE_WORKFLOW_CLASSES[provider_name])
    if provider_name in PROVIDERS:
        return list(DEFAULT_REMOTE_LIVE_WORKFLOW_CLASSES)
    return []


def _production_blockers(
    provider_name: str,
    readiness_status: str,
    missing_required_env: list[str],
    missing_optional_env: list[str],
    uncertified_workflow_classes: list[str],
    ignored_unsupported_evidence_workflow_classes: list[str],
    ignored_provider_mismatch_evidence_workflow_classes: list[str],
) -> list[str]:
    blockers: list[str] = []
    if missing_required_env:
        blockers.append("missing required env vars: " + ", ".join(missing_required_env))
    if readiness_status == "package_missing":
        blockers.append("provider package or CLI is missing")
    if readiness_status == "runtime_missing":
        blockers.append("Playwright browser runtime is missing; run `playwright install chromium`.")
    if provider_name == "decodo-http" and missing_optional_env:
        blockers.append("missing optional residential proxy env vars: " + ", ".join(missing_optional_env))
    if readiness_status == "live_test_stale":
        blockers.append("live-test evidence is stale")
    if readiness_status != "ready_local" and ignored_unsupported_evidence_workflow_classes:
        blockers.append(
            "ignored unsupported live-test evidence for workflow classes: " + ", ".join(ignored_unsupported_evidence_workflow_classes)
        )
    if readiness_status != "ready_local" and ignored_provider_mismatch_evidence_workflow_classes:
        blockers.append(
            "ignored provider-mismatched live-test evidence for workflow classes: " + ", ".join(ignored_provider_mismatch_evidence_workflow_classes)
        )
    if readiness_status in {
        "configured_live_test_required",
        "configured_live_test_recommended",
        "usable_direct_http_no_proxy",
        "live_test_stale",
        "live_test_passed",
    } and uncertified_workflow_classes:
        blockers.append("missing fresh live-test evidence for workflow classes: " + ", ".join(uncertified_workflow_classes))
    return blockers


def _production_ready_scope(readiness_status: str, certified_workflow_classes: list[str]) -> str:
    if readiness_status == "ready_local":
        return "local_verified"
    if readiness_status == "live_test_passed" and certified_workflow_classes:
        return "workflow_class:" + ",".join(certified_workflow_classes)
    return "none"


def _production_gate(provider_name: str, readiness_status: str, certified_workflow_classes: list[str]) -> str:
    if readiness_status == "ready_local":
        return "Local provider is covered by verify-super-browser and fixture live tests."
    if readiness_status == "live_test_passed":
        classes = ", ".join(certified_workflow_classes) if certified_workflow_classes else "unknown workflow class"
        return f"Fresh live-test evidence exists for workflow class: {classes}. Run task-class live tests before broader production use."
    if readiness_status == "live_test_stale":
        return f"Previous provider live-test evidence is stale. Rerun `super-browser live-test --provider {provider_name}`."
    if readiness_status == "runtime_missing":
        return "Run `playwright install chromium`, then rerun `super-browser doctor` and `super-browser live-test --provider local`."
    if readiness_status == "usable_direct_http_no_proxy":
        return "Direct raw HTTP is usable; configure DECODO_PROXY and run a live test before claiming residential-proxy readiness."
    if readiness_status == "configured_live_test_required":
        return f"Run `super-browser live-test --provider {provider_name}` and inspect artifacts before production use."
    if readiness_status == "configured_live_test_recommended":
        return f"Run `super-browser live-test --provider {provider_name}` before production use or customer-facing workflows."
    if readiness_status == "package_missing":
        return "Install the provider package or CLI, then rerun `super-browser doctor`."
    return "Configure missing env vars, then rerun `super-browser doctor` and the provider live test."


def _next_action(provider_name: str, readiness_status: str, missing_required_env: list[str], missing_optional_env: list[str], certified_workflow_classes: list[str]) -> str:
    if readiness_status == "missing_env":
        return "Set env vars: " + ", ".join(missing_required_env)
    if readiness_status == "package_missing":
        return "Install the provider package or CLI required by this adapter."
    if readiness_status == "runtime_missing":
        return "Run `playwright install chromium`, then rerun `super-browser doctor`."
    if readiness_status == "usable_direct_http_no_proxy":
        return "Set DECODO_PROXY for residential proxy routing, or use direct raw HTTP without proxy."
    if readiness_status == "live_test_passed":
        if provider_name == "decodo-http" and missing_optional_env:
            return "Ready for verified direct raw HTTP; set DECODO_PROXY for residential proxy routing."
        classes = ", ".join(certified_workflow_classes) if certified_workflow_classes else "latest workflow"
        return f"Ready for verified workflow class: {classes}."
    if readiness_status == "live_test_stale":
        return f"Rerun `super-browser live-test --provider {provider_name}`."
    if readiness_status in {"configured_live_test_required", "configured_live_test_recommended"}:
        return f"Run `super-browser live-test --provider {provider_name}`."
    if missing_optional_env:
        return "Optional env vars missing: " + ", ".join(missing_optional_env)
    return "Ready for local verified use."
