# UI Walkthrough — driving the sandbox via Playwright MCP

Step 3 of the workflow. After code recon, log into the product's sandbox,
navigate the feature being documented, and capture the raw screenshots that
will back the article.

This file describes the conventions for that session. Screenshot framing,
annotation, and post-processing are in `screenshot-conventions.md`.
Persisted session, reusable flows, and per-article traces are in
`runtime-state.md` — read that before starting the walkthrough.

## Sandbox account guidance

Use a **dedicated sandbox account**, separate from any personal admin
account the user might have. The skill will click around, submit forms, and
upload files; an account used for real work should not be exposed to that.

A few defaults that tend to work:

- **High-tier or unlimited plan**, so most features are reachable from a
  single account without hitting plan-specific limits.
- **A second account on a restricted plan** when documenting plan-gated
  behaviour (e.g. "what happens when I hit the free-tier limit").
- **MFA disabled** on sandbox accounts. The skill does not automate MFA;
  if MFA is required, ask the user to log in once and pass the session.
- **Stable seed data** (see "Test data seed" below).

If the user has not declared sandbox credentials in their config and has
not provided them in the briefing, stop and ask before starting step 3.
Do not echo the credentials back in chat.

## Login flow

Login is a **reusable flow** — `runtime-state.md` covers how it is stored
and replayed. The short version:

1. **Try the cached session first.** If
   `~/.helpdesk-writer/state/<sandbox>.json` exists, load it as the
   browser context's `storageState`. Then `browser_navigate` to the
   sandbox root.
2. **Detect login state from the URL, not a screenshot.** Compare the
   final URL returned by `browser_navigate` against the operator's login
   pattern (default: ends in `/login`, `/signin`, or `/auth`). If it
   matches, the session is stale → run the login flow. If it does not,
   skip ahead.
3. **Login flow** (recorded once in `~/.helpdesk-writer/flows/login.json`,
   replayed every time it is needed):
   - `browser_navigate` → `<SANDBOX_URL>/login`
   - `browser_fill` on the email field with the configured credential
   - `browser_fill` on the password field
   - `browser_click` on the submit button
   - `browser_wait_for` a URL or element that proves login (dashboard
     URL pattern, profile menu)
   - On success, dump the updated storage state back to the cache file.
4. If the product uses SSO (Google, GitHub, etc.), the user must set up
   a sandbox account with email/password auth available, or
   pre-authenticate and hand off a session.

URL-based detection saves a screenshot's worth of tokens every time the
session is still valid — which, with the cached state, should be most of
the time.

### Two-failure rule

If login fails twice in a row, **stop**. Likely causes:

- Test account locked (rate limit)
- Password rotated and config out of date
- Sandbox is down
- Selectors changed and the login flow is broken

Report the symptom to the user and wait for instructions. Do not keep
retrying. Apply the same two-strikes rule to any other replayed flow —
see `runtime-state.md`.

## Browser config defaults

Set these on the Playwright context unless the article explicitly requires
something else:

```
viewport:           <maximum available screen resolution of the user's OS,
                     without fullscreen — query via `browser_evaluate` with
                     `{width: window.screen.availWidth, height: window.screen.availHeight}`
                     before opening the target URL and apply the result>
device_scale_factor: 2          # crisp screenshots
locale:             <article output language>
timezone:           <operator's choice; UTC is safe>
color_scheme:       light       # most products document the light theme
```

If the article documents responsive or mobile behaviour, switch viewport and
device descriptors for those screens specifically, then switch back.

## Language matching

Before starting the walkthrough, check whether the app's UI language matches
the article's output language (set in step 1). If they differ:

1. Look for a language switcher — a button, link, dropdown, or flag component
   anywhere in the UI (header, footer, account settings, profile menu).
2. If found, switch the UI to the article language before capturing any
   screenshot.
3. If no language switcher is found, stop and ask the user how to proceed
   before continuing. Do not capture screenshots in the wrong language.

