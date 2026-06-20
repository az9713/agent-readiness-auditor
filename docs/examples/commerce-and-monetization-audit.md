# Exercising the Commerce and Monetization checks

The [comparative audit](comparative-audit.md) of three tech sites left the **Commerce** and **Monetization** Tier-B groups mostly unexercised — none of those sites is a storefront or a paywalled publisher. This report fills that gap by auditing a Shopify store and news/magazine publishers, and explains a key lesson it surfaced: **where the marker lives determines whether the check can see it.**

**Date:** 2026-06-20 · **Command:** `python agent_audit.py <url> --sample 5` (or `--sample 2` for inner pages)

> **Reminder.** ✅ = signal found · ❌ = Tier-A absent / Tier-B barrier detected · — = no signal visible (Tier-B `—` is **not** proof of absence). The Tier-B checks are proxies; a positive is trustworthy, silence is not.

---

## The headline lesson: homepage vs inner page

The Commerce and Monetization markers do not live on a site's homepage. They live on **product pages** (price/stock) and **article pages** (paywall flags). Auditing only the homepage leaves those checks silent — correctly, because the homepage genuinely has no such markers.

The fix is to point the auditor at the relevant inner page. The contrast is stark:

| Check | Allbirds **homepage** | Allbirds **product page** |
|-------|:---------------------:|:-------------------------:|
| [15] Machine-readable price/stock | — | ✅ `Offer, availability, offers, price, priceCurrency` |
| [11] Structured data | ❌ none | ✅ `ProductGroup` |

| Check | NatGeo **homepage** (implied) | NatGeo **article page** |
|-------|:-----------------------------:|:-----------------------:|
| [24] Machine-readable paywall | — | ✅ `isAccessibleForFree:false` |
| [18] Machine-readable dates | varies | ✅ `06-19-2026 (+3 more)` |

**Takeaway for users:** to audit commerce readiness, point the tool at a product page; to audit paywall/monetization, point it at an article. A homepage audit measures the front door, not the rooms.

---

## Site 1 — Allbirds (Shopify store)

Audited both the homepage and a product page. The product page is where Commerce comes alive.

### Allbirds product page — the Commerce showcase

`python agent_audit.py "https://www.allbirds.com/products/womens-tree-dasher-relay-..." --sample 2`

```text
Tier-A facts   — Read 2/3 · Trust 0/2 · Freshness 2/4 · Discovery 3/3
Tier-B signals — Docs 1/2 · Permissions 1/2 · Commerce 3/4 · Monetization 0/2
```

The full Commerce group, interpreted:

