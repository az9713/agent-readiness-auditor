#!/usr/bin/env python3
"""Agent Readiness Auditor — local web UI.

A single-file, stdlib-only web front-end over agent_audit.py. Enter a URL,
the existing auditor runs, and the Tier-A facts + Tier-B proxy signals are
shown grouped, each with the live finding AND a plain-English explanation.

    python webapp.py            # serves http://127.0.0.1:8000
    python webapp.py --port 9000

ponytail: stdlib http.server, not Flask — one endpoint + one page doesn't
earn a framework or a new dependency. ThreadingHTTPServer so a 20s audit
doesn't freeze the page, and so Playwright's sync API (check #3) runs in a
worker thread with no asyncio loop fighting it.
"""
import argparse
import datetime
import ipaddress
import json
import os
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import agent_audit as audit

# ---------------------------------------------------------------------------
# Plain-English "what this check looks for" — the one thing the CLI lacks.
# Keyed by check id. The auditor's own `detail` explains the *finding*; this
# explains the *check*. Kept here (not in agent_audit.py) so the audit core
# stays presentation-free.
# ---------------------------------------------------------------------------
EXPLAIN = {
    # Tier-A facts
    1:  "A /llms.txt file is a curated map of the site written for AI. Present = the site deliberately guides agents.",
    11: "JSON-LD / microdata on the homepage lets an agent read entities (organisation, product, article) instead of guessing from prose.",
    14: "Whether structured data appears across many sampled pages, not just the homepage — i.e. is it site-wide or a one-off.",
    6:  "Does robots.txt name specific AI crawlers (GPTBot, ClaudeBot, …)? Naming them means the site has an explicit position on AI access.",
    7:  "For each named AI bot, whether it is allowed, partially restricted, or fully blocked.",
    18: "datePublished / dateModified in a machine-readable form, so an agent knows how fresh the content is.",
    19: "HTTP Last-Modified / ETag validators — let an agent cache a page and cheaply re-check whether it changed.",
    20: "A declared canonical URL removes duplicate-URL ambiguity, so an agent knows the one true address for a page.",
    21: "Cache-Control / Expires tell an agent how long a response may be reused before re-fetching.",
    2:  "A machine-readable list of the site's URLs (often with last-modified dates) — the front door for systematic crawling.",
    3:  "How much content is in the raw HTML versus only after a browser runs JavaScript. High = a simple fetch already sees the page.",
    12: "OpenGraph (og:) meta tags give a clean title / description / image — the share-card metadata agents reuse.",
    # Tier-B proxy signals
    4:  "A markdown / plain-text version of the content (content negotiation, /llms-full.txt, or an alternate link) an agent can read without HTML noise.",
    5:  "An OpenAPI / Swagger spec at a common path — a machine-readable contract for programmatic access.",
    9:  "A machine-readable statement of automated-use terms (/.well-known/tdmrep.json or a licence link), rather than terms buried in prose.",
    10: "Served via a CDN (Cloudflare, Fastly, …) that can offer bot-management or pay-per-crawl. This is capability, not confirmation it is switched on.",
    13: "A catalogue an agent can read: /products.json, an RSS/Atom feed, or Product structured data.",
    15: "JSON-LD Offer carrying price / availability — an agent can read the price and stock for an item directly.",
    16: "A CAPTCHA / bot-wall vendor on the page. A detected barrier is the one Tier-B ❌ — it actively impedes agent automation.",
    17: "Whether the site publicly declares an agent-commerce protocol (A2A, AP2, UCP, x402).",
    23: "A declared content-licensing or AI-access programme (tdmrep.json, TollBit, ScalePost, …).",
    24: "A machine-readable paywall marker (isAccessibleForFree:false or a paywall vendor) signalling the content is gated.",
}
# Guard: every check must have an explanation, or the UI would show a blank.
assert set(EXPLAIN) == {c[0] for c in audit.CHECKS}, "EXPLAIN out of sync with CHECKS"

