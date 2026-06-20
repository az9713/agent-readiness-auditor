# Agent Readiness — comparative audit

**Sites:** vercel.com · stripe.com · cloudflare.com
**Date:** 2026-06-20 · **Command:** `python agent_audit.py <url> --sample 5`

This report runs the auditor against three sites and explains how to read every check. Each row of the results matrix is followed by an interpretation guide so the result is never a bare symbol.

> **How to read the symbols.** ✅ = signal found. ❌ = Tier-A: genuinely absent; Tier-B: a detected barrier. — = could not be established (Tier-A) or no signal visible (Tier-B). A Tier-B `—` is **not** proof of absence — the capability may exist in a form the tool cannot see from the outside.

---

## Results at a glance

### Tier-A facts (deterministic)

| # | Check | Vercel | Stripe | Cloudflare |
|---|-------|:------:|:------:|:----------:|
| 1 | llms.txt present | ✅ | ✅ | ✅ |
| 11 | Structured data (homepage) | ✅ | ✅ | ✅ |
| 14 | Structured-data coverage | ❌ | ❌ | ✅ |
| 6 | Explicit AI-bot policy | ❌ | ❌ | ✅ |
| 7 | AI-bot allow/block stance | ❌ | ❌ | ✅ |
| 18 | Machine-readable dates | ❌ | ❌ | ❌ |
| 19 | Last-Modified / ETag | ✅ | ❌ | ❌ |
| 20 | Canonical URL | ✅ | ✅ | ✅ |
| 21 | Cache headers | ✅ | ❌ | ✅ |
| 2 | sitemap.xml present | ✅ | ✅ | ✅ |
| 3 | Readable without JavaScript | ✅ | ✅ | ✅ |
| 12 | OpenGraph tags | ✅ | ✅ | ✅ |
| | **Tier-A tally** | **Read 2/3 · Trust 0/2 · Fresh 3/4 · Disc 3/3** | **Read 2/3 · Trust 0/2 · Fresh 1/4 · Disc 3/3** | **Read 3/3 · Trust 2/2 · Fresh 2/4 · Disc 3/3** |

### Tier-B proxy signals

| # | Check | Vercel | Stripe | Cloudflare |
|---|-------|:------:|:------:|:----------:|
| 4 | Clean text/markdown alternative | ✅ | — | ✅ |
| 5 | Public API spec | — | — | ✅ |
| 9 | Automated-use licence/policy | — | — | — |
| 10 | CDN / pay-per-crawl capable | ✅ | — | ✅ |
| 13 | Machine-readable product feed | — | — | ✅ |
| 15 | Machine-readable price/stock | ✅ | — | — |
| 16 | Checkout bot-wall (CAPTCHA) | — | — | ❌ |
| 17 | Agent-commerce protocol | — | — | ✅ |
| 23 | Content-licensing / AI-access | — | — | — |
| 24 | Machine-readable paywall | — | — | — |
| | **Tier-B tally** | **Docs 1/2 · Perms 1/2 · Comm 1/4 · Mon 0/2** | **Docs 0/2 · Perms 0/2 · Comm 0/4 · Mon 0/2** | **Docs 2/2 · Perms 1/2 · Comm 2/4 · Mon 0/2** |

There is no overall score by design — read each group's tally, not a single number.

---

## How to interpret each check

### Tier A — Read

**[1] llms.txt present.** Does the site publish `/llms.txt`, a clean content map for AI? ✅ on all three — each ships a valid-markdown `llms.txt`. This is the clearest single sign a site is courting AI readers.

**[11] Structured data (homepage).** Is page meaning labelled as data (JSON-LD / microdata)? ✅ everywhere, but the *types* differ and tell you the site's self-description: Vercel = `SoftwareApplication`, Stripe = `Organization, WebSite`, Cloudflare = `Organization, WebPage, WebSite`.

**[14] Structured-data coverage.** Of the sampled pages (not just the homepage), how many carry structured data? ✅ only for Cloudflare (4/5). Vercel and Stripe label the homepage but `0/5` of deeper pages — a common pattern where only the landing page is enriched. A ❌ here means "labelled the front door, not the rooms."

### Tier A — Trust

