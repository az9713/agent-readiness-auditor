#!/usr/bin/env python3
"""Agent Readiness Auditor — v1 (12 Tier-A checks).

Audits ONE url for how usable it is to AI agents. Deterministic checks only:
each is one fetch or one parse -> a clear pass/fail. No scoring, just a
three-state checklist (pass / fail / unknown) grouped by Read/Trust/Freshness/
Discovery. See agent-readiness-auditor.md Section 8 for the design.

Usage:
    python agent_audit.py https://example.com
    python agent_audit.py example.com --json
    python agent_audit.py https://example.com --sample 5
"""
import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import defusedxml.ElementTree as DET  # hardened against XXE / entity-expansion bombs

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TIMEOUT = 15  # ponytail: flat 15s per fetch; make per-check if a site needs it
USER_AGENT = "AgentReadinessAuditor/0.1 (+https://github.com/agent-audit)"
DEFAULT_SAMPLE = 10
JS_TEXT_PASS_RATIO = 0.60  # raw text must be >=60% of rendered text to pass check 3

# Known AI/agent crawler user-agents (lowercased). Easy to extend.
AI_USER_AGENTS = [
    "gptbot", "oai-searchbot", "chatgpt-user", "claudebot", "claude-web",
    "anthropic-ai", "google-extended", "perplexitybot", "ccbot", "bytespider",
    "amazonbot", "applebot-extended", "meta-externalagent", "cohere-ai", "diffbot",
]

PASS, FAIL, UNKNOWN = "pass", "fail", "unknown"
SYMBOL = {PASS: "✅", FAIL: "❌", UNKNOWN: "—"}

READ, TRUST, FRESH, DISC = "Read", "Trust", "Freshness", "Discovery"   # Tier-A dimensions
DOCS, PERMS, COMMERCE, MON = "Docs", "Permissions", "Commerce", "Monetization"  # Tier-B dimensions

# Agent-commerce protocol discovery (Tier-B: a positive hit is a real signal; silence is not proof).
WELLKNOWN_AGENT_CARD = ".well-known/agent-card.json"
WELLKNOWN_AGENT_CARD_LEGACY = ".well-known/agent.json"
WELLKNOWN_UCP = ".well-known/ucp"
AP2_EXTENSION_MARKER = "google-agentic-commerce/ap2"  # version-agnostic substring of the AP2 extension URI

# Tier-B marker tables (substrings matched case-insensitively in raw HTML).
CAPTCHA_MARKERS = {
    "reCAPTCHA": ("recaptcha",),
    "hCaptcha": ("hcaptcha",),
    "Turnstile": ("turnstile",),
    "Arkose/FunCaptcha": ("arkoselabs", "funcaptcha"),
    "GeeTest": ("geetest",),
    "DataDome": ("datadome",),
    "PerimeterX/HUMAN": ("perimeterx", "human-challenge"),
}
PAYWALL_VENDORS = ("piano.io", "tinypass", "poool", "pelcro", "pico.tools", "memberful")
AI_ACCESS_PROVIDERS = ("tollbit", "scalepost", "prorata", "rslcollective",
                       "really simple licensing", "cloudflare ai audit")
OFFER_KEYS = ("offers", "price", "pricecurrency", "availability", "lowprice", "highprice")


