# The Agent Readiness Auditor

A plain-English guide to the idea, the scoring table, and what each part means.

This document assumes **no prior background**. Every technical term is defined
the first time it appears. If you already know a term, skip the definition box —
it will not change later in the document.

---

## 1. The one-paragraph version

The **Agent Readiness Auditor** is a proposed software tool. You give it a
website address. It visits the site the way an automated program would, runs a
series of checks, and produces a scorecard answering one question: *"How easy is
it for an AI agent to find, trust, and act on what is on this site?"*

It is not measuring whether the site looks good to a human. It is measuring
whether a machine can use it.

---

## 2. The words you need first

Before the idea makes sense, four terms have to be clear.

> **Website (HTML).** A web page is mostly a file written in **HTML**
> (HyperText Markup Language). HTML is a system of labels wrapped around content,
> for example `<h1>Welcome</h1>` means "this text is a top-level heading."
> A web browser reads HTML and *renders* it — turns it into the visual page you
> see, with fonts, colours, and layout. HTML was designed to be turned into
> something a **human** looks at.

> **Bot / crawler / scraper.** A **bot** is any program that uses the web
> automatically, without a person clicking at that moment. A **crawler** is a bot
> that systematically visits pages and follows links (search engines like Google
> use crawlers to discover pages). A **scraper** is a bot that pulls specific
> data off a page (for example, copying every price from a shop). These have
> existed for decades.

> **LLM (Large Language Model).** The kind of AI behind ChatGPT, Claude, Gemini,
> and Perplexity. It reads and writes text. On its own it does not browse the
> web; it has to be connected to tools that fetch web pages for it.

> **AI agent.** An LLM that has been given **tools and a goal**, so it can take
> steps on its own. "Find me the three cheapest flights and book the best one" is
> an agent task: the agent searches, reads pages, compares, and acts. When an
> agent works, it sends out many automated web requests on your behalf — this is
> the new kind of bot traffic.

The key shift behind this whole tool: people used to read websites directly.
Increasingly, people ask an AI system, and the **AI** reads the websites for
them. So sites now have a second, growing audience that is not human. The
auditor measures how well a site serves that second audience.

---

## 3. Why this idea exists (the background story)

This tool was proposed in response to a podcast discussion about a striking
statistic: according to **Cloudflare** (a large company that sits in front of a
big slice of the internet and can therefore measure its traffic), roughly **57%
of web requests are now made by bots/agents and only about 43% by humans.**
A "web request" is a single fetch of a page or file — one click, or one
automated grab.

The panel's interpretation, which the auditor is built on, was:

- Bots have been a big share of web traffic for years; this is not brand new.
- What *is* changing is **why** the bots are there. More and more, the human is
  still the origin — but they express their wish through an AI, and the AI does
  the fetching. The web is becoming **machine-mediated**: a machine stands
  between the person and the page.
- If machines are the ones actually reading sites, then sites should be built to
  be **legible to machines**, not only pretty for people.

That last sentence is the entire reason for the auditor. It checks how legible
to machines a site is, and it scores the result so the gap is visible and
fixable.

A useful comparison: there is a well-known free tool called **Lighthouse** that
scores a web page on speed and accessibility *for humans*. The Agent Readiness
Auditor is the same concept, pointed at a different audience: **Lighthouse, but
for AI agents.**

---

## 4. The table

This is the heart of the proposal. The auditor scores a site across six
**dimensions** (areas of concern). Each row is one dimension and the test it
applies.

| Dimension           | Test                                                                |
| ------------------- | ------------------------------------------------------------------- |
| Agent-readable docs | Does the site expose `llms.txt`, clean markdown, sitemap, API docs? |
| Permissioning       | Does it specify bot policy, crawl rules, licensing?                 |
| Structured data     | Schema.org, OpenGraph, JSON-LD, product feeds                       |
| Commerce readiness  | Can an agent compare, cart, checkout, or query inventory?           |
| Freshness           | Are timestamps and canonical sources clear?                         |
| Monetization        | Is there a paid API, content license, or agent access policy?       |

Read on its own, this table is dense and full of jargon. The rest of the
document explains every row in plain language: what it is really asking, why an
agent cares, and the concrete things the auditor would check.

A single thread runs through all six rows. The first three (and the fifth) ask:
*can an agent **read and trust** this site?* The fourth asks: *can an agent
**act** on this site?* The sixth asks: *if agents use this site, does the site
**get paid**?* Hold that structure in mind — it is the skeleton under the table.

---

## 5. The rows, explained

### Row 1 — Agent-readable docs

