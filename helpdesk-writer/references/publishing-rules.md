# Publishing Rules

When to publish directly vs. when to leave as a draft, and the checks that
run before either. The principle: the more sensitive the content, the
stricter the review.

The actual transport call (MCP vs. HTTP, payload shape) lives in
`helpdesk-platforms.md`. This file decides **whether** to publish and
**what to verify first**.

## Decision matrix

| Article type | Default flow | Why |
|---|---|---|
| **New step-by-step / how-to** | Draft → human visual review → publish manually | Screenshots must be eyeballed by a person. A wrong image triggers tickets. |
| **Troubleshooting / error explainer** | Always draft | A poorly written error article makes the experience worse. Review before publishing. |
| **Conceptual / "what is" / FAQ** | Publish directly after chat approval | Low risk, no critical screenshots. |
| **Update to an existing article** | Draft, with a diff against the current version | Compare before overwriting live content. |
| **Format / limit reference** | Draft | A wrong number sets the wrong expectation. |
| **Article touching billing or plan commitments** | Draft, mandatory approval | Commercial promise — a wrong word becomes a problem. |

"Draft" means `status: draft` or whatever the helpdesk platform uses to
mark unpublished content. Drafts must not be reachable by the public.

## Pre-publish checklist (mandatory, draft or live)

Run every check. If any fails, fix and re-run before publishing.

1. **All evidence HTML comments removed.** Grep the final markdown:
   `grep -n '<!--' article.md` must return zero lines.
2. **All screenshots are processed** (referenced from `assets/`, not
   `raw/`).
3. **Sensitive data is blurred.** Open each `assets/*.webp` and scan it
   visually — automated checks miss things.
4. **Glossary respected.** For every term the operator's portal config
   lists under `avoid:`, grep the article: `grep -in "<avoid-term>"
   article.md` must return zero matches. Where it does match, replace
   with the canonical term.
5. **Register consistent.** Same second-person form throughout (no mixing
   formal/informal in the same article).
6. **No leftover placeholders.** `grep -inE 'TODO|FIXME|XXX|\[\.\.\.\]'`
   returns nothing.
7. **Links resolve.** Internal "see also" links use the slug pattern
   declared in the portal config and point at articles that actually
   exist (or will exist — flag the dependency to the user).
8. **Cover image present** at `assets/cover.webp`.

## Calling the transport

Refer to `helpdesk-platforms.md` for the per-platform adapter shape. The
common fields the workflow always supplies:

- `portal_slug` (from portal config)
- `category_slug` (from briefing)
- `title`
- `slug` (per slug rules in `helpdesk-platforms.md`)
- `content` — the cleaned markdown (evidence comments stripped)
- `meta.description` (≤160 chars, see `helpdesk-platforms.md`)
- `meta.tags` (per the operator's tag taxonomy)
- `status` — `draft` or `published`, per the decision matrix
- `cover_image` — path to `assets/cover.webp`
- `inline_assets` — paths to every image referenced in the markdown

If the platform requires assets to be uploaded ahead of the article
(separate CDN step), do that before the article call and substitute the
returned URLs into the markdown.

## After publishing (or creating a draft)

Return a summary in chat. Shape:

```
✓ Article created as <draft|published> on <platform>.

Title: <title>
Slug: <slug>
Edit URL: <platform edit URL>
Public URL: <if published>
Images: <N> attached from drafts/<slug>/assets/

Verified against the source code:
- <claim 1> (<path:line>)
- <claim 2> (<path:line>)
- …

Next step: <what the user should do — usually "review visually and switch
to Published">
```

The verification summary builds trust: it tells the user what claims in
the article have a code trace, so a reviewer can spot-check the high-risk
ones.

## Future direction (not implemented)

A v2 "verification mode": rerun an article's playbook periodically, diff
the new screenshots against the published assets (pixel-level), and open
an issue when the UI has drifted enough to invalidate the article. Skip
for now — note it here so it does not get reinvented from scratch later.
