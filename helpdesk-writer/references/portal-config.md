# Portal Config

This file is the **schema** of the operator's portal configuration. The
operator copies the template below into a file the skill reads at runtime
(default `~/.helpdesk-writer/portal.md`) and fills it in for their
product. The skill ships no defaults for any of these fields — there is
no fallback.

When `~/.helpdesk-writer/portal.md` is missing or incomplete, step 1 of
the workflow (Briefing) collects the missing fields from the user and
offers to persist them.

## What goes in the operator's portal config

```yaml
portal:
  slug: customers-help            # the helpdesk platform's portal slug
  name: Acme Customers            # human-readable
  public_base_url: https://help.acme.com/customers-help  # for "see also" link resolution
  default_locale: en              # ISO code
  allowed_locales: [en, pt_BR]    # the locales this portal serves

categories:
  - slug: getting-started
    name: Getting Started
    description: Onboarding, first steps, initial setup.
  - slug: integrations
    name: Integrations
    description: How the product connects to external systems.
  - slug: troubleshooting
    name: Troubleshooting
    description: Error messages and recovery steps.
  - slug: billing
    name: Plans and Billing
    description: Quotas, upgrades, invoices.

tag_taxonomy:
  - dimension: persona
    values: [new-user, power-user, developer]
  - dimension: plan
    values: [free, starter, growth, pro]
  - dimension: type
    values: [tutorial, reference, troubleshooting, conceptual]

personas:
  - id: new-user
    description: Just signed up, has not used the core flow yet.
    register: informal-second-person   # "you", contractions ok
  - id: power-user
    description: Uses the product daily; expects efficiency over hand-holding.
    register: informal-second-person
  - id: developer
    description: Integrating via API. Tolerates jargon.
    register: technical-second-person  # "you", terms-of-art encouraged

glossary:
  - term: Workspace
    avoid: [tenant, account, org]
    first_mention_long_form: your workspace (where your team and projects live)
  - term: Customer
    avoid: [contact, lead, end-user]
    first_mention_long_form: a customer record in your workspace

reset_script: scripts/reset-sandbox.sh   # optional; used in step 3 briefing
```

The skill reads this file holistically — markdown narrative around the
YAML blocks is fine, the skill just needs the structured data.

## Field reference

### `portal`

| Field | Required | Notes |
|---|---|---|
| `slug` | yes | What the helpdesk platform identifies the portal by |
| `name` | yes | Human-readable, used in the publish-time summary |
| `public_base_url` | yes | Base URL where published articles live; used to resolve "see also" links |
| `default_locale` | yes | Used when an article's locale is not specified |
| `allowed_locales` | yes | List of ISO codes the portal accepts |

### `categories`

A flat list. Each entry needs `slug`, `name`, `description`. The
description is what the skill uses to decide which category a new
article belongs to during step 1 briefing. Be specific — vague category
descriptions lead to misfiled articles.

If categories have a parent/child hierarchy on the platform, declare
them flat here and rely on `slug` conventions (e.g. `billing/plans` and
`billing/invoices`) to express the relationship.

### `tag_taxonomy`

Each dimension is a closed list of values. The skill picks tags only from
these lists; if it needs a new tag it asks the user before publishing.
A new article's tags typically include one value per dimension that
applies.

### `personas`

Each persona declares an `id`, a one-line description, and a `register`.
The briefing step picks one persona for each article; the style guide
applies the matching register.

Available registers:

- `informal-second-person` — "you", contractions allowed, plain words.
- `formal-second-person` — "you", no contractions, careful word choice.
  Pick this for languages where the formal register is a distinct
  grammatical form (e.g. PT-BR `você` formal, ES `usted`, DE `Sie`).
- `technical-second-person` — "you", jargon and terms of art allowed.
  Use for developer-facing content.

If the operator's product needs a custom register, add it to the
operator's portal config under a new id and reference it from
`style-guide.md` in their fork of the skill.

### `glossary`

Each entry declares:

- `term` — the canonical spelling and capitalisation.
- `avoid` — synonyms the skill must not use.
- `first_mention_long_form` — optional gloss inserted in parentheses on
  the first mention of the term in an article.

The skill grep-checks every article against the `avoid` list before
publishing. See `publishing-rules.md`, pre-publish checklist.

### `reset_script`

Optional. A path to a script the operator runs (or asks the skill to
run) to restore the sandbox to a known seed state before a documentation
session. The skill never executes this without asking.

## Migration from another skill or doc system

If the operator already has a portal structure documented elsewhere
(an internal wiki, a Notion page, a YAML in another repo), point the
skill at it during the briefing — Claude can read the source and
draft a `portal.md` for the operator to review.

The skill does not have a one-shot importer for any particular platform.
The first session against a new product is by design a conversation: the
operator confirms each category, glossary term, and persona before they
become enforced rules.
