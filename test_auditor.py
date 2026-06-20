#!/usr/bin/env python3
"""Offline tests for agent_audit.py. No network, no browser.

Run: python test_auditor.py     (plain asserts, exit code = pass/fail)
 or: pytest test_auditor.py      (test_* functions are pytest-discoverable too)

Two layers:
  1. Pure parsing helpers (robots, structured data, OpenGraph, dates, canonical,
     sitemap, llms.txt) — incl. an entity-bomb safety test.
  2. All 12 Tier-A check functions, driven by hand-built Context objects so each
     check's pass/fail/unknown logic is exercised without touching the network.
"""
import agent_audit as aa
from agent_audit import (
    parse_robots, robots_stance, named_ai_agents,
    extract_structured_types, extract_opengraph, extract_dates, extract_canonical,
    llms_wellformed, parse_sitemap_xml, visible_text, detect_protocols,
    find_markdown_alternative, extract_license, extract_offer_signals,
    detect_captcha, detect_paywall, detect_cdn,
)
from agent_audit import PASS, FAIL, UNKNOWN, Context, Resource

ROBOTS = """\
User-agent: *
Disallow: /private

User-agent: GPTBot
User-agent: CCBot
Disallow: /

User-agent: PerplexityBot
Disallow:

Sitemap: https://ex.com/sitemap.xml
"""


def test_robots():
    p = parse_robots(ROBOTS)
    assert "gptbot" in p["groups"] and "ccbot" in p["groups"], "AI agents not parsed"
    assert robots_stance(p["groups"]["gptbot"]) == "blocked", "GPTBot should be blocked"
    assert robots_stance(p["groups"]["ccbot"]) == "blocked", "shared block should apply to CCBot"
    assert robots_stance(p["groups"]["perplexitybot"]) == "allowed", "empty Disallow = allowed"
    assert robots_stance(p["groups"]["*"]) == "partial", "* has a partial disallow"
    assert p["sitemaps"] == ["https://ex.com/sitemap.xml"], "sitemap not captured"
    named = named_ai_agents(p)
    assert set(named) >= {"gptbot", "ccbot", "perplexitybot"}, f"named wrong: {named}"


def test_structured_data():
    html = """<html><head>
      <script type="application/ld+json">
        {"@context":"https://schema.org","@type":"Product","name":"X",
         "datePublished":"2026-01-02","offers":{"@type":"Offer","price":"9"}}
      </script></head>
      <body itemscope itemtype="https://schema.org/Organization"></body></html>"""
    types = extract_structured_types(html)
    assert "Product" in types, f"JSON-LD @type missing: {types}"
    assert "Organization" in types, f"microdata itemtype missing: {types}"
    assert extract_structured_types("<html></html>") == [], "empty page should have no types"


def test_jsonld_graph():
    html = """<script type="application/ld+json">
      {"@graph":[{"@type":"WebSite"},{"@type":["Article","NewsArticle"]}]}</script>"""
    types = extract_structured_types(html)
    assert {"WebSite", "Article", "NewsArticle"} <= set(types), f"@graph/list not flattened: {types}"


def test_opengraph():
    html = '<meta property="og:title" content="Hi"><meta property="og:image" content="x.png">'
    og = extract_opengraph(html)
    assert og.get("og:title") == "Hi", "og:title not extracted"
    assert "og:image" in og, "og:image not extracted"
    assert extract_opengraph("<meta name=description content=x>") == {}, "non-og picked up"


def test_dates():
    assert extract_dates('<meta property="article:modified_time" content="2026-06-01">'), \
        "meta date missed"
    assert extract_dates('<time datetime="2026-06-01">June</time>'), "<time> date missed"
    assert extract_dates('<script type="application/ld+json">{"dateModified":"2026-06-01"}</script>'), \
        "JSON-LD date missed"
    assert extract_dates("<p>no dates here</p>") == [], "false date positive"


def test_canonical():
    assert extract_canonical('<link rel="canonical" href="https://ex.com/a">') == "https://ex.com/a"
    assert extract_canonical("<html></html>", '<https://ex.com/b>; rel="canonical"') == "https://ex.com/b"
    assert extract_canonical("<html></html>") is None, "false canonical positive"


def test_llms():
    assert llms_wellformed("# My Site\n\n- [docs](/docs)"), "valid llms.txt rejected"
    assert not llms_wellformed("just text no heading"), "missing-H1 accepted"
    assert not llms_wellformed(""), "empty accepted"


