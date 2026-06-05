     1|---
     2|name: super-browser
     3|version: "2.0"
     4|description: Five-tier browser and desktop automation stack — Browser Use Cloud (anti-detection), Browserbase (quick tasks), Airtop (no-code), Rtrvr (MCP), Orgo Machines (full desktop VMs), Decodo (raw proxies). Strategic routing by task type and protection level.
     5|---
     6|
     7|# Super Browser — Multi-Layer Automation Stack
     8|
     9|Five-tier automation architecture. From quick single-page extraction to full desktop VM control, with Decodo residential proxies as the raw proxy backbone.
    10|
    11|## Architecture Overview
    12|
    13|```
    14|┌─────────────────────────────────────────────────────────┐
    15|│                   SUPER BROWSER STACK                    │
    16|├─────────────┬─────────────┬──────────┬────────┬─────────┤
    17|│  TIER 1     │  TIER 2     │ TIER 3   │ TIER 4 │ TIER 5  │
    18|│  Browser    │  Browser-   │ Airtop   │ Rtrvr  │ Orgo    │
    19|│  Use Cloud  │  base       │          │        │ Machines│
    20|├─────────────┼─────────────┼──────────┼────────┼─────────┤
    21|│ Anti-detect │ Quick       │ No-code  │ MCP    │ Full    │
    22|│ Hardened    │ Single-page │ SaaS     │ Auth   │ Desktop │
    23|│ Chromium    │ extraction  │ Backup   │ Sessions│ VMs     │
    24|├─────────────┼─────────────┼──────────┼────────┼─────────┤
    25|│ $29/mo      │ Free        │ $26/mo   │ BYOK   │ $29/mo  │
    26|└─────────────┴─────────────┴──────────┴────────┴─────────┘
    27|                      │
    28|              ┌───────┴───────┐
    29|              │    DECODO     │
    30|              │  Raw Proxies  │
    31|              │   $2/GB       │
    32|              └───────────────┘
    33|```
    34|
    35|## Quick Decision Matrix
    36|
    37|| Site Type | Primary | Fallback | Cost |
    38||-----------|---------|----------|------|
    39|| **Meta/Facebook** | Browser Use Cloud | Browserbase | $0.02/hr + $5/GB proxy |
    40|| **LinkedIn** | Browser Use Cloud | Rtrvr Extension | $0.02/hr + $5/GB proxy |
    41|| **Anti-bot protected (Cloudflare, PerimeterX)** | Browser Use Cloud | Airtop | $0.02/hr + $5/GB proxy |
    42|| **JS-heavy SPAs** | Browser Use Cloud | Browserbase | $0.02/hr + $5/GB proxy |
    43|| **Quick single-page** | Browserbase (browser tool) | Rtrvr scrape | Free tier |
    44|| **Authenticated sites (OAuth, cookies)** | Rtrvr Extension | Browser Use Cloud Profiles | Free (BYOK) / $29/mo |
    45|| **Scheduled GTM workflows** | Airtop | Browser Use Cloud cron | $26/mo |
    46|| **Raw API calls (JSON endpoints)** | curl + Decodo proxy | requests + Decodo | $2/GB |
    47|| **Local development/testing** | Browser Use open-source | Playwright + stealth | Free (bring LLM keys) |
    48|
    49|| **Full desktop automation** | Orgo Machines | Manual fallback | $29/mo (5 VMs) |
    50|| **When browser isn't enough** | Orgo Machines | Manual intervention | $29/mo |
    51|
    52|## Tier 1: Browser Use Cloud (PRIMARY WORKHORSE)
    53|
    54|### Why It's #1
    55|
    56|Browser Use Cloud runs a **hardened, forked Chromium** with anti-detect fingerprinting that passes CreepJS and BrowserLeaks. Canvas, WebGL, fonts, and navigator properties are randomized per session. It auto-bypasses Cloudflare, PerimeterX, and most anti-bot challenges. This is the only tool that consistently worked against Meta Ad Library in our testing.
    57|
    58|Built-in **US residential proxies** (195+ countries available) — no separate proxy service needed for most use cases. Ad and cookie banner auto-dismissal included.
    59|
    60|### Pricing
    61|
    62|- **Dev plan: $29/mo** ($29 credits)
    63|- Browser: $0.02/hr
    64|- Proxy bandwidth: $5/GB
    65|- LLM tokens: 1.2x provider rates (Claude Sonnet 4.6 at $3.60/$18.00 per 1M)
    66|- Free tier: 10 tasks/mo, 3 concurrent sessions
    67|
    68|### Python SDK (v3) — Primary Integration
    69|
    70|```python
    71|from browser_use_sdk.v3 import BrowserUse, BuModel, ProxyCountryCode
    72|
    73|# Initialize
    74|client = BrowserUse(api_key="bu_live_...")  # or env: BROWSER_USE_API_KEY
    75|
    76|# Create a session (isolated browser with proxy)
    77|session = client.sessions.create(
    78|    model=BuModel.claude_sonnet_4_6,           # Best for complex tasks
    79|    proxy_country_code=ProxyCountryCode.US,     # US residential proxy
    80|    # proxy_country_code=None,                  # Disable proxy if not needed
    81|    keep_alive=True,                            # Persist between tasks
    82|)
    83|
    84|# Run a task
    85|result = client.sessions.run(
    86|    session_id=session.id,
    87|    task="Go to facebook.com/ads/library, search for 'bath remodel'..."
    88|)
    89|
    90|# Get structured output (Pydantic model)
    91|from pydantic import BaseModel
    92|
    93|class Advertiser(BaseModel):
    94|    name: str
    95|    page_url: str
    96|    ad_count: int
    97|
    98|result = client.sessions.run(
    99|    session_id=session.id,
   100|    task="Extract all advertisers and their ad counts",
   101|    output_schema=Advertiser,  # Returns typed list[Advertiser]
   102|)
   103|
   104|# Stop session when done
   105|client.sessions.stop(session_id=session.id)
   106|```
   107|
   108|### CDP WebSocket (Direct Browser Control)
   109|
   110|Connect Playwright/Puppeteer/Selenium directly to Browser Use's cloud browsers:
   111|
   112|```python
   113|from playwright.async_api import async_playwright
   114|
   115|# Get CDP URL from Browser Use
   116|browser = client.browsers.create(
   117|    proxy_country_code=ProxyCountryCode.US,
   118|    keep_alive=True,
   119|)
   120|cdp_url = browser.cdp_url  # wss://connect.browser-use.com?apiKey=***&sessionId=...
   121|
   122|# Connect Playwright
   123|async with async_playwright() as p:
   124|    browser = await p.chromium.connect_over_cdp(cdp_url)
   125|    page = browser.contexts[0].pages[0]
   126|    await page.goto("https://facebook.com/ads/library")
   127|    # ... full Playwright control ...
   128|```
   129|
   130|### MCP Server (AI Agent Integration)
   131|
   132|Add to Hermes `config.yaml`:
   133|
   134|```yaml
   135|mcp_servers:
   136|  browser-use:
   137|    type: http
   138|    url: https://api.browser-use.com/v3/mcp
   139|    headers:
   140|      Authorization: "Bearer bu_live_YOUR_API_KEY"
   141|```
   142|
   143|### CLI
   144|
   145|```bash
   146|# Install
   147|uvx browser-use install
   148|
   149|# Interactive
   150|browser-use open https://example.com
   151|browser-use state
   152|browser-use click "Login"
   153|browser-use type "username" "hello@example.com"
   154|browser-use screenshot page.png
   155|```
   156|
   157|### Key Features
   158|
   159|- **Profiles**: Persistent cookies/localStorage across sessions
   160|- **2FA handling**: Agent Mail (auto-enabled inbox), TOTP via pyotp, human-in-the-loop
   161|- **Recording**: MP4 video recording of sessions
   162|- **Live preview**: `live_url` for real-time observation
   163|- **Structured output**: Pydantic/Zod schemas
   164|- **Deterministic rerun**: Cache workflows, ~99% cheaper re-runs
   165|- **Workspaces**: Upload/download files for agent use
   166|- **Streaming**: `for await` pattern for real-time agent messages
   167|
   168|### Limitations
   169|
   170|- Session timeout: 15 min inactivity, max 4 hours
   171|- Recording URLs expire in 1 hour
   172|- Custom proxy requires **enterprise plan** (above Scaleup) — can't use Decodo directly
   173|- v3 agent is cloud-only, not in open-source
   174|- $5/GB proxy bandwidth can add up for data-heavy scraping
   175|
   176|---
   177|
   178|## Tier 2: Browserbase (QUICK TASKS)
   179|
   180|Already integrated into Hermes via the `browser_*` tools. Zero setup, zero cost (free tier).
   181|
   182|### Available Tools
   183|
   184|- `browser_navigate` — load a URL, returns accessibility snapshot
   185|- `browser_click` — click elements by ref ID
   186|- `browser_type` — type into input fields
   187|- `browser_scroll` — scroll up/down
   188|- `browser_snapshot` — get page accessibility tree
   189|- `browser_console` — JS execution, console log reading
   190|- `browser_vision` — screenshot + AI analysis
   191|- `browser_get_images` — list all images on page
   192|- `browser_back` — navigate back
   193|- `browser_press` — keyboard keys
   194|
   195|### When to Use
   196|
   197|- Single-page extraction (quick, no session management)
   198|- Visual verification (CAPTCHAs, page rendering)
   199|- Interactive debugging (click around, see what happens)
   200|- Lightweight scraping of non-aggressively-protected pages
   201|
   202|### Known Issues
   203|
   204|- Fragile at scale — **Facebook blocks after ~2-3 queries** (API splash page)
   205|- No persistent profiles between sessions
   206|- No custom proxy injection (uses Browserbase's own infrastructure)
   207|- Subagent timeout at 600s for long-running tasks
   208|- Success rate: ~71% page loads (vs Anchor's claimed 93%)
   209|
   210|### Extraction Pattern (Proven)
   211|
   212|```javascript
   213|// Inside browser_console for Meta Ad Library
   214|const links = document.querySelectorAll('a[href*="/"]');
   215|const advertisers = new Set();
   216|links.forEach(a => {
   217|    const href = a.getAttribute('href');
   218|    if (href && !href.includes('facebook.com/ads')) {
   219|        advertisers.add(JSON.stringify({name: a.textContent.trim(), url: href}));
   220|    }
   221|});
   222|return [...advertisers].map(JSON.parse);
   223|```
   224|
   225|---
   226|
   227|## Tier 3: Airtop (NO-CODE BACKUP)
   228|
   229|### When to Use
   230|
   231|Browser Use Cloud is the primary tool, but Airtop fills gaps:
   232|- **Non-developer workflows** — marketing/sales can build agents without code
   233|- **Pre-built templates** — faster than coding from scratch for common GTM patterns
   234|- **Scheduled monitoring** — built-in scheduling vs coding cron + Browser Use
   235|- **SOC2/HIPAA compliance** — enterprise requirements Browser Use doesn't meet
   236|
   237|### Setup
   238|
   239|- Sign up at airtop.ai
   240|- Starter plan: $26/mo (30K-150K credits)
   241|- API key from portal.airtop.ai/api-keys
   242|- Base URL: `https://api.airtop.ai/api/`
   243|
   244|### REST API
   245|
   246|```bash
   247|# Trigger an agent
   248|curl -X POST "https://api.airtop.ai/api/hooks/agents/{agentId}/webhooks/{webhookId}" \
   249|  -H "Authorization: Bearer *** \
   250|  -H "Content-Type: application/json" \
   251|  -d '{"configVars": {"url": "https://target.com"}}'
   252|
   253|# Get results
   254|curl "https://api.airtop.ai/api/invocations/{invocationId}" \
   255|  -H "Authorization: Bearer ***
   256|```
   257|
   258|### Proxy Support
   259|
   260|- Built-in residential proxy (Starter+)
   261|- Custom proxy (Professional+): Oxylabs, Smartproxy, IPRoyal supported
   262|- Decodo could work as custom proxy on Professional plan ($170/mo)
   263|
   264|---
   265|
   266|## Tier 4: Rtrvr (MCP + AUTH SESSIONS)
   267|
   268|Already documented in `rtrvr` skill. Key use cases in this stack:
   269|
   270|- **Authenticated sessions**: Chrome Extension preserves login state
   271|- **MCP integration**: 8 MCP tools available to any MCP client
   272|- **BYOK (Gemini)**: Free usage with your own Gemini API key
   273|
   274|### When to Prefer Rtrvr Over Browser Use Cloud
   275|
   276|- Task requires logged-in session to a service you already have auth for
   277|- Need MCP-native tool calling (not wrapping a REST API)
   278|- Cost-sensitive: BYOK Gemini = free, vs Browser Use Cloud at $0.02/hr + LLM costs
   279|
   280|---
   281|
   282|---
   283|
   284|## Tier 5: Orgo Machines (FULL DESKTOP VMs)
   285|
   286|### Why It Exists in This Stack
   287|
   288|Sometimes browser automation isn't enough. You need a real computer — a full Linux desktop with applications, file systems, terminals, and multi-window workflows. Orgo provides sub-500ms boot cloud VMs that AI agents can fully control. When Browser Use Cloud or Browserbase can't handle a task because it requires:
   289|
   290|- Desktop applications (not web apps)
   291|- Multi-window workflows
   292|- File system operations + browser simultaneously
   293|- Local development environments
   294|- GPU-accelerated workloads
   295|- Complex software that doesn't expose a web interface
   296|
   297|### Pricing
   298|
   299|| Plan | Price/mo | VMs | vCPU | RAM | Disk | AI Credits |
   300||------|----------|-----|------|-----|------|------------|
   301|| **Hacker** | $29 | 5 | 1 | 4GB | 20GB | $10 |
   302|| Team | $112 | 20 | 2 | 8GB | 30GB | $50 |
   303|| Scale | $224 | 50 | 4 | 16GB | 50GB | $100 |
   304|
   305|Annual billing: ~10% discount. All plans include AI credits for LLM usage.
   306|
   307|### Python SDK
   308|
   309|```python
   310|from orgo import OrgoClient
   311|
   312|client = OrgoClient(api_key="org_...")
   313|
   314|# Create a VM
   315|vm = client.vms.create(
   316|    template="ubuntu-desktop",
   317|    plan="hacker",
   318|)
   319|
   320|# Wait for boot (sub-500ms)
   321|vm.wait_ready()
   322|
   323|# Execute commands
   324|result = vm.execute("ls -la /home/agent")
   325|print(result.stdout)
   326|
   327|# Run browser automation inside the VM
   328|vm.execute("playwright test --headed")
   329|
   330|# Take screenshot of the desktop
   331|screenshot = vm.screenshot()
   332|with open("desktop.png", "wb") as f:
   333|    f.write(screenshot)
   334|
   335|# Transfer files
   336|vm.upload("script.py", "/home/agent/script.py")
   337|vm.download("/home/agent/output.csv", "output.csv")
   338|
   339|# Clean up
   340|vm.terminate()
   341|```
   342|
   343|### WebSocket API (Real-time Control)
   344|
   345|```python
   346|import asyncio
   347|import websockets
   348|
   349|async with websockets.connect("wss://api.orgo.ai/v1/vms/{vm_id}/ws") as ws:
   350|    # Send mouse click
   351|    await ws.send(json.dumps({"type": "click", "x": 500, "y": 300}))
   352|
   353|    # Type text
   354|    await ws.send(json.dumps({"type": "type", "text": "hello world"}))
   355|
   356|    # Receive desktop stream
   357|    async for msg in ws:
   358|        frame = json.loads(msg)
   359|        # frame["screenshot"] = base64 PNG
   360|```
   361|
   362|### Key Features
   363|
   364|- **Sub-500ms cold boot** — fastest in the industry, instant agent dispatch
   365|- **Full Linux desktop** — Xfce/Fluxbox with xdotool for mouse/keyboard control
   366|- **Firecracker micro-VMs** — hardware-level isolation, secure by default
   367|- **Double encryption at rest** — rotating credentials per session
   368|- **File transfer** — upload/download between host and VM
   369|- **Template system** — pre-built Docker images, custom templates
   370|- **GPU roadmap** — NVIDIA MIG partitioning on A100, whole-GPU A10/L40s
   371|- **Multi-model**: Claude Computer Use, OpenAI CUA, OpenClaw, LangChain
   372|
   373|### When to Use Orgo Over Browsers
   374|
   375|```
   376|Browser Use Cloud can't do these. Orgo can:
   377|
   378|• Install and run desktop software → browsers can't install apps
   379|• Multi-window workflows → browsers are single-window
   380|• Local file processing → browsers are sandboxed
   381|• GPU compute → browsers have no GPU access
   382|• Full terminal access → browsers have no shell
   383|• Run Playwright/Selenium locally → full control, no CDP limits
   384|```
   385|
   386|### Open-Source Alternative
   387|
   388|There is an open-source clone at `github.com/Julianb233/orgo-clone`:
   389|- Fastify/PostgreSQL/Drizzle/Dockerode/BullMQ
   390|- Xvfb/Fluxbox/x11vnc/xdotool for headless desktop
   391|- Self-hosted with your own Docker infrastructure
   392|- 85 commits, active development
   393|
   394|### Limitations
   395|
   396|- **Cost per VM** — $29/mo for 5 VMs means ~$5.80/VM, but only 5 concurrent
   397|- **Not a browser tool** — you bring your own browser automation (Playwright, Puppeteer)
   398|- **No built-in stealth** — VMs use standard Linux, no anti-detection out of the box
   399|- **GPU not yet available** — roadmap, not production
   400|- **Proprietary** — closed-source SaaS (use the clone for self-hosting)
   401|
   402|---
   403|
   404|## Decodo Proxy Integration
   405|
   406|### Where Decodo Fits
   407|
   408|Browser Use Cloud has built-in residential proxies, so Decodo is NOT needed for primary browser automation. Decodo's role in this stack:
   409|
   410|1. **Raw HTTP scraping**: curl/requests through residential IPs for API endpoints
   411|2. **Cost optimization**: $2/GB vs Browser Use Cloud's $5/GB for high-volume data extraction
   412|3. **Playwright fallback**: When you need full control of the browser stack
   413|4. **Geo-targeting that Browser Use doesn't support**
   414|
   415|### Decodo Proxy Details
   416|
   417|```
   418|Proxy: http://spo2nwl1tw:***@us.decodo.com:10001
   419|Ports: 10001-10007 (round-robin for IP rotation)
   420|Type: Residential, sticky 10-minute sessions
   421|Cost: $2/GB
   422|```
   423|
   424|### Usage Patterns
   425|
   426|#### Pattern 1: curl + Decodo
   427|
   428|```bash
   429|curl -x "http://spo2nwl1tw:***@us.decodo.com:10001" \
   430|  "https://api.target.com/data" \
   431|  -H "User-Agent: Mozilla/5.0 ..."
   432|```
   433|
   434|#### Pattern 2: Python requests + Decodo
   435|
   436|```python
   437|import requests
   438|
   439|proxies = {
   440|    "http": "http://spo2nwl1tw:***@us.decodo.com:10001",
   441|    "https": "http://spo2nwl1tw:***@us.decodo.com:10001",
   442|}
   443|resp = requests.get("https://api.target.com/data", proxies=proxies)
   444|```
   445|
   446|#### Pattern 3: Playwright + Decodo + Stealth
   447|
   448|```python
   449|from playwright.async_api import async_playwright
   450|
   451|async with async_playwright() as p:
   452|    browser = await p.chromium.launch(
   453|        headless=True,
   454|        proxy={
   455|            "server": "http://us.decodo.com:10001",
   456|            "username": "spo2nwl1tw",
   457|            "password": "***",
   458|        }
   459|    )
   460|    context = await browser.new_context(
   461|        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
   462|        viewport={"width": 1920, "height": 1080},
   463|    )
   464|    page = await context.new_page()
   465|    await page.goto("https://target.com")
   466|```
   467|
   468|**Warning**: Playwright + Decodo + playwright-stealth was tested against Facebook Ad Library and **failed** — Facebook's headless detection still blocks it. Use Browser Use Cloud for Meta.
   469|
   470|#### Pattern 4: Browser Use open-source + Decodo
   471|
   472|The open-source `browser-use` library has **no built-in stealth**. To use Decodo with it:
   473|
   474|```python
   475|from browser_use import Agent, Browser, BrowserConfig
   476|
   477|browser = Browser(
   478|    config=BrowserConfig(
   479|        headless=False,  # Non-headless reduces detection
   480|        proxy={
   481|            "server": "http://us.decodo.com:10001",
   482|            "username": "spo2nwl1tw",
   483|            "password": "***",
   484|        }
   485|    )
   486|)
   487|
   488|agent = Agent(
   489|    task="Extract data from...",
   490|    llm_provider="anthropic",
   491|    llm_model="claude-sonnet-4-6",
   492|    browser=browser,
   493|)
   494|result = await agent.run()
   495|```
   496|
   497|**Warning**: This will NOT bypass advanced anti-bot detection (Cloudflare, Facebook). For those, use Browser Use Cloud.
   498|
   499|---
   500|
   501|