| # | Check | Result | What it means here |
|---|-------|:------:|--------------------|
| 13 | Machine-readable product feed | ✅ | `/products.json` exists — Shopify's standard bulk product endpoint. An agent can read the whole catalogue without scraping. |
| 15 | Machine-readable price/stock | ✅ | The page's JSON-LD carries `Offer` with `price`, `priceCurrency`, `availability` — an agent can read the price and stock for *this* item directly. |
| 16 | Checkout bot-wall (CAPTCHA) | ❌ | reCAPTCHA **and** hCaptcha detected. This is the trustworthy-negative case: a real barrier to agent automation at checkout. The one Tier-B check that returns ❌. |
| 17 | Agent-commerce protocol | ✅ | Declares **UCP** (Google's Universal Commerce Protocol) at `/.well-known/ucp` — Shopify has rolled UCP out, so an agent can discover the store's commerce capabilities. |

This single page demonstrates the full range of Tier-B outcomes: ✅ positive (13, 15, 17), ❌ barrier (16), and — where relevant.

> **Note on #16 being ❌:** Allbirds *wants* agents to read its catalogue (it ships `llms.txt`, `products.json`, and UCP) yet walls the checkout with CAPTCHA. That tension is exactly what the auditor is built to surface — a site can be read-friendly and transact-hostile at the same time.

### Allbirds homepage — for contrast

```text
Tier-B signals — Docs 1/2 · Permissions 1/2 · Commerce 2/4 · Monetization 0/2
```

Same site, but #15 drops to — because the homepage carries no `Offer` data. #13 (products.json) and #17 (UCP) still fire — those are site-wide, not page-specific. This is why the [15]-vs-page distinction matters.

---

## Site 2 — National Geographic article (paywalled publisher)

`python agent_audit.py "https://www.nationalgeographic.com/health/article/women-strength-training-..." --sample 2`

```text
Tier-A facts   — Read 2/3 · Trust 0/2 · Freshness 4/4 · Discovery 3/3
Tier-B signals — Docs 0/2 · Permissions 1/2 · Commerce 0/4 · Monetization 1/2
```

The Monetization group, interpreted:

| # | Check | Result | What it means here |
|---|-------|:------:|--------------------|
| 24 | Machine-readable paywall | ✅ | The article's JSON-LD declares `isAccessibleForFree:false` — a machine-readable signal that this content is gated. The tool sees the *declaration*; it cannot confirm whether an authorised agent could pass the wall. |
| 23 | Content-licensing / AI-access | — | No `tdmrep.json` and no known AI-access provider (TollBit, ScalePost, …) marker. NatGeo may license content, but not in a form detectable from the page. |

It also scores a clean Freshness 4/4 — article pages carry the `datePublished`/`dateModified` and headers that marketing homepages lack.

---

## Site 3 — The New York Times (the AI-policy showcase)

NYT doesn't trip Monetization markers on its homepage, but it is the strongest **Trust** demonstration in any audit so far.

```text
Tier-A facts   — Read 2/3 · Trust 2/2 · Freshness 4/4 · Discovery 2/3
Tier-B signals — Docs 0/2 · Permissions 0/2 · Commerce 1/4 · Monetization 0/2
```

| # | Check | Result | What it means here |
|---|-------|:------:|--------------------|
| 6 | Explicit AI-bot policy | ✅ | Names **15** AI bots in `robots.txt` — the full known roster. |
| 7 | AI-bot allow/block stance | ✅ | Almost all **blocked** (GPTBot, ClaudeBot, Google-Extended, PerplexityBot, CCBot…); only Amazonbot is `partial`. NYT is the archetypal AI-blocker, and the tool reads that stance precisely. |
| 13 | Machine-readable product feed | ✅ | An RSS/Atom feed link — the news-site form of a machine-readable content feed. |
| 16 | Checkout bot-wall (CAPTCHA) | ❌ | reCAPTCHA detected (on the subscription/login flow). |

A `Trust 2/2` here is the mirror image of a storefront: NYT has decided, explicitly and machine-readably, that it does *not* want most AI agents — and that decision is itself a clean, readable signal.

---

## What stayed `—`, and why that is honest

Two patterns are worth calling out, because they show the proxies behaving correctly rather than failing.

**Free articles correctly do not trip #24.** A Wired article and several New Yorker pieces declare `isAccessibleForFree:true`. The paywall check stayed `—` on those — correct, because they are *not* paywalled to crawlers. Only NatGeo's genuinely-gated article (`false`) fired it. The check tracks the declared marker, not a guess.

**Bot-blocking publishers can't be probed at all.** FT and Bloomberg returned no readable content to the tool — they block unfamiliar agents outright. That is its own finding: a site so locked down that even an honest auditor sees nothing. No marker can be read from a door that won't open.

**#23 (content-licensing) stayed `—` everywhere.** Machine-readable AI-access programmes (`tdmrep.json`, TollBit markers) are still rare in the wild. A `—` is the truthful result: the programme may exist commercially, but it is not declared in a form an outside crawler can see.

---

## Summary: every Commerce and Monetization check, demonstrated

| # | Check | Fired ✅/❌ on | 
|---|-------|---------------|
| 13 | Machine-readable product feed | Allbirds (`products.json`), NYT (RSS) |
| 15 | Machine-readable price/stock | Allbirds **product page** (`Offer`) |
| 16 | Checkout bot-wall (CAPTCHA) | Allbirds, NYT, NatGeo (❌ barrier) |
| 17 | Agent-commerce protocol | Allbirds (**UCP**) |
| 23 | Content-licensing / AI-access | *(none — rare in the wild)* |
| 24 | Machine-readable paywall | NatGeo **article page** (`isAccessibleForFree:false`) |

Five of the six now have a live positive; #23 stayed silent everywhere, which is the honest state of machine-readable content-licensing today. The decisive practical lesson: **audit the page that carries the marker** — a product page for commerce, an article for monetization.
