# Web UI

A single-file local web front-end over the same auditor the CLI uses. Type a URL, and the
Tier-A facts and Tier-B proxy signals are shown grouped and colour-coded, each check with its
live finding **and** a plain-English explanation of what it looks for.

![The web UI showing a full audit of vercel.com.](../assets/web-ui.png)

## Run it

From the project root, after [installation](installation.md):

```bash
python webapp.py
```

Then open **http://127.0.0.1:8000**. Enter a domain (the scheme is optional — `vercel.com`
works as well as `https://vercel.com`) and press **Audit**. A single audit takes ~15–40s,
because it does exactly what the CLI does: fetch the homepage, `robots.txt`, sitemap, the
well-known files, and render the page once in a headless browser.

| Option | Default | Effect |
|--------|---------|--------|
| `--port N` | `8000` | Port to listen on. |
| `--host H` | `127.0.0.1` | Interface to bind. Leave as localhost unless you intend to expose it. |

## How to read the page

The page mirrors the CLI's two-tier model exactly:

- **Tier-A facts** — ✅ pass · ❌ fail · — unknown. Verified facts; no blended score.
- **Tier-B proxy signals** — ✅ signal found · ❌ barrier detected · — none visible. A `—` is
  **not** proof of absence (a site may use a capability privately or expose it at a path the
  tool did not guess). Only check #16 (CAPTCHA) returns ❌, because a detected bot-wall is a
  trustworthy *negative*. The page repeats this caveat inline so the proxies are never misread
  as facts. See [key concepts](../overview/key-concepts.md) and the
  [checks reference](../reference/checks.md).

## How it works

`webapp.py` is intentionally small and dependency-free:

- It uses Python's stdlib `http.server` (`ThreadingHTTPServer`) — no Flask, no new dependency.
  One endpoint plus one page doesn't earn a framework.
- It **imports `agent_audit.py` and calls the same `fetch_context → run_checks → summarize`
  functions** the CLI's `--json` path uses. The web layer adds zero audit logic, so the browser
  and the terminal can never disagree about a result.
- `GET /` serves the page; `GET /audit?url=…&sample=N` runs one audit and returns the same JSON
  shape as `python agent_audit.py <url> --json`. The only content the web layer adds is a
  plain-English "what this check looks for" sentence per check.
- It is threaded so a 20–40s audit does not freeze the page, and so check #3's Playwright
  (synchronous API) runs in a worker thread with no asyncio loop to fight.

The web sampling default is `--sample 5` (snappier than the CLI's 10); a `?sample=N` query
parameter overrides it, capped at 25.

## Notes

- **Local by default.** It binds `127.0.0.1`. It has no authentication and runs an audit for any
  URL submitted — keep it on localhost unless you add your own access controls.
- **One unreachable-site case.** If the homepage cannot be fetched, the page shows a clear error
  instead of results — the same condition that makes the CLI exit `2`. Everything else degrades
  to `unknown` rather than failing the run.
- Same troubleshooting applies as for the CLI — see [common issues](../troubleshooting/common-issues.md),
  especially the check #3 render notes.