def test_sitemap():
    xml = """<?xml version="1.0"?>
      <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://ex.com/a</loc><lastmod>2026-06-01</lastmod></url>
        <url><loc>https://ex.com/b</loc></url>
      </urlset>"""
    kind, locs = parse_sitemap_xml(xml)
    assert kind == "urlset", f"kind wrong: {kind}"
    assert locs[0] == ("https://ex.com/a", "2026-06-01"), f"loc/lastmod wrong: {locs[0]}"
    assert locs[1] == ("https://ex.com/b", None), "missing lastmod should be None"
    assert parse_sitemap_xml("<not xml") == (None, []), "garbage should not crash"


def test_billion_laughs_safe():
    """A classic entity-expansion bomb must be refused, not expanded."""
    bomb = """<?xml version="1.0"?>
      <!DOCTYPE lolz [
        <!ENTITY lol "lol">
        <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
        <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
      ]>
      <urlset><url><loc>&lol3;</loc></url></urlset>"""
    kind, _ = parse_sitemap_xml(bomb)  # defusedxml should reject -> (None, [])
    assert kind is None, "entity bomb was not refused"


def test_visible_text_strips_scripts():
    html = "<html><body>hello <script>var x=1</script><style>.a{}</style> world</body></html>"
    txt = visible_text(html)
    assert "hello" in txt and "world" in txt, "visible text lost"
    assert "var x" not in txt, "script text leaked into visible text"


# ===========================================================================
# Layer 2 — the 12 Tier-A check functions, driven by hand-built Context objects
# ===========================================================================
def make_ctx(*, home_html="", home_headers=None, home_text=None, rendered_text=None,
             llms_text=None, robots_text=None, robots_status=200,
             sitemap_kind=None, sitemap_locs=None, sitemap_status=200, samples=None,
             agent_card_text=None, ucp_text=None,
             md_content_type=None, llms_full_text=None, openapi_text=None,
             tdmrep_ok=False, products_json_text=None):
    """Build a Context with only the fields a check needs — no network, no browser."""
    home = Resource(status=200, text=home_html, headers=home_headers or {},
                    final_url="https://t.example/")
    ctx = Context(base_url="https://t.example", home=home)
    ctx.home_text = home_text if home_text is not None else visible_text(home_html)
    ctx.rendered_text = rendered_text
    if robots_text is not None:
        ctx.robots = Resource(status=robots_status, text=robots_text)
        ctx.robots_parsed = parse_robots(robots_text)
    else:
        ctx.robots = Resource(status=404)
    ctx.llms = Resource(status=200, text=llms_text) if llms_text is not None else Resource(status=404)
    ctx.sitemap = Resource(status=sitemap_status)
    ctx.sitemap_kind = sitemap_kind
    ctx.sitemap_locs = sitemap_locs or []
    ctx.samples = samples or []
    ctx.agent_card = Resource(status=200, text=agent_card_text) if agent_card_text is not None else Resource(status=404)
    ctx.ucp = Resource(status=200, text=ucp_text) if ucp_text is not None else Resource(status=404)
    ctx.md_probe = (Resource(status=200, headers={"Content-Type": md_content_type})
                    if md_content_type else Resource(status=404))
    ctx.llms_full = Resource(status=200, text=llms_full_text) if llms_full_text is not None else Resource(status=404)
    ctx.openapi = Resource(status=200, text=openapi_text) if openapi_text is not None else Resource(status=404)
    ctx.tdmrep = Resource(status=200, text="{}") if tdmrep_ok else Resource(status=404)
    ctx.products_json = Resource(status=200, text=products_json_text) if products_json_text is not None else Resource(status=404)
    return ctx


def test_check_1_llms():
    assert aa.check_1(make_ctx(llms_text="# Site\n- [d](/d)"))[0] == PASS
    assert aa.check_1(make_ctx(llms_text="plain, no heading"))[0] == PASS  # exists even if no H1
    assert aa.check_1(make_ctx())[0] == FAIL          # 404
    assert aa.check_1(make_ctx(llms_text="   "))[0] == FAIL  # empty/whitespace


def test_check_2_sitemap():
    ok = make_ctx(sitemap_kind="urlset", sitemap_locs=[("https://t/a", "2026-06-01"),
                                                       ("https://t/b", None)])
    status, detail = aa.check_2(ok)
    assert status == PASS and "2026-06-01" in detail and "2 entries" in detail
    assert aa.check_2(make_ctx(sitemap_kind=None))[0] == FAIL
    miss = make_ctx(sitemap_kind=None)
    miss.sitemap = Resource(status=None, error="timeout")  # transport failure -> unknown
    assert aa.check_2(miss)[0] == UNKNOWN


