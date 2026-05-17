# Style Guide

How articles read. Voice, structure, glossary handling. Tuned to make every
article in the help centre feel like part of one product, not a stitched
collection of one-offs.

The default voice below is calibrated for a non-technical end user in a
hurry. If the operator declares a different audience in their portal config,
adapt: a developer-targeted article can carry more jargon and longer
paragraphs.

## Voice rules

### Address the reader directly, in second person

In English: "you". For other output languages, use the second-person form
the operator declared in their portal config (e.g. PT-BR `você`, ES `tú`
vs `usted` per locale convention). Pick one register and use it
consistently across every article.

Avoid third-person dodges: "the user", "the customer", "the person". They
make the writing sound like a spec, not a tutorial.

### Imperative voice, action first

- ✅ "Click **New customer**."
- ❌ "The user should click on the new customer button located in the top
  right corner of the screen."

### One action per paragraph (in step-by-steps)

Do not stack three clicks in a single sentence. Each short paragraph: one
action, optionally one screenshot.

### Short sentences

If a sentence does not fit in one breath, break it.

### Anticipate the question *before* the screenshot, not after

- ✅ "If you have never created a customer, start in the **Customers** tab:"
  → [screenshot]
- ❌ [screenshot] → "Above you can see the **Customers** tab, which is
  located…"

### Do not explain the obvious

The reader is looking at the screenshot. Do not say "click the blue button
on the right labelled Save". Say "Click **Save**".

### Bold for UI labels

Anything the reader will see on the interface — button labels, screen
names, menu items, tab names — is rendered in **bold**. Makes the article
skimmable.

## Glossary

Operators maintain a glossary of canonical terms for their product in the
portal config. The skill enforces this: once a term is declared, every
article uses the same spelling and capitalisation.

A glossary entry looks like:

```yaml
- term: "Workspace"
  avoid: ["tenant", "account", "org"]
  first_mention_long_form: "your workspace (where your team and projects live)"
```

Rules when writing:

- Use the canonical `term` everywhere.
- Never use anything from `avoid:` — even if the engineering team uses
  those words internally.
- On the first mention in an article, include the `first_mention_long_form`
  in parentheses if defined; subsequent mentions can be just the term.
- If a new product concept comes up that is not in the glossary, ask the
  user before introducing a name — do not invent vocabulary.

## Standard article shapes

### Step-by-step article

```markdown
# How to [verb] [object]

One sentence on when you do this and why. Two sentences max.

## Before you start

Short bullet list of prerequisites. Skip the section if there are none.

## Steps

### 1. [Short action]

Lead-in text (1–2 sentences).

![alt text](assets/step-01.webp)

Closing sentence if needed (1 sentence).

### 2. [Short action]
…

## You're done

Short closing line. Link to a relevant next article.

## Didn't work?

2–3 common problems, each linked to a troubleshooting article.
```

### Error / troubleshooting article

```markdown
# Message: "[exact text of the error]"

## What happened

1–2 sentences in plain language. No jargon.

## Why it happened

The real cause, written from the `recon.md` evidence.

## How to fix it

Numbered steps. Short. Each step ends with the expected result.

## Still not working?

Bullets for support channels and what to send (logs, IDs, screenshots).
```

### Conceptual / "What is X" article

```markdown
# What is [concept]

One-sentence definition. Elevator pitch.

## How it works in practice

Concrete example with real names. Avoid "imagine that…".

## When to use it

Bullets of use cases.

## When NOT to use it

Limitations. Important — this is where you save support tickets later.

## Next steps

Links to related how-to articles.
```

## Error explanation formula

**What happened → Why it happened → What to do.** In that order. Plain
language.

### Bad

> "Error 429: Rate limit exceeded. The user has exceeded the per-minute
> request limit of the contracted plan."

### Good

> ## What happened
> You ran a lot of actions in a short time and the system paused for a
> few seconds.
>
> ## Why it happened
> Each plan has a per-minute limit so the service stays fast for
> everyone.
>
> ## What to do
> 1. Wait one minute and try again — that fixes it most of the time.
> 2. If it keeps happening, you may need to upgrade your plan. See the
>    limits in [Plans and quotas](link).

## Limits and formats — surface them before the steps

Whenever you document a feature, **list limits and accepted formats at the
top of the article**, before the step-by-step. Surprising the reader
mid-tutorial creates support tickets.

Typical examples:

- "Max image size: 5 MB."
- "Accepted formats: JPG, PNG, WEBP. HEIC is auto-converted."
- "You can import up to 100 records at once."
- "Available on the Growth and Pro plans."

## Tone

- Direct, not flattering. Skip "Welcome! We're so glad you're here to learn
  about our amazing product!"
- Empathetic on errors. "This usually happens when…" beats "You did it
  wrong."
- Confident. Avoid "maybe", "probably", "we believe".
- No emoji in article body — unless the product UI uses an emoji in the
  literal label, in which case quote it as-is.

## Cover image

Every article has a cover image: a 1280×640 screenshot of the feature's
main screen, **without annotations**. Details in
`screenshot-conventions.md`. Filename is always `cover.webp`.
