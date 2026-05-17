# Screenshot Conventions

Patterns to keep screenshots consistent across the whole help centre.
Consistency is what makes the helpdesk feel professional.

Browser config (viewport, DPR, locale, theme) is in `ui-walkthrough.md`.
Annotation commands are run by `scripts/annotate.py`.

## File layout and naming

Inside `drafts/<slug>/`:

```
raw/      # untouched screenshots from Playwright. Never overwrite.
assets/   # processed/annotated screenshots — the ones shipped with the article.
```

Filenames in both directories use this shape:

```
step-NN-short-description.png

Examples:
step-01-dashboard-home.png
step-02-new-customer-button.png
step-03-form-filled.png
```

Two-digit step numbers (`01`, `02`, …) keep the file list sorted. The
annotated version in `assets/` keeps the same filename as its `raw/`
counterpart — never overwrite the raw file, you may need to reprocess it
with a different annotation later.

## Annotation types and when to use each

### A. Red outline on the target element (native Playwright highlight)

**When:** orient the reader with a full-screen view and call out where the
relevant element lives. Subtlest annotation — good as the first screenshot
of each step.

**How:** before capturing, call `browser_highlight` (or the equivalent
Playwright MCP tool) on the target element. The highlight injects CSS like
`border: 3px solid #E53935; border-radius: 5px;` and shows up in the
capture. After the screenshot, call `browser_remove_highlight` to clean up.

### B. Numbered markers + arrows

**When:** a step has multiple sub-elements that must be done in order
(e.g. fill three form fields, then click submit). Conveys order visually.

**How:** capture the clean screenshot, then run `scripts/annotate.py`:

```bash
python scripts/annotate.py number \
  --in raw/step-02-form.png \
  --out assets/step-02-form.png \
  --xy 250,180 --n 1

# Add more numbers to the same file, overwriting it in assets/:
python scripts/annotate.py number \
  --in assets/step-02-form.png \
  --out assets/step-02-form.png \
  --xy 250,280 --n 2
```

Coordinates come from the element's bounding box (Playwright MCP exposes
this through `browser_snapshot`, or via `getBoundingClientRect` on the
element). Position the marker **slightly overlapping** the top-left corner
of the element, not over the text or icon itself.

### C. Cropped zoom-in

**When:** small details that would disappear in a full screenshot —
toggles, status icons, badges, single numeric values.

**How:** capture full screen, then crop with padding:

```bash
python scripts/annotate.py crop \
  --in raw/step-04-toggle.png \
  --out assets/step-04-toggle.png \
  --bbox 1080,420,1250,490 \
  --padding 40
```

Leave at least 30–40 px of padding so the crop does not feel cramped. To
emphasise something inside the crop, chain with a box:

```bash
python scripts/annotate.py box \
  --in assets/step-04-toggle.png \
  --out assets/step-04-toggle.png \
  --bbox 80,30,180,90
```

### D. Mixed: outline + numbers

For complex steps that need both an outlined region and ordered
sub-actions. Combine A and B in the same screenshot:

1. `browser_highlight` the main region → screenshot.
2. `annotate.py number` for each sub-element.

### E. Blur (mask sensitive data)

**Always blur:**

- Email addresses that look real (even in a sandbox)
- Government / tax identifiers (SSN, CPF, CNPJ, VAT, etc.)
- Phone numbers, postal addresses
- Names of real end users (customers of the operator's customers)
- Tokens, long IDs, API keys
- Real billing amounts tied to a real account

**Do not blur:** fake names from a clearly synthetic seed
(`Acme Test Co.`, `Demo Customer`, `Test Product 1`). Leaving these
visible gives the screenshot a sense of realism.

```bash
python scripts/annotate.py blur \
  --in raw/step-05-profile.png \
  --out assets/step-05-profile.png \
  --bbox 150,300,500,330
```

When in doubt about whether a value is "real enough" to need blurring,
blur it.

### F. Side-by-side composite (before/after)

For transformations: initial state vs. final state. Useful in conceptual
articles ("what does feature X do to your data?").

```bash
python scripts/annotate.py composite \
  --in raw/before.png,raw/after.png \
  --out assets/comparison.png \
  --labels "Before,After"
```

Label both panels so the reader does not have to guess which is which.

## Article cover image

Every article has a cover: a screenshot of the feature's main screen,
**without annotations**, at 1280×640. Crop from a clean capture:

```bash
python scripts/annotate.py crop \
  --in raw/cover-raw.png \
  --out assets/cover.png \
  --bbox 0,80,1280,720
```

Filename is always `cover.png`.

## Test data in screenshots

Screenshots are easier to keep coherent across articles when they use a
**stable, clearly synthetic seed**. The seed itself is the operator's
responsibility — see "Test data seed" in `ui-walkthrough.md`. From a
screenshot standpoint:

- Prefer obviously-fake names that signal a demo environment.
- Keep the same set of seed entities across articles so the help centre
  feels like one coherent product, not screenshots from different
  installations.
- Avoid demo data that could be mistaken for real customers in casual
  reading — that triggers blur anxiety and slows you down.

## Reproducibility

If an article needs to be regenerated later (UI changed, screenshot went
stale), the playbook for that article must be **rerunnable** and produce
equivalent screenshots. To make that work:

- Use semantic selectors (`getByRole`, `getByLabel`, accessible names),
  not brittle XPath.
- Drive state through the reproducible seed, not via ad-hoc clicks.
- Always use the same viewport and device scale factor for the same
  article — declare them at the top of the playbook.
