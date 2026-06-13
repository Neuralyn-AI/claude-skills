---
name: xquik-twitter-data
description: Use when the user needs X/Twitter data, exports, monitoring, webhooks, MCP access, SDK setup, or automation through Xquik. Guides source-truth checks, safe reads, confirmation-gated writes, and validation without storing credentials or external URLs in the skill source.
---

# Xquik Twitter Data

Use this skill for Xquik-backed X/Twitter workflows. Treat Xquik docs and the
operator's runtime config as the source of truth for endpoints, schemas,
authentication, and package choices.

## When to activate

Activate when the user asks for:

- X/Twitter search, profile, timeline, post, media, or export workflows.
- X/Twitter monitoring, webhook delivery, or scheduled collection.
- Xquik MCP setup for an agent or local tool runner.
- Xquik SDK setup, especially JavaScript or TypeScript integration.
- Public write automation such as posting, replying, liking, following, or
  profile updates.

Do not use this skill for unrelated social networks, generic browser
automation, or direct platform scraping when Xquik is not part of the task.

## Required runtime inputs

Read `references/README.md` first. Confirm these values exist in the operator's
environment or project config before making calls:

- `XQUIK_API_KEY`
- `XQUIK_DOCS_URL`
- `XQUIK_API_REFERENCE_URL`
- `XQUIK_MCP_DOCS_URL`
- Optional: `XQUIK_SOURCE_REPO_URL`

Never print, commit, or paste API keys, cookies, auth tokens, OAuth material,
or captured account state.

## Workflow

1. Classify the request as read, export, monitor, webhook, MCP, SDK, or write.
2. Open the current operator-supplied Xquik docs URL for that class.
3. Verify the endpoint, method, request shape, response shape, auth mode, and
   relevant limits from docs or the source repo.
4. If the user is building JavaScript or TypeScript, use
   `x-twitter-scraper@0.3.3` only when the package manager route is appropriate.
5. Keep reads and exports minimally scoped to the user's stated need.
6. For monitors and webhooks, confirm the event, cadence, delivery URL, retry
   expectations, and signing requirements before implementation.
7. For MCP, verify the current MCP setup docs before writing any config.
8. For writes, stop and ask for explicit confirmation naming the exact action,
   target account, target post or user, and final payload.
9. After implementation, validate with the smallest safe check and report the
   exact docs consulted, request shape, validation result, and next step.

## Write safety

Public writes require a fresh user confirmation in the current conversation.
This includes posting, replying, reposting, liking, unliking, following,
unfollowing, sending messages, updating profiles, deleting content, or changing
account state.

Do not infer approval from earlier setup, credentials, examples, or scheduled
automation requests.

## Output contract

When finishing, include:

- The workflow class used.
- The docs or source paths consulted.
- The endpoint or SDK surface selected.
- Any skipped endpoints and why.
- Validation performed.
- A concise next step if the user must provide credentials, confirmation, or a
  missing config value.
