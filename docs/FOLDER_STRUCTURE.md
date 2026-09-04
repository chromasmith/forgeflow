> **SUPERSEDED (2026-09-04).** This document describes the legacy Forge Flow 10 methodology. The live system is the **ForgeFlow Master** in [`master/`](../master/) — one master rendered per repo by `master/render.py`; see `master/BLUEPRINT.yaml`, `master/RENDER_PROCEDURE.md` and `master/registered-repos.yaml`. This file is kept for the record and is not maintained.

# Folder Structure

This document defines every file in a Forge Flow project, its canonical location, and its purpose.

## Overview

Forge Flow files live in two locations: the repository root and the `.forge/` directory. The split is intentional — it controls what AI coding agents see automatically versus what gets injected surgically through prompts.

TEMPLATE_STRUCTURE:

    repo-root/
    ├── CLAUDE.md                          # Entry point for AI agents
    ├── CHANGELOG.yaml                     # Public-facing product wins (newest first)
    │
    └── .forge/
        ├── backlog.yaml                   # Work queue — prioritized tasks
        ├── session-state.yaml             # Current session snapshot
        ├── session-history.yaml           # Rolling log of past sessions
        ├── active-bugs.yaml               # Currently unresolved bugs only
        ├── GOTCHAS.yaml                   # Friction lessons (append-only)
        │
        ├── blueprint/
        │   ├── Blueprint.yaml             # Full architecture spec (large, never auto-read)
        │   └── Blueprint-manifest.yaml    # Implementation tracking against blueprint
        │
        ├── specs/                         # Domain-specific specifications
        │   ├── api-spec.yaml              # API endpoints and schemas
        │   ├── deployment.yaml            # Infrastructure and hosting
        │   ├── integrations.yaml          # External services and third-party connections
        │   ├── testing.yaml               # Test strategy and coverage
        │   └── [project-specific].yaml    # Additional specs as needed
        │
        ├── style/
        │   └── tokens.yaml                # Design system tokens
        │
        └── chromaswarm.yaml               # (Optional) ChromaSwarm agent configuration

## Root-Level Files

These files live at the repository root because they need to be immediately visible.

### CLAUDE.md

The single most important file in a Forge Flow project. This is the first thing any AI agent reads. It contains:

- Project identity (name, owner, stack, key paths)
- Build commands (how to compile, type-check, lint)
- A directory of `.forge/` files with read/avoid guidance
- Project-specific coding conventions
- Current status summary (what's done, what's next)

**Rules:**
- Always at repo root
- Always read by AI agents at session start
- Keep concise — this file should fit comfortably in a context window
- Conventions defined here are the single source of truth (never duplicated elsewhere)

### CHANGELOG.yaml

Public-facing record of product wins, features, and milestones. Written as if a potential customer or acquirer is reading it.

**Rules:**
- Lives at repo root (it's a project artifact, not internal tooling)
- Newest entries first (prepend)
- Only changelog-worthy content passes the quality gate (see [File Schemas](FILE_SCHEMAS.md))
- Updated at session end, only when something qualifies

## Session Files (.forge/)

These are the operational heartbeat. They get read at session start and written at session end.

### backlog.yaml

The work queue. Contains prioritized tasks with IDs, estimates, descriptions, and dependency information. Divided into `in_progress` (actively being worked) and `backlog` (queued).

**Rules:**
- Overwrite each session (Claude Web generates complete file)
- Completed items are removed (they move to session-history)
- New items discovered during a session are added
- Task IDs use project prefixes (SC- for Synclips, NT- for Ntarsia, CV- for Convergible)

### session-state.yaml

A fresh snapshot of where the current/most recent session ended. Milestones achieved, decisions made, blockers, and next steps.

**Rules:**
- Overwrite each session (previous content is replaced entirely)
- This is the "resume from here" file — the first thing to read when picking up work

### session-history.yaml

Rolling log of every past session. Date, duration, what was completed, commits, key changes, files modified.

**Rules:**
- Append only (new entry added at end of sessions list)
- Never edited or truncated
- Will grow large over time — this is expected
- AI agents read it for recent context at session start but don't need the full history

### active-bugs.yaml

Contains only bugs that are currently unresolved. Not a historical record — just what's broken right now.

**Rules:**
- Overwrite each session
- Fixed bugs are removed
- New bugs are added
- If no bugs exist, the list is empty (file still exists with empty array)

### GOTCHAS.yaml

Friction lessons learned during build sessions. Things that tripped up a stateless AI agent and would trip up the next one too.

**Rules:**
- Append only (new entries added when friction is discovered)
- Rarely if ever deleted — these represent permanent institutional knowledge
- Entries are sequential (GOTCHA-001, GOTCHA-002, etc.)
- AI agents should read this at session start to avoid known pitfalls

## Reference Files (.forge/blueprint/, .forge/specs/, .forge/style/)

These files contain deep project knowledge that is only needed when a specific task requires it. They are never auto-read by AI agents — the captain injects relevant sections through surgical prompts.

### blueprint/Blueprint.yaml

The full architecture specification. Database schemas, processing pipelines, system design, feature specifications. This file is often very large (2,000+ lines, 70KB+).

**Rules:**
- Never auto-read by AI agents (explicitly blocked in CLAUDE.md)
- The captain (Claude Web) reads it and extracts only the sections relevant to the current task
- May include version numbers in filename (e.g., Blueprint.v8.0.yaml)

### blueprint/Blueprint-manifest.yaml

Tracks implementation progress against the blueprint. Which sections are built, which are pending, which have changed.

**Rules:**
- Updated as features are completed
- Serves as a high-level progress map

### specs/

Domain-specific specification files. Every project gets four standard specs, plus additional project-specific specs as needed.

**Standard specs:**
- `api-spec.yaml` — API routes, request/response schemas, auth patterns
- `deployment.yaml` — Environments, hosting, CI/CD, infrastructure
- `integrations.yaml` — External services, credentials, SDK usage
- `testing.yaml` — Test strategy, coverage targets, patterns

**Project-specific specs (examples):**
- `local-processing.yaml` — Local worker processing contracts
- `dji-sidecar-discovery.yaml` — Hardware-specific data extraction

**Rules:**
- Read only when the current task touches that domain
- Captain references specific sections in focused prompts
- Extensible — add new spec files as the project needs them

### style/tokens.yaml

Design system tokens. Colors, typography, spacing, border radius, shadows, motion, component specs, accessibility standards.

**Rules:**
- Read only when doing UI/styling work
- Referenced by AI agents when building components to ensure design consistency

## Optional Integration Files

### chromaswarm.yaml

Configuration for ChromaSwarm multi-agent sessions. Defines repo-specific rules for Prospector, Blacksmith, Crucible, and Hallmark agents. Includes scope boundaries, commit conventions, QA settings, and key paths.

**Rules:**
- Only present in repos that use ChromaSwarm
- Only read during ChromaSwarm sessions (not standard captain/agent sessions)
- References CLAUDE.md for conventions (never duplicates them)

## Files That Do NOT Belong in .forge/

The following are explicitly not part of the Forge Flow specification:

- **Source code** — lives in standard project directories
- **Node modules / dependencies** — managed by package managers
- **Environment variables / secrets** — managed by hosting platforms
- **CI/CD configs** — live at repo root (.github/workflows/, etc.)
- **ChromaQA output** — lives in .chromaqa/ (separate system)
- **ChromaSwarm friction journal** — lives at repo root (system-level, not project-level)
