# Deploying the live demo

The web UI (`webapp.py`) needs a host that can run Python **and launch a headless Chromium per
audit** — so it ships as a Docker image built on Playwright's official base. That rules out
static hosts (GitHub Pages) and is a poor fit for short-lived serverless functions (an audit
takes 15–40s and spawns a browser). A container host — **Render**, Railway, or Fly.io — is the
right shape. Render has a free tier and reads the `render.yaml` blueprint in this repo, so it is
the path of least resistance.

## Render (recommended, free tier)

1. Push this repo to GitHub (already done for `az9713/agent-readiness-auditor`).
2. Go to <https://dashboard.render.com> → **New** → **Blueprint**.
3. Connect the GitHub repo. Render reads [`render.yaml`](render.yaml), sees the Docker service,
   and pre-fills everything (including `PUBLIC_DEMO=1` and `HOST=0.0.0.0`).
4. Click **Apply**. First build takes a few minutes (it pulls the ~2 GB Playwright image once).
5. The service comes up at `https://agent-readiness-auditor.onrender.com` (or whatever name you
   chose). That URL is the live demo.

One-click variant: the **Deploy to Render** button in the README opens the same flow pre-pointed
at the repo.

> **Free-tier note.** The free plan spins the service down when idle, so the *first* request
> after a quiet period is a cold start (~30–60s) — the page just takes a while on that first
> audit, then is fast until it idles again.

## Railway / Fly.io (alternatives)

Both build the same `Dockerfile`. Set the env vars `PUBLIC_DEMO=1` and `HOST=0.0.0.0`; the
platform supplies `PORT`. Fly: `fly launch` (it detects the Dockerfile), then `fly deploy`.

## Security posture of the public demo

The demo fetches whatever URL a visitor submits, which is an SSRF vector. With `PUBLIC_DEMO=1`
set, `webapp.py` enforces a guard (`reject_if_unsafe`) that resolves the target host and
**refuses private, loopback, link-local, and reserved addresses** (e.g. `127.0.0.1`,
`169.254.169.254`, `10.0.0.0/8`) and any non-`http(s)` scheme. This is verified by the
`test_ssrf_*` tests.

**Known limitation:** the guard checks the *submitted* host, not redirect hops. A public host
that 302-redirects to an internal address would slip through, because `requests` follows
redirects. If the demo ever sees abuse, close this by re-validating each hop (a custom
`requests` `HTTPAdapter`) or by disabling redirects. For a low-traffic portfolio demo the direct
guard is the pragmatic line.

There is no rate limiting. If you expose this widely, put it behind the platform's rate limiter
or a CDN, since each audit launches a browser and is comparatively expensive.

## After it's live

Send the URL and it goes into the README's **Try it live** section (replacing the placeholder).
