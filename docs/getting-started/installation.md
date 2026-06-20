# Installation

The auditor is a single Python script with five dependencies and one browser engine. Setup takes about five minutes.

---

## Requirements

| Requirement | Version | Verify |
|-------------|---------|--------|
| Python | 3.11+ | `python --version` |
| pip | any recent | `pip --version` |
| Disk space | ~400 MB | for the Chromium browser Playwright installs |
| Network | outbound HTTPS | the tool fetches the sites it audits |

> **Note:** Python 3.11 or newer is required because the code uses the `X | Y` type-union syntax in annotations. 3.13 is what the project was built and tested on.

---

## Step 1: Install the Python dependencies

```bash
pip install -r requirements.txt
```

This installs:

| Package | Used for |
|---------|----------|
| `requests` | Fetching pages, robots.txt, sitemap, llms.txt |
| `beautifulsoup4` | Parsing HTML (structured data, OpenGraph, canonical, dates) |
| `lxml` | The fast HTML/XML parser BeautifulSoup uses |
| `playwright` | Rendering the page in a real browser for the JavaScript check |
| `defusedxml` | Parsing sitemap XML safely against entity-expansion attacks |

## Step 2: Install the Chromium browser

Playwright needs a browser binary, which is downloaded separately from the Python package:

```bash
python -m playwright install chromium
```

Expected output ends with a line confirming Chromium was downloaded to a local cache.

> **Warning:** Skipping this step does not crash the tool, but check #3 (Readable without JavaScript) will report `unknown` on every run, because it cannot launch a browser.

## Step 3: Verify the install

Run the offline test suite. It needs no network and no website — it only exercises the parsing logic:

```bash
python test_auditor.py
```

Expected output:

```text
  ok  test_billion_laughs_safe
  ok  test_broken_check_is_isolated
  ...
All 34 offline checks passed.
```

If all 34 pass, the install is correct.

## Step 4: Run a real audit

```bash
python agent_audit.py https://example.com
```

If you see a checklist with ✅ / ❌ / — markers, you are ready. See the [quickstart](quickstart.md) for a guided first run.

---

## Troubleshooting the install

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'requests'` | Re-run Step 1. |
| Check #3 always shows `unknown` | Run Step 2 (`python -m playwright install chromium`). |
| `playwright install` fails behind a proxy | Set `HTTPS_PROXY` and retry, or download Chromium on a machine with open access. |

More in [troubleshooting](../troubleshooting/common-issues.md).
