# <Article title>

<One or two sentences on what this article gets the reader. Plain
language, no jargon. This is what shows up in search results — make it
specific.>

## Before you start

- <Prerequisite, including a link to a related article if relevant>
- <Limits and accepted formats. Cite each from recon.md with an evidence
  comment.> <!-- src: <path:line> -->

## Steps

### 1. <Short action>

<One or two sentences leading into the screenshot. Describe what the
reader will see and what to do.>

![<alt text describing what the screenshot shows>](assets/step-01-<short>.png)

<Closing sentence only if needed.>

### 2. <Short action>

<lead-in>

![<alt>](assets/step-02-<short>.png)

> **<Inline note about a non-obvious detail.>** <Plain-language
> explanation of a constraint, with the evidence comment.>
> <!-- src: <path:line> -->

### 3. <Short action>

<lead-in>

![<alt>](assets/step-03-<short>.png)

## You're done

<Confirmation that the action succeeded — what the reader should see now.>

![<alt>](assets/step-N-confirmation.png)

## See also

- [<Related article title>](/<category-slug>/<related-slug>)
- [<Related article title>](/<category-slug>/<related-slug>)

## Didn't work?

- <Common problem, in the reader's words> → [<troubleshooting article>](/<...>)
- <Common problem> → [<troubleshooting article>](/<...>)

---

This file is the canonical shape of a finished step-by-step article in
this skill. Use the same structure for new articles. Variants for
troubleshooting and conceptual articles live in `../references/style-guide.md`.

Notes for whoever writes a real article using this template:

- Replace every `<placeholder>` with concrete content from the recon and
  the walkthrough.
- Keep every evidence comment (`<!-- src: path:line -->`) until publish
  time. `../references/publishing-rules.md` strips them in the final upload payload.
- Images live in `drafts/<slug>/assets/`. The local paths in the
  markdown are substituted with public URLs by the helpdesk adapter at
  publish time — see `../references/helpdesk-platforms.md`.
- Cover image is always `assets/cover.png`, 1280×640, no annotations.
