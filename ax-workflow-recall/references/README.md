# ax-workflow-recall

A Claude Code skill for reconstructing how shipped work happened from a local
ax graph. It is useful after a feature, PR, demo, or incident response when the
team wants a concise account of the workflow that produced the result.

## Installation

```bash
# 1. Copy the skill into Claude Code's skills directory
cp -r ax-workflow-recall ~/.claude/skills/

# 2. Make sure ax or axctl is available
ax --help

# 3. Start the local ax database if it is not already running
# Use the database start command from your ax checkout or installation.

# 4. Ingest local sessions before asking for workflow recall
ax ingest
```

The skill does not store credentials or external service configuration. It uses
only the local ax database and the project/session history already indexed
there.

## How to use it

Inside Claude Code, ask for a concrete reconstruction:

> "How did we ship the live ingest dashboard?"

Or anchor the request more directly:

> "Extract the workflow around commit 92951bb."

Claude Code then:

1. Resolves the anchor to a commit, date, topic, or project window.
2. Queries the matching ax sessions.
3. Inspects relevant session details, skills, tools, and subagents.
4. Summarizes the ordered workflow and the decisions that mattered.
5. Produces a repeatable recipe for similar work.

## File layout

```text
ax-workflow-recall/
├── SKILL.md              # entry point; workflow and guardrails
└── references/
    └── README.md         # this file; install and usage
```

## Principles

1. **Local evidence first.** Use ax output, commits, and session metadata.
2. **Reconstruct a specific result.** Do not turn generic recent activity into
   a fake recipe.
3. **Name uncertainty.** If the local graph is incomplete, say what is missing.
4. **Keep the output usable.** The final answer should help someone repeat the
   workflow, not just list events.
5. **Do not over-quote transcripts.** Use short evidence snippets only when
   they clarify a decision.

## License note

This wrapper skill is original material contributed under this repository's MIT
license. It depends on the separate ax project and command-line tool; check the
ax project for its own license before redistributing ax itself.