**[6] Explicit AI-bot policy.** Does `robots.txt` name known AI crawlers (GPTBot, ClaudeBot, …)? ✅ only Cloudflare, which names eight. Vercel and Stripe have a `robots.txt` but mention no AI bots → ❌. This does not mean they block AI; it means they have not taken an explicit machine-readable stance.

**[7] AI-bot allow/block stance.** For the bots that *are* named, what is the rule? Cloudflare = `partial` for all eight (some paths allowed, some not). ❌ for the other two because there is no named bot to have a stance. Note ✅ here means the stance is *readable*, not that bots are allowed.

### Tier A — Freshness

**[18] Machine-readable dates.** A publish/modify date a machine can read (JSON-LD date, `<time>`, article meta). ❌ on all three — marketing homepages rarely carry article dates. Expect ✅ mainly on blogs, docs, and news.

**[19] Last-Modified / ETag.** Response headers that let an agent cheaply tell if a page changed. ✅ Vercel (etag). ❌ Stripe and Cloudflare strip them — typical of edge-rendered pages, but it makes incremental re-fetching harder for an agent.

**[20] Canonical URL.** Is the one official URL declared, so duplicates aren't mistaken for separate pages? ✅ everywhere — table stakes for these sites.

**[21] Cache headers.** `Cache-Control` / `Expires`. ✅ Vercel and Cloudflare. ❌ Stripe omits them on the homepage.

### Tier A — Discovery

**[2] sitemap.xml present.** A machine-readable list of pages. ✅ all three — note the scale and shape: Vercel `urlset` 7,092 entries, Stripe `sitemapindex` (8 child sitemaps), Cloudflare `urlset` 901 entries. An agent uses this to find content without guessing.

**[3] Readable without JavaScript.** Does the content survive without running JS? Measured as raw-HTML text ÷ browser-rendered text; ≥60% passes. ✅ all three. Ratios above 100% (Vercel 400%, Stripe 109%) are normal — the browser strips boilerplate the raw HTML still contains. A ❌ here would mean an agent doing a simple fetch sees little.

**[12] OpenGraph tags.** `og:` tags that summarise the page. ✅ all three (5–7 tags each). Cheap and near-universal among polished sites.

### Tier B — Docs (proxies)

**[4] Clean text/markdown alternative.** Can an agent get a clean text version (content negotiation, `<link rel=alternate>`, `/llms-full.txt`)? ✅ Vercel (`/llms-full.txt`) and Cloudflare (all three signals). — Stripe: none visible, which is not proof none exists.

**[5] Public API spec.** An OpenAPI/Swagger spec at a common path. ✅ only Cloudflare (OpenAPI 3.1.0). — for Vercel and Stripe: both *have* APIs, but not at the probed paths — a textbook proxy false-negative, correctly reported as `—`, not ❌.

### Tier B — Permissions (proxies)

**[9] Automated-use licence/policy.** A machine-readable licence or TDM-reservation file. — on all three. The honest read: none publishes one in a detectable form; terms may still exist in prose.

**[10] CDN / pay-per-crawl capable.** A CDN whose infrastructure *could* meter or charge bots. ✅ Vercel (served via Vercel) and Cloudflare (served via Cloudflare). — Stripe: headers reveal no known CDN fingerprint (it fronts its own edge). "Capable," not "enabled" — the proxy can't confirm charging is on.

### Tier B — Commerce (proxies)

**[13] Machine-readable product feed.** `/products.json`, an RSS/Atom feed, or `Product` structured data. ✅ Cloudflare (Product structured data). — Vercel and Stripe.

**[15] Machine-readable price/stock.** JSON-LD `Offer` / `price` / `availability`. ✅ Vercel — its homepage carries plan/pricing offers (`Offer, availability, offers, price, priceCurrency`). — for Stripe and Cloudflare. This is the SaaS-pricing signal, not a retail catalogue.

**[16] Checkout bot-wall (CAPTCHA).** The one Tier-B check that can return ❌. ❌ Cloudflare — its own **Turnstile** is detected, a trustworthy negative for agent automation. — Vercel and Stripe: no bot-wall on the homepage (other pages not probed).

**[17] Agent-commerce protocol.** Public A2A / AP2 / UCP / x402 discovery. ✅ Cloudflare declares **A2A** (it serves an agent card). — Vercel and Stripe: nothing on their own domain — but a site can run ACP or onboard payments through a platform and show nothing, so this is `—`, not ❌.

