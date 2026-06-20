# CLI reference

Complete reference for the `agent_audit.py` command: arguments, flags, output formats, the JSON schema, exit codes, and the tunable constants.

---

## Synopsis

```bash
python agent_audit.py <url> [--json] [--sample N]
```

The tool audits exactly one URL per run.

---

## Arguments

### url

Type: string (positional, required)

The site to audit. The scheme is optional — `https://` is added if you omit it, so `example.com` and `https://example.com` are equivalent.

The tool follows redirects and reports the final URL it landed on (which may differ from what you typed).

```bash
python agent_audit.py example.com
python agent_audit.py https://example.com/some/page
```

---

## Options

### --json

Type: flag (default: off)

Emit a JSON object instead of the human-readable text checklist. See [JSON output](#json-output) for the schema.

```bash
python agent_audit.py example.com --json
```

### --sample N

Type: integer (default: 10)

How many pages to sample from the sitemap for the structured-data coverage check (#14). Lower it to run faster; raise it for a more representative coverage figure. Has no effect if the site has no sitemap (check #14 then falls back to the homepage alone).

```bash
python agent_audit.py example.com --sample 3
```

---

## Text output

The default format. Structure:

```text
Agent Readiness — <final URL>
============================================================

<Group>
  <symbol> [<id>] <check name> — <detail>
  ...

------------------------------------------------------------
<group tallies>   (legend)
```

- Tier-A checks are grouped Read, Trust, Freshness, Discovery, in that order.
- Each line shows the status symbol (✅ / ❌ / —), the check ID, its name, and a one-line detail.
- After the Tier-A groups, a separate **Tier-B proxy signals** section lists the 10 proxy checks, sub-grouped Docs, Permissions, Commerce, Monetization, under a banner so a proxy signal is never mistaken for a verified fact.
- The footer shows two lines, kept separate by design: `Tier-A facts —` with pass counts per group (`Read 1/3 · …`), then `Tier-B signals —` with found counts per group (`Docs 2/2 · Permissions 1/2 · …`).

The status symbols:

| Symbol | Status | Meaning |
|--------|--------|---------|
| ✅ | pass | Tier-A: fact found. Tier-B: trustworthy positive signal. |
| ❌ | fail | Tier-A: fact genuinely absent. Tier-B: a detected barrier (check #16 only). |
| — | unknown | Tier-A: could not perform. Tier-B: no signal visible (not proof of absence). |

---

## JSON output

With `--json`, the tool prints a single JSON object.

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | The final URL audited (after redirects). |
| `audited_at` | string | ISO-8601 UTC timestamp of the run. |
| `checks` | array | One object per check (22 entries). |
| `summary` | object | Tier-A per-group pass tallies, plus a `signals` block for Tier-B. |

### Each `checks[]` entry

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | The check ID (non-contiguous; see [checks reference](checks.md)). |
| `name` | string | The check name. |
| `group` | string | Tier-A: `Read`, `Trust`, `Freshness`, `Discovery`. Tier-B: `Docs`, `Permissions`, `Commerce`, `Monetization`. |
| `tier` | string | `A` (deterministic fact) or `B` (proxy signal). |
| `status` | string | `pass`, `fail`, or `unknown`. A Tier-B check returns `fail` only for a detected barrier (check #16). |
| `detail` | string | The same one-line detail shown in text output. |

### The `summary` object

Two parts, kept separate by design so a fact and a proxy signal are never blended:

- One key per **Tier-A group** (`Read`, `Trust`, `Freshness`, `Discovery`), each mapping to `{ "pass": <int>, "total": <int> }`.
- A `signals` key (present when Tier-B checks ran), mapping each Tier-B group (`Docs`, `Permissions`, `Commerce`, `Monetization`) to `{ "found": <int>, "probed": <int> }`, where `found` counts positive (✅) signals only.

### Example

```json
{
  "url": "https://www.cloudflare.com/",
  "audited_at": "2026-06-20T05:01:46.840208+00:00",
  "checks": [
    {
      "id": 1,
      "name": "llms.txt present",
      "group": "Read",
      "tier": "A",
      "status": "pass",
      "detail": "/llms.txt found (valid markdown)"
    },
    {
      "id": 16,
      "name": "Checkout bot-wall (CAPTCHA)",
      "group": "Commerce",
      "tier": "B",
      "status": "fail",
      "detail": "bot-wall detected (Turnstile) — agent automation likely impeded; checkout pages not probed"
    },
    {
      "id": 17,
      "name": "Agent-commerce protocol",
      "group": "Commerce",
      "tier": "B",
      "status": "pass",
      "detail": "declares: A2A"
    }
  ],
  "summary": {
    "Read":      { "pass": 3, "total": 3 },
    "Trust":     { "pass": 2, "total": 2 },
    "Freshness": { "pass": 2, "total": 4 },
    "Discovery": { "pass": 3, "total": 3 },
    "signals": {
      "Docs":         { "found": 2, "probed": 2 },
      "Permissions":  { "found": 1, "probed": 2 },
      "Commerce":     { "found": 2, "probed": 4 },
      "Monetization": { "found": 0, "probed": 2 }
    }
  }
}
```

> **Tip:** Pipe JSON output to a parser to extract one field, for example `python agent_audit.py example.com --json | python -c "import json,sys; print(json.load(sys.stdin)['summary'])"`.

---

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | The audit ran. (This does **not** mean every check passed — it means the run completed.) |
| `2` | The audit could not run: the homepage was unreachable (DNS failure, connection refused, timeout), or the command-line arguments were invalid. |

A homepage that is unreachable prints `error: could not reach <url>: <reason>` to standard error and exits `2`. Individual check failures never change the exit code — they are reported as ❌ within a successful (exit `0`) run.

---

## No score by design

The tool never prints an overall number. Each group shows a raw count like `Read 1/3`. This is deliberate:

- A single score is a lossy compression of the checklist; the actionable value is in the individual results.
- Any weighting between groups would be arbitrary.
- The footer count is honest and specific, and never implies a precision the tool does not have.

The full reasoning is in the [design reference](../../agent-readiness-auditor.md), Section 8, and the [development journey](../../development-journey.md#fork-5-no-scoring-system).

---

## Tunable constants

The tool has no config file and no environment variables. A few behaviours are module-level constants at the top of `agent_audit.py`. To change one, edit the file.

| Constant | Default | Effect |
|----------|---------|--------|
| `TIMEOUT` | `15` | Seconds before any single fetch gives up. |
| `JS_TEXT_PASS_RATIO` | `0.60` | The raw-to-rendered text ratio at or above which check #3 passes. |
| `DEFAULT_SAMPLE` | `10` | Default for `--sample` when the flag is omitted. |
| `USER_AGENT` | `AgentReadinessAuditor/0.1 (+https://github.com/agent-audit)` | The User-Agent header the tool sends, for both `requests` and the browser. |
| `AI_USER_AGENTS` | 15 names | The AI crawler names checks 6 and 7 look for. See the [checks reference](checks.md#known-ai-user-agents). |

> **Note:** `USER_AGENT` matters when a site blocks unfamiliar agents. Some sites return a 403 to the tool's default agent; changing it to a common browser string is the usual workaround. See [troubleshooting](../troubleshooting/common-issues.md#a-site-returns-403-or-blocks-the-audit).
