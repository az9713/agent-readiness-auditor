# Checks reference

The complete reference for all 22 checks the auditor runs: **12 Tier-A facts** plus **10 Tier-B proxies**.

The two tiers report differently:

| Tier | What it is | Statuses it returns |
|------|-----------|---------------------|
| **A** (facts) | Deterministic — one fetch or one parse, a clear result. | `pass`, `fail`, or `unknown` |
| **B** (proxy) | An indirect signal. A positive result is trustworthy; silence is not proof of absence. | `pass` or `unknown` — and **`fail` only for a detected barrier** (check #16) |

Each status:

| Status | Symbol | Meaning |
|--------|--------|---------|
| `pass` | ✅ | The signal was looked for and found. For Tier B, a trustworthy positive. |
| `fail` | ❌ | Tier A: the signal is genuinely absent. Tier B: a trustworthy *negative* barrier was detected (only check #16). |
| `unknown` | — | Tier A: the check could not be performed. Tier B: no signal was visible — **not** proof the capability is absent. |

The checks keep their original ID numbers from the [design reference](../../agent-readiness-auditor.md)'s 25-check catalog, so check IDs are non-contiguous (the gaps are the 3 Tier-C checks, which cannot be measured from outside and are not run).

**Why a Tier-B `—` is not a `❌`:** a Tier-B proxy measures an indirect clue. When the clue is absent, the real capability may still be present in a form the tool cannot see (an API at an unguessed path, a licence in prose, a protocol onboarded through a platform). Reporting that as `unknown` rather than `fail` is the core honesty rule. See [development journey, Fork 4](../../development-journey.md#fork-4-what-proxy-means).

---

## Summary table

| ID | Name | Group | Looks at |
|----|------|-------|----------|
| 1 | llms.txt present | Read | `GET /llms.txt` |
| 11 | Structured data (homepage) | Read | Homepage HTML |
| 14 | Structured-data coverage | Read | Sampled pages from the sitemap |
| 6 | Explicit AI-bot policy | Trust | `GET /robots.txt` |
| 7 | AI-bot allow/block stance | Trust | Parsed `robots.txt` |
| 18 | Machine-readable dates | Freshness | Homepage HTML |
| 19 | Last-Modified / ETag | Freshness | Homepage response headers |
| 20 | Canonical URL | Freshness | Homepage HTML / `Link` header |
| 21 | Cache headers | Freshness | Homepage response headers |
| 2 | sitemap.xml present | Discovery | `GET /sitemap.xml` |
| 3 | Readable without JavaScript | Discovery | Raw HTML text vs browser-rendered text |
| 12 | OpenGraph tags | Discovery | Homepage HTML |

The 10 Tier-B proxies, grouped into their own dimensions (Docs, Permissions, Commerce, Monetization):

| ID | Name | Group | Looks at |
|----|------|-------|----------|
| 4 | Clean text/markdown alternative | Docs | `Accept: text/markdown` negotiation, `<link rel=alternate>`, `/llms-full.txt` |
| 5 | Public API spec | Docs | `/openapi.json`, `/.well-known/openapi.json`, `/swagger.json` |
| 9 | Automated-use licence/policy | Permissions | `/.well-known/tdmrep.json`, `<link rel=license>` / licence meta |
| 10 | CDN / pay-per-crawl capable | Permissions | Response headers (CDN fingerprints) |
| 13 | Machine-readable product feed | Commerce | `/products.json`, RSS/Atom link, `Product` structured data |
| 15 | Machine-readable price/stock | Commerce | JSON-LD `Offer` / `price` / `availability` |
| 16 | Checkout bot-wall (CAPTCHA) | Commerce | CAPTCHA vendor scripts in the homepage |
| 17 | Agent-commerce protocol | Commerce | `/.well-known/` probes + homepage status |
| 23 | Content-licensing / AI-access | Monetization | `tdmrep.json`, known AI-access provider markers |
| 24 | Machine-readable paywall | Monetization | `isAccessibleForFree`, content-tier meta, paywall vendors |

Output is printed Tier-A first (Read, Trust, Freshness, Discovery), then a Tier-B section grouped Docs, Permissions, Commerce, Monetization.

---

## Read group

### Check 1 — llms.txt present

**Looks at:** `GET /llms.txt` at the site root.

**Passes when:** the response is HTTP 200 and the body is non-empty. The detail notes whether the file has a Markdown `#` heading (`valid markdown`) or not (`present, no H1`); either way it passes if the file exists with content.

**Fails when:** the file is missing (404) or empty.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `/llms.txt found (valid markdown)` |
| ❌ fail | `no /llms.txt` |

### Check 11 — Structured data (homepage)

**Looks at:** the homepage HTML for JSON-LD blocks (`<script type="application/ld+json">`) and microdata (`itemtype` attributes).

**Passes when:** at least one structured-data block is found. The detail lists the unique Schema.org `@type` values.

**Fails when:** no JSON-LD or microdata is present.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `3 block(s): Article, Organization, WebSite` |
| ❌ fail | `no JSON-LD or microdata` |

### Check 14 — Structured-data coverage

**Looks at:** a sample of pages from the sitemap (default 10, set by `--sample`), running the check-11 logic on each.

**Passes when:** at least one sampled page carries structured data. The detail reports the fraction.

**Fails when:** none of the sampled pages carry structured data.

**No sitemap:** the check falls back to the homepage alone and says so.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `7/10 sampled pages carry structured data` |
| ✅ pass (fallback) | `no sitemap — homepage only: has data` |
| ❌ fail | `0/10 sampled pages carry structured data` |

---

## Trust group

### Check 6 — Explicit AI-bot policy

**Looks at:** the parsed `robots.txt` for any known AI user-agent (see the [list below](#known-ai-user-agents)).

**Passes when:** `robots.txt` exists and names at least one known AI user-agent.

**Fails when:** there is no `robots.txt`, or it exists but mentions no AI bots.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `names 8 AI bot(s): gptbot, chatgpt-user, claude-web, anthropic-ai, google-extended, perplexitybot, ccbot, cohere-ai` |
| ❌ fail | `no robots.txt` |
| ❌ fail | `robots.txt present but names no AI bots` |

### Check 7 — AI-bot allow/block stance

**Looks at:** the rules for each named AI user-agent, reducing each to a stance.

| Stance | Meaning |
|--------|---------|
| `blocked` | The agent is disallowed from the whole site (`Disallow: /`). |
| `partial` | The agent has some allow/disallow rules but is not fully blocked. |
| `allowed` | The agent is named but has no restricting rules. |

**Passes when:** at least one AI user-agent is named (so a stance can be read). The detail lists each agent and its stance.

**Fails when:** no AI user-agent is named.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `gptbot: blocked; perplexitybot: allowed` |
| ❌ fail | `no AI bots named to have a stance` |

> **Note:** A pass here means the site's stance is *readable*, not that bots are allowed. `gptbot: blocked` is a pass — the policy was stated clearly.

---

## Freshness group

### Check 18 — Machine-readable dates

**Looks at:** the homepage for a machine-readable publish or modify date: JSON-LD `datePublished`/`dateModified`, `article:published_time`/`article:modified_time` meta tags, or `<time datetime="...">`.

**Passes when:** at least one such date is found.

**Fails when:** none is found.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `found: 2026-06-01 (+2 more)` |
| ❌ fail | `no machine-readable dates` |

### Check 19 — Last-Modified / ETag

**Looks at:** the homepage response headers (case-insensitively).

**Passes when:** either `Last-Modified` or `ETag` is present.

**Fails when:** neither is present.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `last-modified, etag` |
| ❌ fail | `neither Last-Modified nor ETag` |

### Check 20 — Canonical URL

**Looks at:** `<link rel="canonical">` in the homepage HTML, then the `Link:` response header.

**Passes when:** a canonical URL is declared. The detail is the URL.

**Fails when:** no canonical is declared.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `https://www.example.com/` |
| ❌ fail | `no rel=canonical` |

### Check 21 — Cache headers

**Looks at:** the homepage response headers (case-insensitively).

**Passes when:** either `Cache-Control` or `Expires` is present.

**Fails when:** neither is present.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `cache-control` |
| ❌ fail | `no Cache-Control or Expires` |

---

## Discovery group

### Check 2 — sitemap.xml present

**Looks at:** `GET /sitemap.xml`, or a `Sitemap:` URL declared in `robots.txt` if one is present.

**Passes when:** the response parses as a `<urlset>` or `<sitemapindex>`. The detail reports the entry count and the freshest `lastmod` date if any.

**Fails when:** no parseable sitemap is found.

**Unknown when:** the sitemap fetch failed at the transport level (timeout, connection error).

| Result | Example detail |
|--------|----------------|
| ✅ pass | `urlset, 3217 entries, freshest: 2026-06-01` |
| ❌ fail | `no parseable sitemap.xml` |
| — unknown | `sitemap fetch failed: <error>` |

### Check 3 — Readable without JavaScript

**Looks at:** the visible text of the raw HTML versus the visible text after a headless browser renders the page.

**Passes when:** the raw text is at least 60% of the rendered text — the content is present without running JavaScript.

**Fails when:** the raw text is well below 60% — the content depends on JavaScript.

**Unknown when:** the browser could not render the page, or the rendered page had no text.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `raw text is 110% of rendered — readable without JS` |
| ❌ fail | `raw text only 12% of rendered — content needs JavaScript` |
| — unknown | `could not render: <error>` |

> **Note:** Ratios above 100% are normal — a browser often strips boilerplate that the raw text still contains, so raw can exceed rendered. Any ratio at or above 60% passes. The threshold is the `JS_TEXT_PASS_RATIO` constant; see the [CLI reference](cli.md#tunable-constants).

### Check 12 — OpenGraph tags

**Looks at:** the homepage `<meta property="og:...">` tags.

**Passes when:** at least `og:title` is present. The detail counts all `og:` tags.

**Fails when:** `og:title` is absent.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `11 og: tag(s) incl. og:title` |
| ❌ fail | `no og:title` |

---

## Tier-B proxy checks

Every check below is a **proxy**: an indirect signal, not a verified fact. A ✅ is a trustworthy positive. A `—` means no signal was visible, which is **not** proof the capability is absent. Only check #16 returns `❌`, because detecting a bot-wall is a trustworthy *negative*.

### Docs

#### Check 4 — Clean text/markdown alternative

**Looks at:** a content-negotiated request (`Accept: text/markdown`), a `<link rel="alternate">` pointing to markdown/plain/`.md`, and `/llms-full.txt`.

**Passes when:** any of those yields a machine-friendly text version.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `clean text version: content negotiation → markdown; /llms-full.txt` |
| — unknown | `no machine-friendly text/markdown alternative detected (may exist at an unguessed path)` |

#### Check 5 — Public API spec

**Looks at:** `/openapi.json`, `/.well-known/openapi.json`, `/swagger.json`.

**Passes when:** one returns JSON with an `openapi` or `swagger` key.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `OpenAPI/Swagger spec found (version 3.1.0)` |
| — unknown | `no public API spec at common paths (an API may exist at an unguessed path)` |

### Permissions

#### Check 9 — Automated-use licence/policy

**Looks at:** `/.well-known/tdmrep.json` (the TDM Reservation Protocol, a machine-readable statement of text-and-data-mining permission) and `<link rel="license">` / licence meta tags.

**Passes when:** a machine-readable licence or TDM policy is found.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `automated-use policy declared: /.well-known/tdmrep.json (TDM reservation)` |
| — unknown | `no machine-readable licence/TDM policy found (terms may exist only in prose)` |

#### Check 10 — CDN / pay-per-crawl capable

**Looks at:** response headers for CDN fingerprints (Cloudflare, Fastly, CloudFront, Akamai, Vercel).

**Passes when:** a CDN is detected — meaning the infrastructure to charge or gate bots (pay-per-crawl) *could* exist.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `served via Cloudflare (bot-management / pay-per-crawl capable; cannot confirm it is enabled)` |
| — unknown | `no CDN / bot-management signal in response headers` |

### Commerce

#### Check 13 — Machine-readable product feed

**Looks at:** `/products.json` (Shopify-style), an RSS/Atom feed link, and `Product` structured data across the homepage and sampled pages.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `machine-readable product data: /products.json; Product structured data` |
| — unknown | `no machine-readable product feed detected` |

#### Check 15 — Machine-readable price/stock

**Looks at:** JSON-LD `Offer` / `price` / `availability` fields on the homepage and sampled pages.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `machine-readable price/stock: Offer, availability, price` |
| — unknown | `no machine-readable price/availability (Offer) data found` |

#### Check 16 — Checkout bot-wall (CAPTCHA)

**Looks at:** known CAPTCHA / bot-wall vendor scripts in the homepage (reCAPTCHA, hCaptcha, Turnstile, Arkose, GeeTest, DataDome, PerimeterX).

**This is the one Tier-B check that returns `❌`** — a detected bot-wall is a trustworthy negative signal for agent automation.

| Result | Example detail |
|--------|----------------|
| ❌ fail | `bot-wall detected (Turnstile) — agent automation likely impeded; checkout pages not probed` |
| — unknown | `no CAPTCHA/bot-wall on the homepage (other pages not probed)` |

#### Check 17 — Agent-commerce protocol

**Looks at:** public discovery surfaces for agent-commerce standards:

| Protocol | How it is detected |
|----------|--------------------|
| A2A (Agent2Agent) | `GET /.well-known/agent-card.json` (falls back to legacy `/.well-known/agent.json`) returns valid JSON. |
| AP2 (Agent Payments Protocol) | The A2A card's `capabilities.extensions` contains the AP2 extension URI (`…/google-agentic-commerce/ap2…`). |
| UCP (Universal Commerce Protocol) | `GET /.well-known/ucp` returns valid JSON. |
| x402 | The homepage responds with HTTP 402 or a `Payment-Required` header (best-effort — a full probe needs a paid endpoint). |

| Result | Example detail |
|--------|----------------|
| ✅ pass | `declares: A2A, AP2` |
| — unknown | `no public agent-commerce protocol found (a site can still use ACP or onboard via a platform — not visible from outside)` |

> **Note:** ACP (OpenAI/Stripe), MCP, and the Visa/Mastercard agent-payment networks are **not** detectable from a site crawl — they onboard through platforms or operate inside the card networks. A site using only those will show `—` here. See [development journey, Fork 3](../../development-journey.md#fork-3-agent-commerce-protocols) for the full protocol landscape.

### Monetization

#### Check 23 — Content-licensing / AI-access

**Looks at:** `/.well-known/tdmrep.json` and markers for known AI-access programs (TollBit, ScalePost, ProRata, RSL Collective, Cloudflare AI Audit).

| Result | Example detail |
|--------|----------------|
| ✅ pass | `content-licensing / AI-access signal: tdmrep.json; tollbit` |
| — unknown | `no content-licensing or AI-access program detected` |

#### Check 24 — Machine-readable paywall

**Looks at:** JSON-LD `isAccessibleForFree: false`, `content_tier` meta tags (`locked`/`metered`), and known paywall vendors (Piano, Tinypass, Poool, Pelcro, Memberful).

**Passes when:** a machine-readable paywall marker is found — the site signals gated content to machines. It cannot confirm an authorised agent could pass it.

| Result | Example detail |
|--------|----------------|
| ✅ pass | `machine-readable paywall markers: isAccessibleForFree:false (cannot confirm authorised-agent access)` |
| — unknown | `no machine-readable paywall markers found` |

---

## Known AI user-agents

Checks 6 and 7 match against this list (compared case-insensitively). It is the `AI_USER_AGENTS` constant in `agent_audit.py` and is easy to extend.

```text
gptbot              oai-searchbot       chatgpt-user
claudebot           claude-web          anthropic-ai
google-extended     perplexitybot       ccbot
bytespider          amazonbot           applebot-extended
meta-externalagent  cohere-ai           diffbot
```

---

## What these checks do not tell you

A passing check means a signal is *present*, not that any agent will succeed. The tool measures machine-legibility, not outcomes or content quality. For the full boundary of what the auditor does and does not claim, read the transparency section of the [development journey](../../development-journey.md#what-the-app-does-and-does-not-do).