# ===========================================================================
# Pure parsing helpers  (no network — unit-tested offline in test_auditor.py)
# ===========================================================================
def parse_robots(text):
    """Parse robots.txt into {'groups': {agent: {allow:[], disallow:[]}}, 'sitemaps': []}."""
    groups, sitemaps, current, last_was_agent = {}, [], [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field_name, value = line.split(":", 1)
        field_name, value = field_name.strip().lower(), value.strip()
        if field_name == "user-agent":
            if not last_was_agent:
                current = []
            current.append(value.lower())
            groups.setdefault(value.lower(), {"allow": [], "disallow": []})
            last_was_agent = True
        elif field_name in ("allow", "disallow"):
            for agent in current:
                groups[agent][field_name].append(value)
            last_was_agent = False
        elif field_name == "sitemap":
            sitemaps.append(value)
            last_was_agent = False
        else:
            last_was_agent = False
    return {"groups": groups, "sitemaps": sitemaps}


def robots_stance(rules):
    """Reduce one agent's rules to: blocked / partial / allowed."""
    disallow = [d for d in rules["disallow"] if d != ""]
    if any(d.strip() == "/" for d in disallow):
        return "blocked"
    if disallow or rules["allow"]:
        return "partial"
    return "allowed"  # named but unrestricted


def named_ai_agents(parsed):
    """Which known AI user-agents appear in a parsed robots.txt."""
    return [a for a in AI_USER_AGENTS if a in parsed["groups"]]


def _attr(tag, name):
    """Single string value of an attribute (bs4 returns a list for multi-valued attrs)."""
    v = tag.get(name)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def visible_text(html):
    """Human-visible text of an HTML string (scripts/styles stripped)."""
    soup = BeautifulSoup(html or "", "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)


def extract_structured_types(html):
    """All schema.org @type values from JSON-LD + microdata in an HTML string."""
    soup = BeautifulSoup(html or "", "lxml")
    types = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
        except (ValueError, TypeError):
            continue
        types.extend(_jsonld_types(data))
    for el in soup.find_all(attrs={"itemtype": True}):  # microdata
        it = _attr(el, "itemtype")
        if it:
            types.append(it.rstrip("/").rsplit("/", 1)[-1])
    return [t for t in types if t]


def _jsonld_types(data):
    """Recursively pull @type out of a parsed JSON-LD blob (handles @graph / lists)."""
    out = []
    if isinstance(data, list):
        for item in data:
            out.extend(_jsonld_types(item))
    elif isinstance(data, dict):
        t = data.get("@type")
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, list):
            out.extend(x for x in t if isinstance(x, str))
        if "@graph" in data:
            out.extend(_jsonld_types(data["@graph"]))
    return out


def extract_opengraph(html):
    """{og:property: content} from an HTML string."""
    soup = BeautifulSoup(html or "", "lxml")
    og = {}
    for meta in soup.find_all("meta"):
        prop = _attr(meta, "property") or ""
        content = _attr(meta, "content")
        if prop.startswith("og:") and content:
            og[prop] = content
    return og


def extract_dates(html):
    """Machine-readable publish/modify dates from an HTML string."""
    soup = BeautifulSoup(html or "", "lxml")
    found = []
    for meta in soup.find_all("meta"):
        key = (_attr(meta, "property") or _attr(meta, "name") or _attr(meta, "itemprop") or "")
        content = _attr(meta, "content")
        if key.lower() in ("article:published_time", "article:modified_time",
                            "date", "datepublished", "datemodified") and content:
            found.append(content)
    for t in soup.find_all("time"):
        dt = _attr(t, "datetime")
        if dt:
            found.append(dt)
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            blob = json.loads(script.string or "")
        except (ValueError, TypeError):
            continue
        found.extend(_jsonld_dates(blob))
    return found


def _jsonld_dates(data):
    out = []
    if isinstance(data, list):
        for item in data:
            out.extend(_jsonld_dates(item))
    elif isinstance(data, dict):
        for k in ("datePublished", "dateModified"):
            if isinstance(data.get(k), str):
                out.append(data[k])
        if "@graph" in data:
            out.extend(_jsonld_dates(data["@graph"]))
    return out


def extract_canonical(html, link_header=""):
    """Canonical URL from <link rel=canonical> or a Link: response header."""
    soup = BeautifulSoup(html or "", "lxml")
    for link in soup.find_all("link"):
        rel = link.get("rel") or []
        rel = [rel] if isinstance(rel, str) else rel
        if any(r.lower() == "canonical" for r in rel):
            href = _attr(link, "href")
            if href:
                return href
    m = re.search(r'<([^>]+)>\s*;\s*rel="?canonical"?', link_header or "")
    return m.group(1) if m else None


def llms_wellformed(text):
    """Loose llms.txt sanity: non-empty and has a markdown H1."""
    if not text or not text.strip():
        return False
    return any(re.match(r"#\s+\S", line) for line in text.splitlines())


def parse_sitemap_xml(xml_text):
    """Return (kind, locs) where kind is 'urlset'|'sitemapindex'|None.

    locs is a list of (loc, lastmod-or-None).
    """
    try:
        root = DET.fromstring(xml_text)
    except Exception:  # ponytail: any parse failure (malformed OR a forbidden entity bomb) -> "no usable sitemap", never crash the audit
        return None, []
    tag = root.tag.rsplit("}", 1)[-1]  # strip namespace
    if tag not in ("urlset", "sitemapindex"):
        return None, []
    locs = []
    for child in root:
        loc = lastmod = None
        for sub in child:
            name = sub.tag.rsplit("}", 1)[-1]
            if name == "loc":
                loc = (sub.text or "").strip()
            elif name == "lastmod":
                lastmod = (sub.text or "").strip()
        if loc:
            locs.append((loc, lastmod))
    return tag, locs


def detect_protocols(agent_card_text, agent_card_ok, ucp_text, ucp_ok, home_status, home_headers):
    """Which agent-commerce protocols a site PUBLICLY declares. Tier-B, positive-only.

    Returns a list like ['A2A', 'AP2', 'UCP']. An empty list means nothing was visible
    from the outside — NOT proof the site cannot transact. A site can run ACP (OpenAI/
    Stripe) or onboard payments through a platform and declare nothing on its own domain.
    """
    found = []
    card = None
    if agent_card_ok:
        try:
            card = json.loads(agent_card_text)
        except (ValueError, TypeError):
            card = None
    if isinstance(card, dict):  # a valid agent card IS the A2A signal
        found.append("A2A")
        extensions = (card.get("capabilities") or {}).get("extensions") or []
        uris = []
        for ext in extensions:
            if isinstance(ext, dict) and ext.get("uri"):
                uris.append(ext["uri"])
            elif isinstance(ext, str):
                uris.append(ext)
        if any(AP2_EXTENSION_MARKER in u for u in uris):
            found.append("AP2")
    if ucp_ok:
        try:
            json.loads(ucp_text)
            found.append("UCP")
        except (ValueError, TypeError):
            pass
    headers = home_headers or {}
    # x402: best-effort only — a true probe needs a paid endpoint; we can catch a 402 if the
    # homepage itself returns one. ponytail: cheap opportunistic check, not a full x402 client.
    if home_status == 402 or any(k.lower() == "payment-required" for k in headers):
        found.append("x402")
    return found


def _header(headers, name):
    """Case-insensitive header lookup; '' if absent."""
    for k, v in (headers or {}).items():
        if k.lower() == name.lower():
            return v or ""
    return ""


def find_markdown_alternative(html):
    """True if the page links a markdown / plain-text alternate version."""
    soup = BeautifulSoup(html or "", "lxml")
    for link in soup.find_all("link"):
        rel = link.get("rel") or []
        rel = [rel] if isinstance(rel, str) else rel
        if not any(r.lower() == "alternate" for r in rel):
            continue
        typ = (_attr(link, "type") or "").lower()
        href = (_attr(link, "href") or "").lower()
        if "markdown" in typ or typ == "text/plain" or href.endswith(".md"):
            return True
    return False


def has_feed_alternate(html):
    """True if the page links an RSS/Atom feed alternate."""
    soup = BeautifulSoup(html or "", "lxml")
    for link in soup.find_all("link"):
        rel = link.get("rel") or []
        rel = [rel] if isinstance(rel, str) else rel
        if not any(r.lower() == "alternate" for r in rel):
            continue
        typ = (_attr(link, "type") or "").lower()
        if "rss" in typ or "atom" in typ:
            return True
    return False


def extract_license(html):
    """A label for a machine-readable licence declaration, or None."""
    soup = BeautifulSoup(html or "", "lxml")
    for link in soup.find_all("link"):
        rel = link.get("rel") or []
        rel = [rel] if isinstance(rel, str) else rel
        if any(r.lower() == "license" for r in rel) and _attr(link, "href"):
            return "<link rel=license>"
    for meta in soup.find_all("meta"):
        key = (_attr(meta, "property") or _attr(meta, "name") or "").lower()
        if key in ("license", "dc.rights", "dcterms.license") and _attr(meta, "content"):
            return f"meta {key}"
    return None


def extract_offer_signals(html):
    """Tokens indicating machine-readable price/stock (JSON-LD Offer / price / availability)."""
    soup = BeautifulSoup(html or "", "lxml")
    found = set()
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            blob = json.loads(script.string or "")
        except (ValueError, TypeError):
            continue
        _walk_offers(blob, found)
    return sorted(found)


def _walk_offers(data, found):
    if isinstance(data, list):
        for it in data:
            _walk_offers(it, found)
    elif isinstance(data, dict):
        t = data.get("@type")
        types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
        if any(isinstance(tv, str) and tv.lower() in ("offer", "aggregateoffer") for tv in types):
            found.add("Offer")
        for k in data:
            if k.lower() in OFFER_KEYS:
                found.add(k)
        for v in data.values():
            _walk_offers(v, found)


def detect_captcha(html):
    """Names of CAPTCHA / bot-wall vendors referenced in the page."""
    low = (html or "").lower()
    return [name for name, needles in CAPTCHA_MARKERS.items() if any(n in low for n in needles)]


def detect_paywall(html):
    """Machine-readable paywall markers found in the page."""
    soup = BeautifulSoup(html or "", "lxml")
    markers = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            blob = json.loads(script.string or "")
        except (ValueError, TypeError):
            continue
        if _has_paywalled_flag(blob):
            markers.append("isAccessibleForFree:false")
            break
    for meta in soup.find_all("meta"):
        key = (_attr(meta, "property") or _attr(meta, "name") or "").lower()
        val = (_attr(meta, "content") or "").lower()
        if "content_tier" in key and val in ("locked", "metered"):
            markers.append(f"content_tier:{val}")
    low = (html or "").lower()
    markers.extend(v for v in PAYWALL_VENDORS if v in low)
    return markers


def _has_paywalled_flag(data):
    if isinstance(data, list):
        return any(_has_paywalled_flag(x) for x in data)
    if isinstance(data, dict):
        if data.get("isAccessibleForFree") in (False, "False", "false"):
            return True
        return any(_has_paywalled_flag(x) for x in data.values())
    return False


def detect_cdn(headers):
    """Name of a CDN / bot-management layer inferred from response headers, or None."""
    h = {k.lower(): (v or "").lower() for k, v in (headers or {}).items()}
    server = h.get("server", "")
    if "cf-ray" in h or "cf-cache-status" in h or "cloudflare" in server:
        return "Cloudflare"
    if "fastly" in (h.get("x-served-by", "") + h.get("via", "")):
        return "Fastly"
    if "x-amz-cf-id" in h or "cloudfront" in server:
        return "CloudFront"
    if any(k.startswith("x-akamai") for k in h) or "akamai" in server:
        return "Akamai"
    if "x-vercel-id" in h:
        return "Vercel"
    return None


# ===========================================================================
# Network layer
# ===========================================================================
@dataclass
class Resource:
    status: int | None = None
    text: str = ""
    headers: dict = field(default_factory=dict)
    final_url: str = ""
    error: str = ""


@dataclass
class Context:
    base_url: str
    home: Resource
    home_text: str = ""
    rendered_text: str | None = None
    rendered_error: str = ""
    robots: Resource = field(default_factory=Resource)
    robots_parsed: dict = field(default_factory=lambda: {"groups": {}, "sitemaps": []})
    sitemap: Resource = field(default_factory=Resource)
    sitemap_kind: str | None = None
    sitemap_locs: list = field(default_factory=list)
    llms: Resource = field(default_factory=Resource)
    agent_card: Resource = field(default_factory=Resource)  # A2A / AP2 discovery
    ucp: Resource = field(default_factory=Resource)          # UCP discovery
    md_probe: Resource = field(default_factory=Resource)     # content-negotiation for markdown
    llms_full: Resource = field(default_factory=Resource)    # /llms-full.txt
    openapi: Resource = field(default_factory=Resource)      # public API spec
    tdmrep: Resource = field(default_factory=Resource)       # /.well-known/tdmrep.json
    products_json: Resource = field(default_factory=Resource)  # Shopify-style product feed
    samples: list = field(default_factory=list)  # [(url, html)]


def fetch(url, accept=None):
    """GET a url; never raise — return a Resource (status None on transport error)."""
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=headers, allow_redirects=True)
        return Resource(status=r.status_code, text=r.text, headers=dict(r.headers),
                        final_url=r.url)
    except requests.RequestException as e:
        return Resource(error=str(e))


