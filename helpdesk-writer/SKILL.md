---
name: helpdesk-writer
description: Writes user-facing helpdesk articles for a SaaS product by cross-referencing three sources of truth — the product's source code (backend + frontend), the live UI driven via Playwright MCP using real account credentials, and a voice/style guide — and publishes the draft to a helpdesk platform via MCP or HTTP. Use when the user asks to create, update, or draft documentation, a tutorial, a how-to, a step-by-step guide, or an article explaining a feature, error message, format, limit, or workflow. The skill captures annotated screenshots and never publishes without explicit human review.
---

# Helpdesk Writer

Produces helpdesk articles backed by technically verified information: it
cross-checks the product's source code, the live UI in a sandbox account, and
a voice guide before writing a single line. Publishes a draft to the
configured helpdesk platform.

## When to activate

Requests to write, update, or draft:

- Tutorial / step-by-step / how-to
- Explanation of a product feature, flow, or concept
- Troubleshooting article / error message explainer
- Reference for a data format, limit, or requirement
- FAQ or conceptual article

## Expected environment prerequisites

- **Playwright MCP** installed: `claude mcp add playwright npx @playwright/mcp@latest`
- **A helpdesk transport** available — an MCP server or an HTTP API the
  operator has chosen. See `references/helpdesk-platforms.md` for supported adapters.
  Chatwoot MCP is the default used during development.
- Product repositories cloned locally (backend, frontend, any other relevant
  repos).
- Python 3 with Pillow: `pip install Pillow`

The skill itself ships **no product-specific configuration**. Repo paths,
sandbox credentials, the chosen helpdesk transport, and the helpdesk portal
structure (categories, slug conventions, tag taxonomy, URL pattern) all come
from the operator — either persisted in a config file or provided at runtime
in the conversation. See "Runtime configuration discovery" below.

## Runtime configuration discovery

Before doing any work, resolve configuration in this order. Stop at the first
source that provides a given value.

1. **Env / config file.** Default location: `~/.helpdesk-writer.env` for
   simple key/value (sandbox URL, credentials, repo paths, transport choice,
   output language) and `~/.helpdesk-writer/portal.md` for the richer
   helpdesk portal structure. If the operator points you at different paths,
   use those.
2. **Runtime prompt.** For anything still missing, ask the user in the same
   round as the briefing (step 1 below). Be specific about what you need and
   why.
3. **Persistence (optional).** After collecting values at runtime, offer to
   save them to the config file so the next session does not re-ask. Do not
   write secrets to disk without confirmation.

Never hard-code credentials, repo paths, URLs, product names, portal slugs,
or category lists anywhere in the skill source.

## Master workflow

For every article request, execute these steps in order. **Do not skip
steps.** The hard rule: **no technical claim enters the article without
traceable evidence — from the code or from the UI.**

### 1. Briefing

First, check `playbooks/` for a `.md` whose name or topic matches the
request. If one exists, follow it instead of starting from scratch —
playbooks encode the steps, recon hints, and screenshot plan for that
topic.

Then, in a single round, gather:

- **Article topic and target helpdesk category.** If no portal structure
  is configured yet (see "Runtime configuration discovery"), ask the user
  to describe the portal using the schema in `references/portal-config.md`
  (portal identity, categories, tag taxonomy, personas, glossary, output
  language). Offer to persist the result.
- **Target persona.** Pick from the personas the operator declared in the
  portal config; ask if none are declared.
- **New article or update?** If update, the existing article id or slug.
- **Any missing runtime configuration** — sandbox credentials, repo
  paths, helpdesk transport choice — that step 2 and step 3 will need.
  Collect everything in one round; do not interrupt the workflow later to
  ask for a credential you could have asked for now.

If the article type is obvious from the request, infer instead of asking.
Treat secrets carefully: do not echo passwords or tokens back in chat; if
you must reference them, refer by name.

### 2. Code recon (read `references/code-recon.md`)

Before touching the UI, recon the code:

- **Preflight.** For each configured target repo, read its `CLAUDE.md` (or
  `AGENTS.md` / `GEMINI.md`) if present. These often describe architecture,
  module layout, naming conventions, and sometimes the specific feature you
  are documenting. Use them to scope the search instead of grepping the repo
  from scratch. Be aware they can drift from code; verify any concrete
  claim against the source.