def test_check_3_js():
    assert aa.check_3(make_ctx(home_text="x" * 100, rendered_text="x" * 100))[0] == PASS  # 100%
    assert aa.check_3(make_ctx(home_text="x" * 65, rendered_text="x" * 100))[0] == PASS   # 65% >= 60
    assert aa.check_3(make_ctx(home_text="x" * 10, rendered_text="x" * 100))[0] == FAIL   # JS-heavy
    assert aa.check_3(make_ctx(home_text="x", rendered_text=None))[0] == UNKNOWN          # no render
    assert aa.check_3(make_ctx(home_text="x", rendered_text="   "))[0] == UNKNOWN         # empty render


def test_check_6_7_robots():
    blocks = "User-agent: GPTBot\nDisallow: /\nUser-agent: PerplexityBot\nDisallow:\n"
    ctx = make_ctx(robots_text=blocks)
    assert aa.check_6(ctx)[0] == PASS
    s7, d7 = aa.check_7(ctx)
    assert s7 == PASS and "gptbot: blocked" in d7 and "perplexitybot: allowed" in d7
    assert aa.check_6(make_ctx())[0] == FAIL                          # no robots.txt
    assert aa.check_6(make_ctx(robots_text="User-agent: *\nDisallow:"))[0] == FAIL  # no AI named
    assert aa.check_7(make_ctx(robots_text="User-agent: *\nDisallow:"))[0] == FAIL


def test_check_11_structured():
    html = '<script type="application/ld+json">{"@type":"Product"}</script>'
    s, d = aa.check_11(make_ctx(home_html=html))
    assert s == PASS and "Product" in d
    assert aa.check_11(make_ctx(home_html="<p>nothing</p>"))[0] == FAIL


def test_check_12_opengraph():
    assert aa.check_12(make_ctx(home_html='<meta property="og:title" content="Hi">'))[0] == PASS
    assert aa.check_12(make_ctx(home_html='<meta property="og:image" content="x">'))[0] == FAIL  # no title
    assert aa.check_12(make_ctx(home_html="<p>x</p>"))[0] == FAIL


def test_check_14_coverage():
    has = '<script type="application/ld+json">{"@type":"Article"}</script>'
    samples = [("u1", has), ("u2", "<p>plain</p>"), ("u3", has)]
    s, d = aa.check_14(make_ctx(samples=samples))
    assert s == PASS and "2/3" in d
    assert aa.check_14(make_ctx(samples=[("u", "<p>x</p>")]))[0] == FAIL
    # no sitemap -> homepage fallback
    assert aa.check_14(make_ctx(home_html=has))[0] == PASS
    assert aa.check_14(make_ctx(home_html="<p>x</p>"))[0] == FAIL


def test_check_18_dates():
    assert aa.check_18(make_ctx(home_html='<time datetime="2026-06-01">x</time>'))[0] == PASS
    assert aa.check_18(make_ctx(home_html="<p>no dates</p>"))[0] == FAIL


def test_check_19_headers_case_insensitive():
    # headers come through with original casing; the check must match case-insensitively
    assert aa.check_19(make_ctx(home_headers={"Last-Modified": "Mon"}))[0] == PASS
    assert aa.check_19(make_ctx(home_headers={"ETag": '"abc"'}))[0] == PASS
    assert aa.check_19(make_ctx(home_headers={"Content-Type": "text/html"}))[0] == FAIL


def test_check_20_canonical():
    assert aa.check_20(make_ctx(home_html='<link rel="canonical" href="https://t/a">'))[0] == PASS
    hdr = make_ctx(home_headers={"Link": '<https://t/b>; rel="canonical"'})
    assert aa.check_20(hdr)[0] == PASS
    assert aa.check_20(make_ctx(home_html="<p>x</p>"))[0] == FAIL


def test_check_21_cache():
    assert aa.check_21(make_ctx(home_headers={"Cache-Control": "max-age=60"}))[0] == PASS
    assert aa.check_21(make_ctx(home_headers={"Expires": "Mon"}))[0] == PASS
    assert aa.check_21(make_ctx(home_headers={"Server": "nginx"}))[0] == FAIL


