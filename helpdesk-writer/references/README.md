# helpdesk-writer

A Claude Code skill that writes user-facing helpdesk articles for a SaaS
product by cross-referencing three sources of truth — the product's
**source code** (backend + frontend), the **live UI** driven via
Playwright MCP using real account credentials, and a **voice/style
guide** — and publishes the draft to a helpdesk platform via an MCP or
HTTP transport of the operator's choice.

End-users read the output. So correctness, traceability, and human
review gates matter more than throughput.

## Installation

```bash
# 1. Copy the skill into Claude Code's skills directory
cp -r helpdesk-writer ~/.claude/skills/

# 2. Install the required MCPs
claude mcp add playwright npx @playwright/mcp@latest

# Chatwoot is the default helpdesk transport during development.
# Point at your own deployment of github.com/Neuralyn-AI/chatwoot-mcp:
claude mcp add --transport http chatwoot \
  https://chatwoot-mcp.<subdomain>.workers.dev/mcp \
  --header "Authorization: Bearer <MCP_AUTH_TOKEN>"

# 3. Install the Python dependency for screenshot annotations
pip install Pillow

# 4. Configure the operator env file (do not commit this)
cat > ~/.helpdesk-writer.env <<'EOF'
HELPDESK_WRITER_SANDBOX_URL=https://sandbox.example.com
HELPDESK_WRITER_SANDBOX_EMAIL=helpdesk-bot@example.com
HELPDESK_WRITER_SANDBOX_PASSWORD=...
HELPDESK_WRITER_REPO_BACKEND=/path/to/your-backend
HELPDESK_WRITER_REPO_FRONTEND=/path/to/your-frontend
HELPDESK_WRITER_TRANSPORT=chatwoot-mcp
HELPDESK_WRITER_OUTPUT_LANG=en
EOF

chmod 600 ~/.helpdesk-writer.env

# 5. Describe your helpdesk portal (categories, glossary, personas)
mkdir -p ~/.helpdesk-writer
# Copy the schema from references/portal-config.md and fill it in:
$EDITOR ~/.helpdesk-writer/portal.md
```

Any field not declared in the env or `portal.md` will be asked of you at
the start of the session; you can persist your answers back to the
config files when prompted.

## How to use it

Inside Claude Code, just ask:

> "Write a helpdesk article on how to create customers."

The skill activates automatically. Claude Code then:

1. **Code recon** in the configured repos — extracts limits, formats,
   error codes, conditional flows. Reads each repo's `CLAUDE.md` /
   `AGENTS.md` first to scope the search.
2. **Logs into the sandbox** via Playwright MCP.
3. **Captures and annotates** screenshots step by step.
4. **Writes the markdown** with traceable evidence comments next to each
   technical claim.
5. **Shows the draft** for you to review.
6. **Publishes as a draft** on the configured helpdesk platform after
   your explicit approval.

The skill never publishes without a human review gate.

## File layout

```
helpdesk-writer/
├── SKILL.md                       # entry point; master workflow (only .md at root)
├── references/
│   ├── README.md                  # this file — install + usage
│   ├── code-recon.md              # how to extract truth from a codebase
│   ├── ui-walkthrough.md          # Playwright MCP + sandbox conventions
│   ├── runtime-state.md           # storage state, reusable flows, per-article trace
│   ├── screenshot-conventions.md  # framing, naming, annotation types, WebP budget
│   ├── style-guide.md             # voice rules; per-project overridable
│   ├── helpdesk-platforms.md      # adapter specs + universal conventions
│   ├── portal-config.md           # shape of the operator's portal config
│   └── publishing-rules.md        # draft vs. publish + pre-flight checks
├── scripts/
│   └── annotate.py                # Pillow-based screenshot annotator
├── playbooks/
│   └── _template.md               # skeleton for a reusable per-topic playbook
└── examples/
    └── _template.md               # canonical shape of a finished article
```

## Principles

1. **Code truth > UI truth > impression.**
2. **Every technical claim has a trace** (`path:line`).
3. **Never publish without human review.**
4. **If code and UI disagree, stop and report.**
5. **Never invent.** If a feature has no corresponding code, warn the
   user instead of speculating.
6. **Speak the user's language, not the developer's.** The final
   article must not read like a GitHub issue.

## Customising

The skill is designed to be edited by the teams that install it.

- Add a new article topic → drop a playbook in `playbooks/` based on
  `_template.md`.
- Adjust the voice → edit `references/style-guide.md`.
- Add a new helpdesk platform → add an adapter doc next to
  `references/helpdesk-platforms.md` (see "Adding a new adapter" in that file).
- Change the screenshot annotation style → edit
  `references/screenshot-conventions.md` and the defaults in `scripts/annotate.py`.

The portal-specific configuration (categories, glossary, personas) lives
in the operator's `~/.helpdesk-writer/portal.md`, never in the skill
source.
