# Playbook: <article topic>

Reusable recipe for generating the article "<final article title>". When
this playbook runs, it executes the walkthrough in the sandbox, captures
screenshots, and produces a draft of the article.

A playbook is opinionated about one article. If the same product feature
needs several articles (a how-to + a troubleshooting + a conceptual
explainer), write one playbook per article and cross-link them at the
bottom.

## Metadata

| Field | Value |
|---|---|
| Category slug | `<from ../references/portal-config.md>` |
| Article slug (stem) | `<lowercase-hyphenated>` |
| Persona | `<id from ../references/portal-config.md personas>` |
| Article type | `<step-by-step | troubleshooting | conceptual | reference>` |
| Publishing flow | `<draft → review → publish | publish directly>` (see ../references/publishing-rules.md) |
| Output language | `<defaults to ../references/portal-config.md default_locale>` |

## Code recon — where to look

List the specific search paths and patterns the skill should hit in step
2. Phrase them so a fresh agent can run them without context.

1. **Endpoint(s)**: grep patterns for the route/handler.
2. **Input schema**: where validation lives (zod, pydantic, etc.).
3. **Limits and constants**: file paths and constant name patterns.
4. **Error codes**: where they are defined; how they map to user-facing
   text.
5. **Feature flags or plan gates**: if relevant.

Output of this recon goes to `drafts/<slug>/recon.md`. The article must
cite each technical claim from there with `<!-- src: path:line -->`.

## Walkthrough in the sandbox

Pre-condition: the operator's sandbox is in the seed state declared in
`../references/portal-config.md`, and the skill is logged in via Playwright MCP as the
sandbox account.

### Step 1 — <action>

- Navigate to: `<route>`
- Wait for: `<element/condition>`
- Capture: `drafts/<slug>/raw/step-01-<short>.png`
- Annotation: `<none | red outline on <element> | numbered markers |
  cropped zoom | composite>`
- Notes for the article: `<one-line hint to the writer>`

### Step 2 — <action>

[same shape as step 1]

### Step N — <action>

[same shape]

## Cover image

Source: `<which step's raw capture, or a dedicated capture>`. Crop to
1280×640 with `annotate.py crop`. Filename: `assets/cover.png`.

## Article structure

Follow the matching template in `../references/style-guide.md` (step-by-step,
troubleshooting, or conceptual). The skill renders the final article in
`drafts/<slug>/article.md` keeping evidence comments. Strip them at
publish time per `../references/publishing-rules.md`.

Suggested outline for this playbook:

```markdown
# <Final article title>

<1–2 sentences on what this article gets you.>

## Before you start

- <Prerequisites>
- <Limits and accepted formats — cite from recon.md>

## Steps

### 1. <Short action>
<lead-in>
![<alt text>](assets/step-01-<short>.png)
<closing if needed>

### 2. <Short action>
...

## You're done

<one-line wrap-up + link to next article>

## Didn't work?

- <common problem> → <link to troubleshooting article>
```

## Spin-off articles

If running this playbook surfaces error codes that deserve their own
articles, list them here so future sessions know to write them:

- `<ERROR_CODE>` → suggested title "<...>", category `<slug>`
- `<ERROR_CODE>` → …

Each spin-off gets its own playbook in this directory.
