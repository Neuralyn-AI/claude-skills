# claude-skills

A monorepo of Claude Code **skills** maintained by Neuralyn. Each top-level
directory is one self-contained skill that can be installed independently
into `~/.claude/skills/<skill-name>/` on any maintainer's machine.

Skills share a common style, release discipline, and language policy — but
they are not interdependent. You can install one without the others.

## What is a Claude Code skill?

A skill is a markdown-driven instruction set that Claude Code loads at
session start. It tells the agent *how* to approach a specific category of
task: which steps to take, in what order, which tools to use, and where the
review gates are. Skills are invoked explicitly (e.g. `/helpdesk-writer`) or
auto-detected by Claude based on the user's request.

## Installation

```bash
# Clone this repo
git clone https://github.com/Neuralyn-AI/claude-skills.git

# Copy (or symlink) the skill you want into Claude Code's skills directory
cp -r claude-skills/helpdesk-writer ~/.claude/skills/
# or: ln -s /path/to/claude-skills/helpdesk-writer ~/.claude/skills/helpdesk-writer
```

Each skill may have additional prerequisites (MCPs, Python packages, env
files). See the skill's own `references/README.md` for the full setup
instructions.

## Skills

### `helpdesk-writer`

Writes user-facing helpdesk articles for a SaaS product. Before writing a
single line, it cross-references three sources of truth: the product's
**source code** (backend + frontend), the **live UI** driven via Playwright
MCP using real sandbox credentials, and a **voice/style guide**. Publishes
only after an explicit human review gate, via an MCP or HTTP transport
the operator configures.

**Key features:**
- Every technical claim carries a `path:line` evidence trace during drafting.
- Code truth takes precedence over UI truth; if they disagree the skill
  stops and reports instead of guessing.
- Ships product-agnostic: repo paths, credentials, helpdesk backend, and
  output language are all operator-supplied at runtime.
- Supports any helpdesk platform through a pluggable transport adapter
  (default: Chatwoot via MCP).

**Prerequisites:** Playwright MCP, Python 3 + Pillow, a helpdesk transport.

See [`helpdesk-writer/references/README.md`](helpdesk-writer/references/README.md)
for full installation and usage instructions.

---

### `ax-workflow-recall`

Reconstructs how shipped software work happened by querying a local ax graph.
It anchors on a commit, date, topic, PR, or recent project window, then asks
Claude Code to inspect the relevant sessions, skills, tool calls, subagents,
cost signals, and decisions before writing a concise workflow narrative.

**Key features:**

- Turns local agent history into a repeatable "how this shipped" brief.
- Uses `ax sessions`, `ax recall`, and optional subagent expansion instead of
  relying on memory.
- Separates generic recent activity from artifact-specific workflow recall.
- Keeps all evidence local; value depends on sessions already ingested by ax.

**Prerequisites:** ax/axctl, a running local ax database, and indexed local
Claude Code, Codex, OpenCode, Cursor, or Pi sessions.

See [`ax-workflow-recall/references/README.md`](ax-workflow-recall/references/README.md)
for installation and usage instructions.

---

## Repository conventions

| Surface | Language |
|---|---|
| Skill files (`SKILL.md`, references, playbooks, examples) | English |
| Code, comments, CLI help text | English |
| Commit messages, PR descriptions | English |
| `CLAUDE.md` files and working notes | Local-only (gitignored) |

Per-skill layout (every skill follows this structure):

```
<skill-name>/
├── SKILL.md            # entry point — the ONLY .md at the skill root
├── references/         # every other .md the skill points to
│   └── README.md       # install + usage for end teams
├── scripts/            # executables
├── playbooks/          # reusable per-topic workflows (when applicable)
└── examples/           # canonical finished output samples (when applicable)
```

## Contributing

1. Create a new top-level directory for the skill.
2. Write `SKILL.md` as the entry point (YAML frontmatter: `name`, `description`).
3. Put every other `.md` under `references/`.
4. Add the skill to the table in `CLAUDE.md` (repo root) and to this README.
5. Keep all external references (URLs, credentials, repo paths) out of the
   skill source — those go in the operator's env file.