**Plain-English question:** Can a machine get the actual content of this site
*easily*, without having to wade through messy visual page code?

Remember that HTML is built for display. A page might contain menus, ads,
pop-ups, cookie banners, and sidebars wrapped around the one paragraph that
matters. A human's eye skips the clutter automatically. A machine does not — it
has to untangle all of it, which is slow and error-prone.

So a site is "agent-readable" when it offers a **clean, machine-friendly version
of its content** alongside the pretty human version.

> **`llms.txt`.** An emerging convention: a simple text file placed at the root
> of a site (for example `example.com/llms.txt`) that gives an AI a tidy map and
> summary of the site's important content. The point is that the AI reads this
> clean file instead of scraping cluttered HTML. (The podcast called it
> "LLM.ext"; the real name is `llms.txt`.)

> **Markdown.** A lightweight, plain-text way of writing formatted documents
> using simple marks — `#` for a heading, `*` for a bullet. It is far easier for
> a machine to parse than HTML. Many documentation sites now publish a Markdown
> version of each page.

> **Sitemap.** A file (usually `sitemap.xml`) that lists every important page on
> the site. It is a table of contents for machines, so a crawler does not have to
> discover pages by guesswork.

> **API (Application Programming Interface).** A doorway built specifically for
> programs (not people) to request data in a clean, predictable format. If a site
> has an API, an agent can ask it directly — "give me this product's price" —
> instead of reading a page meant for human eyes.

> **API docs.** Documentation describing how to use that API. Without docs, even
> an existing API is hard for an agent to use.

**What the auditor checks:**
- Is there an `llms.txt` file, and is it well-formed?
- Is there a current `sitemap.xml`?
- Does the content appear in the raw page, or only after the browser runs
  JavaScript? (*JavaScript* is a programming language that builds parts of a page
  *after* it loads. Content that only appears via JavaScript is often invisible
  to a simple fetch — bad for agents.)
- Are Markdown or plain-text versions of pages available?
- Is there a public API with usable documentation?

---

### Row 2 — Permissioning

**Plain-English question:** Does the site clearly state what bots are *allowed*
to do here?

An honest, well-behaved agent will follow the rules — but only if the rules are
written down. This row checks whether the site publishes its rules and whether
they are explicit about AI.

> **`robots.txt`.** A long-standing file at the root of a site (for example
> `example.com/robots.txt`) where the owner lists which bots may visit which
> parts of the site. It works on the honour system: well-behaved bots read it and
> obey; it is a posted rule, not a locked gate.

