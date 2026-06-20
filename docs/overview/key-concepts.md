# Key concepts

Definitions for every term used across these docs. Grouped by topic. Each definition stands alone.

---

## The tool

**Agent Readiness Auditor** — a command-line tool that audits one website for how usable it is to AI agents rather than to humans, and prints a pass/fail/unknown checklist. Example: `python agent_audit.py https://example.com` audits one site and prints 12 results.

**Check** — one of the 12 individual tests the tool runs, each with a numeric ID, a name, and a group. Example: check #1 tests whether the site publishes an `llms.txt` file.

**Group** — the category a check belongs to in the output. Four groups: Read, Trust, Freshness, Discovery. Example: check #6 (AI-bot policy) is in the Trust group.

**Three-state checklist** — the output format: every check is `pass` (✅), `fail` (❌), or `unknown` (—). There is deliberately no numeric score. Example: `Read 1/3` means one of three Read-group checks passed.

---

## The agent web

**AI agent** — a large language model given tools and a goal, so it can act on its own: search, read pages, compare, and decide. When an agent works, it makes many automated web requests on a person's behalf. Example: "find the three cheapest flights and book one" is an agent task.

**Bot / crawler / scraper** — a bot is any program that uses the web automatically. A crawler systematically visits pages and follows links; a scraper pulls specific data off a page. Example: a search-engine crawler discovers pages to index.

**User-agent** — the name a bot announces itself by. AI crawlers have recognisable names. Example: `GPTBot` (OpenAI), `ClaudeBot` (Anthropic), `PerplexityBot` (Perplexity).

---

## Files a site can publish for machines

**`llms.txt`** — a plain-text file at a site's root (`example.com/llms.txt`) giving an AI a clean map and summary of the site's content, so it reads that instead of scraping messy HTML. Example: a docs site lists its key pages as Markdown links in `llms.txt`.

**`robots.txt`** — a long-standing file at a site's root listing which bots may visit which parts of the site. It works on the honour system. Example: `Disallow: /` under `User-agent: GPTBot` asks GPTBot not to crawl anything.

**Sitemap** — a file (usually `sitemap.xml`) listing the site's important pages. A table of contents for machines. Example: a 3,000-entry `urlset` lets the auditor sample pages without guessing URLs.

---

## Structured data

**Structured data** — invisible labelling in a page that states, in machine terms, what each value means ("this is the price", "this is the publish date"). Example: a price marked as structured data is unambiguous to an agent, even though a human just sees `$49.99`.

**Schema.org** — a shared vocabulary of labels for common things: `Product`, `Article`, `Organization`, `Offer`. Example: a product page tagged `@type: Product` tells any machine what it is.

**JSON-LD** — the most common format for embedding structured data, sitting in a hidden `<script>` block in the page. Example: `<script type="application/ld+json">{"@type":"Article"}</script>`.

**Microdata** — an older way of attaching the same labels directly onto visible HTML tags via `itemscope`/`itemtype` attributes. Example: `<body itemscope itemtype="https://schema.org/Organization">`.

**OpenGraph** — a small set of `<meta>` tags describing a page for sharing: title, summary, preview image. Originally for social-media link previews; also useful to any machine summarising the page. Example: `<meta property="og:title" content="...">`.

**Coverage** — for check #14, the fraction of sampled pages that carry structured data, not just whether one page does. Example: `7/10 sampled pages carry structured data`.

---

## Freshness signals

**Canonical URL** — the single official address for a piece of content, declared with `<link rel="canonical">` or a `Link:` header, so machines do not treat duplicates as separate pages. Example: a print version points its canonical at the main article.

**HTTP headers** — behind-the-scenes information sent with every page, separate from the visible content. The auditor reads four:

| Header | Meaning |
|--------|---------|
| `Last-Modified` | When the page last changed |
| `ETag` | A fingerprint that changes when the content changes |
| `Cache-Control` | How the page may be cached |
| `Expires` | When a cached copy goes stale |

**Machine-readable date** — a publish or modify date a machine can read directly: a JSON-LD `datePublished`/`dateModified`, an `article:modified_time` meta tag, or a `<time datetime="...">` element. Example: `<time datetime="2026-06-01">`.

---

## How the tool reads pages

**Headless browser** — a real browser engine running without a visible window, driven by a program. The auditor uses one to see content that only appears after a page's JavaScript runs. Example: check #3 compares the raw HTML text to the browser-rendered text.

**Playwright** — the library the auditor uses to drive a headless Chromium browser. Example: `python -m playwright install chromium` downloads the browser it needs.

**Readable without JavaScript** — check #3's question: does the page's content survive without running JavaScript? A page whose text only appears after JS is harder for simple agents to read. Example: `raw text is 110% of rendered — readable without JS` is a pass.

---

## The feasibility model

**Tier A** — a check that is deterministic: one fetch or one parse gives a clear, repeatable yes/no. Twelve of the tool's checks are Tier A. Example: "does `/robots.txt` exist?" is Tier A.

**Tier B** — a check that can only be done as a proxy: an indirect clue that usually correlates with the real answer. All 10 Tier-B checks are built, grouped into the dimensions Docs, Permissions, Commerce, and Monetization. A Tier-B check returns `pass` (a trustworthy positive) or `unknown` (no signal — not proof of absence); the one exception is check #16, which returns `fail` when it detects a bot-wall, because detecting a barrier is a trustworthy negative.

**Tier C** — a check that cannot be done from outside at all, because it needs to transact, needs abusive probing, or is a human judgement. Not built in this version. Example: "does this site's API charge per use?"

**Proxy** — a stand-in measurement used when the real thing cannot be measured directly. A clue, not the truth, and usually wrong in the direction of a false negative. Example: "no machine-readable price data detected" is an observation, not the verdict "this site cannot do commerce". Full treatment in the [design reference](../../agent-readiness-auditor.md) and [development journey](../../development-journey.md).

**From the outside** — the auditor sees only what any anonymous visitor sees; it cannot log in or read private code. This constraint is what separates Tier A from Tiers B and C.

---

## Agent-commerce protocols

These are emerging standards for agents to discover capabilities and pay. Check #17 (Tier B) detects the publicly discoverable ones — A2A, AP2, UCP, and a best-effort x402 signal. The others (ACP, MCP, Visa/Mastercard) are not visible from a crawl. Full landscape: [development journey](../../development-journey.md#fork-3-agent-commerce-protocols).

**A2A (Agent2Agent)** — an open standard for agents to find and delegate work to each other; discoverable at `/.well-known/agent-card.json`.

**AP2 (Agent Payments Protocol)** — a payment extension of A2A, declared by a fixed URI inside the A2A card.

**UCP (Universal Commerce Protocol)** — Google's merchant-capability standard, discoverable at `/.well-known/ucp`.

**x402** — Coinbase's standard that revives HTTP status code 402 (Payment Required) to describe how to pay for a resource.

**ACP (Agentic Commerce Protocol)** — OpenAI and Stripe's standard powering ChatGPT Instant Checkout; onboarded through a platform, so not visible to an outside crawler.

---

## Safety

**Billion-laughs attack** — a tiny XML file crafted to expand to gigabytes when parsed, exhausting memory. Sitemaps come from arbitrary third-party sites, so this is a real risk. Example: nested entity definitions that each reference the previous one ten times.

**`defusedxml`** — the hardened XML library the auditor uses to parse sitemaps, which refuses entity-expansion bombs instead of expanding them.