### Tier B — Monetization (proxies)

**[23] Content-licensing / AI-access.** `tdmrep.json` or a known AI-access provider (TollBit, ScalePost, …). — on all three. None runs a detectable content-licensing programme.

**[24] Machine-readable paywall.** `isAccessibleForFree:false`, content-tier meta, or a paywall vendor. — on all three. None of these is a paywalled publisher, so there is nothing to find.

---

## Full reports

### vercel.com

```text
Tier-A facts   — Read 2/3 · Trust 0/2 · Freshness 3/4 · Discovery 3/3
Tier-B signals — Docs 1/2 · Permissions 1/2 · Commerce 1/4 · Monetization 0/2
```
Highlights: `llms.txt` + `llms-full.txt`, a 7,092-entry sitemap, `SoftwareApplication` schema, and SaaS pricing offers (#15). No explicit AI-bot policy; deeper pages lack structured data (#14).

### stripe.com

```text
Tier-A facts   — Read 2/3 · Trust 0/2 · Freshness 1/4 · Discovery 3/3
Tier-B signals — Docs 0/2 · Permissions 0/2 · Commerce 0/4 · Monetization 0/2
```
The leanest profile: strong Discovery (sitemapindex, OG, JS-free) and `llms.txt`, but no AI-bot policy, no freshness headers, and zero detectable Tier-B signals — even the CDN is invisible because Stripe fronts its own edge. A reminder that a famous, well-built site can still be opaque to an outside agent probe.

### cloudflare.com

```text
Tier-A facts   — Read 3/3 · Trust 2/2 · Freshness 2/4 · Discovery 3/3
Tier-B signals — Docs 2/2 · Permissions 1/2 · Commerce 2/4 · Monetization 0/2
```
The richest profile, fittingly for the company that produced the 57%-bot-traffic stat: names eight AI bots, full structured-data coverage, an OpenAPI spec, an A2A agent card, *and* a Turnstile bot-wall (#16 ❌) — a site that both invites agents and walls parts of itself.

---

## Are these three good candidates?

**Yes for a contrast set, but skewed.** They are all polished tech sites, so they exercise **Tier-A** well and show real variation (Cloudflare 10/12 Tier-A passes vs Stripe 6/12). They also cover the **Docs**, **Permissions**, and **protocol** Tier-B proxies nicely, and Cloudflare alone trips the CAPTCHA barrier and an A2A declaration.

**But they under-exercise two Tier-B groups:**

- **Commerce** (product feed #13, price/stock #15, checkout #16) — none is a retail storefront, so these stay mostly `—`. Vercel's #15 ✅ is SaaS pricing, not a product catalogue.
- **Monetization** (content-licensing #23, paywall #24) — none is a paywalled publisher, so both are `—` across the board.

A `—` in those rows is honest ("no signal visible"), but it means the checks are never seen *passing*, which is unsatisfying for a demo of what the tool can detect.

### Suggested additions to cover the gaps

| To exercise | Add a site like | Why |
|-------------|-----------------|-----|
| Commerce (#13, #15) | A Shopify storefront — e.g. **allbirds.com**, **gymshark.com** | Shopify exposes `/products.json` and rich `Product`/`Offer` structured data — should light up #13 and #15. |
| Checkout bot-wall (#16) | Any retail **checkout page** behind a CAPTCHA | Probes the barrier polarity directly (other pages not probed by default). |
| Monetization (#23, #24) | A paywalled publisher — **nytimes.com**, **wsj.com**, **theatlantic.com** | `isAccessibleForFree:false` / content-tier meta (#24); some run AI-access programmes like TollBit (#23). |
| Freshness dates (#18) | A blog or docs article page (not a marketing homepage) | Article pages carry `datePublished`/`dateModified`, which marketing homepages lack. |
| Agent-commerce protocol (#17) | Hard to source live A2A/AP2/UCP sites; Cloudflare already demonstrates A2A | These standards are new; positive hits are rare in the wild. |

**Recommendation:** keep the three as the "tech-site" baseline, and add **one Shopify store** + **one paywalled news site** to give every Tier-B group at least one live ✅. That five-site set would demonstrate the full range of the auditor.
