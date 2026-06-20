# Agent Readiness Auditor — development journey and transparency

This document traces how the Agent Readiness Auditor came to exist, every design fork along the way, and — most importantly — states plainly what the tool does, what it cannot do, and how to read its output. Read it alongside the design reference, [agent-readiness-auditor.md](agent-readiness-auditor.md), which holds the full 25-check catalog.

---

## Contents

| Section | What's inside |
|---------|---------------|
| [Where it started](#where-it-started-a-podcast) | The YouTube episode that seeded the idea |
| [The journey at a glance](#the-journey-at-a-glance) | Every fork and the decision taken |
| [Fork 1: the six-dimension table](#fork-1-the-six-dimension-table) | The original concept |
| [Fork 2: what can actually be built](#fork-2-what-can-actually-be-built-tiers-a-b-c) | Tiers A, B, C |
| [Fork 3: agent-commerce protocols](#fork-3-agent-commerce-protocols) | ACP, AP2, A2A, UCP, x402 |
| [Fork 4: what "proxy" means](#fork-4-what-proxy-means) | The 10 Tier-B checks |
| [Fork 5: no scoring system](#fork-5-no-scoring-system) | Why there is no 0–100 score |
| [Fork 6: building v1](#fork-6-building-v1) | Language, browser, I/O decisions |
| [Fork 7: security hardening](#fork-7-security-hardening) | The XML-bomb fix |
| [What the app does — and does not — do](#what-the-app-does-and-does-not-do) | The transparency core |
| [Running it](#running-it-examples-and-expected-output) | Examples and expected output |
| [Interpreting results](#interpreting-results) | How to read the checklist |
| [Out of scope and roadmap](#out-of-scope-and-roadmap) | What was deliberately left out |
| [File map](#file-map) | Where everything lives |

---

## Where it started: a podcast

The idea came from one episode of IBM's *Mixture of Experts* podcast: ["Microsoft's new AI models & bots dominate the internet"](https://www.youtube.com/watch?v=SvBheXuKY8s&t=5s).

The episode covered three stories. Two set up the problem this tool addresses:

| Story | The relevant point |
|-------|--------------------|
| Bots now generate 57% of web traffic (Cloudflare) | People increasingly reach websites *through* an AI, not directly. Sites have a second audience that is not human. |
| Microsoft's MAI-Thinking-1 and the rise of agents | Agents read, compare, and act on web content on a person's behalf. |
| AI films at the Tribeca Film Festival | (Context only — not relevant to this tool.) |

A companion analysis of the episode proposed a concrete project: an **Agent Readiness Auditor** — a tool that scores how usable a website is to an AI agent rather than to a human. That proposal is where this project began.

The core premise, taken straight from the episode: if machines are increasingly the ones reading websites, sites should be built to be legible to machines. The auditor measures how legible a given site is.

---

## The journey at a glance

The project advanced through a series of decisions. Each row is a fork where a question had more than one answer.

| Fork | Question | Decision |
|------|----------|----------|
| 1 | What does the auditor measure? | Six dimensions, 25 individual checks |
| 2 | Which checks can actually be built? | Sort into Tiers A / B / C by feasibility |
| 3 | Can we detect agent-commerce protocols? | Yes for `.well-known`-discoverable ones; upgrade check #17 |
| 4 | How do we report the unreliable checks? | As clearly-marked proxies, never as facts |
| 5 | Do we need a 0–100 score? | No — ship a three-state checklist |
| 6 | How do we build v1? | Python, Playwright required, single URL, text + JSON |
| 7 | Is parsing third-party XML safe? | No — harden with `defusedxml` |

The sections below walk each fork in turn.

---

## Fork 1: the six-dimension table

The auditor scores a site across six dimensions, each answering one question an agent cares about.

| Dimension | The question it asks |
|-----------|----------------------|
| Agent-readable docs | Can a machine get the content without parsing messy HTML? |
| Permissioning | Does the site state what bots are allowed to do? |
| Structured data | Is the meaning of content labelled as data, not just laid out visually? |
| Commerce readiness | Can an agent compare, cart, check out, query stock? |
| Freshness | Can an agent tell how recent and authoritative a page is? |
| Monetization | If agents consume the site, does the site get paid? |

These six group naturally into three jobs an agent must do:

- **Read** the content (agent-readable docs, structured data).
- **Trust** it (permissioning, freshness).
- **Transact** with the site and let the site get paid (commerce readiness, monetization).

The full breakdown of all 25 checks under these dimensions lives in [agent-readiness-auditor.md](agent-readiness-auditor.md), Section 5.

---

## Fork 2: what can actually be built (Tiers A, B, C)

A tool that visits a site as an outside stranger cannot measure everything. The 25 checks sort into three tiers by how well an outside program can perform them.

> **Key term — from the outside.** The auditor sees only what any anonymous visitor sees. It cannot log into the site's admin panel or read its private code. This constraint is what creates the tiers.

| Tier | Meaning | Build verdict |
|------|---------|---------------|
| **A** | Deterministic. One fetch or one parse gives a clear, repeatable yes/no. | Build it, trust it. |
| **B** | A proxy — an indirect clue that usually correlates with the real thing. | Build it, but label it a proxy. |
| **C** | Needs to actually transact, or needs abusive probing, or is a human judgement. | Cannot be done from outside. |

The 25 checks fall out as **12 Tier-A, 10 Tier-B, 3 Tier-C**.

| Tier | Count | Check IDs |
|------|-------|-----------|
| A | 12 | 1, 2, 3, 6, 7, 11, 12, 14, 18, 19, 20, 21 |
| B | 10 | 4, 5, 9, 10, 13, 15, 16, 17, 23, 24 |
| C | 3 | 8, 22, 25 |

The honest tension this exposed: the checks that would tell you the most — whether an agent can truly transact, whether the site earns from agents — are exactly the ones an outside tool struggles to perform. The hard-to-fake signals are also the hard-to-measure ones.

The decision that followed: **v1 ships only the 12 Tier-A checks.** They are reliable, they cover Read / Trust / Freshness completely, and they need no hedging.

---

## Fork 3: agent-commerce protocols

One Tier-C check was reconsidered and upgraded. Check #17 — "does the site support an agent-payment standard?" — was first rated Tier C on the assumption that these standards leave no detectable trace. That was too pessimistic.

Several leading standards adopted the `/.well-known/` discovery pattern, which a crawler *can* read. Whether a protocol is detectable depends on one thing: does it announce itself on the merchant's own site, or onboard through a platform out-of-band?

> **Key term — `/.well-known/` path.** A reserved folder at a site's root (`example.com/.well-known/…`) where standards agree to publish machine-readable declaration files. It is the web's convention for "if you support protocol X, announce it here."

The leading standards as of early 2026, and whether an outside probe can detect them:

| Protocol | Owner | How to detect it | Detectable? |
|----------|-------|------------------|-------------|
| **A2A** (Agent2Agent) | Google → Linux Foundation | `GET /.well-known/agent-card.json` (legacy `/.well-known/agent.json`) | Yes — high |
| **AP2** (Agent Payments Protocol) | Google + Mastercard, PayPal, others | Read `capabilities.extensions` in the A2A card for URI `https://github.com/google-agentic-commerce/ap2/tree/v0.1` | Yes — high, if A2A present |
| **UCP** (Universal Commerce Protocol) | Google | `GET /.well-known/ucp` | Yes — high |
| **x402** | Coinbase | Request a protected endpoint; inspect for HTTP **402** + a `PAYMENT-REQUIRED` header / `accepts[]` body | Partial — need an endpoint to hit |
| **ACP** (Agentic Commerce Protocol) | OpenAI + Stripe (+ Meta) | Onboards through OpenAI; no public discovery path | Mostly no — out-of-band |
| **MCP** (Model Context Protocol) | Anthropic | Website discovery still emerging | Weak |
| **Visa Intelligent Commerce / Mastercard Agent Pay** | Visa / Mastercard | Token issuance happens inside the card networks | No — network-side |

Four of these — A2A, AP2, UCP, x402 — are genuinely detectable. That moved check #17 from Tier C to **Tier B**. It stays at B, not A, for one honest reason: a *positive* result is trustworthy ("this site declares AP2"), but a *negative* result is not proof — a merchant can run ACP or onboard entirely through a platform and show nothing.

> **Note:** Check #17 is built. The app probes `/.well-known/agent-card.json` (A2A), the AP2 extension inside it, `/.well-known/ucp` (UCP), and a best-effort x402 signal. It is one of the 10 Tier-B proxies now in the tool, and it follows the proxy rule: a positive result is a real signal, a negative is reported as `unknown`. See [What the app does and does not do](#what-the-app-does-and-does-not-do).

---

## Fork 4: what "proxy" means

Every Tier-B check is a proxy, so the word needs pinning down.

> **Key term — proxy.** A stand-in measurement. When you cannot measure the thing you care about, you measure something else that usually travels with it. Example: you cannot see someone's bank balance, so you guess their wealth from the car they drive. The car is a proxy — often right, but a rich person might drive an old beater (proxy says "poor" when they're rich) and someone might lease a car they cannot afford (proxy says "rich" when they're broke). A proxy is a clue, not the truth.

Each Tier-B check has a real question it cannot answer directly, so it measures a visible clue instead. All ten:

| # | Real question | Proxy measured | How it misleads |
|---|---------------|----------------|-----------------|
| 4 | Can an agent get a clean Markdown/text version? | Probe common URL patterns + content negotiation | A site may serve clean text in a way we didn't guess → false "no." |
| 5 | Is there a usable public API with good docs? | Look for an API spec at common locations | A real API at a non-standard path is missed; a found spec doesn't prove the docs are usable. |
| 9 | Does the site permit automated/AI use? | Read machine-readable licence files / meta tags | A licence buried in prose terms-of-service is invisible → false "no." |
| 10 | Is pay-per-crawl / bot-charging active? | Detect the CDN and certain headers | We see a CDN is present, not that the charging feature is switched on. |
| 13 | Is there a machine-readable product feed? | Look for `Product` labels on pages | Labels suggest a feed could exist; they don't confirm a bulk feed. |
| 15 | Can an agent read price/stock per item? | Read `Offer`/availability labels | Labels hint at machine-readable data; they don't prove a queryable endpoint. |
| 16 | Are checkout steps open, not CAPTCHA-walled? | Detect CAPTCHA scripts on the page | We see the CAPTCHA exists; we can't confirm stable endpoints without buying. |
| 17 | Does the site support an agent-payment standard? | Probe `.well-known/` (A2A/AP2/UCP) and the x402 signature | A positive hit is trustworthy; silence is not — a site can run ACP and show nothing. |
| 23 | Is there a content-licensing / AI-access program? | Detect known providers + machine-readable licence files | Only declared programs are visible; a private deal leaves no trace. |
| 24 | Could an authorised agent pass the paywall? | Detect that a paywall exists | We confirm presence, not whether an authorised agent gets through cleanly. |

Notice the pattern: nearly every proxy fails in the same direction — a **false negative**. The clue is absent, so the tool says "no," when the real capability is simply present in a form the tool cannot see.

The rule that keeps this honest: a proxy result must be phrased as an observation, never a verdict.

- Fair: *"No machine-readable price data detected."* (states what was observed)
- Overclaim: *"This site cannot do agentic commerce."* (states a conclusion the proxy doesn't support)

---

## Fork 5: no scoring system

The instinct was to copy Lighthouse's single 0–100 number. The decision was not to.

The value of an audit is in the individual results — "no `llms.txt`," "robots.txt blocks ClaudeBot." Those are what a site owner fixes. A headline "67/100" tells them nothing actionable. The number is a lossy compression of the thing that matters.

A weighted score also carries three costs:

1. **Arbitrary weights.** Who decides permissioning is worth 20% and freshness 15%? Any number is a guess dressed as precision.
2. **Laundered uncertainty.** Averaging a Tier-A fact with a Tier-B proxy hides the difference between "we read this" and "we guessed this."
3. **False completeness.** A single score reads as "we measured everything," when 3 checks are unmeasurable and 10 are proxies.

What ships instead is a **three-state checklist**:

| Symbol | Status | Meaning |
|--------|--------|---------|
| ✅ | pass | Tier-A fact (verified present), or a positive Tier-B hit |
| ❌ | fail | Tier-A fact: the thing is genuinely absent |
| — | unknown | A check could not be performed (proxy found nothing, or a fetch failed) |

A score would earn its place only for ranking many sites or tracking one site over time. Until that need is real, it is deferred. Full reasoning: [agent-readiness-auditor.md](agent-readiness-auditor.md), Section 8.

---

## Fork 6: building v1

Three decisions fixed the shape of the v1 script.

| Decision | Choice | Why |
|----------|--------|-----|
| Language | Python | Fastest to write and read; mature HTTP and HTML libraries. |
| Headless browser | Playwright, **required** | Check #3 (readable without JavaScript) needs a real browser engine. Making it required means every check always runs. |
| Input / output | Single URL; text by default, `--json` flag | One site per run keeps v1 focused. JSON enables machine use without bloating the default. |

The architecture is deliberately flat: fetch the shared resources once (homepage HTML and headers, the browser-rendered page, `robots.txt`, `sitemap.xml`, `llms.txt`, the `/.well-known/` protocol and TDM files, an API spec, a product feed, and a sample of sitemap pages), then run each of the 22 checks as a pure function over that fetched context.

---

## Fork 7: security hardening

The auditor parses `sitemap.xml` files fetched from arbitrary third-party sites. That is untrusted input at a trust boundary.

Python's standard-library XML parser is vulnerable to entity-expansion attacks (the "billion laughs" bomb: a tiny file that expands to gigabytes and exhausts memory). A malicious site could serve such a sitemap and crash the auditor.

The fix: parse sitemaps with `defusedxml` instead of the standard library. A test confirms a billion-laughs bomb is refused, not expanded. This is the one place where the "laziest solution that works" was explicitly *not* taken, because security at a trust boundary is never the place to cut corners.

---

## What the app does and does not do

This is the transparency core. Read it before trusting any result.

### What the app does

- Audits **one URL** per run.
- Performs the **12 Tier-A checks** — deterministic checks where one fetch or one parse gives a clear answer.
- Performs **all 10 Tier-B proxy checks** — clean-text/API docs, licence/CDN permissions, product-feed/price/CAPTCHA/protocol commerce, and licensing/paywall monetization — reported as clearly-marked proxies in their own grouped section.
- Reports Tier-A checks as **pass / fail / unknown** (Read / Trust / Freshness / Discovery), and Tier-B checks as **pass / unknown** — plus **fail** only for a detected bot-wall (check #16), a trustworthy negative.
- Keeps the two tiers separate in the summary — Tier-A pass counts, Tier-B signal counts — never blended.
- Outputs human-readable text, or JSON with `--json`.
- Follows redirects and reports the final URL it actually audited.
- Renders the homepage in a real browser to test whether content survives without JavaScript.
- Samples pages from the sitemap (default 10) to measure structured-data coverage.

### What the app does not do

| Not done | Why |
|----------|-----|
| The 3 Tier-C checks | Not measurable from outside at all — they need an actual transaction. |
| Detect ACP, MCP, or Visa/Mastercard agent-pay | These onboard through platforms or run inside card networks — invisible to a crawl. Check #17 only sees A2A / AP2 / UCP / x402. |
| Prove an API/feed/protocol is absent | A Tier-B `—` means no signal was visible, not that the capability is missing — it may sit at a path the tool did not guess. |
| Confirm a purchase, login, or paywall bypass | Tier-B detects *markers* (an Offer, a paywall flag, a checkout CAPTCHA); it never transacts to verify them. |
| Any numeric or weighted score | Deliberate design decision ([Fork 5](#fork-5-no-scoring-system)). |
| Crawl beyond the sitemap sample | Out of scope for v1. |
| Audit multiple sites in one run | Single URL only. |
| Verify a purchase, login, or paywall bypass | Would require actually transacting. |
| Judge content *quality* | It measures machine-legibility, not whether the writing is good. |

### What a result means — and does not mean

- A ❌ on a Tier-A check is a **fact**: the thing was looked for directly and is absent. "No `robots.txt`" means there is no `robots.txt`.
- A — (unknown) on a Tier-A check means the check **could not be performed** — usually a network failure or, for check #3, a page that would not render.
- A ✅ on the Tier-B check (#17) is a **trustworthy positive**: the site really does declare that protocol. A — on it means **no signal was visible**, which is not proof of absence — the site may use an undetectable protocol.
- The tool measures **readiness signals**, not outcomes. A site that passes every check is *legible* to agents; it does not prove any specific agent will succeed on it.

---

## Running it: examples and expected output

### Setup

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### Run the offline tests first

```bash
python test_auditor.py
```

Expected output (34 checks, all green):

```text
  ok  test_billion_laughs_safe
  ok  test_check_1_llms
  ...
All 34 offline checks passed.
```

### Example 1: a bare static site

```bash
python agent_audit.py https://example.com --sample 3
```

Expected output:

```text
Agent Readiness — https://example.com/
============================================================

Read
  ❌ [ 1] llms.txt present — no /llms.txt
  ❌ [11] Structured data (homepage) — no JSON-LD or microdata
  ❌ [14] Structured-data coverage — no sitemap — homepage only: no data

Trust
  ❌ [ 6] Explicit AI-bot policy — no robots.txt
  ❌ [ 7] AI-bot allow/block stance — no AI bots named to have a stance

Freshness
  ❌ [18] Machine-readable dates — no machine-readable dates
  ✅ [19] Last-Modified / ETag — last-modified
  ❌ [20] Canonical URL — no rel=canonical
  ❌ [21] Cache headers — no Cache-Control or Expires

Discovery
  ❌ [ 2] sitemap.xml present — no parseable sitemap.xml
  ✅ [ 3] Readable without JavaScript — raw text is 110% of rendered — readable without JS
  ❌ [12] OpenGraph tags — no og:title

Tier-B proxy signals  (✅ positive · ❌ barrier detected · — none visible — NOT proof of absence)
  Docs
    — [ 4] Clean text/markdown alternative — no machine-friendly text/markdown alternative detected (may exist at an unguessed path)
    — [ 5] Public API spec — no public API spec at common paths (an API may exist at an unguessed path)
  Permissions
    — [ 9] Automated-use licence/policy — no machine-readable licence/TDM policy found (terms may exist only in prose)
    ✅ [10] CDN / pay-per-crawl capable — served via Cloudflare (bot-management / pay-per-crawl capable; cannot confirm it is enabled)
  Commerce
    — [13] Machine-readable product feed — no machine-readable product feed detected
    — [15] Machine-readable price/stock — no machine-readable price/availability (Offer) data found
    — [16] Checkout bot-wall (CAPTCHA) — no CAPTCHA/bot-wall on the homepage (other pages not probed)
    — [17] Agent-commerce protocol — no public agent-commerce protocol found (a site can still use ACP or onboard via a platform — not visible from outside)
  Monetization
    — [23] Content-licensing / AI-access — no content-licensing or AI-access program detected
    — [24] Machine-readable paywall — no machine-readable paywall markers found

------------------------------------------------------------
Tier-A facts   — Read 0/3 · Trust 0/2 · Freshness 1/4 · Discovery 1/3   (✅ pass · ❌ fail · — unknown; no blended score)
Tier-B signals — Docs 0/2 · Permissions 1/2 · Commerce 0/4 · Monetization 0/2   (✅ found · ❌ barrier · — none visible; signals, not proof)
```

This is the expected shape for a minimal static page: it passes "readable without JavaScript" and carries a `Last-Modified` header, and the one Tier-B signal it trips is the CDN (it is served via Cloudflare). Everything else is silent — `—`, not a failure.

### Example 2: a documentation site

```bash
python agent_audit.py https://docs.anthropic.com --sample 5
```

Key lines from the output:

```text
Agent Readiness — https://platform.claude.com/docs/en/home
...
Read
  ✅ [ 1] llms.txt present — /llms.txt found (valid markdown)
...
Discovery
  ✅ [ 2] sitemap.xml present — urlset, 3217 entries, freshest: no lastmod dates
  ✅ [ 3] Readable without JavaScript — raw text is 111% of rendered — readable without JS
  ✅ [12] OpenGraph tags — 11 og: tag(s) incl. og:title
...
Read 1/3 · Trust 0/2 · Freshness 2/4 · Discovery 3/3
```

Two things to note. The audited URL (`platform.claude.com/...`) differs from the input because the tool followed a redirect and reports where it actually landed. And `llms.txt` passes here but failed on example.com — the positive-versus-negative contrast that proves the check responds to real differences.

### Example 3: JSON output

```bash
python agent_audit.py cloudflare.com --json --sample 2
```

The JSON shape:

```json
{
  "url": "https://www.cloudflare.com/",
  "audited_at": "2026-06-20T05:01:46.840208+00:00",
  "checks": [
    {
      "id": 6,
      "name": "Explicit AI-bot policy",
      "group": "Trust",
      "status": "pass",
      "detail": "names 8 AI bot(s): gptbot, chatgpt-user, claude-web, anthropic-ai, google-extended, perplexitybot, ccbot, cohere-ai"
    }
  ],
  "summary": {
    "Read":      { "pass": 3, "total": 3 },
    "Trust":     { "pass": 2, "total": 2 },
    "Freshness": { "pass": 2, "total": 4 },
    "Discovery": { "pass": 3, "total": 3 }
  }
}
```

Fittingly, Cloudflare — the company that produced the 57%-bot-traffic figure that started this whole project — is the one running an explicit AI-bot policy, naming eight agents by name.

### Command-line options

| Option | Default | Effect |
|--------|---------|--------|
| `url` (positional) | — | The site to audit. Scheme optional; `https://` is added if missing. |
| `--json` | off | Emit JSON instead of the text checklist. |
| `--sample N` | 10 | How many pages to sample from the sitemap for the coverage check (#14). |

---

## Interpreting results

Read the output in this order:

1. **Check the audited URL in the header.** If it differs from your input, the site redirected and you are seeing results for the destination.
2. **Read each group's tally**, not a single number. `Trust 0/2` is a clear, specific statement: the site has no AI-bot policy a machine can read. There is no blended score to over-interpret.
3. **Treat ❌ as a fact and — as silence.** A failing Tier-A check means the signal is genuinely absent. A `—` means the tool could not establish it — for Tier-A usually a network or render failure; for Tier-B it means no signal was visible, which is *not* proof of absence.
4. **Read Tier-B as signals, not verdicts.** A Tier-B ✅ is a trustworthy positive. The one ❌ a Tier-B check can show is the CAPTCHA bot-wall (#16), a trustworthy negative. Everything else absent is `—`.
5. **Remember the ceiling.** Passing every check means the site is *legible* to agents. It is a readiness signal, not a guarantee that any particular agent task will succeed.

A useful mental model: this tool answers "has this site done the basic, visible things that make it usable by machines?" It does not answer "is this site good," "will my agent succeed here," or "does this site make money from agents."

---

## Out of scope and roadmap

Built so far: the 12 Tier-A checks and all 10 Tier-B proxies (Docs, Permissions, Commerce, Monetization).

Deliberately still out:

- The 3 Tier-C checks (they need an actual transaction — see [Fork 2](#fork-2-what-can-actually-be-built-tiers-a-b-c)).
- Any scoring engine.
- Batch auditing, deeper crawling, result persistence, and any web UI.

The natural next step is the Tier-C frontier (which needs real transactions), or operational features — batch auditing, persistence, a web UI. Every Tier-B proxy added kept the same discipline: clearly marked as a proxy, phrased as an observation, never a verdict, per [Fork 4](#fork-4-what-proxy-means).

---

## File map

| File | Purpose |
|------|---------|
| [agent_audit.py](agent_audit.py) | The tool: fetch context once, run the 12 Tier-A + 10 Tier-B checks, print text or JSON. |
| [test_auditor.py](test_auditor.py) | 34 offline tests — parsing helpers, all 22 checks, protocol/CAPTCHA/paywall/CDN detection, integration, and the XML-bomb safety test. |
| [requirements.txt](requirements.txt) | `requests`, `beautifulsoup4`, `lxml`, `playwright`, `defusedxml`. |
| [agent-readiness-auditor.md](agent-readiness-auditor.md) | The design reference — the full 25-check catalog, tier analysis, and scoring decision. |
| development-journey.md | This document. |

### Provenance

- Origin: the *Mixture of Experts* episode ["Microsoft's new AI models & bots dominate the internet"](https://www.youtube.com/watch?v=SvBheXuKY8s&t=5s).
- Protocol facts (A2A, AP2, UCP, x402, ACP) verified against their published specifications in early 2026. These standards move quickly; re-check the exact paths and identifiers before building the probes.
