# Agent Readiness Auditor

A command-line tool that audits one website for how usable it is to AI agents rather than to humans. It runs 12 deterministic (Tier-A) checks plus 10 proxy (Tier-B) checks, and prints a pass/fail/unknown checklist — no blended score.

---

## Documentation

| Section | What's inside |
|---------|---------------|
| [Installation](getting-started/installation.md) | Dependencies, Playwright browser, verify commands |
| [Quickstart](getting-started/quickstart.md) | First real audit in under 10 minutes |
| [Key concepts](overview/key-concepts.md) | Glossary of every term used in these docs |
| [Checks reference](reference/checks.md) | All 22 checks (12 Tier-A + 10 Tier-B): source, pass/fail logic, example output |
| [CLI reference](reference/cli.md) | Arguments, flags, output formats, JSON schema, exit codes, tunables |
| [System design](architecture/system-design.md) | Architecture, the tier model, security, testing |
| [Example audit](examples/comparative-audit.md) | A worked comparison of vercel.com, stripe.com, cloudflare.com with per-check interpretation |
| [Commerce & Monetization audit](examples/commerce-and-monetization-audit.md) | Exercising the storefront and paywall checks on Shopify and publisher sites |
| [Troubleshooting](troubleshooting/common-issues.md) | The errors you are most likely to hit, and their fixes |

## Background reading

Two longer documents explain the *why* behind the tool. They live in the project root:

| Document | What's inside |
|----------|---------------|
| [Design reference](../agent-readiness-auditor.md) | The full 25-check catalog, the Tier A/B/C feasibility model, the no-score decision |
| [Development journey](../development-journey.md) | How the tool came to exist, every design fork, the agent-commerce protocols, and a transparency statement of what it does and does not do |

> **New here?** Read [what the auditor is](overview/key-concepts.md#the-tool), then run the [quickstart](getting-started/quickstart.md).
