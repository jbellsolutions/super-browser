from __future__ import annotations

PROVIDER_SIGNUP = {
    "BROWSER_USE_API_KEY": {
        "provider": "browser-use",
        "label": "Browser Use Cloud",
        "signup_url": "https://cloud.browser-use.com/",
        "docs_url": "https://docs.browser-use.com/",
        "env_var": "BROWSER_USE_API_KEY",
        "required_for": "Anti-bot cloud browser, profiles, recordings",
    },
    "HYPERBROWSER_API_KEY": {
        "provider": "hyperbrowser",
        "label": "Hyperbrowser",
        "signup_url": "https://www.hyperbrowser.ai/",
        "docs_url": "https://docs.hyperbrowser.ai/",
        "env_var": "HYPERBROWSER_API_KEY",
        "required_for": "Cloud scrape jobs and scale browser automation",
    },
    "AIRTOP_API_KEY": {
        "provider": "airtop",
        "label": "Airtop",
        "signup_url": "https://www.airtop.ai/",
        "docs_url": "https://docs.airtop.ai/",
        "env_var": "AIRTOP_API_KEY",
        "required_for": "Cloud sessions, page-query, scheduled GTM workflows",
    },
    "STEEL_API_KEY": {
        "provider": "steel",
        "label": "Steel",
        "signup_url": "https://steel.dev/",
        "docs_url": "https://docs.steel.dev/",
        "env_var": "STEEL_API_KEY",
        "required_for": "Hosted Chromium sessions over Playwright CDP",
    },
    "ORGO_API_KEY": {
        "provider": "orgo",
        "label": "Orgo",
        "signup_url": "https://orgo.ai/",
        "docs_url": "https://docs.orgo.ai/api-reference/introduction",
        "env_var": "ORGO_API_KEY",
        "required_for": "Full desktop / computer-use VMs",
    },
    "DECODO_PROXY": {
        "provider": "decodo-http",
        "label": "Decodo residential proxy",
        "signup_url": "https://decodo.com/",
        "docs_url": "https://decodo.com/proxies/residential-proxies",
        "env_var": "DECODO_PROXY",
        "required_for": "Optional residential proxy routing for raw HTTP (not required for direct HTTP)",
        "optional": True,
    },
}
