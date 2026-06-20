# Full audit log — every site, every test

A complete, uncompressed record of every site audited in this session, documenting all 22 checks for each. Where a result is available it is explained; where the tool or the research process hit a problem, the problem is explained.

**Tool:** `agent_audit.py` · **Date:** 2026-06-20

## Legend

- ✅ **pass** — the signal was found.
- ❌ **fail** — Tier-A: the signal is genuinely absent; Tier-B: a barrier was detected (only check #16).
- — **unknown** — Tier-A: the check could not be performed; Tier-B: no signal was visible (**not** proof of absence).

The 22 checks, in the order the tool prints them:

| Group | Checks |
|-------|--------|
| Read (Tier A) | 1 llms.txt · 11 structured data · 14 coverage |
| Trust (Tier A) | 6 AI-bot policy · 7 allow/block stance |
| Freshness (Tier A) | 18 dates · 19 Last-Modified/ETag · 20 canonical · 21 cache |
| Discovery (Tier A) | 2 sitemap · 3 readable-without-JS · 12 OpenGraph |
| Docs (Tier B) | 4 markdown alt · 5 API spec |
| Permissions (Tier B) | 9 licence/TDM · 10 CDN |
| Commerce (Tier B) | 13 product feed · 15 price/stock · 16 CAPTCHA · 17 protocol |
| Monetization (Tier B) | 23 licensing/AI-access · 24 paywall |

Sites are listed in the order they were tested.

---

## 1. vercel.com

`python agent_audit.py https://vercel.com --sample 5` — audited `https://vercel.com/`.

**Read**
- ✅ **[1] llms.txt** — `/llms.txt found (valid markdown)`. Vercel publishes a clean content map for AI.
- ✅ **[11] Structured data** — `1 block(s): SoftwareApplication`. The homepage labels itself as software.
- ❌ **[14] Coverage** — `0/5 sampled pages carry structured data`. Only the homepage is enriched; the sampled deeper pages are not.

**Trust**
- ❌ **[6] AI-bot policy** — `robots.txt present but names no AI bots`. A robots file exists, but it takes no explicit stance on AI crawlers.
- ❌ **[7] Allow/block stance** — `no AI bots named to have a stance`. Follows from #6 — nothing named, nothing to read.

**Freshness**
- ❌ **[18] Dates** — `no machine-readable dates`. A marketing homepage with no article/publish date.
- ✅ **[19] Last-Modified/ETag** — `etag`. An `ETag` header is present, so an agent can cheaply detect change.
- ✅ **[20] Canonical** — `https://vercel.com`. The official URL is declared.
- ✅ **[21] Cache** — `cache-control`. Caching is declared.

**Discovery**
- ✅ **[2] sitemap** — `urlset, 7092 entries, freshest: 2026-06-20T13:36:00.133Z`. A large, fresh sitemap.
- ✅ **[3] Readable-without-JS** — `raw text is 400% of rendered`. The raw HTML carries more text than the rendered page — fully readable without JavaScript.
- ✅ **[12] OpenGraph** — `7 og: tag(s) incl. og:title`. Rich share metadata.

**Docs (Tier B)**
- ✅ **[4] Markdown alt** — `clean text version: /llms-full.txt`. A full-text machine version exists.
- — **[5] API spec** — `no public API spec at common paths`. Vercel has an API, but not at the probed paths — a proxy false-negative, correctly reported as unknown.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`. None declared in a detectable form.
- ✅ **[10] CDN** — `served via Vercel`. Self-hosted on Vercel's edge — pay-per-crawl-capable infrastructure (not confirmed enabled).

**Commerce (Tier B)**
- — **[13] Product feed** — `no machine-readable product feed detected`. Not a storefront.
- ✅ **[15] Price/stock** — `Offer, availability, offers, price, priceCurrency`. The homepage carries SaaS plan pricing as structured `Offer` data.
- — **[16] CAPTCHA** — `no CAPTCHA/bot-wall on the homepage`. No bot-wall on the front page.
- — **[17] Protocol** — `no public agent-commerce protocol found`. No A2A/AP2/UCP/x402 surface.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`. Not a paywalled publisher.

**Tally:** Tier-A Read 2/3 · Trust 0/2 · Freshness 3/4 · Discovery 3/3 — Tier-B Docs 1/2 · Permissions 1/2 · Commerce 1/4 · Monetization 0/2.

---

## 2. stripe.com

`python agent_audit.py https://stripe.com --sample 5` — audited `https://stripe.com/`.

**Read**
- ✅ **[1] llms.txt** — `/llms.txt found (valid markdown)`.
- ✅ **[11] Structured data** — `2 block(s): Organization, WebSite`.
- ❌ **[14] Coverage** — `0/5 sampled pages carry structured data`. Homepage only.

**Trust**
- ❌ **[6] AI-bot policy** — `robots.txt present but names no AI bots`.
- ❌ **[7] Allow/block stance** — `no AI bots named to have a stance`.

**Freshness**
- ❌ **[18] Dates** — `no machine-readable dates`.
- ❌ **[19] Last-Modified/ETag** — `neither Last-Modified nor ETag`. Edge-rendered; no change headers.
- ✅ **[20] Canonical** — `https://stripe.com/`.
- ❌ **[21] Cache** — `no Cache-Control or Expires`. No caching declared on the homepage.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 8 entries`. A sitemap index pointing to 8 child sitemaps.
- ✅ **[3] Readable-without-JS** — `raw text is 109% of rendered`. Content survives without JS.
- ✅ **[12] OpenGraph** — `5 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- — **[4] Markdown alt** — `no machine-friendly text/markdown alternative detected`.
- — **[5] API spec** — `no public API spec at common paths`. Stripe has a famous API, just not at the probed default paths — the clearest proxy false-negative in the whole set.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- — **[10] CDN** — `no CDN / bot-management signal in response headers`. Stripe fronts its own edge; no recognised CDN fingerprint.

**Commerce (Tier B)**
- — **[13] Product feed** — `no machine-readable product feed detected`.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`.
- — **[16] CAPTCHA** — `no CAPTCHA/bot-wall on the homepage`.
- — **[17] Protocol** — `no public agent-commerce protocol found`. (Stripe co-authors ACP, but ACP onboards through platforms and leaves nothing on stripe.com to detect.)

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`.

**Tally:** Tier-A Read 2/3 · Trust 0/2 · Freshness 1/4 · Discovery 3/3 — Tier-B Docs 0/2 · Permissions 0/2 · Commerce 0/4 · Monetization 0/2. The leanest profile in the set — a famous, well-built site that is nonetheless opaque to an outside agent probe.

---

## 3. cloudflare.com

`python agent_audit.py https://www.cloudflare.com --sample 5` — audited `https://www.cloudflare.com/`.

**Read**
- ✅ **[1] llms.txt** — `/llms.txt found (valid markdown)`.
- ✅ **[11] Structured data** — `3 block(s): Organization, WebPage, WebSite`.
- ✅ **[14] Coverage** — `4/5 sampled pages carry structured data`. Enrichment runs site-wide, not just the homepage.

**Trust**
- ✅ **[6] AI-bot policy** — `names 8 AI bot(s): gptbot, chatgpt-user, claude-web, anthropic-ai, google-extended, perplexitybot, ccbot, cohere-ai`.
- ✅ **[7] Allow/block stance** — all 8 `partial`. Some paths allowed, some disallowed — a nuanced, readable policy.

**Freshness**
- ❌ **[18] Dates** — `no machine-readable dates`.
- ❌ **[19] Last-Modified/ETag** — `neither Last-Modified nor ETag`.
- ✅ **[20] Canonical** — `https://www.cloudflare.com/`.
- ✅ **[21] Cache** — `cache-control`.

**Discovery**
- ✅ **[2] sitemap** — `urlset, 901 entries, freshest: 2026-06-20`.
- ✅ **[3] Readable-without-JS** — `raw text is 73% of rendered`. Above the 60% threshold — readable.
- ✅ **[12] OpenGraph** — `5 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- ✅ **[4] Markdown alt** — `content negotiation → markdown; <link rel=alternate markdown>; /llms-full.txt`. All three markdown signals present — the most agent-friendly Docs result in the set.
- ✅ **[5] API spec** — `OpenAPI/Swagger spec found (version 3.1.0)`. A discoverable API spec.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- ✅ **[10] CDN** — `served via Cloudflare`. Its own CDN — pay-per-crawl-capable.

**Commerce (Tier B)**
- ✅ **[13] Product feed** — `Product structured data`. Product markup present.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`.
- ❌ **[16] CAPTCHA** — `bot-wall detected (Turnstile)`. Cloudflare's own Turnstile — a trustworthy negative for agent automation.
- ✅ **[17] Protocol** — `declares: A2A`. Serves an agent card at `/.well-known/agent-card.json`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`.

**Tally:** Tier-A Read 3/3 · Trust 2/2 · Freshness 2/4 · Discovery 3/3 — Tier-B Docs 2/2 · Permissions 1/2 · Commerce 2/4 · Monetization 0/2. The richest profile: it both invites agents (A2A, OpenAPI, markdown) and walls parts of itself (Turnstile).

---

## 4. allbirds.com — homepage

`python agent_audit.py https://www.allbirds.com --sample 5` — audited `https://www.allbirds.com/`.

**Read**
- ✅ **[1] llms.txt** — `/llms.txt found (valid markdown)`.
- ❌ **[11] Structured data** — `no JSON-LD or microdata`. The homepage itself carries none (product pages do — see §5).
- ❌ **[14] Coverage** — `0/1 sampled pages carry structured data`. Only one page sampled before the sitemap ran out at this depth.

**Trust**
- ❌ **[6] AI-bot policy** — `robots.txt present but names no AI bots`.
- ❌ **[7] Allow/block stance** — `no AI bots named to have a stance`.

**Freshness**
- ❌ **[18] Dates** — `no machine-readable dates`.
- ✅ **[19] Last-Modified/ETag** — `etag`.
- ✅ **[20] Canonical** — `https://www.allbirds.com/`.
- ❌ **[21] Cache** — `no Cache-Control or Expires`.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 6 entries`.
- ✅ **[3] Readable-without-JS** — `raw text is 4295% of rendered`. *(Re-run after the [render fix](#problem-a-the-3-render-timeout-now-fixed); was `unknown` — a `networkidle` timeout — before.)* The raw HTML is very text-rich, so it passes comfortably.
- ✅ **[12] OpenGraph** — `9 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- ✅ **[4] Markdown alt** — `content negotiation → markdown; /llms-full.txt`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- ✅ **[10] CDN** — `served via Cloudflare`.

**Commerce (Tier B)**
- ✅ **[13] Product feed** — `/products.json`. Shopify's standard bulk product endpoint — an agent can read the whole catalogue.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`. The homepage has no per-item Offer data (the product page does — see §5).
- ❌ **[16] CAPTCHA** — `bot-wall detected (reCAPTCHA, hCaptcha)`. Two CAPTCHA vendors detected.
- ✅ **[17] Protocol** — `declares: UCP`. Shopify exposes Google's Universal Commerce Protocol at `/.well-known/ucp`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`.

**Tally:** Tier-A Read 1/3 · Trust 0/2 · Freshness 2/4 · Discovery 3/3 — Tier-B Docs 1/2 · Permissions 1/2 · Commerce 2/4 · Monetization 0/2. *(Discovery rose from 2/3 to 3/3 after the #3 fix.)*

---

## 5. allbirds.com — product page

`python agent_audit.py "https://www.allbirds.com/products/womens-tree-dasher-relay-natural-black-twilight-teal" --sample 2`. This is the same site as §4, pointed at a **product page** to exercise the per-item commerce checks.

**Read**
- ✅ **[1] llms.txt** — `/llms.txt found (valid markdown)`.
- ✅ **[11] Structured data** — `1 block(s): ProductGroup`. The product page is labelled as a product.
- ❌ **[14] Coverage** — `0/1 sampled pages carry structured data`.

**Trust**
- ❌ **[6] AI-bot policy** — `robots.txt present but names no AI bots`.
- ❌ **[7] Allow/block stance** — `no AI bots named to have a stance`.

**Freshness**
- ❌ **[18] Dates** — `no machine-readable dates`.
- ✅ **[19] Last-Modified/ETag** — `etag`.
- ✅ **[20] Canonical** — `https://www.allbirds.com/products/womens-tree-dasher-relay-natural-black-twilight-teal`.
- ❌ **[21] Cache** — `no Cache-Control or Expires`.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 6 entries`.
- ✅ **[3] Readable-without-JS** — `raw text is 3126% of rendered`. The product page's raw HTML is text-rich (and the render returned little) — comfortably passes. Notably this page rendered fine while the homepage (§4) timed out.
- ✅ **[12] OpenGraph** — `11 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- ✅ **[4] Markdown alt** — `/llms-full.txt`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- ✅ **[10] CDN** — `served via Cloudflare`.

**Commerce (Tier B)**
- ✅ **[13] Product feed** — `/products.json`.
- ✅ **[15] Price/stock** — `Offer, availability, offers, price, priceCurrency`. **This is the payoff:** the product page's JSON-LD carries the full price/stock fields, so an agent can read this item's price and availability directly.
- ❌ **[16] CAPTCHA** — `bot-wall detected (reCAPTCHA, hCaptcha)`.
- ✅ **[17] Protocol** — `declares: UCP`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`.

**Tally:** Tier-A Read 2/3 · Trust 0/2 · Freshness 2/4 · Discovery 3/3 — Tier-B Docs 1/2 · Permissions 1/2 · **Commerce 3/4** · Monetization 0/2. The Commerce group jumps from 2/4 to 3/4 versus the homepage, purely because #15 now sees the Offer data.

---

## 6. gymshark.com

`python agent_audit.py https://www.gymshark.com --sample 5` — audited `https://www.gymshark.com/`. A second Shopify-style store, for contrast with Allbirds.

**Read**
- ❌ **[1] llms.txt** — `no /llms.txt`. Unlike Allbirds, Gymshark publishes none.
- ✅ **[11] Structured data** — `2 block(s): Organization, WebSite`.
- ✅ **[14] Coverage** — `1/5 sampled pages carry structured data`.

**Trust**
- ❌ **[6] AI-bot policy** — `robots.txt present but names no AI bots`.
- ❌ **[7] Allow/block stance** — `no AI bots named to have a stance`.

**Freshness**
- ❌ **[18] Dates** — `no machine-readable dates`.
- ✅ **[19] Last-Modified/ETag** — `etag`.
- ✅ **[20] Canonical** — `https://www.gymshark.com`.
- ✅ **[21] Cache** — `cache-control`.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 9 entries`.
- ✅ **[3] Readable-without-JS** — `raw text is 221% of rendered`. *(Re-run after the [render fix](#problem-a-the-3-render-timeout-now-fixed); was `unknown` before.)* Readable without JavaScript.
- ✅ **[12] OpenGraph** — `7 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- — **[4] Markdown alt** — `no machine-friendly text/markdown alternative detected`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- ✅ **[10] CDN** — `served via CloudFront`. Amazon CloudFront fingerprint.

**Commerce (Tier B)**
- — **[13] Product feed** — `no machine-readable product feed detected`. Its `/products.json` was not reachable/JSON at the probed path on the homepage audit.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`. Homepage carries no Offer data (a product page likely would, as with Allbirds).
- — **[16] CAPTCHA** — `no CAPTCHA/bot-wall on the homepage`.
- — **[17] Protocol** — `no public agent-commerce protocol found`. No UCP surface (unlike Allbirds).

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`.

**Tally:** Tier-A Read 2/3 · Trust 0/2 · Freshness 3/4 · Discovery 3/3 — Tier-B Docs 0/2 · Permissions 1/2 · Commerce 0/4 · Monetization 0/2. *(Discovery rose from 2/3 to 3/3 after the #3 fix.)* A Shopify store with far fewer agent-facing signals than Allbirds — a reminder that "runs on Shopify" does not guarantee agent-readiness; it depends on what the merchant enables.

---

## 7. nytimes.com

`python agent_audit.py https://www.nytimes.com --sample 5` — audited `https://www.nytimes.com/`.

**Read**
- ❌ **[1] llms.txt** — `no /llms.txt`.
- ✅ **[11] Structured data** — `2 block(s): NewsMediaOrganization, WebSite`.
- ✅ **[14] Coverage** — `1/1 sampled pages carry structured data`.

**Trust**
- ✅ **[6] AI-bot policy** — `names 15 AI bot(s): gptbot, oai-searchbot, chatgpt-user, claudebot, claude-web, anthropic-ai, google-extended, perplexitybot, ccbot, bytespider, amazonbot, applebot-extended, meta-externalagent, cohere-ai, diffbot`. The full known roster.
- ✅ **[7] Allow/block stance** — almost all `blocked`; only `amazonbot: partial`. The archetypal AI-blocker, read precisely.

**Freshness**
- ✅ **[18] Dates** — `found: 2026-06-20T14:27:28.071Z`.
- ✅ **[19] Last-Modified/ETag** — `last-modified`.
- ✅ **[20] Canonical** — `https://www.nytimes.com`.
- ✅ **[21] Cache** — `cache-control`. A clean Freshness 4/4 — news pages carry the dates and headers marketing homepages lack.

**Discovery**
- ✅ **[2] sitemap** — `urlset, 633 entries, freshest: 2026-06-20T14:30:14Z`.
- ❌ **[3] Readable-without-JS** — `raw text only 50% of rendered — content needs JavaScript`. *(Re-run after the [render fix](#problem-a-the-3-render-timeout-now-fixed); was `unknown` before.)* This is now a genuine ❌, not a timeout: NYT renders much of its content client-side, so the raw HTML carries only half the rendered text — a real finding an agent doing a simple fetch would face.
- ✅ **[12] OpenGraph** — `5 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- — **[4] Markdown alt** — `no machine-friendly text/markdown alternative detected`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- — **[10] CDN** — `no CDN / bot-management signal in response headers`. NYT fronts its own edge.

**Commerce (Tier B)**
- ✅ **[13] Product feed** — `RSS/Atom feed link`. The news-site form of a machine-readable content feed.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`.
- ❌ **[16] CAPTCHA** — `bot-wall detected (reCAPTCHA)`. On the subscription/login flow.
- — **[17] Protocol** — `no public agent-commerce protocol found`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`. **Note:** NYT *is* paywalled, but the homepage carries no `isAccessibleForFree` flag, and the sampled article did not expose one to the crawler. The marker lives on locked article pages — see [Problem C](#problem-c-paywall-markers-are-rare-and-page-specific).

**Tally:** Tier-A Read 2/3 · Trust 2/2 · Freshness 4/4 · Discovery 2/3 — Tier-B Docs 0/2 · Permissions 0/2 · Commerce 1/4 · Monetization 0/2. *(Discovery stays 2/3 after the #3 fix: #3 is now a real ❌ rather than `unknown`.)*

---

## 8. theatlantic.com

`python agent_audit.py https://www.theatlantic.com --sample 5` — audited `https://www.theatlantic.com/`.

**Read**
- ❌ **[1] llms.txt** — `no /llms.txt`.
- ✅ **[11] Structured data** — `2 block(s): Organization, WebSite`.
- ✅ **[14] Coverage** — `2/2 sampled pages carry structured data`.

**Trust**
- ✅ **[6] AI-bot policy** — `names 15 AI bot(s)` (full roster).
- ✅ **[7] Allow/block stance** — mixed: `gptbot/oai-searchbot/chatgpt-user: partial`; the rest (ClaudeBot, Google-Extended, PerplexityBot, CCBot, Bytespider, Amazonbot, Applebot-Extended, Meta-ExternalAgent, cohere-ai, diffbot) `blocked`. A more granular policy than NYT's near-blanket block.

**Freshness**
- ✅ **[18] Dates** — `found: 2026-06-20T13:00:00Z (+19 more)`.
- ❌ **[19] Last-Modified/ETag** — `neither Last-Modified nor ETag`.
- ❌ **[20] Canonical** — `no rel=canonical`. The homepage declares no canonical.
- ✅ **[21] Cache** — `cache-control`.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 452 entries, freshest: 2026-06-20T10:02:15-04:00`.
- ✅ **[3] Readable-without-JS** — `raw text is 113% of rendered`. *(Re-run after the [render fix](#problem-a-the-3-render-timeout-now-fixed); was `unknown` before.)* Readable without JavaScript.
- ✅ **[12] OpenGraph** — `6 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- — **[4] Markdown alt** — `no machine-friendly text/markdown alternative detected`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- ✅ **[10] CDN** — `served via Cloudflare`.

**Commerce (Tier B)**
- ✅ **[13] Product feed** — `RSS/Atom feed link`.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`.
- ❌ **[16] CAPTCHA** — `bot-wall detected (reCAPTCHA)`.
- — **[17] Protocol** — `no public agent-commerce protocol found`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`. Same homepage-vs-article limitation as NYT ([Problem C](#problem-c-paywall-markers-are-rare-and-page-specific)).

**Tally:** Tier-A Read 2/3 · Trust 2/2 · Freshness 2/4 · Discovery 3/3 — Tier-B Docs 0/2 · Permissions 1/2 · Commerce 1/4 · Monetization 0/2. *(Discovery rose from 2/3 to 3/3 after the #3 fix.)*

---

## 9. wired.com — article page

`python agent_audit.py "https://www.wired.com/story/how-peter-thiels-private-dialog-club-secretly-ranks-its-members/" --sample 2`. Pointed at an article to test the paywall check.

**Read**
- ❌ **[1] llms.txt** — `no /llms.txt`.
- ✅ **[11] Structured data** — `2 block(s): BreadcrumbList, NewsArticle`. Proper article markup.
- ✅ **[14] Coverage** — `2/2 sampled pages carry structured data`.

**Trust**
- ✅ **[6] AI-bot policy** — `names 10 AI bot(s): claudebot, google-extended, perplexitybot, ccbot, bytespider, amazonbot, applebot-extended, meta-externalagent, cohere-ai, diffbot`.
- ✅ **[7] Allow/block stance** — all 10 `blocked`. (Notably GPTBot is absent from the list, so it is not blocked here.)

**Freshness**
- ✅ **[18] Dates** — `found: 2026-06-18T22:12:45.152Z (+3 more)`.
- ❌ **[19] Last-Modified/ETag** — `neither Last-Modified nor ETag`.
- ✅ **[20] Canonical** — the article URL.
- ✅ **[21] Cache** — `cache-control`.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 60 entries, freshest: 2026-06-20T07:00:00.000-04:00`.
- ✅ **[3] Readable-without-JS** — `raw text is 98% of rendered`. *(Re-run after the [render fix](#problem-a-the-3-render-timeout-now-fixed); was `unknown` before.)* Readable without JavaScript.
- ✅ **[12] OpenGraph** — `8 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- — **[4] Markdown alt** — `no machine-friendly text/markdown alternative detected`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- ✅ **[10] CDN** — `served via Cloudflare`.

**Commerce (Tier B)**
- ✅ **[13] Product feed** — `RSS/Atom feed link`.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`.
- ❌ **[16] CAPTCHA** — `bot-wall detected (reCAPTCHA)`.
- — **[17] Protocol** — `no public agent-commerce protocol found`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`. **Important:** this article declares `isAccessibleForFree: true` — it is a *free* article, so #24 correctly stays silent. The check tracks the declared marker, not a guess. See [Problem C](#problem-c-paywall-markers-are-rare-and-page-specific).

**Tally:** Tier-A Read 2/3 · Trust 2/2 · Freshness 3/4 · Discovery 3/3 — Tier-B Docs 0/2 · Permissions 1/2 · Commerce 1/4 · Monetization 0/2. *(Discovery rose from 2/3 to 3/3 after the #3 fix.)*

---

## 10. nationalgeographic.com — article page

`python agent_audit.py "https://www.nationalgeographic.com/health/article/women-strength-training-hormones-muscle-growth" --sample 2`. The article chosen *after confirming* it carries `isAccessibleForFree:false` — to demonstrate #24 firing.

**Read**
- ❌ **[1] llms.txt** — `no /llms.txt`.
- ✅ **[11] Structured data** — `7 block(s): BreadcrumbList, ImageObject, NewsArticle, NewsMediaOrganization, Person, WebPage, WebSite`. The richest structured-data set in the entire session.
- ✅ **[14] Coverage** — `1/2 sampled pages carry structured data`.

**Trust**
- ❌ **[6] AI-bot policy** — `robots.txt present but names no AI bots`.
- ❌ **[7] Allow/block stance** — `no AI bots named to have a stance`.

**Freshness**
- ✅ **[18] Dates** — `found: 06-19-2026 (+3 more)`.
- ✅ **[19] Last-Modified/ETag** — `last-modified`.
- ✅ **[20] Canonical** — the article URL.
- ✅ **[21] Cache** — `cache-control, expires`. A clean Freshness 4/4.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 54 entries`.
- ✅ **[3] Readable-without-JS** — `raw text is 100% of rendered`. **It rendered successfully** — one of the few publisher pages that did not time out, because its background activity settled within 15s.
- ✅ **[12] OpenGraph** — `9 og: tag(s) incl. og:title`.

**Docs (Tier B)**
- — **[4] Markdown alt** — `no machine-friendly text/markdown alternative detected`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- ✅ **[10] CDN** — `served via CloudFront`.

**Commerce (Tier B)**
- — **[13] Product feed** — `no machine-readable product feed detected`.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`.
- — **[16] CAPTCHA** — `no CAPTCHA/bot-wall on the homepage`.
- — **[17] Protocol** — `no public agent-commerce protocol found`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- ✅ **[24] Paywall** — `isAccessibleForFree:false (cannot confirm authorised-agent access)`. **The payoff:** the article's JSON-LD declares it is gated. The tool reads the declaration; it cannot confirm whether an authorised agent could pass the wall.

**Tally:** Tier-A Read 2/3 · Trust 0/2 · Freshness 4/4 · Discovery 3/3 — Tier-B Docs 0/2 · Permissions 1/2 · Commerce 0/4 · **Monetization 1/2**. The only site in the set to fire #24.

---

## 11. ft.com

`python agent_audit.py https://www.ft.com --sample 3` — audited `https://www.ft.com/`.

> **Correction to an earlier note.** During the research phase a separate helper script failed to extract an article link from ft.com ("no article"), and I initially described FT as bot-blocked. That was wrong: the *auditor itself ran fine* (exit 0) and read the homepage. The earlier failure was only my article-link-extraction script choking on FT's JavaScript-rendered navigation, not the audit. The full result is below.

**Read**
- ❌ **[1] llms.txt** — `no /llms.txt`.
- ✅ **[11] Structured data** — `1 block(s): WebSite`.
- ✅ **[14] Coverage** — `1/1 sampled pages carry structured data`.

**Trust**
- ✅ **[6] AI-bot policy** — `names 11 AI bot(s): claudebot, claude-web, anthropic-ai, google-extended, perplexitybot, ccbot, bytespider, applebot-extended, meta-externalagent, cohere-ai, diffbot`.
- ✅ **[7] Allow/block stance** — all 11 `blocked`. (GPTBot is absent from FT's list, so not blocked.)

**Freshness**
- ✅ **[18] Dates** — `found: 2026-06-20T11:00:09+0000 (+9 more)`.
- ❌ **[19] Last-Modified/ETag** — `neither Last-Modified nor ETag`.
- ❌ **[20] Canonical** — `no rel=canonical`.
- ✅ **[21] Cache** — `cache-control`.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 287 entries, freshest: 2026-06-20T14:44:41.000Z`.
- ✅ **[3] Readable-without-JS** — `raw text is 162% of rendered`. *(Re-run after the [render fix](#problem-a-the-3-render-timeout-now-fixed); was `unknown` before.)* Readable without JavaScript.
- ❌ **[12] OpenGraph** — `no og:title`. FT's homepage exposes no OpenGraph title — unusual for a major site.

**Docs (Tier B)**
- — **[4] Markdown alt** — `no machine-friendly text/markdown alternative detected`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- ✅ **[10] CDN** — `served via Cloudflare`.

**Commerce (Tier B)**
- ✅ **[13] Product feed** — `RSS/Atom feed link`.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`.
- — **[16] CAPTCHA** — `no CAPTCHA/bot-wall on the homepage`.
- — **[17] Protocol** — `no public agent-commerce protocol found`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`. FT is hard-paywalled, but the homepage carries no machine-readable flag, and FT blocks article-link discovery by non-JS clients ([Problem B](#problem-b-article-url-discovery-on-js-heavy-publishers)).

**Tally:** Tier-A Read 2/3 · Trust 2/2 · Freshness 2/4 · Discovery 2/3 — Tier-B Docs 0/2 · Permissions 1/2 · Commerce 1/4 · Monetization 0/2. *(Discovery rose from 1/3 to 2/3 after the #3 fix.)*

---

## 12. bloomberg.com

`python agent_audit.py https://www.bloomberg.com --sample 3` — audited `https://www.bloomberg.com/`.

> Same correction as FT: the audit ran fine (exit 0); only my separate article-link probe failed on Bloomberg's JS navigation. Bloomberg's homepage, however, is genuinely sparse to a crawler — see below.

**Read**
- ❌ **[1] llms.txt** — `no /llms.txt`.
- ❌ **[11] Structured data** — `no JSON-LD or microdata`. The homepage exposes none.
- ❌ **[14] Coverage** — `no sitemap — homepage only: no data`. The coverage check fell back to the homepage (no usable sitemap sample) and found nothing.

**Trust**
- ✅ **[6] AI-bot policy** — `names 15 AI bot(s)` (full roster).
- ✅ **[7] Allow/block stance** — all 15 `blocked`. The most comprehensive block in the set.

**Freshness**
- ❌ **[18] Dates** — `no machine-readable dates`.
- ❌ **[19] Last-Modified/ETag** — `neither Last-Modified nor ETag`.
- ❌ **[20] Canonical** — `no rel=canonical`.
- ❌ **[21] Cache** — `no Cache-Control or Expires`. A clean Freshness 0/4 — nothing for an agent to anchor on.

**Discovery**
- ✅ **[2] sitemap** — `sitemapindex, 426 entries, freshest: 2026-06-20`.
- ✅ **[3] Readable-without-JS** — `raw text is 113% of rendered`. **It rendered** — one of the few that did, because the sparse homepage settled quickly.
- ❌ **[12] OpenGraph** — `no og:title`.

**Docs (Tier B)**
- — **[4] Markdown alt** — `no machine-friendly text/markdown alternative detected`.
- — **[5] API spec** — `no public API spec at common paths`.

**Permissions (Tier B)**
- — **[9] Licence/TDM** — `no machine-readable licence/TDM policy found`.
- — **[10] CDN** — `no CDN / bot-management signal in response headers`.

**Commerce (Tier B)**
- — **[13] Product feed** — `no machine-readable product feed detected`.
- — **[15] Price/stock** — `no machine-readable price/availability (Offer) data found`.
- — **[16] CAPTCHA** — `no CAPTCHA/bot-wall on the homepage`.
- — **[17] Protocol** — `no public agent-commerce protocol found`.

**Monetization (Tier B)**
- — **[23] Licensing/AI-access** — `no content-licensing or AI-access program detected`.
- — **[24] Paywall** — `no machine-readable paywall markers found`.

**Tally:** Tier-A Read 0/3 · Trust 2/2 · Freshness 0/4 · Discovery 2/3 — Tier-B Docs 0/2 · Permissions 0/2 · Commerce 0/4 · Monetization 0/2. A striking profile: Bloomberg has decided, machine-readably, to block every AI bot, and otherwise exposes almost nothing to a crawler — strong Trust, near-empty everything else.

---

## Problems encountered

These are the recurring issues — one a genuine tool limitation, two research-process frictions.

### Problem A — the #3 render timeout (now fixed)

**Status: FIXED.** This was the one genuine tool limitation the audit surfaced, and it has been resolved. The six affected sites were re-run; their #3 results above reflect the fix.

**Original symptom:** check #3 returned `— could not render: Page.goto: Timeout 15000ms exceeded` on allbirds (homepage), gymshark, nytimes, theatlantic, wired, and ft — six of the twelve audits.

**Cause:** check #3 rendered the page with Playwright using `wait_until="networkidle"`, which waits for the network to be quiet for 500ms. Heavy commercial sites never go quiet — ads, analytics beacons, chat widgets, and websockets keep firing — so the 15-second timeout (`TIMEOUT`) elapsed and the render failed. The check correctly degraded to `unknown` rather than crashing, and the other 21 checks were unaffected (they use the plain HTTP fetch, not the browser).

**The fix:** navigate with `wait_until="domcontentloaded"` (reliable and fast), then *best-effort* wait up to 5s for `networkidle` and capture whatever has rendered, without failing if the network never settles. This gives client-side JS time to render while never hanging on a busy site.

**Result after the fix — all six now return a real value:**

| Site | Before | After |
|------|--------|-------|
| allbirds (homepage) | `unknown` | ✅ 4295% of rendered |
| gymshark | `unknown` | ✅ 221% |
| theatlantic | `unknown` | ✅ 113% |
| wired (article) | `unknown` | ✅ 98% |
| ft | `unknown` | ✅ 162% |
| nytimes | `unknown` | ❌ 50% — *content needs JavaScript* |

Five now pass; NYT correctly **fails**, because it genuinely renders much of its content client-side — exactly the situation check #3 exists to catch. The fix turned six non-answers into five passes and one true negative. The 34 offline tests still pass (the change is in browser-only code, which the offline suite does not exercise; it was verified by re-running the live audits).

### Problem B — article-URL discovery on JS-heavy publishers

**Symptom:** to test the paywall check I needed real article URLs. Several discovery attempts failed:
- `theatlantic.com/sitemaps/news.xml` returned **404**.
- `nytimes.com/sitemaps/new/news.xml.gz` parsed but yielded **image URLs**, not article URLs (it is an image-news sitemap).
- Extracting article links from the **ft.com** and **bloomberg.com** homepages returned "no article" — their navigation is rendered by JavaScript, so a plain HTML parse sees no article `<a>` tags.
- A **medium.com** tag page yielded no article links for the same reason.

**Cause:** this is a research-script limitation, **not** an auditor limitation — the auditor reads whatever URL it is given. It only affected my hunt for suitable test URLs. I worked around it by extracting links from publisher homepages that *do* render server-side, and by reading product handles from Shopify's `/products.json`.

**Important correction:** because of this, I initially mis-described ft.com and bloomberg.com as "bot-blocked." They are not — the auditor produced full reports for both (§11, §12). Only my separate link-extraction helper failed on their JS navigation.

### Problem C — paywall markers are rare and page-specific

**Symptom:** the paywall check #24 stayed `—` on every publisher *homepage* and on most article pages, firing on only one site (National Geographic).

**Cause, two parts:**
1. **Page-specific.** The `isAccessibleForFree:false` flag lives on individual locked article pages, never on the homepage. Auditing a homepage cannot find it by design.
2. **Declared-free for crawlers.** Many publishers that paywall in the browser nonetheless declare `isAccessibleForFree:true` to crawlers (Wired's article, several New Yorker magazine pieces) and enforce the wall with client-side JavaScript the auditor never executes. On those, #24 *correctly* stays silent — there is no machine-readable "locked" signal to find.

**Resolution:** I confirmed the marker's presence before auditing, found that **National Geographic** and **The Athletic** declare `isAccessibleForFree:false`, and audited the NatGeo article (§10) to demonstrate #24 firing.

### Sites probed but not audited

To find a paywalled article that would fire #24, I checked these for the marker but did not run a full audit on them: **newyorker.com** (magazine pieces — all `isAccessibleForFree:true`), **economist.com** (no marker found), **businessinsider.com** (no marker found), **medium.com** (links not extractable without JS), and **theathletic.com** (`isAccessibleForFree:false` confirmed but NatGeo was used as the demonstration instead). These were marker probes only, not audits, so they have no 22-check report.

---

## Closing note

Across twelve audits, every Tier-A check and nine of the ten Tier-B checks produced at least one live result. The only check never seen firing is **[23] content-licensing / AI-access**, which stayed `—` everywhere — an honest reflection that machine-readable AI-licensing programmes (`tdmrep.json`, TollBit-style markers) remain rare in the wild as of mid-2026. The one genuine tool limitation this exercise surfaced — the [#3 render timeout](#problem-a-the-3-render-timeout-now-fixed) — has since been **fixed**, turning six `unknown`s into five passes and one true negative.
