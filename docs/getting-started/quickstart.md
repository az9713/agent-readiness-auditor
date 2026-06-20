# Quickstart

Audit your first website and read the result. This takes about 10 minutes, including install.

---

## Prerequisites

Complete the [installation](installation.md) first. You need the Python dependencies and the Chromium browser.

---

## 1. Audit a bare static site

Start with `example.com` — it has almost none of the agent-facing signals, which makes the output easy to read:

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

## 2. Audit a site that does more

Now run a documentation site, which publishes `llms.txt`, a sitemap, and OpenGraph tags:

```bash
python agent_audit.py https://docs.anthropic.com --sample 5
```

Key lines from the output:

```text
Agent Readiness — https://platform.claude.com/docs/en/home
...
  ✅ [ 1] llms.txt present — /llms.txt found (valid markdown)
  ✅ [ 2] sitemap.xml present — urlset, 3217 entries, freshest: no lastmod dates
  ✅ [12] OpenGraph tags — 11 og: tag(s) incl. og:title
...
Read 1/3 · Trust 0/2 · Freshness 2/4 · Discovery 3/3
```

Two things to notice. The audited URL in the header (`platform.claude.com/...`) is not what you typed — the site redirected, and the tool reports where it actually landed. And `llms.txt` passes here but failed on `example.com`: the same check responding to a real difference.

## 3. Get machine-readable output

Add `--json` to get a structured object instead of the text checklist:

```bash
python agent_audit.py cloudflare.com --json --sample 2
```

The output is a JSON object with `url`, `audited_at`, an array of 22 `checks`, and a `summary` with Tier-A tallies plus a Tier-B `signals` block. See the [CLI reference](../reference/cli.md#json-output) for the full schema.

---

## What happened

Each run fetched the homepage (and rendered it in a browser), plus `robots.txt`, `sitemap.xml`, `llms.txt`, the `/.well-known/` protocol files, an API spec, a TDM/licence file, a product feed, and a sample of pages from the sitemap. It then ran 22 independent checks over that data.

The first 12 are **Tier-A facts** (Read, Trust, Freshness, Discovery), each pass / fail / unknown. The next 10 are **Tier-B proxies** (Docs, Permissions, Commerce, Monetization) — indirect signals printed in their own section. A Tier-B ✅ is a trustworthy positive; a `—` means no signal was visible, which is *not* proof of absence. Only the CAPTCHA check (#16) can show ❌, because detecting a bot-wall is a trustworthy negative.

There is no overall score. Each group shows a raw count like `Read 1/3` — a specific, honest statement, not a weighted number. The two tiers are tallied on separate footer lines so a verified fact and a proxy signal are never blended. See [why there is no score](../reference/cli.md#no-score-by-design).

---

## Next steps

- [Checks reference](../reference/checks.md) — what each of the 12 checks looks for.
- [CLI reference](../reference/cli.md) — every flag, the JSON schema, and exit codes.
- [Key concepts](../overview/key-concepts.md) — definitions for `llms.txt`, structured data, canonical URL, and the rest.
