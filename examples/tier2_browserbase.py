#!/usr/bin/env python3
"""
Tier 2: Browserbase — Quick single-page extraction via Hermes browser tools.

Already integrated into Hermes Agent. Zero setup, zero cost (free tier).
Best for: quick lookups, visual verification, debugging, lightweight scraping.

⚠️ Known limitation: Facebook blocks Browserbase after ~2-3 queries.
For Meta/LinkedIn/Cloudflare, use Tier 1 (Browser Use Cloud).

Hermes browser tools available:
    browser_navigate, browser_click, browser_type, browser_scroll,
    browser_snapshot, browser_console, browser_vision, browser_get_images,
    browser_back, browser_press

Usage: Called by Hermes Agent directly, not standalone.
"""

# ============================================================================
# PATTERN 1: Single-Page Extraction
# ============================================================================

"""
# When Hermes encounters a simple extraction task, use this flow:

browser_navigate("https://example.com/products")
browser_snapshot(full=True)  # Get full page content
browser_console(expression="document.querySelectorAll('.product').length")

# Extract specific data
browser_console(expression='''
    Array.from(document.querySelectorAll('.product-card')).map(card => ({
        name: card.querySelector('.name').textContent,
        price: card.querySelector('.price').textContent,
        url: card.querySelector('a').href
    }))
''')
"""


# ============================================================================
# PATTERN 2: Meta Ad Library Extraction (Proven JavaScript)
# ============================================================================

"""
This is the JavaScript pattern that successfully extracted 105 advertisers
for "bath remodel" and 92 for "solar installation" from Meta Ad Library.

Steps:
    1. browser_navigate("https://www.facebook.com/ads/library/...")
    2. browser_console with the extraction script below
    3. Process results

IMPORTANT: Facebook blocks after 2-3 queries. Use Tier 1 for scale.
"""

META_AD_EXTRACTION_JS = """
// Extract unique advertisers from Meta Ad Library results page
const links = document.querySelectorAll('a[href*="/"]');
const advertisers = new Set();

links.forEach(a => {
    const href = a.getAttribute('href');
    const text = a.textContent.trim();

    // Skip internal Facebook links and empty text
    if (!href || !text) return;
    if (href.includes('facebook.com/ads/library')) return;
    if (href.includes('facebook.com/help')) return;
    if (href.includes('facebook.com/business')) return;

    // Only keep links that look like advertiser pages
    if (text.length > 2 && text.length < 100) {
        advertisers.add(JSON.stringify({
            name: text,
            url: href.startsWith('http') ? href : 'https://www.facebook.com' + href
        }));
    }
});

// Return as array of objects
JSON.stringify([...advertisers].map(JSON.parse));
"""


# ============================================================================
# PATTERN 3: Scroll-Based Pagination
# ============================================================================

"""
For pages with infinite scroll, you need to scroll before extracting.

browser_scroll("down")
browser_scroll("down")
browser_scroll("down")
# Then extract...
browser_console(expression=META_AD_EXTRACTION_JS)
"""


# ============================================================================
# PATTERN 4: Visual Verification
# ============================================================================

"""
When you need to see what the page actually looks like (CAPTCHAs, rendering issues):

browser_vision(question="Is this page showing results or a login wall?")
browser_vision(question="What CAPTCHA type is displayed?")
browser_vision(question="Are there any ad results visible on this page?")
"""


# ============================================================================
# PATTERN 5: Batch Extraction (Multi-URL)
# ============================================================================

"""
For multiple URLs, use delegate_task to parallelize:

delegate_task(
    goal="Scrape advertisers from these Meta Ad Library URLs",
    tasks=[
        {"goal": "Extract advertisers from URL 1", "toolsets": ["browser"]},
        {"goal": "Extract advertisers from URL 2", "toolsets": ["browser"]},
        {"goal": "Extract advertisers from URL 3", "toolsets": ["browser"]},
    ]
)

⚠️ Each subagent gets its own browser session. Facebook blocks after
2-3 sessions per IP range. Don't expect more than 2-3 to succeed.
"""


# ============================================================================
# KNOWN BUGS & WORKAROUNDS
# ============================================================================

"""
1. Facebook API splash page
   Symptom: Page loads but shows "Ads Library API" splash instead of results
   Cause: Facebook detects the browser and serves a degraded version
   Fix: Switch to Tier 1 (Browser Use Cloud)

2. Instagram rate limits
   Symptom: Results stop loading after ~24 scrolls
   Cause: Instagram's aggressive rate limiting
   Fix: Add delays between scrolls, switch to Tier 1

3. Subagent timeout (600s)
   Symptom: delegate_task subagent never returns
   Cause: Browser operations are slow, subagent timeout is hardcoded
   Fix: Use smaller batches, fewer scrolls per subagent

4. DOM not ready
   Symptom: JavaScript extraction returns empty array
   Cause: Page hasn't finished rendering
   Fix: browser_scroll first, then wait 2-3 seconds, then extract
"""