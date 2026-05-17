# Helpdesk Platforms

How the workflow talks to a helpdesk backend. The skill itself is
platform-agnostic — this file lists the supported adapters and the
universal publishing conventions every adapter must respect.

Portal-specific details (categories, tag taxonomy, slug conventions,
glossary) belong in the operator's portal config, not here. See
`portal-config.md`.

## Transport model

A "transport" is the concrete way the workflow turns a finished article
into something the helpdesk platform stores. The operator chooses one in
their env file:

```
HELPDESK_WRITER_TRANSPORT=chatwoot-mcp
# or:
HELPDESK_WRITER_TRANSPORT=http
HELPDESK_WRITER_HTTP_BASE_URL=https://helpdesk.example.com/api
HELPDESK_WRITER_HTTP_TOKEN=...
```

The workflow itself does not know which transport is configured. It
gathers the canonical article payload (see "Common payload" below) and
hands it to an adapter that knows how to translate it.

## Adapters

### Chatwoot via MCP (default)

In-house MCP server at <https://github.com/Neuralyn-AI/chatwoot-mcp>.
Install with:

```bash
claude mcp add --transport http chatwoot \
  https://chatwoot-mcp.<subdomain>.workers.dev/mcp \
  --header "Authorization: Bearer <MCP_AUTH_TOKEN>"
```

The adapter uses these tools:

| Workflow step | Tool | Notes |
|---|---|---|
| Discover existing article for an update | `chatwoot_list_articles` | Filter by `locale` and `category_slug` |
| Read current content for diff | `chatwoot_get_article` | Returns full markdown; ADR 0002 of chatwoot-mcp notes that `locale` / `category_id` / `associated_article_id` are absent here — use list to get those |
| Upload each `assets/*.webp` | `chatwoot_upload_attachment` | `data_base64 + filename + content_type` (`image/webp`) for local files; returns `file_url` to embed in markdown |
| Publish a new article | `chatwoot_create_article` | Stem slug; server prepends a timestamp prefix and returns the final slug |
| Push an update | `chatwoot_update_article` | PATCHes only the fields you pass |
| Clean up a bad draft | `chatwoot_delete_article` | Optional, irreversible |

Status values are exposed as a string enum (`draft` / `published` /
`archived`) and mapped to Chatwoot's integer field by the tools. The
workflow always asks for `draft` unless `publishing-rules.md` decides
otherwise.

Categories are addressed by **id**, not slug, on Chatwoot's create/update
endpoints. The adapter resolves slug → id using
`chatwoot_list_categories` once at the start of the session and caches
the mapping. The operator's portal config supplies the slug.

### Generic HTTP API

For platforms without an MCP. The operator declares:

- `HELPDESK_WRITER_HTTP_BASE_URL` — base URL of the helpdesk API
- `HELPDESK_WRITER_HTTP_TOKEN` — bearer or API token, sent as
  `Authorization` (operator chooses the scheme in env)
- A short YAML or markdown mapping declared in the env (or alongside it)
  that maps the canonical payload fields to the platform's endpoint
  paths and field names — see "Adding a new adapter" below.

The skill performs uploads as multipart/form-data and article CRUD as
JSON.

### Adding a new adapter

To support a new platform, write a thin adapter document that answers:

1. **Auth.** Which header(s), how the operator declares the token.
2. **Article create.** Endpoint, method, payload shape, response shape,
   how `draft` vs `published` is expressed.
3. **Article update.** Endpoint, method, what fields are patch-friendly.
4. **Article list / get.** How to look up by slug or id.
5. **Asset upload.** Endpoint, multipart vs. JSON, what the response
   returns (a public URL is required for inline embedding).
6. **Delete.** Optional — used only by the cleanup decision in
   `publishing-rules.md`.

Place the adapter document next to this file (`helpdesk-platforms/<name>.md`)
and reference it from the operator's env. The workflow itself does not
change.

## Common payload

Every adapter receives this canonical shape from the workflow at publish
time. Adapter is responsible for translating field names and shapes to
the platform's API.

```yaml
title: string
slug: string                # stem slug; some platforms decorate it
content: string             # cleaned markdown, no evidence comments
description: string         # short summary, ≤160 chars
category:
  slug: string              # from the operator's portal config
  # id is resolved by the adapter at runtime
locale: string              # default from portal config, overridable per article
status: draft|published|archived
tags: [string]              # from the operator's tag taxonomy
cover_image: path           # local path to assets/cover.webp
inline_assets:              # local paths referenced inside content
  - assets/step-01.webp
  - assets/step-02.webp
associated_article: slug?   # if this is a translation of another article
```

## Universal publishing conventions

These apply to every adapter and every platform. Encode them in any new
adapter you write.

### Slug rules

- Lowercase, hyphen-separated.
- Drop stop words that don't carry meaning. Keep them when they belong
  in a how-to title (e.g. `how-to-x`).
- Keep slugs short but readable — aim for ≤50 characters.
- Slugs are **immutable** after publishing. Changing a slug breaks
  inbound links. If a title needs to change, change the title, not the
  slug.

Examples:

- ✅ `how-to-create-customers`
- ✅ `error-quota-exceeded`
- ✅ `integration-shopify`
- ❌ `step-by-step-tutorial-on-how-you-can-create-customers-in-your-workspace`

### Meta description

- ≤160 characters.
- One complete sentence; reads on its own.
- Contains the primary term a user would search for.

Example: *"Learn how to create customers in your workspace, including
the accepted fields and per-plan limits."*

### Tags

Pull tags from the operator's tag taxonomy in `portal-config.md`. Do not
invent tags on the fly; if the article needs a tag that doesn't exist,
ask the user to add it to the taxonomy first.

### "See also" links

At the end of every article, include 2–4 related articles. Use
**relative slug paths**, not absolute URLs — relative paths survive
migrations.

```markdown
## See also

- [Accepted image formats](/catalog/accepted-image-formats)
- [Plan limits](/plans-billing/limits)
```

The adapter is responsible for resolving these relative paths at publish
time (most helpdesk platforms expect either the article's full URL or
its id; the adapter looks it up). If a referenced article doesn't exist
yet, flag the dependency to the user — do not publish a broken link.

### Inline asset references

Image references in the markdown source use **local paths**:

```markdown
![dashboard home](assets/step-01-dashboard-home.webp)
```

At publish time, the adapter uploads each asset, gets back a public URL,
and substitutes the local path with the URL **only in the upload
payload**. The local markdown in `drafts/<slug>/article.md` keeps the
local paths so the article remains regenerable.
