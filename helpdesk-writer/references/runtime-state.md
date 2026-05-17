# Runtime State

Persistent state the skill keeps between sessions so it does not relearn the
same flow every time. Three artefacts:

| Artefact | Path | Scope | Lifetime |
|---|---|---|---|
| **Storage state** | `~/.helpdesk-writer/state/<sandbox>.json` | One sandbox account | Until the cookie expires or the sandbox rotates credentials |
| **Reusable flow** | `~/.helpdesk-writer/flows/<flow>.json` | All articles in this sandbox | Until selectors break |
| **Article trace** | `drafts/<slug>/trace.json` | One article | Lives with the draft folder forever |

The skill **never** writes secrets here. Storage state holds session cookies,
not the password; flows and traces hold selectors and URL patterns, not
credentials.

## Storage state (Playwright session)

After a successful login, dump the Playwright browser context's storage
state. Next session, load it before navigating — the user is already logged
in if the cookie is still valid.

```text
~/.helpdesk-writer/state/<sandbox-slug>.json
```

`<sandbox-slug>` is derived from the sandbox URL host (e.g.
`sandbox.example.com` → `sandbox-example-com`). One file per sandbox lets the
operator keep state for multiple environments side by side.

### How the agent uses it

1. **Before any navigation**, check if `state/<sandbox-slug>.json` exists.
   If yes, pass it to Playwright MCP as the context's `storageState` (or the
   equivalent option exposed by the MCP).
2. `browser_navigate` to the sandbox URL.
3. **Check the resulting URL**, not a screenshot. If it matches the login
   pattern declared in the operator's env (e.g. ends in `/login`,
   `/signin`, `/auth`), the session is stale → run the login flow (below).
4. If it does not match the login pattern, you are logged in — proceed.

URL-based detection is the cheap path: `browser_navigate` returns the final
URL and you can compare it against a substring or regex. **Do not** capture a
screenshot to figure out where you are. Screenshots cost tokens; URLs are
free.

After login, dump the updated storage state back to the same path. Overwrite
is fine — the file is a cache, not history.

## Reusable flows

For actions that repeat across every article (the canonical example is
**login**), record a flow once and replay it. Flows live in:

```text
~/.helpdesk-writer/flows/<flow-name>.json
```

Schema:

```json
{
  "name": "login",
  "sandbox": "sandbox.example.com",
  "captured_at": "2026-05-17T14:02:11Z",
  "steps": [
    {
      "action": "navigate",
      "url": "{SANDBOX_URL}/login",
      "wait_for": { "url_matches": "/login" }
    },
    {
      "action": "fill",
      "selector": { "role": "textbox", "name": "Email" },
      "value": "{SANDBOX_EMAIL}"
    },
    {
      "action": "fill",
      "selector": { "role": "textbox", "name": "Password" },
      "value": "{SANDBOX_PASSWORD}"
    },
    {
      "action": "click",
      "selector": { "role": "button", "name": "Sign in" }
    },
    {
      "action": "wait_for",
      "url_matches": "/dashboard",
      "timeout_ms": 8000
    }
  ],
  "post": { "save_storage_state": true }
}
```

Conventions:

- **Selectors are semantic** (`getByRole`, `getByLabel`, accessible name).
  Never raw XPath. If the agent has to fall back to text selectors, that is
  a signal the flow is brittle — note it in the flow with `"brittle": true`.
- **Placeholders in `{BRACES}`** are resolved at replay time from the
  operator's env file. Credentials never get written into the JSON.
- **`wait_for`** is required after every action that triggers navigation or
  a network round-trip. Prefer URL match or role match over fixed delays;
  fall back to `delay_ms` only when nothing else fits.
- **`api_calls`** (optional array on a step) records endpoints observed via
  `browser_network_requests` during capture. The agent uses this on replay
  to detect "the form did not submit" without taking a screenshot — if the
  expected POST never fired, something is wrong.

### When to record a flow

The first time the agent does an action that will recur. Login is the
obvious one. Others worth recording the first time they happen:

- Switching workspace / tenant
- Opening the feature's parent area (e.g. "go to Settings → Integrations")
- Resetting the sandbox seed (if there is a UI affordance for it)

A flow becomes worth recording when the next article would otherwise have
the agent rediscovering the same selectors.

### When a flow fails on replay

Two-strikes rule (mirrors the login two-failure rule in
`ui-walkthrough.md`):

1. **First failure**: re-resolve the selector once (the page may have just
   not finished loading). If the action succeeds, continue.
2. **Second failure**: stop. Report which step broke, in which flow, and
   what the current URL / visible elements are. Do not silently fall back
   to ad-hoc clicking — the user needs to know the flow drifted.

## Article trace

Per-article record of what the agent actually did to produce the
screenshots. Lives next to the draft:

```text
drafts/<slug>/trace.json
```

Same shape as a flow, with two extras:

- Each step that produced a screenshot records the raw filename, the bbox
  used for annotation, and the annotation type applied.
- The top-level object records the playbook (if any) and the article
  language, so a re-run for a different language can be detected as such.

```json
{
  "article_slug": "create-customer",
  "playbook": "playbooks/create-customer.md",
  "language": "en",
  "sandbox": "sandbox.example.com",
  "captured_at": "2026-05-17T14:18:42Z",
  "viewport": [1280, 800],
  "device_scale_factor": 2,
  "steps": [
    {
      "n": 1,
      "action": "navigate",
      "url": "{SANDBOX_URL}/customers",
      "wait_for": { "selector": { "role": "heading", "name": "Customers" } },
      "screenshot": {
        "raw": "raw/step-01-customers-list.png",
        "annotation": "outline",
        "bbox": [980, 60, 1200, 110]
      }
    }
  ]
}
```

### Why this matters for translations

When the user asks for the same article in another language, the agent
should **not re-explore the UI**. The replay path:

1. Load `trace.json` from the existing draft.
2. Switch the Playwright context's `locale` to the target language.
3. Replay each step. For UIs that translate visible text, re-capture
   screenshots into `raw/` and `assets/`. For UIs that do not (the entire
   product chrome is in one language), reuse the existing assets.
4. Re-run the writer over `recon.md` + `trace.json` with the new
   `language` field. Code recon does not change.

The same path covers "the UI changed, regenerate the screenshots" — replay
the trace; if a step fails (selector gone), surface it and let the user
decide whether to update the playbook.

### Trace vs. playbook

A **playbook** is hand-written and authoritative — the operator's intent.
A **trace** is generated and observational — what the agent actually did
on a given run. They are not the same artefact: edit the playbook to
change intent, regenerate the trace by re-running.

If a trace consistently diverges from its playbook (e.g. the agent had to
add an extra wait), surface it at the end of the run and offer to update
the playbook.