def test_detect_protocols():
    card = '{"name":"shop","capabilities":{"extensions":[{"uri":"https://github.com/google-agentic-commerce/ap2/tree/v0.1"}]}}'
    found = detect_protocols(card, True, "{}", True, 200, {})
    assert found == ["A2A", "AP2", "UCP"], f"full stack not detected: {found}"
    # A2A only — valid card, no AP2 extension, no UCP
    assert detect_protocols('{"name":"x"}', True, "", False, 200, {}) == ["A2A"]
    # AP2 extension given as a bare string, not an object
    bare = '{"capabilities":{"extensions":["https://github.com/google-agentic-commerce/ap2"]}}'
    assert detect_protocols(bare, True, "", False, 200, {}) == ["A2A", "AP2"]
    # nothing visible
    assert detect_protocols("", False, "", False, 200, {}) == []
    # malformed agent card must not crash and must not count as A2A
    assert detect_protocols("not json", True, "", False, 200, {}) == []
    # x402 via a 402 status
    assert detect_protocols("", False, "", False, 402, {}) == ["x402"]


def test_check_17_proxy_semantics():
    card = '{"capabilities":{"extensions":[{"uri":"https://github.com/google-agentic-commerce/ap2/tree/v0.1"}]}}'
    s, d = aa.check_17(make_ctx(agent_card_text=card))
    assert s == PASS and "A2A" in d and "AP2" in d
    # the honesty rule: nothing found is UNKNOWN, never FAIL
    s2, _ = aa.check_17(make_ctx())
    assert s2 == UNKNOWN, "absence of a protocol signal must be unknown, not fail"


def test_summary_keeps_tiers_separate():
    """Tier-B signals are reported on their own, never folded into a Tier-A fraction."""
    card = '{"name":"x"}'  # A2A only; nothing else declared
    results = aa.run_checks(make_ctx(agent_card_text=card))
    summary = aa.summarize(results)
    assert "signals" in summary, "Tier-B signals missing from summary"
    # Commerce has 4 Tier-B checks (13,15,16,17); only 17 found here.
    assert summary["signals"]["Commerce"] == {"found": 1, "probed": 4}
    assert summary["signals"]["Docs"]["probed"] == 2
    # Commerce must NOT appear as a Tier-A group fraction
    assert "Commerce" not in {k for k in summary if k != "signals"}


# --- Tier-B helper + check tests -------------------------------------------
def test_detect_captcha():
    assert detect_captcha('<script src="https://www.google.com/recaptcha/api.js">') == ["reCAPTCHA"]
    assert "Turnstile" in detect_captcha('<div class="cf-turnstile"></div>')
    assert detect_captcha("<p>clean page</p>") == []


def test_extract_offer_signals():
    html = '<script type="application/ld+json">{"@type":"Product","offers":{"@type":"Offer","price":"9","availability":"InStock"}}</script>'
    sig = extract_offer_signals(html)
    assert "Offer" in sig and "price" in sig and "availability" in sig
    assert extract_offer_signals("<p>no offers</p>") == []


def test_detect_paywall():
    assert "isAccessibleForFree:false" in detect_paywall(
        '<script type="application/ld+json">{"@type":"Article","isAccessibleForFree":false}</script>')
    assert any("content_tier" in m for m in detect_paywall(
        '<meta property="article:content_tier" content="locked">'))
    assert detect_paywall("<p>free content</p>") == []


def test_detect_cdn():
    assert detect_cdn({"CF-Ray": "abc", "Server": "cloudflare"}) == "Cloudflare"
    assert detect_cdn({"X-Vercel-Id": "x"}) == "Vercel"
    assert detect_cdn({"Server": "nginx"}) is None


def test_markdown_and_license_helpers():
    assert find_markdown_alternative('<link rel="alternate" type="text/markdown" href="/p.md">')
    assert not find_markdown_alternative('<link rel="alternate" type="application/rss+xml" href="/f">')
    assert extract_license('<link rel="license" href="/l">') == "<link rel=license>"
    assert extract_license("<p>none</p>") is None


def test_check_16_barrier_semantics():
    """A detected bot-wall is a trustworthy NEGATIVE: ❌, not unknown. Absence is unknown, not pass."""
    s, _ = aa.check_16(make_ctx(home_html='<script src="hcaptcha.com/1.js">'))
    assert s == FAIL, "a detected CAPTCHA must be a fail, not unknown"
    s2, _ = aa.check_16(make_ctx(home_html="<p>clean</p>"))
    assert s2 == UNKNOWN, "no CAPTCHA must be unknown (other pages unprobed), never pass"


