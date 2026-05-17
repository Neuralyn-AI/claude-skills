# Code Recon — finding the truth in the source code

This is the most important step of the skill, and the one that separates a
good article from a generic one. Before writing, find out what the code
actually does.

## Principle

**No technical claim enters the article without having been found in the
code.** Do not write "the limit is 100 items" unless you have seen a
constant like `MAX_ITEMS = 100` in the repository. Find it and cite it.

If you cannot find the evidence, two paths:

1. Report to the user ("I couldn't find this constant — can you point me to
   where it lives?")
2. Omit the claim from the article

Never guess.

## Preflight: read project-level docs first

Before running broad searches, scan each configured target repo for
project-level documentation that can scope your work:

- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` at the repo root or in a `.claude/`
  / `.agents/` directory — these usually describe architecture, module
  layout, naming conventions, and sometimes the specific feature you are
  documenting.
- `README.md` and `docs/` — useful for high-level orientation, less useful
  for hard limits and edge cases.
- Any architecture decision records (`adr/`, `decisions/`).

Use these to **narrow** the recon: which module to read, which files own
this feature, what the team's vocabulary is. Treat them as **hints, not
truth** — they drift from code over time. Every concrete claim still has to
be verified against the source it describes.

If the docs explicitly contradict the code, prefer the code and flag the
drift to the user.

## Where to look (typical patterns by layer)

The skill ships with no assumption about the product's stack. Below are
search patterns that tend to work across language and framework choices.
Adapt them to what you actually see in the repo.

### Backend / API

| What to look for | Search patterns | Why it matters |
|---|---|---|
| Input validation schemas | `zod`, `z.object`, `pydantic`, `BaseModel`, `joi`, `yup`, `class-validator`, `*Schema`, `*Input` | Defines the exact shape of accepted data: types, sizes, required fields |
| Numeric/size limits | `MAX_`, `LIMIT_`, `_LIMIT`, `const \w+ = \d+`, `MIN_`, `MAX_LENGTH` | Hard-coded limits (quotas, sizes, retries) |
| Error definitions | `throw new`, `HTTPException`, `ApiError`, `ErrorCode`, `errors.ts`, `errors.py` | Exhaustive list of errors the backend can emit |
| Error messages | `message:`, `errorCode:`, `messages.ts`, `errors.json` | Literal text the frontend renders |
| Defaults | `??`, `\|\|`, `default:`, `defaultValue`, function param defaults | Values that fill in when a field is omitted |
| Shared types | `types/`, `schemas/`, `shared/`, `packages/types` | API contracts |
| Routing | `app.get(`, `app.post(`, `@router.`, `Route`, decorators | Maps an endpoint to its handler |
| Quotas / billing | `quota`, `usage`, `plan`, `tier`, `entitlement` | Per-plan limits |

### Frontend (web app or widget)

| What to look for | Patterns | Why it matters |
|---|---|---|
| UI strings / i18n | `i18n`, `translations`, `locales/`, `t(`, `<Trans`, `.json` translation files | Literal text the end user sees — use the same wording in the article |
| Client-side validators | `react-hook-form`, `zod`, `formik`, `validate`, `pattern=` | Often stricter than the backend |
| Rendered error messages | grep for the backend's `errorCode` in the frontend | How an error actually appears to the user |
| Feature flags | `flag`, `enabled`, `experimental`, `useFeature` | Whether the feature is on for all plans/users |
| Error components | `Error`, `Toast`, `Alert`, `Snackbar` | How the error is surfaced visually |

## Search strategy

Do not try to read the repo end to end. Search in a directed way.

1. **Start from the feature name in the UI.** If the article is about
   "creating a customer", grep the frontend for the visible text or the
   route name. From the component, find the endpoint it calls. From the
   endpoint, jump to the handler in the backend.

2. **Use Glob + Grep aggressively.** Prefer exact searches over reading
   whole files:

   ```bash
   # Find the handler for an endpoint
   grep -rn "customers.*post\|POST.*customers" <backend-repo>/src

   # Find the validation schema
   grep -rn "customerSchema\|CustomerInput" <backend-repo>/src

   # Find every error this handler can throw
   grep -rn "throw\|ApiError" <backend-repo>/src/routes/customers/
   ```

3. **Follow imports.** Found the schema? Read it whole. See what it imports
   (sub-schemas, validation regexes, enums). Found the constant? See where
   it's used.

4. **Check shared types.** In monorepos, frontend and backend often share
   types. Confirm whether what you're documenting is the shared shape or a
   transformation of it.

## How to record the evidence

After the recon, create `drafts/<slug>/recon.md` with this shape:

```markdown
# Recon: <article-slug>

## Main endpoint
- POST /api/customers
  src: `backend/src/routes/customers.ts:34`

## Input schema
- `name`: string, 3–120 chars, required
  src: `backend/packages/schemas/src/customer.ts:8`
- `email`: string, RFC 5322, required
  src: `packages/schemas/src/customer.ts:11`
- `tags`: array of strings, max 10 items
  src: `packages/schemas/src/customer.ts:18`

## Limits
- Max customers per batch import: 100
  src: `backend/src/routes/customers.ts:42` (const `BATCH_LIMIT`)
- Max tags per customer: 10
  src: `packages/schemas/src/customer.ts:18`

## Possible errors
| Code | When | Rendered message (locale: en) |
|---|---|---|
| `CUSTOMER_EMAIL_DUPLICATE` | Email already exists in the workspace | "This email is already registered…" (src: `frontend/locales/en.json:142`) |
| `IMPORT_TOO_LARGE` | More than 100 rows | "Your file has too many rows…" |
| `QUOTA_EXCEEDED` | Workspace hit its plan limit | varies by plan (see `plans.ts:18`) |

## Conditional behavior
- If `tags` is omitted, defaults to `[]` and the customer is created without tags
  src: `backend/src/services/customers.ts:55`
- Customers with no email are flagged as "incomplete" and excluded from campaigns
  src: `backend/src/services/customers.ts:78`
```

This `recon.md` is the source of every technical claim in the article. Each
`<!-- src: ... -->` comment in the draft points back to a line of this
recon.

## When code and UI disagree

A common case. Real examples:

- Code allows 100 items, UI shows "max. 50" → likely a double validation;
  the UI is stricter for a good reason (or because of a bug). Stop and ask.
- Code emits `INVALID_FORMAT`, frontend shows "Unknown error" → missing
  translation. Document the message the user **actually sees**, not the one
  the code emits, and flag it so someone can fix the i18n.
- UI shows a button with no matching backend route → feature flag, mock, or
  dead feature.

In all cases: **report to the user before writing**. Do not pick a side
silently.

## What NOT to document

Some things you will find in the code that **do not belong in the article**:

- Internal endpoints (admin, debug, health checks)
- Validations that exist but are flagged for removal (TODO, deprecated)
- Implementation details the user does not see (queue choice, cache layer,
  vendor for an AI call)
- Internal error codes that never surface in the UI
- Test or dev constants (`MAX_ITEMS_DEV = 999999`)

The rule: **does the end user need this to use the product?** If not, leave
it out.
