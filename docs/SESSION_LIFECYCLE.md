> **SUPERSEDED (2026-09-04).** This document describes the legacy Forge Flow 10 methodology. The live system is the **ForgeFlow Master** in [`master/`](../master/) — one master rendered per repo by `master/render.py`; see `master/BLUEPRINT.yaml`, `master/RENDER_PROCEDURE.md` and `master/registered-repos.yaml`. This file is kept for the record and is not maintained.

# Session Lifecycle

A Forge Flow session follows a consistent three-phase pattern: Start → Build → End. This document describes each phase, who does what, and how the files are used.

## Participants

| Role | Who | Responsibilities |
|------|-----|-----------------|
| **User** | You | Describes tasks in plain English, routes friction lessons, approves work |
| **Captain** | Claude Web | Holds full project context, generates focused prompts, manages session state |
| **Agent** | Claude Code | Executes tasks with minimal context, reports friction, writes files |

## Phase 1: Session Start

### What Happens

1. User uploads the current repo ZIP to Claude Web
2. Captain extracts and indexes the repo locally
3. Captain reads all `.forge/` session files for situational awareness
4. Captain provides a Session Context Summary
5. Captain checks ChromaQA debt (if `.chromaqa/CQA-debt.jsonl` exists)
6. Captain announces "Ready for tasks"

### Session Context Summary

The captain reads these files and provides a brief summary (5-8 lines max):

- `.forge/session-state.yaml` — Where the last session left off
- `.forge/backlog.yaml` — Queued work items and priorities
- `.forge/active-bugs.yaml` — Current bugs
- `.forge/session-history.yaml` — Recent session context
- `.forge/GOTCHAS.yaml` — Friction lessons to keep in mind

Template:

    **Session Context Summary**
    - **Last session:** [date and brief description]
    - **In progress:** [any incomplete work]
    - **Active bugs:** [count and brief note if any are critical]
    - **Backlog:** [count of items, note top priority]
    - **Gotchas to keep in mind:** [any particularly relevant ones]

Missing files are skipped silently — not all repos will have all files.

### ChromaQA Debt Check

If `.chromaqa/CQA-debt.jsonl` exists and exceeds 25 entries, alert the user and wait for their decision. If file doesn't exist or is under threshold, proceed silently.

## Phase 2: Build (Repeat as Needed)

### Task Flow

1. User describes what they want in plain English
2. Captain reads relevant Tier 2/3 files (specs, blueprint, tokens)
3. Captain generates a focused prompt with:
   - Override preamble (context mode, approval code, no auto-init)
   - Repo location step (clone/pull)
   - Required context (specific files and line numbers)
   - Task description with rationale and proposed approach
   - Available tools (Supabase, Vercel, GitHub MCP access)
   - Output format (green completion message + reflection questions)
4. Captain outputs the prompt as a single fenced code block
5. User copies prompt to Claude Code
6. Agent executes the task
7. Agent answers two reflection questions
8. User reviews answers and decides whether to log friction

### The Override Preamble

Every focused prompt starts with:

    CONTEXT MODE: SELECTIVE
    APPROVAL CODE: 3949
    Do NOT run /start or any session initialization commands.
    DO read CLAUDE.md — it contains project-specific guidance.
    I am providing exactly the context you need for this task.
    Work only with what I give you below.

    COLLABORATION NOTE: I've outlined my proposed approach below.
    If you see a clearly better pattern or significant improvement,
    suggest it briefly before you build. Otherwise, dive in.

### The Two Reflection Questions

Every Claude Code task ends with:

1. **What would have made this prompt better or more effective?**
2. **Did you encounter anything that would cause a future session (with no memory of this task) to fail or waste significant time?**

These questions are the input to the GOTCHAS system. If the agent reports meaningful friction, the user triggers a GOTCHAS log entry.

### Logging Friction (GOTCHAS Flow)

When an agent's reflection answer reveals something worth preserving:

1. User says "Good work. That 'remembered for future tasks' item — log it now."
2. Agent creates or appends to `.forge/GOTCHAS.yaml` with a new entry
3. Agent commits and pushes

Alternatively, the captain can include the GOTCHAS entry in the end-session prompt.

## Phase 3: End Session

### What Happens

1. User triggers end session ("end session", "wrap up", etc.)
2. Captain identifies which project was worked on
3. Captain reads current `.forge/` files from the extracted repo
4. Captain generates updated content for each file
5. Captain outputs a single prompt for Claude Code
6. Agent writes all files, commits, and deploys

### File Update Behaviors

| File | Action | What Captain Generates |
|------|--------|----------------------|
| session-state.yaml | Overwrite | Complete file content (fresh snapshot) |
| active-bugs.yaml | Overwrite | Complete file content (reconciled) |
| backlog.yaml | Overwrite | Complete file content (completed items removed, new items added) |
| session-history.yaml | Append | Only the new session entry |
| GOTCHAS.yaml | Append (if new) | Only new entries, if any |
| CHANGELOG.yaml | Prepend (if worthy) | Only the new entry, if it passes quality gate |

### The End Session Prompt

The captain generates a single fenced code block containing:

1. Override preamble + repo location
2. All file writes with explicit OVERWRITE or APPEND instructions
3. Commit message: "docs: end session [YYYY-MM-DD] - [N] milestones"
4. Deploy step (if applicable)
5. Constraints (no proposals, no intermediate output, write exactly as provided)

### Manual Fallback

If Claude Code fails or times out on the end-session prompt, the captain provides explicit manual instructions with full GitHub URLs, complete content to paste, and step-by-step click instructions. One file at a time to avoid overwhelming the user.

## Between Sessions

The `.forge/` files carry state between sessions. When the user starts a new session (even days or weeks later), the captain reads these files and picks up exactly where things left off. The user doesn't need to re-explain context — it's all in the files.

This is the core value proposition of Forge Flow: **AI agents are stateless, but your project isn't.**