def test_tier_b_checks_positive():
    offers = '<script type="application/ld+json">{"@type":"Offer","price":"9"}</script>'
    assert aa.check_15(make_ctx(home_html=offers))[0] == PASS
    assert aa.check_13(make_ctx(products_json_text='{"products":[]}'))[0] == PASS
    assert aa.check_4(make_ctx(md_content_type="text/markdown"))[0] == PASS
    assert aa.check_5(make_ctx(openapi_text='{"openapi":"3.0.0"}'))[0] == PASS
    assert aa.check_9(make_ctx(tdmrep_ok=True))[0] == PASS
    assert aa.check_10(make_ctx(home_headers={"CF-Ray": "x"}))[0] == PASS
    assert aa.check_23(make_ctx(home_html='<script src="https://tollbit.io/x.js">'))[0] == PASS
    assert aa.check_24(make_ctx(home_html='<script type="application/ld+json">{"isAccessibleForFree":false}</script>'))[0] == PASS


def test_tier_b_silence_is_never_a_fact():
    """On an empty page, no Tier-B check claims a positive; none fabricates a fail except a real barrier."""
    results = [r for r in aa.run_checks(make_ctx()) if r["tier"] == "B"]
    assert results, "expected Tier-B results"
    assert all(r["status"] != PASS for r in results), "no Tier-B check should pass on an empty page"
    # the only way a Tier-B check fails is a detected barrier; an empty page has none
    assert all(r["status"] == UNKNOWN for r in results), \
        "empty page Tier-B checks must all be unknown: " + \
        str([(r["id"], r["status"]) for r in results if r["status"] != UNKNOWN])


def test_integration_run_and_render():
    """A fully-populated context runs all 22 checks, summarizes, and renders cleanly."""
    html = ('<meta property="og:title" content="T">'
            '<link rel="canonical" href="https://t/a">'
            '<link rel="alternate" type="text/markdown" href="/p.md">'
            '<link rel="license" href="/l">'
            '<script src="https://tollbit.io/x.js"></script>'
            '<script type="application/ld+json">{"@type":["WebSite","Product"],"dateModified":"2026-06-01",'
            '"isAccessibleForFree":false,"offers":{"@type":"Offer","price":"9","availability":"InStock"}}</script>')
    card = '{"name":"shop","capabilities":{"extensions":[{"uri":"https://github.com/google-agentic-commerce/ap2/tree/v0.1"}]}}'
    ctx = make_ctx(
        home_html=html,
        home_headers={"Last-Modified": "Mon", "Cache-Control": "max-age=60", "CF-Ray": "abc"},
        home_text="x" * 100, rendered_text="x" * 100,
        llms_text="# Site",
        robots_text="User-agent: GPTBot\nDisallow:\n",
        sitemap_kind="urlset", sitemap_locs=[("https://t/a", "2026-06-01")],
        samples=[("u", html)],
        agent_card_text=card, ucp_text="{}",
        md_content_type="text/markdown", openapi_text='{"openapi":"3.0.0"}',
        tdmrep_ok=True, products_json_text='{"products":[]}',
    )
    results = aa.run_checks(ctx)
    assert len(results) == 22, "should produce exactly 22 results"
    assert {r["id"] for r in results} == {1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13,
                                          14, 15, 16, 17, 18, 19, 20, 21, 23, 24}
    # every Tier-A check passes
    assert all(r["status"] == PASS for r in results if r["tier"] == "A"), \
        "Tier-A must be all green: " + str([(r["id"], r["status"]) for r in results
                                            if r["tier"] == "A" and r["status"] != PASS])
    # every Tier-B EXCEPT the CAPTCHA barrier (16) passes; 16 is unknown (no captcha in fixture)
    by_id = {r["id"]: r["status"] for r in results}
    assert by_id[16] == UNKNOWN
    assert all(by_id[i] == PASS for i in (4, 5, 9, 10, 13, 15, 17, 23, 24)), \
        "Tier-B positives expected: " + str({i: by_id[i] for i in (4, 5, 9, 10, 13, 15, 17, 23, 24)})
    summary = aa.summarize(results)
    assert summary["Read"] == {"pass": 3, "total": 3}
    assert summary["signals"]["Commerce"]["found"] == 3  # 13,15,17 (16 is the barrier)
    assert summary["signals"]["Monetization"] == {"found": 2, "probed": 2}
    report = aa.render_text_report("https://t.example", results, summary)
    assert "Agent Readiness" in report and "no blended score" in report
    assert "Tier-B proxy signals" in report and "Commerce" in report and "Monetization" in report


def test_broken_check_is_isolated():
    """A check that raises must degrade to 'unknown', not crash run_checks."""
    ctx = make_ctx()
    ctx.home = None  # type: ignore  # force checks that read ctx.home.* to raise
    results = aa.run_checks(ctx)
    assert len(results) == 22, "run_checks must still return all 22 results"
    assert any(r["status"] == UNKNOWN for r in results), "a raising check should become unknown"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\nAll {len(tests)} offline checks passed.")