- Identify the relevant files (handlers, schemas, validators, error maps,
  constants).
- Extract: accepted formats, numeric limits, exhaustive list of possible
  errors, defaults, conditional flows.
- Save findings to `drafts/<slug>/recon.md` with `path:line` for every
  piece of evidence.

If the feature has no corresponding code, **warn the user and do not
invent**.

### 3. UI walkthrough (read `references/ui-walkthrough.md` and `references/screenshot-conventions.md`)

Log into the sandbox via Playwright MCP using the credentials resolved per
"Runtime configuration discovery". For each step of the article outline:

- Navigate to the screen
- Capture a screenshot (full page or specific element, per convention)
- For native annotations: use `browser_highlight` before the screenshot when
  applicable
- Save to `drafts/<slug>/raw/step-NN.png`

If the UI contradicts the code (for example: the code allows up to 100 items
but the UI displays "max. 50"), **stop and report to the user**. It may be a
bug, a double validation, or stale documentation. Do not silently pick a side.

### 4. Image post-processing (read `references/screenshot-conventions.md`)

Run `scripts/annotate.py` to apply the right annotation for each step:

- **Red outline** (subtle overlay or native highlight): screen overview with a
  highlighted element
- **Numbered markers + arrows**: when a step has multiple sub-elements in
  sequence
- **Cropped zoom-in**: small details (toggles, icons, badges)
- **Blur**: any time test data looks real (email, tax ID, customer name)

Save the processed images to `drafts/<slug>/assets/step-NN.png`.

### 5. Article writing (read `references/style-guide.md`)

Compose the markdown following the standard structure for the article type.
Non-negotiable rules:

- Write in the configured output language, addressing the reader directly
  ("you")
- Every technical claim carries an HTML comment with its source:
  `<!-- src: backend/api/products.ts:42 — limit 100 -->`
- Every screenshot has text before (introduces what the reader will see) and
  text after (what to do next)
- Errors are explained as **what happened, why it happened, what to do** — in
  that order

### 6. Human review

Show the draft in chat (rendered markdown + list of generated screenshots).
**Never publish directly.** Wait for explicit approval.

If the user requests changes, redo the relevant steps and show again.

### 7. Publication (read `references/publishing-rules.md` and `references/helpdesk-platforms.md`)

Based on the article type, choose the mode (draft vs. publish directly).
Before upload, **strip every evidence HTML comment** from the final markdown.
Those comments are for audit, not for the reader.

Call the configured helpdesk transport (MCP server or HTTP API) with the
canonical payload defined in `references/helpdesk-platforms.md` (title,
slug, content, category, locale, status, description, tags, cover_image,
inline_assets, associated_article).

## Reference files

| File | When to read |
|---|---|
| `references/code-recon.md` | Before step 2 |
| `references/ui-walkthrough.md` | Before step 3 |
| `references/screenshot-conventions.md` | Steps 3 and 4 |
| `references/style-guide.md` | Step 5 |
| `references/helpdesk-platforms.md` | Steps 1 and 7 — platform adapters + generic publishing conventions (slug, meta, "see also") |
| `references/portal-config.md` | Step 1 — shape of the operator's portal config; what to ask when none exists |
| `references/publishing-rules.md` | Step 7 |
| `playbooks/*.md` | When the user requests an article whose topic already has a playbook |
| `examples/*.md` | For reference of the final format |

## Scripts

- `scripts/annotate.py` — image annotations (number, arrow, box, crop, blur,
  composite). Run `python scripts/annotate.py --help`.

## Draft structure

```
drafts/<slug>/
├── recon.md              # code evidence (step 2)
├── outline.md            # outline with steps (steps 1 + 2)
├── raw/                  # raw screenshots from Playwright
├── assets/               # annotated screenshots (final)
└── article.md            # article markdown (with evidence comments)
```

Keep the `drafts/<slug>/` folder even after publishing — it serves as history
and as the source for future updates.

## Principles

1. **Code truth > UI truth > impression.** In that order.
2. **Every technical claim has a trace** (`path:line`) in the draft.
3. **Never publish without human review.** Prior approval does not carry over
   to a new article.
4. **If code and UI disagree, stop and report.** Do not pick a side.
5. **Never invent.** If a feature has no corresponding code, warn the user
   instead of speculating.
6. **Speak the user's language, not the developer's.** The final article
   must not read like a GitHub issue.