SYMBOL = {audit.PASS: "✅", audit.FAIL: "❌", audit.UNKNOWN: "—"}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Readiness Auditor</title>
<style>
  :root { --bg:#0f1115; --card:#191c23; --line:#2a2f3a; --fg:#e6e9ef; --mut:#9aa3b2;
          --pass:#3fb950; --fail:#f85149; --unk:#8b949e; --accent:#58a6ff; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
         font:15px/1.55 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
  .wrap { max-width:880px; margin:0 auto; padding:32px 20px 80px; }
  h1 { font-size:24px; margin:0 0 4px; }
  .sub { color:var(--mut); margin:0 0 24px; }
  form { display:flex; gap:8px; margin-bottom:8px; }
  input[type=text] { flex:1; padding:11px 13px; border:1px solid var(--line); border-radius:8px;
                    background:var(--card); color:var(--fg); font-size:15px; }
  input[type=text]:focus { outline:none; border-color:var(--accent); }
  button { padding:11px 18px; border:0; border-radius:8px; background:var(--accent);
           color:#06223f; font-weight:600; font-size:15px; cursor:pointer; }
  button:disabled { opacity:.55; cursor:default; }
  .hint { color:var(--mut); font-size:13px; margin:0 0 24px; }
  .tally { display:flex; flex-wrap:wrap; gap:8px 16px; margin:18px 0 6px; color:var(--mut); font-size:14px; }
  .tally b { color:var(--fg); font-weight:600; }
  h2 { font-size:14px; text-transform:uppercase; letter-spacing:.06em; color:var(--mut);
       margin:28px 0 10px; border-bottom:1px solid var(--line); padding-bottom:6px; }
  .grp { margin:18px 0 6px; font-weight:600; color:var(--accent); font-size:14px; }
  .row { background:var(--card); border:1px solid var(--line); border-radius:10px;
         padding:12px 14px; margin:8px 0; }
  .row .top { display:flex; gap:10px; align-items:baseline; }
  .sym { font-size:16px; width:22px; flex:none; text-align:center; }
  .nm { font-weight:600; }
  .id { color:var(--mut); font-size:12px; }
  .detail { margin:4px 0 0 32px; }
  .pass .detail { color:var(--pass); } .fail .detail { color:var(--fail); } .unknown .detail { color:var(--unk); }
  .why { margin:6px 0 0 32px; color:var(--mut); font-size:13px; }
  .note { background:#1b222e; border:1px solid var(--line); border-radius:8px; color:var(--mut);
          padding:10px 13px; font-size:13px; margin:10px 0 0; }
  .err { color:var(--fail); background:var(--card); border:1px solid var(--fail);
         border-radius:8px; padding:12px 14px; }
  #status { color:var(--mut); margin:18px 0; }
  .meta { color:var(--mut); font-size:12px; margin-top:6px; }
  a { color:var(--accent); }
</style>
</head>
<body>
<div class="wrap">
  <h1>Agent Readiness Auditor</h1>
  <p class="sub">How usable is a website to an AI agent — not to a human?</p>
  <form id="f">
    <input id="url" type="text" placeholder="example.com (scheme optional)" required autofocus>
    <button id="go" type="submit">Audit</button>
  </form>
  <p class="hint">Runs 12 Tier-A fact checks + 10 Tier-B proxy signals. A single audit takes ~15&ndash;40s
     (it fetches the homepage, robots.txt, sitemap, well-known files, and renders the page in a headless browser).</p>
  <div id="status"></div>
  <div id="out"></div>
</div>
<script>
const EXPLAIN = __EXPLAIN__;
const A_ORDER = __A_ORDER__;
const B_ORDER = __B_ORDER__;
const SYM = {pass:"✅", fail:"❌", unknown:"—"};

const f = document.getElementById('f'), urlIn = document.getElementById('url'),
      go = document.getElementById('go'), statusEl = document.getElementById('status'),
      out = document.getElementById('out');

f.addEventListener('submit', async (e) => {
  e.preventDefault();
  const url = urlIn.value.trim();
  if (!url) return;
  out.innerHTML = '';
  go.disabled = true;
  statusEl.textContent = 'Auditing ' + url + ' … (fetching + headless render, please wait)';
  try {
    const r = await fetch('/audit?url=' + encodeURIComponent(url));
    const data = await r.json();
    if (data.error) { render_error(data.error); }
    else { render(data); }
  } catch (err) {
    // A failed fetch (TypeError) almost always means the local server isn't running —
    // give that hint instead of the cryptic "Failed to fetch".
    const net = (err instanceof TypeError);
    render_error(net
      ? "Could not reach the auditor server. Is it still running? Start it with: python webapp.py"
      : String(err));
  } finally {
    go.disabled = false;
    statusEl.textContent = '';
  }
});

function esc(s){ const d=document.createElement('div'); d.textContent=s==null?'':s; return d.innerHTML; }

function render_error(msg){
  out.innerHTML = '<div class="err"><b>Could not audit this site.</b><br>' + esc(msg) + '</div>';
}

function rowHtml(c){
  return '<div class="row ' + c.status + '">' +
    '<div class="top"><span class="sym">' + SYM[c.status] + '</span>' +
    '<span class="nm">' + esc(c.name) + '</span> <span class="id">[#' + c.id + ']</span></div>' +
    '<div class="detail">' + esc(c.detail) + '</div>' +
    '<div class="why">' + esc(EXPLAIN[c.id]) + '</div></div>';
}

function tallyHtml(label, parts, legend){
  return '<div class="tally"><span>' + label + '</span>' +
    parts.map(p => '<b>' + p + '</b>').join('') + '</div>' +
    '<div class="meta">' + legend + '</div>';
}

function render(data){
  const byId = {}; data.checks.forEach(c => byId[c.id] = c);
  let html = '<div class="meta">Audited ' + esc(data.url) + ' &middot; ' + esc(data.audited_at) + '</div>';

  // Tier-A tally + groups
  const aParts = A_ORDER.map(g => g + ' ' + data.summary[g].pass + '/' + data.summary[g].total);
  html += tallyHtml('Tier-A facts', aParts,
      '✅ pass &middot; ❌ fail &middot; — unknown &mdash; verified facts, no blended score');
  html += '<h2>Tier-A facts</h2>';
  A_ORDER.forEach(g => {
    const grp = data.checks.filter(c => c.tier === 'A' && c.group === g);
    if (!grp.length) return;
    html += '<div class="grp">' + g + '</div>';
    grp.forEach(c => html += rowHtml(c));
  });

  // Tier-B tally + groups
  if (data.summary.signals){
    const bParts = Object.entries(data.summary.signals).map(([g,v]) => g + ' ' + v.found + '/' + v.probed);
    html += tallyHtml('Tier-B signals', bParts,
        '✅ signal found &middot; ❌ barrier detected &middot; — none visible');
    html += '<h2>Tier-B proxy signals</h2>';
    html += '<div class="note"><b>Read these as proxies, not facts.</b> A ✅ is a trustworthy positive ' +
            'signal. A — means nothing was visible from outside &mdash; it is <b>not</b> proof the site lacks the ' +
            'capability (it may use it privately, or expose it at a path we did not guess). Only #16 returns ' +
            '❌, because a detected bot-wall is a trustworthy <i>negative</i>.</div>';
    B_ORDER.forEach(g => {
      const grp = data.checks.filter(c => c.tier === 'B' && c.group === g);
      if (!grp.length) return;
      html += '<div class="grp">' + g + '</div>';
      grp.forEach(c => html += rowHtml(c));
    });
  }
  out.innerHTML = html;
}
</script>
</body>
</html>
"""


def render_page():
    """The single HTML page, with the static explanation/order data injected."""
    return (PAGE
            .replace("__EXPLAIN__", json.dumps(EXPLAIN))
            .replace("__A_ORDER__", json.dumps(audit.GROUP_ORDER))
            .replace("__B_ORDER__", json.dumps(audit.TIER_B_GROUP_ORDER)))


# ---------------------------------------------------------------------------
# SSRF guard — only enforced on the public demo (env PUBLIC_DEMO set). A public
# endpoint that fetches any URL a stranger submits is an SSRF vector: without
# this, someone points it at 169.254.169.254 (cloud metadata) or 127.0.0.1 to
# reach internal services. Local CLI/web use is the operator auditing their own
# targets, so the guard stays off there.
# ponytail: this blocks DIRECT private targets (the common attack). It does NOT
# re-check redirect hops — requests follows redirects, so a public host that 302s
# to 169.254.169.254 is the residual hole. Upgrade path if the demo sees abuse:
# a requests HTTPAdapter that re-validates every hop, or allow_redirects=False.
# ---------------------------------------------------------------------------
def _ip_is_blocked(ip):
    """True if an IP must never be fetched from the public demo. Pure (no DNS) — unit-tested."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return True  # unparseable → block
    if addr.version == 6 and addr.ipv4_mapped is not None:
        return _ip_is_blocked(str(addr.ipv4_mapped))  # ::ffff:127.0.0.1 etc.
    return (addr.is_private or addr.is_loopback or addr.is_link_local
            or addr.is_reserved or addr.is_multicast or addr.is_unspecified)


def reject_if_unsafe(url):
    """Raise ValueError unless url is a public http(s) target. SSRF guard for the demo."""
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        raise ValueError(f"only http/https URLs are allowed (got '{p.scheme or 'none'}')")
    host = p.hostname
    if not host:
        raise ValueError("no host in URL")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise ValueError(f"could not resolve host: {e}")
    for info in infos:
        if _ip_is_blocked(info[4][0]):
            raise ValueError("refusing to audit a private, loopback, or link-local address")


def run_audit(url, sample):
    """Run the existing auditor and return the same JSON shape the CLI's --json emits."""
    if "://" not in url:
        url = "https://" + url
    if os.environ.get("PUBLIC_DEMO"):
        reject_if_unsafe(url)  # raises ValueError on private/loopback/non-http targets
    ctx = audit.fetch_context(url, sample=sample)          # may raise ConnectionError
    results = audit.run_checks(ctx)
    summary = audit.summarize(results)
    return {
        "url": ctx.home.final_url or url,
        "audited_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "checks": results,
        "summary": summary,
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parts = urlparse(self.path)
        if parts.path == "/":
            self._send(200, render_page(), "text/html")
            return
        if parts.path == "/audit":
            q = parse_qs(parts.query)
            url = (q.get("url") or [""])[0].strip()
            if not url:
                self._send(400, json.dumps({"error": "missing ?url="}), "application/json")
                return
            try:
                sample = int((q.get("sample") or ["5"])[0])  # default 5: snappier than CLI's 10
            except ValueError:
                sample = 5
            try:
                payload = run_audit(url, sample=max(0, min(sample, 25)))
                self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")
            except ValueError as e:
                # SSRF guard / bad input rejection — show the reason, don't audit.
                self._send(200, json.dumps({"error": str(e)}), "application/json")
            except ConnectionError as e:
                # Site unreachable is the auditor's one expected failure — report, don't 500.
                self._send(200, json.dumps({"error": str(e)}), "application/json")
            except Exception as e:  # noqa: BLE001 — a crash must return JSON the page can show, not hang
                self._send(200, json.dumps({"error": f"audit failed: {e}"}), "application/json")
            return
        self._send(404, json.dumps({"error": "not found"}), "application/json")

    def log_message(self, format, *args):  # noqa: A002 — name fixed by base class
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Local web UI for the Agent Readiness Auditor")
    # Defaults come from env so a host (Render/Railway/Fly) can set PORT and HOST=0.0.0.0
    # without CLI args. Local default stays 127.0.0.1 — bind public only when you mean to.
    ap.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    args = ap.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    demo = " [PUBLIC_DEMO: SSRF guard on]" if os.environ.get("PUBLIC_DEMO") else ""
    print(f"Agent Readiness Auditor — http://{args.host}:{args.port}{demo}  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure:
        try:
            reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass
    sys.exit(main())
