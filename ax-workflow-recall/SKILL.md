---
name: ax-workflow-recall
description: Use when the user asks how a feature shipped, what made an artifact work, what happened around a commit/date/topic, or wants a workflow reconstructed from local AI coding-agent history. Requires ax/axctl, a running local ax database, and indexed sessions.
---

# ax Workflow Recall

Reconstruct the workflow behind a shipped result from local ax history. Use
ax commands to locate the relevant sessions, inspect the skill/tool/subagent
activity, and return a clear narrative of what happened.

## When to activate

Use this skill for artifact-specific reconstruction requests:

- "How did we ship this feature?"
- "What made this demo work?"
- "Extract the workflow around this commit."
- "What happened on this date?"
- "Turn the history behind this PR into a recipe."

Do not use this skill for broad status summaries such as "what did I do today?"
or "show recent activity." Those are session-listing requests, not workflow
reconstruction.

## Expected environment prerequisites

- `ax` or `axctl` is installed and available on `PATH`.
- The local ax database is running.
- Relevant sessions have already been ingested with `ax ingest`.
- The command is run from the target project when using `here` or commit-scoped
  queries.

If ax cannot connect to the database, stop and ask the operator to start ax's
local database before continuing.

## Master workflow

Execute these steps in order.

### Step 1 - Resolve the anchor

Identify the strongest anchor from the user's request:

- Commit SHA: run `ax sessions near <sha> --json`.
- Date: run `ax sessions around <date> --days=3 --json`.
- Topic or artifact name: run `ax recall "<topic>" --sources=commit --json`.
- Current repo, recent work: run `ax sessions here --days=14 --json`.

For topic mode, use recall to find candidate commits first. If several commits
look equally plausible, ask the user to choose before continuing.

### Step 2 - Select sessions

From the anchor query, choose the most relevant sessions. Prefer sessions with:

- Matching commits or file paths.
- Higher turn counts around the delivery window.
- Skill, tool, or subagent activity related to the artifact.
- Verification or repair activity near the end of the workflow.

Default to the best five sessions unless the result is obviously smaller.

### Step 3 - Inspect evidence

For each selected session, inspect details:

```bash
ax sessions show <session-id> --json
ax sessions show <session-id> --by-role
```

If a child agent appears central to the shipped result, expand it:

```bash
ax sessions show <session-id> --expand=<subagent-uuid>
```

Use `ax recall` for targeted decisions when needed:

```bash
ax recall "<keyword>" --sources=turn,commit,skill --json
```

### Step 4 - Write the workflow recall

Return the result in chat. Do not create files unless the user explicitly asks.

Use this structure:

1. **Anchor** - commit, date, topic, or project window used.
2. **Sessions inspected** - session IDs and why they mattered.
3. **Workflow arc** - ordered steps, skills, tools, and subagents.
4. **Key decisions** - user or agent choices that changed direction.
5. **Verification** - checks, reviews, or repair loops that made the result
   credible.
6. **Reusable recipe** - how to repeat the workflow next time.

## Guardrails

- Keep claims tied to ax output, commits, or session evidence.
- Mark gaps clearly when the local graph does not contain enough data.
- Do not infer hidden reasoning or unstored conversation content.
- Do not paste long transcript excerpts; quote only short evidence snippets when
  useful.
- Treat costs, routing, and skill usage as local analytics, not universal
  quality scores.

## Licensing note

This is an original wrapper skill contributed under this repository's MIT
license. It depends on the separate ax project and command-line tool, whose
source license may differ.
