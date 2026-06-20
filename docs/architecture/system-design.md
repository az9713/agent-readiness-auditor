# System design

The technical architecture for developers who will work on the auditor, not just run it.

---

## High-level shape

The tool does one thing: fetch everything a single audit needs in one pass, then run each check as a pure function over that fetched data.

```text
  CLI (argparse)
        │  url, --json, --sample
        ▼
  fetch_context(url)  ──────────────► Context
        │  one network pass            (all fetched data, no logic)
        │   • homepage HTML + headers
        │   • homepage rendered (Playwright)
        │   • robots.txt        • sitemap.xml
        │   • llms.txt          • sampled pages
        │   • .well-known/agent-card.json, .well-known/ucp
        ▼
  run_checks(ctx)  ─────────────────► [ {id, name, group, tier, status, detail} × 22 ]
        │  22 pure check fns (12 Tier-A + 10 Tier-B)
        ▼
  summarize(ctx)  ──────────────────► Tier-A pass tallies + Tier-B signal counts
        ▼
  render: text checklist  OR  JSON
```

The separation is the point: all network and browser work happens in `fetch_context`. Every check is then a pure function from `Context` to `(status, detail)`, which makes the checks trivially testable offline.

---

## Components

| Component | Responsibility |
|-----------|----------------|
| Pure parsing helpers | Turn raw bytes into facts: `parse_robots`, `extract_structured_types`, `extract_opengraph`, `extract_dates`, `extract_canonical`, `parse_sitemap_xml`, `detect_protocols`, `visible_text`, `llms_wellformed`. No network. |
| Network layer | `fetch` (one HTTP GET, never raises), `render_text` (Playwright), `fetch_context` (orchestrates the single pass). |
| Checks | `check_1` … `check_21`, each `fn(ctx) -> (status, detail)`. Registered in the `CHECKS` list with id, name, group, and tier. |
| Runner / render | `run_checks`, `summarize`, `render_text_report`, and `main` (CLI). |

The `Context` and `Resource` dataclasses are plain data carriers — a `Resource` holds one fetched thing (status, text, headers, final URL, error); the `Context` holds all of them plus the derived text.

---

## Data flow for one audit

1. `main` normalises the URL (adds `https://` if absent) and calls `fetch_context`.
2. `fetch_context` fetches the homepage first. If it is unreachable, it raises `ConnectionError` and `main` exits `2`.
3. It derives the site root from the homepage's final URL (so redirects are honoured), then fetches `robots.txt`, `sitemap.xml` (preferring a `Sitemap:` line in robots), `llms.txt`, and the protocol-discovery files `/.well-known/agent-card.json` (with a legacy `/.well-known/agent.json` fallback) and `/.well-known/ucp`.
4. It renders the homepage with Playwright to get the JavaScript-rendered text for check #3.
5. It samples up to `--sample` page URLs from the sitemap and fetches each, for the coverage check.
6. `run_checks` runs all 22 checks over the assembled `Context`. A check that raises is caught and downgraded to `unknown` — one broken check never sinks the run.
7. `main` renders text or JSON.

---

## Key design decisions

### Fetch once, then pure checks

Checks never touch the network. This makes them deterministic and unit-testable with hand-built `Context` objects (no mocking of HTTP). It also means each network resource is fetched exactly once, no matter how many checks read it.

### Tier A facts plus Tier B proxies

The tool implements the 12 deterministic (Tier A) checks and all 10 Tier-B proxies. The 3 Tier-C checks from the [design reference](../../agent-readiness-auditor.md) are out of scope because they cannot be measured at all from the outside (they need an actual transaction). This is why check IDs are non-contiguous — the gaps are the Tier-C checks. Full reasoning: [development journey, Fork 2](../../development-journey.md#fork-2-what-can-actually-be-built-tiers-a-b-c).

Tier-A and Tier-B results are kept separate everywhere: a Tier-B check returns `pass` or `unknown` (and `fail` only for a detected barrier, check #16), renders in its own grouped Tier-B section, and is summarized as a signal count rather than folded into a Tier-A fraction. A verified fact and a proxy signal must never blend into one number.

### Three-state results, no score

Every check is `pass`, `fail`, or `unknown`, and the output has no blended number. A score would either weight groups arbitrarily or hide the difference between a verified fact and an unmeasured one. See [development journey, Fork 5](../../development-journey.md#fork-5-no-scoring-system).

### Faults are isolated, never fatal

`fetch` returns a `Resource` with `status=None` on any transport error rather than raising, and `run_checks` wraps each check in a try/except that yields `unknown`. The only fatal condition is an unreachable homepage, because with no homepage there is nothing to audit.

---

## Security

Sitemaps are XML fetched from arbitrary third-party sites — untrusted input at a trust boundary. Python's standard-library XML parser is vulnerable to entity-expansion ("billion laughs") attacks, so the tool parses sitemaps with `defusedxml` instead. `parse_sitemap_xml` catches every parse error and returns "no usable sitemap", so a malformed or malicious sitemap degrades a single check rather than crashing the run. A test (`test_billion_laughs_safe`) confirms a bomb is refused.

See [development journey, Fork 7](../../development-journey.md#fork-7-security-hardening) for the history.

---

## Testing

`test_auditor.py` holds 34 offline tests, run with `python test_auditor.py` or `pytest`. They need no network and no browser:

| Layer | What it covers |
|-------|----------------|
| Parsing helpers | robots parse/stance, structured-data / OpenGraph / date / canonical extraction, sitemap parse, protocol detection, CAPTCHA / paywall / CDN / offer / licence detection, llms.txt sanity, script-stripping, the entity-bomb safety test. |
| Check functions | All 22 checks, driven by hand-built `Context` objects to exercise pass / fail / unknown branches, including Tier-B proxy semantics (positive-only, barrier-as-fail for #16, silence-is-never-a-fact). |
| Integration | One all-green fixture through `run_checks` / `summarize` / `render_text_report`; a test that Tier-A and Tier-B summaries stay separate; one fault-isolation test proving a raising check becomes `unknown`. |

The checks being pure functions over a data object is what makes this possible without HTTP mocking.

---

## Scaling characteristics

The tool audits one site per run and is bounded by network latency plus one browser launch. The sitemap sample (`--sample`, default 10) is the main cost lever — each sampled page is a separate fetch. There is no concurrency, no persistence, and no batch mode; those are deliberately out of scope for this version.

---

## Dependencies

| Dependency | Role |
|------------|------|
| `requests` | HTTP fetching with redirects and timeouts. |
| `beautifulsoup4` + `lxml` | HTML parsing for structured data, OpenGraph, canonical, dates. |
| `defusedxml` | Safe sitemap XML parsing. |
| `playwright` (Chromium) | Rendering the homepage for the JavaScript check. |

No database, no external services, no API keys.