## Test data seed

Articles are easier to maintain when the screenshots reference **stable
test data**. If the user already has a seed strategy, follow it. If not,
suggest one in step 1 (briefing):

- A small, fixed set of demo entities (users, products, projects, tickets —
  whatever the product's primary noun is).
- Names that do not look like real customers (avoid plausible real names,
  CPFs/SSNs/tax IDs, real email addresses).
- A label or tag on every seed entity so cleanup scripts can find them.

The skill itself does not own the seed — the user maintains a reset script
in their own project (typical name `scripts/reset-sandbox.sh`) that
restores the seed before a documentation session. Mention this script in
the briefing if it exists; offer to draft one if it does not.

## What NOT to do in the sandbox

Even a sandbox can break in ways that hurt later sessions. Avoid:

- **Destructive account-level actions** (delete workspace, delete account,
  cancel subscription) unless the article is specifically about that flow
  and the user has confirmed.
- **Plan changes** (upgrade/downgrade) — these often have billing side
  effects even in sandbox. Use a pre-provisioned second account instead.
- **Sending real emails / SMS / push** — confirm the sandbox routes
  transactional messages to a test inbox before triggering any flow that
  sends a notification.
- **Webhooks pointing at production** — verify webhook targets are sandbox
  endpoints, never production URLs.
- **Uploading real-person images, files containing real PII, or anything
  the operator has not consented to share in screenshots.**
- **Choosing a file to upload without asking.** Whenever a flow requires a
  file upload, ALWAYS stop and ask the user for the file path. Never pick,
  generate, or assume a file. Wait for the path before proceeding.

When in doubt, ask the user before clicking.

## Multi-persona walkthroughs

Some articles need more than one viewpoint — e.g. an admin invites a member,
the member receives the invite. Two ways to do this:

1. **Two browser contexts** in the same session: log in as admin in context
   A, member in context B, switch between them.
2. **Sequential sessions**: complete the admin steps, then log out and back
   in as the member, with the screenshots clearly labelled by persona.

Pick whichever keeps the screenshot sequence readable. If switching mid-flow
would be confusing, do sequential.

## Recording the trace

While walking through the feature, append each step to
`drafts/<slug>/trace.json` (schema in `runtime-state.md`). Capture the
selector, the URL it lived on, the wait condition, and the screenshot
filename. When the user later asks for the same article in another
language — or the UI changes and the article needs to be regenerated —
the trace is replayed instead of being rediscovered.

If a step matches an existing reusable flow (e.g. "go to Settings →
Integrations" already lives in `flows/`), reference the flow by name in
the trace step instead of duplicating its actions.

## Handing off to step 4

For every step that needs an image:

1. **Wait for full load before shooting.** Before taking any screenshot, wait
   until the page has no pending network requests and is fully rendered — use
   `browser_wait_for` with `networkidle` or equivalent. Then wait an additional
   3 seconds to allow animations, lazy renders, and deferred content to settle.
   Never capture while requests are still in flight.
2. **Scroll before shooting.** Before taking any screenshot, scroll the page
   until the element you want to show is fully visible inside the current
   viewport. Never capture a screenshot that includes content outside the
   viewport or that requires the reader to imagine off-screen areas.
3. **Verify the action worked.** After every interaction (click, form submit,
   file upload, etc.), take a screenshot and read the thumb to confirm the
   expected outcome is visible — success message, new state, navigation
   change, etc. If the screenshot does not confirm success, stop and report
   to the user before continuing.
4. Save the raw capture to `drafts/<slug>/raw/step-NN-<short>.png`.
5. Generate a thumb for your own analysis:
   `python scripts/annotate.py thumbnail --in raw/step-NN-<short>.png --out thumbs/step-NN-<short>.webp`.
   Read the thumb, not the raw — see `screenshot-conventions.md` for the
   quality budget.
6. Do not annotate yet. Step 4 runs the annotator over the raw files and
   writes the final assets as `.webp`.