> **User-agent.** The name a bot announces itself by. Modern AI crawlers have
> recognisable names — for example `GPTBot` (OpenAI), `ClaudeBot` (Anthropic),
> `Google-Extended` (Google's AI), `PerplexityBot` (Perplexity). A site can allow
> or block each one by name in `robots.txt`.

> **Rate limit.** A cap on how often a bot may make requests, so it does not
> overload the site. Sites signal this with specific responses (a "429 Too Many
> Requests" message and a "Retry-After" instruction telling the bot how long to
> wait).

> **Licensing.** A statement of the legal terms under which the content may be
> used — including whether an AI is allowed to use it for training or answering
> questions. This matters because content has an owner, and using it outside the
> stated terms can be a legal problem.

> **Pay-per-crawl.** A newer idea (pushed by Cloudflare among others) where a site
> can charge bots for access — the bot pays a small fee to fetch a page. This row
> notes whether such a policy is present.

**What the auditor checks:**
- Does `robots.txt` exist, and does it name AI user-agents specifically?
- Does it allow or block them?
- Are rate-limit signals present and clear?
- Is there a stated content licence or terms covering automated/AI use?
- Are pay-per-crawl or bot-management policies in place?

---

### Row 3 — Structured data

**Plain-English question:** Is the *meaning* of the content labelled as data, or
does it only exist in the visual layout?

Consider a product page. A human sees "$49.99" in large red type next to a photo
and instantly understands: *that is the price.* A machine sees a number on a page
and has to guess whether it is a price, a weight, a star rating, or a phone
number. **Structured data** removes the guessing: it is extra, invisible
labelling in the page that says, in machine terms, "this value is the price,
this is the product name, this is the rating."

> **Schema.org.** A shared, industry-standard vocabulary of labels for common
> things — `Product`, `Price`, `Article`, `Event`, `Organization`, and so on. If
> a site uses Schema.org labels, any machine knows exactly what each piece of
> content is.

> **JSON-LD.** The most common modern *format* for embedding that structured data
> in a page. (JSON is a simple, widely used text format for organised data;
> "-LD" means "Linked Data.") It usually sits in a hidden block in the page and
> does not affect what the human sees — it exists purely for machines.

> **Microdata.** An older way of attaching the same kind of labels directly onto
> the visible HTML tags. Serves the same purpose as JSON-LD.

> **OpenGraph.** A small set of tags that describe a page for sharing — its
> title, summary, and preview image. Originally built so links look good when
> pasted into social media, but the same tags help any machine summarise a page.

> **Product feed.** A structured file listing a store's products with their
> details (name, price, availability, identifier), formatted for machines to
> ingest in bulk rather than reading one page at a time.

**What the auditor checks:**
- Are there JSON-LD or microdata blocks, and which Schema.org types do they use?
- Are OpenGraph tags present?
- For shops, is there a machine-readable product feed?
- It scores by **coverage** — what fraction of the important pages actually carry
  valid structured data, not just whether one page has it.

---

### Row 4 — Commerce readiness

**Plain-English question:** Can an agent not just *read* this site, but *do
business* on it — compare options, add to a cart, check out, check stock?

This is the difference between an agent that **informs** you and an agent that
**acts** for you. Reading is easy; acting is hard. The podcast described the
dream — instead of you tiredly browsing ten pairs of shoes, comparing prices,
and checking out, an agent does the whole errand. That is called **agentic
commerce**, and almost no site is fully ready for it today.

> **Agentic commerce.** Shopping (or any transaction) carried out end-to-end by
> an AI agent on a person's behalf: finding options, comparing, selecting,
> adding to cart, paying, and arranging delivery.

> **Endpoint.** A specific web address that a program talks to in order to do one
> thing — for example, an "add to cart" endpoint or a "check inventory" endpoint.
> Stable, documented endpoints let an agent act reliably. Hidden or constantly
> changing ones do not.

> **CAPTCHA.** Those "click all the traffic lights" or "prove you're human"
> challenges. They exist precisely to *stop* bots. A checkout walled behind a
> CAPTCHA is, by design, not agent-ready.

> **Agent-payment protocols.** New, emerging standards (being developed by
> payment companies such as Stripe, Visa, and Mastercard) that let an AI agent
> pay for something safely and with the owner's authorisation. Where these exist,
> a site is far more commerce-ready.

**What the auditor checks:**
- Is there a public way to read product, price, and stock information
  programmatically (per item)?
- Are there stable add-to-cart and checkout endpoints, or is everything locked
  behind CAPTCHAs and human-only screens?
- Does the site support any emerging agent-payment standard?

This is one of the two hardest rows to score honestly (the other is Row 6),
because truly testing it would mean actually trying to buy something. So in a
practical version, the auditor scores **declared capability** — does the
endpoint or policy exist? — rather than proving a full purchase end-to-end.

---

### Row 5 — Freshness

**Plain-English question:** Can an agent tell how *recent* and how *authoritative*
a page is?

When an agent answers a question, it often pulls from many pages at once and has
to decide which to trust. Two signals drive that decision: *how new is this?* and
*is this the original, canonical source or a copy?* If a page hides those
signals, a careful agent may downrank or ignore it.

> **Timestamp.** A recorded date — when a page was published and when it was last
> changed. Sites can state this both in the visible content and in hidden
> machine-readable form.

> **Canonical source / canonical URL.** The single, official address for a piece
> of content. The same article often lives at several addresses (with tracking
> codes, print versions, mirrors). A `canonical` tag tells machines "this one is
> the real, primary version" so they do not treat duplicates as separate, or
> trust a copy over the original.

> **HTTP headers.** Small pieces of behind-the-scenes information sent with every
> page, separate from the visible content. Two relevant ones: `Last-Modified`
> (when the page last changed) and `ETag` (a fingerprint that changes when the
> content changes). Both let a machine know, cheaply, whether anything is new.

> **Caching.** Storing a copy of a page so it does not have to be fetched fresh
> every time. Clear freshness signals also tell systems when a cached copy is
> still good — which matters because AI traffic is often hard to cache, raising
> a site's running costs.

**What the auditor checks:**
- Are publish/modified dates present, both visibly and in machine-readable form?
- Are `Last-Modified` and `ETag` headers set?
- Is a `canonical` URL declared, so duplicates are not mistaken for separate
  pages?
- Are caching signals clear?

---

### Row 6 — Monetization

**Plain-English question:** If agents are the ones consuming this site, is there
any way for the site to *get paid*?

This is the deepest open question in the whole discussion. The traditional way
most free content (news, journalism, blogs) makes money is:

```
human visits page  →  sees an advertisement  →  publisher earns money
```

But if an agent reads the page, distils it, and hands the answer to the person —
who never visits and never sees the ad — that chain breaks:

```
agent reads page  →  gives person the answer  →  no visit, no ad seen, no money
```

So this row asks whether the site has *any* business model that still works in an
agent-mediated world. A site can be perfectly readable by agents and still be
quietly going broke; this row catches that.

> **Paywall.** A barrier requiring payment or a subscription to see content. The
> question for agents is whether an *authorised* agent (one acting for a paying
> subscriber) can get through it cleanly.

> **Content licence / AI-access program.** A formal arrangement letting an AI
> company use the site's content in exchange for payment. New marketplaces and
> services (and the pay-per-crawl idea from Row 2) exist to broker exactly this.

> **Metered/paid API.** An API (see Row 1) that charges per use. This lets a site
> earn money directly from machine access, with no human pageview required —
> arguably the cleanest fit for an agent-driven web.

**What the auditor checks:**
- Is there a paid or metered API?
- Is there a content-licensing or AI-access program?
- Is there a paywall an authorised agent could pass through?
- Is there any monetisation that survives without a human pageview?

---

## 6. My interpretation of the table

Six rows can blur together. Here is the structure I read underneath them, and
why I think the table is well-chosen.

### The rows answer three different questions

The six dimensions are not a flat list — they fall into three groups, matching
the three things an agent has to be able to do.

| Group        | Rows                                   | The question it answers          |
| ------------ | -------------------------------------- | -------------------------------- |
| **Read**     | 1 Agent-readable docs, 3 Structured data | Can the agent *get the content*? |
| **Trust**    | 2 Permissioning, 5 Freshness           | *Is it allowed, current, real?*  |
| **Transact** | 4 Commerce readiness, 6 Monetization   | Can the agent *act*, and does the site *get paid*? |

That mirrors the podcast's central split between two jobs: **serving information**
(read + trust) and **agentic commerce** (transact). A site can be excellent at
one group and useless at another — a news site might ace Read and Trust but have
no Transact story at all, while a shop might be the reverse.

### Easy rows versus hard rows

The six are not equally easy to measure, and being honest about that matters.

- **Cheap to check (Rows 1, 2, 3, 5):** these need only simple automated visits
  and reading of files and page code. A first version of the tool can do them
  well and reliably.
- **Hard to check (Rows 4 and 6):** truly verifying that an agent can *buy*
  something, or that the site *earns* from agents, would mean actually
  transacting. A realistic tool therefore scores these on **whether the
  capability is declared** — does the endpoint, policy, or programme exist? — not
  on a proven end-to-end purchase. The tool should say plainly which rows are
  measured directly and which are inferred, so the score is not oversold.

### Where the real signal is

Rows 1, 2, 3, and 5 are increasingly easy for any site to satisfy — adding an
`llms.txt` file or some structured-data labels is a small job. Because they are
easy, they will become common, and a high score there will soon say little.

The rows that genuinely separate one site from another are **4 (Commerce
readiness)** and **6 (Monetization)** — because they are *hard to fake*. Letting
an agent actually transact, or actually paying the source for what it consumes,
requires real infrastructure and a real business decision. If this tool is going
to tell people something they could not already guess, that "something" lives in
rows 4 and 6.

### Why the framing works

Calling it "Lighthouse for the agent web" is more than a slogan. Lighthouse
succeeded because it turned a vague worry ("is my site good?") into a concrete
score with a fix list. This table does the same for a newer, vaguer worry
("is my site ready for AI?"). The six dimensions convert that worry into
something you can measure, rank, and act on — which is exactly what makes a tool
useful rather than merely interesting.

---

## 7. One-paragraph summary

The Agent Readiness Auditor scores a website on how usable it is to AI agents
rather than to humans. Its six dimensions sort into three jobs an agent must do —
**read** the content (agent-readable docs, structured data), **trust** it
(permissioning, freshness), and **transact** with the site while letting the site
get paid (commerce readiness, monetization). The first four-ish dimensions are
easy to check and will soon be common; the real, hard-to-fake signal is whether
an agent can actually do business on the site and whether the site earns anything
when agents — not humans — are the ones consuming it.

---

## 8. Which checks can actually be built? (feasibility)

Section 5 lists 25 individual checks across the six rows. A fair question before
building anything is: *how many of these can a program actually perform from the
outside and get a meaningful answer?* "From the outside" matters — the auditor
visits a site as a stranger, the same way an agent would. It cannot log into the
site's admin panel or read its private code. It only sees what any visitor sees.

Two new terms make the rest of this section readable.

> **Deterministic check.** A check that gives the same clear yes/no every time,
> from a single fetch or a direct read of the page. "Does `/robots.txt` exist?"
> is deterministic — you ask, you get a definite answer.

> **Heuristic / proxy check.** A check that *guesses* using indirect clues
> because the real thing cannot be measured directly. It returns a useful signal
> but with false alarms and misses. "This page carries a `Product` label, so an
> agent can *probably* read its price" is a proxy — helpful, but not proof.

A few more terms are defined in boxes where they first appear below.

### The three tiers

I sorted every check into one of three tiers by how well it can be built.

- **Tier A — Build it, trust it.** Deterministic. One fetch or one parse of the
  page gives a clear, meaningful result. These are the auditor's solid core.
- **Tier B — Build it, but as a proxy.** Implementable and worth doing, but the
  result is a *clue*, not a verdict. It will sometimes say "no" when the answer
  is really "yes, just done in a way I can't see." Useful if reported honestly.
- **Tier C — Can't really do it from outside.** Either it needs you to actually
  transact (buy something), or it needs aggressive probing that would abuse the
  site, or it is a human judgement rather than a measurement. An automated tool
  cannot return a trustworthy result here.

### The full verdict, check by check

| # | Row | Check (shortened) | Tier | Why |
|---|-----|-------------------|------|-----|
| 1 | 1 Docs | `llms.txt` exists and is well-formed | **A** | One fetch of `/llms.txt`. Format is a loose convention, so "well-formed" is partial — existence is rock-solid. |
| 2 | 1 Docs | Current `sitemap.xml` | **A** | One fetch of `/sitemap.xml` (and `robots.txt` names it). "Current" = read the dates inside. |
| 3 | 1 Docs | Content in raw page vs JavaScript-only | **A** | Fetch the raw page, then fetch it again through a *headless browser*; compare the text. Reliable. |
| 4 | 1 Docs | Markdown / plain-text versions exist | **B** | No universal rule for where these live. You probe common patterns and use *content negotiation*; you find some, miss others. |
| 5 | 1 Docs | Public API with usable docs | **B** | You can find an API spec at common locations; judging whether docs are "usable" is not automatable. Finds the obvious, misses the rest. |
| 6 | 2 Perms | `robots.txt` exists and names AI bots | **A** | Fetch and text-match known AI bot names. Exact. |
| 7 | 2 Perms | Allows or blocks those bots | **A** | Parse the allow/deny rules. Exact. |
| 8 | 2 Perms | Rate-limit signals clear | **C** | The "429 / slow down" reply only appears once you *exceed* the limit. Detecting it means hammering the site — rude and unreliable. |
| 9 | 2 Perms | Stated licence for automated/AI use | **B** | Machine-readable licences (a `tdmrep.json` file, licence meta tags) are checkable; a licence buried in prose terms-of-service is not. |
| 10 | 2 Perms | Pay-per-crawl / bot-management present | **B** | You can detect the *CDN* and some headers; knowing pay-per-crawl is actually switched on is partial. |
| 11 | 3 Data | JSON-LD / microdata blocks and their types | **A** | Parse the page for these blocks — this is exactly what Google's structured-data testers do. Strong. |
| 12 | 3 Data | OpenGraph tags present | **A** | Read the `og:` meta tags. Exact. |
| 13 | 3 Data | Machine-readable product feed | **B** | No standard location for the feed; detecting `Product` labels on pages is a fair proxy. |
| 14 | 3 Data | Coverage across important pages | **A** | Sample many pages via the sitemap, run check 11 on each, report the percentage. Solid given a crawl budget. |
| 15 | 4 Commerce | Read product/price/stock programmatically | **B** | True only if there's an API (hard to confirm) — but `Offer`/availability labels are a strong proxy. |
| 16 | 4 Commerce | Stable cart/checkout endpoints, not CAPTCHA-walled | **B** | You can detect a *CAPTCHA* script on the page; you cannot confirm "stable endpoints" without trying to buy. Partial. |
| 17 | 4 Commerce | Supports an agent-payment standard | **B** | Upgraded — several of these standards *do* leave a discoverable surface (see "Detecting agent-commerce protocols" below). Presence is detectable; absence is not proof. |
| 18 | 5 Fresh | Publish/modified dates, machine-readable | **A** | Read `datePublished`/`dateModified` labels and `<time>` tags. Exact. |
| 19 | 5 Fresh | `Last-Modified` and `ETag` headers set | **A** | Read the response headers. Exact. |
| 20 | 5 Fresh | Canonical URL declared | **A** | Read the `<link rel="canonical">` tag / header. Exact. |
| 21 | 5 Fresh | Caching signals clear | **A** | Read the `Cache-Control` / `Expires` headers. Exact. |
| 22 | 6 Money | Paid or metered API | **C** | From outside you cannot tell whether an API charges per use. Not measurable. |
| 23 | 6 Money | Content-licensing / AI-access program | **B** | Detectable *if* declared in a machine-readable file or via a known provider; otherwise invisible. |
| 24 | 6 Money | Paywall an authorised agent could pass through | **B** | You can detect that a paywall *exists*; whether an authorised agent gets through cleanly needs real credentials. Presence only. |
| 25 | 6 Money | Monetisation that survives without a pageview | **C** | This is an interpretation of the business model, not something on the page. A judgement, not a check. |

> **Headless browser (check 3).** A real web browser engine running without a
> visible window, driven by a program. The auditor needs one to see content that
> only appears *after* a page's JavaScript runs — a plain fetch would miss it.

> **Content negotiation (check 4).** A built-in web mechanism where the visitor
> says "I'd prefer this format" (for example, "give me Markdown if you have it")
> and a well-set-up site can answer with that version. The auditor can ask, but
> most sites don't offer alternatives, so a "no" is often inconclusive.

> **CDN — Content Delivery Network (check 10).** A company (Cloudflare, Fastly,
> Akamai) whose servers sit in front of a website to speed it up and filter
> traffic. Its presence is easy to spot from the response, and CDNs are where
> bot-charging features like pay-per-crawl live.

> **`tdmrep.json` / machine-readable licence (checks 9, 23).** "TDM" means *text
> and data mining* — exactly what AI systems do when they read a site. A small
> standard file lets a site state, in a form machines can read, whether that use
> is allowed or reserved. Only sites that publish one can be scored on it.

### Detecting agent-commerce protocols (this upgrades check #17)

Check #17 — "does the site support an agent-payment standard?" — was originally
rated Tier C, on the assumption that these standards leave no detectable trace.
That was too pessimistic. Several of the leading standards adopted the
`/.well-known/` discovery pattern, which means a crawler *can* spot them. The
split depends entirely on whether a protocol **announces itself on the merchant's
own site** or **onboards through a platform** (out-of-band — see Section 8 intro).

The leading standards, as of early 2026:

> **A2A — Agent2Agent.** An open standard (Google, now under the Linux
> Foundation) for AI agents to find and delegate work to each other. It is the
> base layer several payment standards build on.

> **AP2 — Agent Payments Protocol.** Google-led, with Mastercard, PayPal, and
> others. It is an *extension* of A2A: it adds cryptographically signed "mandates"
> that authorise an agent to pay.

> **UCP — Universal Commerce Protocol.** Google's merchant-capability standard;
> agents discover what a merchant can do via a `/.well-known/ucp` endpoint.

> **x402.** Coinbase's standard that revives the long-dormant HTTP status code
> **402 Payment Required**: a protected resource answers a request with a 402 and
> a machine-readable description of how to pay.

> **ACP — Agentic Commerce Protocol.** OpenAI + Stripe (+ Meta). Powers ChatGPT's
> "Instant Checkout." Its discovery is **centralised through merchant onboarding**
> with OpenAI, so it is the main one *not* visible from a site crawl.

Here is the concrete probe list — what the auditor would actually do for each:

| Protocol | What the auditor probes | A positive signal looks like | Detectable? |
|----------|-------------------------|------------------------------|-------------|
| **A2A** | `GET /.well-known/agent-card.json` (fall back to legacy `/.well-known/agent.json`) | HTTP 200 with a valid JSON "agent card"; A2A servers are *required* to publish one | **Yes — high** |
| **AP2** | Inside that agent card, read `capabilities.extensions` | The list contains the AP2 extension URI `https://github.com/google-agentic-commerce/ap2/tree/v0.1` | **Yes — high (if A2A present)** |
| **UCP** | `GET /.well-known/ucp` | HTTP 200 with a capability document | **Yes — high** |
| **x402** | Request a known protected/paid endpoint and inspect the response | HTTP **402** plus the `PAYMENT-REQUIRED` header / an `accepts[]` JSON body describing the payment | **Partial — need an endpoint to hit** |
| **ACP** | (no public discovery path) | Nothing on the site; you could only *infer* it from a published OpenAI product feed, if any | **Mostly no — out-of-band** |
| **MCP** | Probe emerging `/.well-known` patterns | Varies; discovery is not yet standardised for websites | **Weak** |
| **Visa Intelligent Commerce / Mastercard Agent Pay** | (nothing on the merchant page) | Token issuance happens inside the card networks | **No — network-side** |

> **`capabilities.extensions` (AP2 row).** A list *inside* the A2A agent card
> where an agent declares the optional add-ons it supports. AP2 is declared here
> by its fixed URI, so finding A2A first, then reading this list, tells you
> whether payments are supported — no guesswork.

The takeaway: **four of these (A2A, AP2, UCP, x402) are genuinely detectable** —
three by a single `/.well-known/` fetch, one by an HTTP-402 signature. That is
why check #17 moves from Tier C to **Tier B**. It stays at B, not A, for one
honest reason: a *positive* result is trustworthy ("this site declares AP2"), but
a *negative* result is not proof — a merchant can run ACP, or onboard payments
entirely through a platform, and show nothing on its own site.

One caveat for whoever builds this: these specs are young and moving quickly. The
exact paths and identifiers above (`agent-card.json` vs `agent.json`, the AP2
extension URI, the x402 header names) were current in early 2026 but should be
re-checked against the live specifications before the probe is written.

### What "proxy" means (and the 10 Tier-B checks spelled out)

The Tier-B checks are all **proxies**, so the word is worth pinning down.

> **Proxy.** A stand-in measurement. When you cannot measure the thing you
> actually care about, you measure something *else* that usually travels with it,
> and treat that second thing as a stand-in. Everyday example: you cannot see
> someone's bank balance, so you guess their wealth from the car they drive. The
> car is a proxy for wealth — often right, but a rich person might drive an old
> beater (the proxy says "poor" when they're rich) and someone might lease a car
> they cannot afford (the proxy says "rich" when they're broke). A proxy is a
> *clue*, not the truth.

Every Tier-B check works this way: there is a **real question** the auditor wants
answered, but it cannot see the real answer from outside — so it measures a
**visible clue** that usually correlates, and reports that. Here are all ten, as
*real question → what we actually measure → how the proxy can mislead*:

| # | Real question | Proxy we measure | How it misleads |
|---|---------------|------------------|-----------------|
| **4** | Can an agent get a clean Markdown/text version of pages? | Probe a few common URL patterns and ask via content negotiation | A site may serve clean text in a way we didn't guess → **false "no."** |
| **5** | Is there a usable public API with good docs? | Look for an API spec at common locations (`/openapi.json`, etc.) | A real, well-documented API at a non-standard path is missed; finding a spec doesn't prove the docs are actually *usable*. |
| **9** | Does the site permit automated/AI use? | Read machine-readable licence files / meta tags | A licence written only in prose terms-of-service is invisible to us → **false "no."** |
| **10** | Is pay-per-crawl / bot-charging active? | Detect the CDN and certain headers | We can see a CDN is *present*, not that the charging feature is switched *on*. |
| **13** | Is there a machine-readable product feed? | Look for `Product` structured-data labels on pages | Labels suggest a feed *could* exist; they don't confirm a real bulk feed, and a hidden feed is missed. |
| **15** | Can an agent read price/stock per item programmatically? | Read `Offer`/availability structured-data labels | Labels hint that data is machine-readable; they don't prove a queryable endpoint exists. |
| **16** | Are checkout steps open to an agent, not CAPTCHA-walled? | Detect CAPTCHA scripts on the page | We see the CAPTCHA *exists*; we can't confirm "stable endpoints" without actually trying to buy. |
| **17** | Does the site support an agent-payment standard? | Probe `/.well-known/` (A2A/AP2/UCP) and the x402 signature | A *positive* hit is trustworthy; **silence isn't** — a site can run ACP or onboard via a platform and show nothing. |
| **23** | Is there a content-licensing / AI-access program? | Detect known providers + machine-readable licence files | Only *declared* programs are visible; a private licensing deal leaves no public trace. |
| **24** | Could an authorised agent pass the paywall? | Detect that a paywall *exists* | We confirm presence, not whether an authorised agent gets through cleanly (that needs real credentials). |

Notice the pattern: nearly every proxy fails in the same direction — it produces
**false negatives.** The visible clue is absent, so the tool says "no," when the
real capability is simply present in a form the tool cannot see. A few (#16, #24)
can also over-claim if read carelessly.

**"Clearly-marked" is the rule that keeps this honest.** The report must *label*
these results as proxies, in wording that matches what was actually measured —
never inflate the clue into a verdict:

- ✅ Fair: *"No machine-readable price data detected."* (states the observation)
- ❌ Overclaim: *"This site cannot do agentic commerce."* (states a conclusion the
  proxy doesn't support)

A Tier-A check earns a flat statement of fact ("`robots.txt` blocks GPTBot" — we
read it directly). A Tier-B check only earns a hedged observation ("we found no
signal of X"), because absence of the clue is not proof of absence of the thing.
Mark them clearly and the score stays trustworthy; present them as certainties
and the tool starts lying.

### Do we need a scoring system?

Not for v1 — and probably never the weighted 0–100 kind. The instinct is to copy
Lighthouse's single headline number, but think about what is actually useful to
the person running the audit. The value is in the *individual* results — "no
`llms.txt`," "`robots.txt` blocks ClaudeBot," "no machine-readable price data
found." Those are what a site owner fixes. A headline "67/100" tells them nothing
actionable; they have to expand it back into the checklist anyway. The number is
a lossy compression of the thing that matters.

A weighted score also carries three real costs:

1. **The weights are arbitrary and you defend them forever.** Who decides
   permissioning is worth 20% and freshness 15%? Any number is a guess dressed as
   precision.
2. **It launders uncertainty** — the exact failure this section warns against.
   Averaging a Tier-A *fact* with a Tier-B *proxy* into one figure lets a
   false-negative proxy quietly drag down a number that looks authoritative,
   hiding the difference between "we read this" and "we guessed this."
3. **It implies completeness you don't have** — 3 checks aren't measurable at all
   and 10 are proxies, but one score reads as "we measured everything."

**What to ship instead is a three-state checklist:**

```
✅ pass      Tier-A fact (verified present), or a positive Tier-B hit
❌ fail      Tier-A fact: the thing is genuinely absent
—  unknown   Tier-B proxy found nothing — could be absent, could be invisible
```

…grouped by Read / Trust / Transact. If a one-line summary is wanted, use raw
counts that need no weighting and never blend tiers:

> Read 4/4 · Trust 3/4 · Freshness 4/4 · Transact: 1 signal found, 3 unknown

That is honest, free to compute, and never dresses a guess as a fact.

**When a real score would finally earn its place:** only when the checklist
cannot serve a concrete need —
- **ranking many sites against each other** (a leaderboard / bulk audit), or
- **tracking one site improving over time** ("40 → 70").

Even then, keep **two separate numbers** — a Tier-A "verified" score and a Tier-B
"signals" score, never one blended figure — and make weights **profile-based**
(a publisher weights Trust/Monetization; a shop weights Transact) rather than
universal. Until that need is real, the score is deferred.

### The bottom line, in numbers

After the check-#17 upgrade above, of the 25 checks:

- **12 are Tier A** — fully buildable today, deterministic, meaningful out of the
  box. These are checks **1, 2, 3, 6, 7, 11, 12, 14, 18, 19, 20, 21**.
- **10 are Tier B** — buildable as honest proxies; useful signals with caveats.
  These are checks **4, 5, 9, 10, 13, 15, 16, 17, 23, 24**.
- **3 are Tier C** — not meaningfully automatable from outside. These are checks
  **8, 22, 25**.

So **about half (12/25) give clean, trustworthy results immediately**, and a
further ten give useful-but-fuzzy signals — meaning **roughly 22 of 25 are worth
implementing in some form**, as long as the proxies are clearly labelled as
proxies. Only three return nothing an automated tool should claim to know.

### The honest tension this exposes

Look at *where* the tiers fall, and an awkward fact appears:

| Row group | Mostly which tier? |
| --------- | ------------------ |
| **Read** (docs, structured data) | Tier A — easy and reliable |
| **Trust** (permissioning, freshness) | Mostly Tier A, a little B |
| **Transact** (commerce, monetization) | Tier B and C — hard or impossible |

Section 6 argued that the **real, hard-to-fake signal lives in the Transact rows
(4 and 6)** — anyone can add an `llms.txt` file, but few sites can truly let an
agent buy something or pay the source. This feasibility pass shows the catch:
**the hard-to-fake rows are also the hard-to-measure rows.** The checks that
would tell you the most are exactly the ones an outside tool struggles to perform.

That is not a reason to abandon the tool — it is the most important thing to be
honest about when building it. A credible v1 should:

1. **Ship the 12 Tier-A checks first.** They are reliable and cover Read,
   Trust, and Freshness completely — already a genuinely useful product.
2. **Add the 10 Tier-B checks as clearly-marked proxies**, never dressed up as
   certainty. "We detected no machine-readable price data" is fair; "this site
   cannot do agentic commerce" is not. (This now includes the agent-commerce
   protocol probes — a declared AP2/UCP/x402/A2A surface is a real, positive
   signal; silence is not a verdict.)
3. **Leave the 3 Tier-C checks out of the automated score**, or present them as
   a manual questionnaire the site owner answers, rather than pretend to measure
   them.

The score is only worth trusting if it never claims to know what it cannot see.
