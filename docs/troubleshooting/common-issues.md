# Troubleshooting

The failures you are most likely to hit, ordered by how often they happen. Each has a symptom, the cause, and an exact fix.

---

## Check #3 always shows "unknown"

**Symptom:** Every run shows `— [ 3] Readable without JavaScript — could not render: ...`.

**Cause:** Playwright's Chromium browser is not installed. The Python package alone is not enough — the browser binary is a separate download.

**Fix:**

```bash
python -m playwright install chromium
```

**If that doesn't work:** you are likely behind a proxy. Set `HTTPS_PROXY` and retry, or run the install on a machine with open outbound access and copy the browser cache.

---

## ModuleNotFoundError on startup

**Symptom:** `ModuleNotFoundError: No module named 'requests'` (or `bs4`, `defusedxml`, `playwright`).

**Cause:** The Python dependencies are not installed, or you are running a different Python than the one you installed them into.

**Fix:**

```bash
pip install -r requirements.txt
```

**If that doesn't work:** confirm you are using one interpreter throughout. Run `python -m pip install -r requirements.txt` so pip targets the same `python` you run the tool with.

---

## "error: could not reach <url>" and exit code 2

**Symptom:** The tool prints `error: could not reach https://... : <reason>` and stops with exit code 2.

**Cause:** The homepage could not be fetched — DNS failure, connection refused, or a timeout. With no homepage there is nothing to audit, so this is the one fatal condition.

**Fix:**

1. Confirm the URL opens in a browser.
2. Check your network and any proxy.
3. If the site is slow, raise the `TIMEOUT` constant in `agent_audit.py` (default 15 seconds).

**If that doesn't work:** the site may be blocking the tool's User-Agent — see the next entry.

---

## A site returns 403 or blocks the audit

**Symptom:** The homepage fetch fails, or every check fails on a site you know is well-built.

**Cause:** Some sites reject requests from unfamiliar User-Agent strings. The tool announces itself as `AgentReadinessAuditor/0.1`, which a bot-filter may block.

**Fix:** change the `USER_AGENT` constant near the top of `agent_audit.py` to a common browser string, then re-run. See the [CLI reference](../reference/cli.md#tunable-constants).

**If that doesn't work:** the site may require JavaScript or a login the tool cannot pass. The audit is limited to what an anonymous visitor sees.

---

## The checklist prints garbled characters instead of ✅ / ❌

**Symptom:** The status symbols appear as `?` or mojibake, usually on an older Windows console.

**Cause:** The terminal's code page cannot encode the Unicode symbols.

**Fix:** the tool already reconfigures standard output to UTF-8 on startup. If your terminal still mangles them, switch the console code page first:

```bash
chcp 65001
python agent_audit.py https://example.com
```

Or use `--json`, which avoids the symbols entirely.

---

## A check shows "unknown" other than #3

**Symptom:** A check (commonly #2, sitemap) shows `—` with a detail like `sitemap fetch failed: ...`.

**Cause:** A secondary resource could not be fetched (timeout or connection error). Unlike the homepage, a missing secondary resource does not stop the run — the check that needed it reports `unknown`.

**Fix:** usually transient. Re-run. If it persists, the resource may be genuinely unreachable or very slow; raising `TIMEOUT` in `agent_audit.py` can help.

---

## "All checks fail" on a JavaScript-heavy site

**Symptom:** A modern single-page app fails structured-data, OpenGraph, and date checks even though the rendered page clearly has that content.

**Cause:** Those checks read the **raw** homepage HTML, not the browser-rendered version. If the site injects its metadata via JavaScript, the raw HTML has none of it — which is itself an accurate finding: an agent doing a simple fetch would also miss it.

**Fix:** none needed — this is a true result, not a tool error. Check #3 will also fail or score low, confirming the content depends on JavaScript. The remedy is on the site's side (server-side rendering), not the tool's.

---

## Tests fail after editing the code

**Symptom:** `python test_auditor.py` reports a failed assertion after you changed `agent_audit.py`.

**Cause:** A check's logic or its detail string changed, and a test asserts the old behaviour.

**Fix:** run the suite to see which assertion failed, then update either the code or the test to match the intended behaviour:

```bash
python test_auditor.py
```

The tests are the contract for the 12 checks — keep them green. See [system design, Testing](../architecture/system-design.md#testing).