def fetch_first(urls):
    """Fetch each url until one returns 200; return that Resource (or the last attempt)."""
    last = Resource(status=404)
    for u in urls:
        r = fetch(u)
        if r.status == 200:
            return r
        last = r
    return last


def render_text(url):
    """Playwright-rendered visible text, or (None, error)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        return None, f"playwright not installed: {e}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(user_agent=USER_AGENT)
            # domcontentloaded is reliable and fast; then give client-side JS a moment to
            # render. ponytail: don't wait for networkidle as the goto condition — ad/
            # analytics/websocket traffic on heavy sites never settles, so it would time out
            # and return nothing. Instead best-effort-wait for idle, capture whatever rendered.
            page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT * 1000)
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass  # network never idled — fine, capture the text rendered so far
            text = page.inner_text("body")
            browser.close()
            return text, ""
    except Exception as e:  # noqa: BLE001 — Playwright raises many types; treat all as render failure
        return None, str(e)


def root_of(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def fetch_context(base_url, sample=DEFAULT_SAMPLE):
    home = fetch(base_url)
    if home.status is None:
        raise ConnectionError(f"could not reach {base_url}: {home.error}")
    root = root_of(home.final_url or base_url)

    ctx = Context(base_url=base_url, home=home)
    ctx.home_text = visible_text(home.text)
    ctx.rendered_text, ctx.rendered_error = render_text(home.final_url or base_url)

    ctx.robots = fetch(urljoin(root + "/", "robots.txt"))
    if ctx.robots.status == 200:
        ctx.robots_parsed = parse_robots(ctx.robots.text)

    # sitemap: prefer one declared in robots, else /sitemap.xml
    sitemap_url = (ctx.robots_parsed["sitemaps"] or [urljoin(root + "/", "sitemap.xml")])[0]
    ctx.sitemap = fetch(sitemap_url)
    if ctx.sitemap.status == 200:
        ctx.sitemap_kind, ctx.sitemap_locs = parse_sitemap_xml(ctx.sitemap.text)

    ctx.llms = fetch(urljoin(root + "/", "llms.txt"))

    # agent-commerce protocol discovery (check 17, Tier-B)
    ctx.agent_card = fetch(urljoin(root + "/", WELLKNOWN_AGENT_CARD))
    if ctx.agent_card.status != 200:
        ctx.agent_card = fetch(urljoin(root + "/", WELLKNOWN_AGENT_CARD_LEGACY))
    ctx.ucp = fetch(urljoin(root + "/", WELLKNOWN_UCP))

    # remaining Tier-B proxy resources
    ctx.md_probe = fetch(home.final_url or base_url, accept="text/markdown")   # check 4
    ctx.llms_full = fetch(urljoin(root + "/", "llms-full.txt"))                 # check 4
    ctx.openapi = fetch_first([urljoin(root + "/", p) for p in                  # check 5
                               ("openapi.json", ".well-known/openapi.json", "swagger.json")])
    ctx.tdmrep = fetch(urljoin(root + "/", ".well-known/tdmrep.json"))          # checks 9, 23
    ctx.products_json = fetch(urljoin(root + "/", "products.json"))             # check 13

    # sampling for coverage (check 14)
    page_urls = _sample_page_urls(ctx, sample)
    for u in page_urls:
        r = fetch(u)
        if r.status == 200:
            ctx.samples.append((u, r.text))
    return ctx


def _sample_page_urls(ctx, sample):
    """Up to `sample` content-page URLs from the sitemap (follows one index level)."""
    if ctx.sitemap_kind == "urlset":
        return [loc for loc, _ in ctx.sitemap_locs[:sample]]
    if ctx.sitemap_kind == "sitemapindex" and ctx.sitemap_locs:
        child = fetch(ctx.sitemap_locs[0][0])
        if child.status == 200:
            _, locs = parse_sitemap_xml(child.text)
            return [loc for loc, _ in locs[:sample]]
    return []  # check 14 falls back to homepage-only


# ===========================================================================
# Checks  (each returns (status, detail))
# ===========================================================================
def check_1(ctx):  # llms.txt present
    if ctx.llms.status == 200 and ctx.llms.text.strip():
        note = "valid markdown" if llms_wellformed(ctx.llms.text) else "present, no H1"
        return PASS, f"/llms.txt found ({note})"
    return FAIL, "no /llms.txt"


def check_2(ctx):  # sitemap present & current
    if ctx.sitemap_kind in ("urlset", "sitemapindex"):
        lastmods = [lm for _, lm in ctx.sitemap_locs if lm]
        freshest = max(lastmods) if lastmods else "no lastmod dates"
        return PASS, f"{ctx.sitemap_kind}, {len(ctx.sitemap_locs)} entries, freshest: {freshest}"
    if ctx.sitemap.status is None:
        return UNKNOWN, f"sitemap fetch failed: {ctx.sitemap.error}"
    return FAIL, "no parseable sitemap.xml"


def check_3(ctx):  # content readable without JS
    if ctx.rendered_text is None:
        return UNKNOWN, f"could not render: {ctx.rendered_error}"
    rendered = len(ctx.rendered_text.strip())
    raw = len(ctx.home_text.strip())
    if rendered == 0:
        return UNKNOWN, "rendered page had no text"
    ratio = raw / rendered
    if ratio >= JS_TEXT_PASS_RATIO:
        return PASS, f"raw text is {ratio:.0%} of rendered — readable without JS"
    return FAIL, f"raw text only {ratio:.0%} of rendered — content needs JavaScript"


def check_6(ctx):  # explicit AI-bot policy
    if ctx.robots.status != 200:
        return FAIL, "no robots.txt"
    named = named_ai_agents(ctx.robots_parsed)
    if named:
        return PASS, f"names {len(named)} AI bot(s): {', '.join(named)}"
    return FAIL, "robots.txt present but names no AI bots"


def check_7(ctx):  # allow/block stance
    named = named_ai_agents(ctx.robots_parsed)
    if not named:
        return FAIL, "no AI bots named to have a stance"
    parts = [f"{a}: {robots_stance(ctx.robots_parsed['groups'][a])}" for a in named]
    return PASS, "; ".join(parts)


def check_11(ctx):  # structured data on homepage
    types = extract_structured_types(ctx.home.text)
    if types:
        uniq = sorted(set(types))
        return PASS, f"{len(types)} block(s): {', '.join(uniq)}"
    return FAIL, "no JSON-LD or microdata"


def check_12(ctx):  # OpenGraph
    og = extract_opengraph(ctx.home.text)
    if "og:title" in og:
        return PASS, f"{len(og)} og: tag(s) incl. og:title"
    return FAIL, "no og:title"


def check_14(ctx):  # structured-data coverage
    if not ctx.samples:
        types = extract_structured_types(ctx.home.text)
        status = PASS if types else FAIL
        return status, "no sitemap — homepage only: " + ("has data" if types else "no data")
    hits = sum(1 for _, html in ctx.samples if extract_structured_types(html))
    total = len(ctx.samples)
    status = PASS if hits else FAIL
    return status, f"{hits}/{total} sampled pages carry structured data"


def check_18(ctx):  # machine-readable dates
    dates = extract_dates(ctx.home.text)
    if dates:
        return PASS, f"found: {dates[0]}" + (f" (+{len(dates)-1} more)" if len(dates) > 1 else "")
    return FAIL, "no machine-readable dates"


def check_19(ctx):  # Last-Modified / ETag headers
    h = {k.lower(): v for k, v in ctx.home.headers.items()}
    present = [name for name in ("last-modified", "etag") if name in h]
    if present:
        return PASS, ", ".join(present)
    return FAIL, "neither Last-Modified nor ETag"


def check_20(ctx):  # canonical URL
    canon = extract_canonical(ctx.home.text, ctx.home.headers.get("Link", ""))
    if canon:
        return PASS, canon
    return FAIL, "no rel=canonical"


def check_21(ctx):  # cache headers
    h = {k.lower(): v for k, v in ctx.home.headers.items()}
    present = [name for name in ("cache-control", "expires") if name in h]
    if present:
        return PASS, ", ".join(present)
    return FAIL, "no Cache-Control or Expires"


def check_17(ctx):  # agent-commerce protocol — Tier-B proxy (positive-only)
    found = detect_protocols(
        ctx.agent_card.text, ctx.agent_card.status == 200,
        ctx.ucp.text, ctx.ucp.status == 200,
        ctx.home.status, ctx.home.headers,
    )
    if found:
        return PASS, "declares: " + ", ".join(found)
    # Tier-B honesty: absence of a signal is UNKNOWN, never FAIL.
    return UNKNOWN, ("no public agent-commerce protocol found "
                     "(a site can still use ACP or onboard via a platform — not visible from outside)")


# --- remaining Tier-B proxies. Honesty rule: ✅ only on a trustworthy positive signal; absence is
#     — (unknown), never a fact. Exception: a detected barrier (#16) is a trustworthy NEGATIVE → ❌.

def check_4(ctx):  # clean text / markdown alternative — Docs
    sig = []
    if ctx.md_probe.status == 200 and "markdown" in _header(ctx.md_probe.headers, "Content-Type").lower():
        sig.append("content negotiation → markdown")
    if find_markdown_alternative(ctx.home.text):
        sig.append("<link rel=alternate markdown>")
    if ctx.llms_full.status == 200 and ctx.llms_full.text.strip():
        sig.append("/llms-full.txt")
    if sig:
        return PASS, "clean text version: " + "; ".join(sig)
    return UNKNOWN, "no machine-friendly text/markdown alternative detected (may exist at an unguessed path)"


def check_5(ctx):  # public API spec — Docs
    r = ctx.openapi
    if r.status == 200:
        try:
            spec = json.loads(r.text)
        except (ValueError, TypeError):
            spec = None
        if isinstance(spec, dict) and ("openapi" in spec or "swagger" in spec):
            ver = spec.get("openapi") or spec.get("swagger")
            return PASS, f"OpenAPI/Swagger spec found (version {ver})"
    return UNKNOWN, "no public API spec at common paths (an API may exist at an unguessed path)"


def check_9(ctx):  # automated-use licence / policy declared — Permissions
    sig = []
    if ctx.tdmrep.status == 200:
        sig.append("/.well-known/tdmrep.json (TDM reservation)")
    lic = extract_license(ctx.home.text)
    if lic:
        sig.append(lic)
    if sig:
        return PASS, "automated-use policy declared: " + "; ".join(sig)
    return UNKNOWN, "no machine-readable licence/TDM policy found (terms may exist only in prose)"


def check_10(ctx):  # CDN / pay-per-crawl capable — Permissions
    cdn = detect_cdn(ctx.home.headers)
    if cdn:
        return PASS, f"served via {cdn} (bot-management / pay-per-crawl capable; cannot confirm it is enabled)"
    return UNKNOWN, "no CDN / bot-management signal in response headers"


def check_13(ctx):  # machine-readable product feed — Commerce
    sig = []
    if ctx.products_json.status == 200:
        try:
            j = json.loads(ctx.products_json.text)
        except (ValueError, TypeError):
            j = None
        if isinstance(j, dict) and "products" in j:
            sig.append("/products.json")
    if has_feed_alternate(ctx.home.text):
        sig.append("RSS/Atom feed link")
    pages = [ctx.home.text] + [h for _, h in ctx.samples]
    if any("product" in [t.lower() for t in extract_structured_types(h)] for h in pages):
        sig.append("Product structured data")
    if sig:
        return PASS, "machine-readable product data: " + "; ".join(sig)
    return UNKNOWN, "no machine-readable product feed detected"


def check_15(ctx):  # machine-readable price / stock — Commerce
    for h in [ctx.home.text] + [html for _, html in ctx.samples]:
        offers = extract_offer_signals(h)
        if offers:
            return PASS, "machine-readable price/stock: " + ", ".join(offers)
    return UNKNOWN, "no machine-readable price/availability (Offer) data found"


def check_16(ctx):  # checkout bot-wall (CAPTCHA) — Commerce. Barrier detection → ❌ on a hit.
    vendors = detect_captcha(ctx.home.text)
    if vendors:
        return FAIL, ("bot-wall detected (" + ", ".join(vendors) +
                      ") — agent automation likely impeded; checkout pages not probed")
    return UNKNOWN, "no CAPTCHA/bot-wall on the homepage (other pages not probed)"


def check_23(ctx):  # content-licensing / AI-access program — Monetization
    sig = []
    if ctx.tdmrep.status == 200:
        sig.append("tdmrep.json")
    low = (ctx.home.text or "").lower()
    sig.extend(p for p in AI_ACCESS_PROVIDERS if p in low)
    if sig:
        return PASS, "content-licensing / AI-access signal: " + "; ".join(dict.fromkeys(sig))
    return UNKNOWN, "no content-licensing or AI-access program detected"


def check_24(ctx):  # machine-readable paywall — Monetization
    markers = detect_paywall(ctx.home.text)
    if markers:
        return PASS, ("machine-readable paywall markers: " + ", ".join(markers) +
                      " (cannot confirm authorised-agent access)")
    return UNKNOWN, "no machine-readable paywall markers found"


# Registry: (id, name, group, tier, fn). Tier A = deterministic fact; Tier B = proxy signal.
CHECKS = [
    (1, "llms.txt present", READ, "A", check_1),
    (11, "Structured data (homepage)", READ, "A", check_11),
    (14, "Structured-data coverage", READ, "A", check_14),
    (6, "Explicit AI-bot policy", TRUST, "A", check_6),
    (7, "AI-bot allow/block stance", TRUST, "A", check_7),
    (18, "Machine-readable dates", FRESH, "A", check_18),
    (19, "Last-Modified / ETag", FRESH, "A", check_19),
    (20, "Canonical URL", FRESH, "A", check_20),
    (21, "Cache headers", FRESH, "A", check_21),
    (2, "sitemap.xml present", DISC, "A", check_2),
    (3, "Readable without JavaScript", DISC, "A", check_3),
    (12, "OpenGraph tags", DISC, "A", check_12),
    # Tier-B proxies
    (4, "Clean text/markdown alternative", DOCS, "B", check_4),
    (5, "Public API spec", DOCS, "B", check_5),
    (9, "Automated-use licence/policy", PERMS, "B", check_9),
    (10, "CDN / pay-per-crawl capable", PERMS, "B", check_10),
    (13, "Machine-readable product feed", COMMERCE, "B", check_13),
    (15, "Machine-readable price/stock", COMMERCE, "B", check_15),
    (16, "Checkout bot-wall (CAPTCHA)", COMMERCE, "B", check_16),
    (17, "Agent-commerce protocol", COMMERCE, "B", check_17),
    (23, "Content-licensing / AI-access", MON, "B", check_23),
    (24, "Machine-readable paywall", MON, "B", check_24),
]
GROUP_ORDER = [READ, TRUST, FRESH, DISC]          # Tier-A groups, in print order
TIER_B_GROUP_ORDER = [DOCS, PERMS, COMMERCE, MON]  # Tier-B groups, in print order


# ===========================================================================
# Run + render
# ===========================================================================
def run_checks(ctx):
    results = []
    for cid, name, group, tier, fn in CHECKS:
        try:
            status, detail = fn(ctx)
        except Exception as e:  # noqa: BLE001 — a broken check must not sink the rest
            status, detail = UNKNOWN, f"check error: {e}"
        results.append({"id": cid, "name": name, "group": group, "tier": tier,
                        "status": status, "detail": detail})
    return results


def summarize(results):
    """Tier-A groups → pass/total fractions. Tier-B groups → found/probed signal counts.

    The two are kept separate, never blended into one number — a verified fact and a
    proxy signal don't belong in the same tally.
    """
    out = {}
    for g in GROUP_ORDER:  # Tier-A facts
        grp = [r for r in results if r["group"] == g and r["tier"] == "A"]
        out[g] = {"pass": sum(1 for r in grp if r["status"] == PASS), "total": len(grp)}
    btier = [r for r in results if r["tier"] == "B"]
    if btier:
        signals = {}
        for r in btier:
            s = signals.setdefault(r["group"], {"found": 0, "probed": 0})
            s["probed"] += 1
            if r["status"] == PASS:
                s["found"] += 1
        out["signals"] = signals
    return out


def render_text_report(url, results, summary):
    lines = [f"Agent Readiness — {url}", "=" * 60]
    for g in GROUP_ORDER:  # Tier-A facts
        grp = [r for r in results if r["group"] == g and r["tier"] == "A"]
        if not grp:
            continue
        lines.append(f"\n{g}")
        for r in grp:
            lines.append(f"  {SYMBOL[r['status']]} [{r['id']:>2}] {r['name']} — {r['detail']}")
    btier = [r for r in results if r["tier"] == "B"]
    if btier:
        lines.append("\nTier-B proxy signals  (✅ positive · ❌ barrier detected · — none visible — NOT proof of absence)")
        for g in TIER_B_GROUP_ORDER:
            grp = [r for r in btier if r["group"] == g]
            if not grp:
                continue
            lines.append(f"  {g}")
            for r in grp:
                lines.append(f"    {SYMBOL[r['status']]} [{r['id']:>2}] {r['name']} — {r['detail']}")
    lines.append("\n" + "-" * 60)
    tally = " · ".join(f"{g} {summary[g]['pass']}/{summary[g]['total']}" for g in GROUP_ORDER)
    lines.append("Tier-A facts   — " + tally + "   (✅ pass · ❌ fail · — unknown; no blended score)")
    if "signals" in summary:
        sig = " · ".join(f"{g} {v['found']}/{v['probed']}" for g, v in summary["signals"].items())
        lines.append("Tier-B signals — " + sig + "   (✅ found · ❌ barrier · — none visible; signals, not proof)")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Agent Readiness Auditor — 12 Tier-A fact checks + 10 Tier-B proxy signals")
    ap.add_argument("url", help="site to audit (scheme optional)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    ap.add_argument("--sample", type=int, default=DEFAULT_SAMPLE,
                    help=f"pages to sample for coverage (default {DEFAULT_SAMPLE})")
    args = ap.parse_args(argv)

    url = args.url if "://" in args.url else "https://" + args.url

    try:
        ctx = fetch_context(url, sample=args.sample)
    except ConnectionError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    results = run_checks(ctx)
    summary = summarize(results)

    if args.json:
        payload = {
            "url": ctx.home.final_url or url,
            "audited_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "checks": results,
            "summary": summary,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_text_report(ctx.home.final_url or url, results, summary))
    return 0


if __name__ == "__main__":
    reconfigure = getattr(sys.stdout, "reconfigure", None)  # so ✅/❌ survive legacy code pages
    if reconfigure:
        try:
            reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass
    sys.exit(main())
