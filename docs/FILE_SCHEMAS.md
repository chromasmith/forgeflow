# File Schemas

Complete schema definitions for every Forge Flow file. Each schema includes the YAML structure, field descriptions, write behavior, and a real-world example.

---

## CLAUDE.md

**Location:** Repo root
**Format:** Markdown
**Write behavior:** Manual edit (updated as project evolves)

### Structure

    # [Project Name]
    [One-line description of what the project is]

    **Owner:** [Name / Company]
    **Stack:** [Tech stack summary]
    **Database:** [Database details]
    **Storage:** [Storage details]

    ---

    ## Key Paths
    [Code block listing the most important directories and files]

    ## Build Commands
    [Code block with exact commands — specify which directory to run from]

    ---

    ## .forge/ Documentation
    [Directory of .forge files with DO NOT READ and SAFE TO READ guidance]

    ---

    ## Conventions
    [Project-specific coding conventions — single source of truth]

    ## MCP Profiles
    [MCP service names if applicable]

    ## Infrastructure
    [Hosting, CDN, external service details]

    ## Current Status
    [What's completed, what's next — brief]

### Key Principles

- Keep it concise enough to fit in a context window without strain
- The "DO NOT READ" section is critical — it prevents agents from consuming the Blueprint
- Conventions defined here are never duplicated in other files
- Update the Current Status section at session end so agents have immediate context

---

## CHANGELOG.yaml

**Location:** Repo root
**Write behavior:** Prepend new entries (newest first)
**Skip condition:** If nothing passes the quality gate, don't add an entry

### Schema

```yaml
entries:
  - date: YYYY-MM-DD
    slug: url-friendly-identifier
    title: "Benefit-focused headline"
    summary: "User-facing description, 1-2 sentences"
    category: feature | milestone | improvement | integration | infrastructure
    technical: "Architecture and implementation details"
    tags:
      - keyword
      - keyword
    impact: "Why it matters — business or user value"
```

### Quality Gate

Before adding an entry, ask:
1. Would a potential customer care about this?
2. Would a potential buyer (acquiring company) see this as value?
3. Is this a visible, tangible improvement to the product?

If YES to any → include. If NO to all → skip.

**Good entries:** New features shipped, architecture milestones, integrations, performance wins.
**Not changelog-worthy:** Bug fixes, dependency updates, refactors, error handling, internal tooling.

### Tone

- **title:** Confident, benefit-first, active voice. Never start with "Added" or "New."
- **summary:** Clear, accessible. One or two sentences a non-technical person understands.
- **technical:** Precise, credible, stack-aware. Name the tools, patterns, and decisions.
- **impact:** Strategic. Connect the feature to business or user value.
- **Overall voice:** Forward momentum. Competence. Active development.

### Example

```yaml
entries:
  - date: 2026-02-15
    slug: renderforge-render-orchestration
    title: "RenderForge: Render Queue and Proxy Generation Dashboard"
    summary: "Submit bulk proxy generation jobs, monitor render node health, and track job progress in real-time."
    category: feature
    technical: "New Supabase schema (render_jobs, render_nodes) with atomic job claiming, RLS, and custom enums. React dashboard with tab navigation, job queue table with detail modal, and Supabase Realtime subscriptions replacing polling."
    tags:
      - renderforge
      - render-queue
      - proxy-generation
      - supabase-realtime
    impact: "Foundation for automated render pipeline. Proxy generation is fully submittable from the UI."
```

---

## backlog.yaml

**Location:** `.forge/backlog.yaml`
**Write behavior:** Overwrite (Claude Web generates complete file each session)

### Schema

```yaml
in_progress:
  - id: XX-NNN
    name: Task name
    priority: P0 | P1 | P2 | P3
    estimate: Time estimate (e.g., "2hr", "30min")
    description: |
      What needs to be done. Multi-line description
      with enough context for a stateless agent.
    status: in_progress | blocked | prompt_ready
    notes: "Optional additional context"
    blocked_by: "What's blocking, if blocked"

backlog:
  - id: XX-NNN
    name: Task name
    priority: P0 | P1 | P2 | P3
    estimate: Time estimate
    description: |
      What needs to be done.
    status: ready | blocked
    blocked_by: "What's blocking, if blocked"
    spec_ref: "Optional reference to spec section"
    subtasks:
      - Subtask description
```

### Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| id | Yes | Project prefix + sequential number (SC-001, NT-015, CV-003). Special prefixes for subsystems (SC-ING-001 for Ingest, SC-RF-001 for RenderForge). |
| name | Yes | Short, descriptive task name |
| priority | Yes | P0 = critical/blocking, P1 = important, P2 = nice-to-have, P3 = polish |
| estimate | Recommended | Time estimate for right-sizing sessions (30min - 4hr ideal) |
| description | Yes | Enough context for a stateless agent to understand the task |
| status | Yes | Current state of the task |
| blocked_by | If blocked | What's preventing work from starting |
| spec_ref | Optional | Pointer to relevant spec section for the captain to extract |
| subtasks | Optional | Breakdown for larger tasks |
| notes | Optional | Additional context, workarounds, considerations |

### Rules

- Completed items are removed (they move to session-history.yaml)
- No "completed" section exists in backlog — it's forward-looking only
- Tasks should be right-sized: 30min - 4hr each for one Claude Code session
- Dependencies should be visible through blocked_by fields

### Example

```yaml
in_progress:
  - id: SC-OB-014
    name: "Existing Project folder browser redesign"
    priority: P1
    estimate: 4-6hr
    description: |
      Onboarding modal Existing Project mode now has folder browser integration
      with ChromaSync /inspect-project-folder endpoint. Frontend code is in place.
      Needs live testing.
    status: in-progress
    notes: "ChromaSync endpoint delivered separately."

backlog:
  - id: SC-ING-005
    name: Ingest-to-Library handoff
    priority: P1
    estimate: 2hr
    description: |
      Workflow to move ingested clips from Ingest Tool to Library.
      Create assets from approved clips, link segments as children.
    status: ready

  - id: SC-006
    name: Release management
    priority: P2
    estimate: 3hr
    status: blocked
    blocked_by: Database schema for releases table
```

---

## session-state.yaml

**Location:** `.forge/session-state.yaml`
**Write behavior:** Overwrite (fresh snapshot each session)

### Schema

```yaml
session_date: "YYYY-MM-DD"
project: project-name

milestones:
  - "Terse description of what was completed"

decisions:
  - decision: What was decided
    rationale: Why, one line
    impact: What this affects going forward

blockers:
  - "Unresolved blockers, or empty list if none"

next_steps:
  - priority: high | medium | low
    task: "Specific, actionable task"

context: |
  Critical info for the next session that doesn't fit above.
  Keep this terse — it's a handoff note, not a report.
```

### Example

```yaml
session_date: "2026-02-11"
project: synclips-platform

milestones:
  - "Fixed onboarding modal horizontal overflow"
  - "SC-GF-010 fixed — batch counter race condition replaced with atomic Postgres RPC"
  - "ESLint warnings reduced from 1 to 0"

decisions:
  - decision: Use atomic Postgres RPC for batch counter increments
    rationale: Parallel job completions can race, losing counts
    impact: New migration needs to be applied via Supabase CLI before deploying

blockers:
  - "Migration 20260211 needs to be applied via Supabase CLI"

next_steps:
  - priority: high
    task: "Apply Supabase migration for atomic batch increment RPC function"
  - priority: medium
    task: "SC-ING-008 — Build seed description inheritance in Ingest Tool"

context: |
  Focused fix session — 5 targeted changes across 3 files plus 1 new migration.
  ChromaQA passes. Pre-existing TS errors in packages/adapters are outside scope.
```

---

## session-history.yaml

**Location:** `.forge/session-history.yaml`
**Write behavior:** Append (new entry added to sessions list)

### Schema

```yaml
sessions:

  - date: YYYY-MM-DD
    duration: ~Xhr estimate
    completed:
      - Item that was finished
    commits:
      - message: "commit message"
    key_changes:
      - Significant change made
    files_modified:
      - path/to/key/file.ts
    blockers_remaining:
      - Any blockers carried forward
```

### Rules

- Never edited or truncated — append only
- Claude Web generates only the new entry; Claude Code appends it
- Will grow large over time (1,000+ lines is normal for active projects)
- Serves as the permanent completion record

---

## active-bugs.yaml

**Location:** `.forge/active-bugs.yaml`
**Write behavior:** Overwrite (only currently unresolved bugs)

### Schema

```yaml
schema_version: "1.0"
session_date: "YYYY-MM-DD"
project: project-name

active_bugs:
  - id: BUG-NNN
    summary: One-line description
    symptom: What it looks like
    context: Where/when it occurs
    severity: blocker | high | medium | low
    notes: |
      Details, workarounds, theories
```

### Rules

- Fixed bugs are removed — this is not a historical record
- If no bugs exist: `active_bugs: []`
- Bug IDs are sequential (BUG-001, BUG-002)

---

## GOTCHAS.yaml

**Location:** `.forge/GOTCHAS.yaml`
**Write behavior:** Append (new entries when friction is discovered)

### Schema

```yaml
# GOTCHAS.yaml
# Lessons learned for future Claude Code sessions in this repo

- id: GOTCHA-NNN
  date: YYYY-MM-DD
  problem: |
    What went wrong or caused friction.
  prevention: |
    How to avoid this in future sessions.
  files:
    - path/to/relevant/file.ts
  tags: [category, subcategory]
```

### Alternative Format (also valid)

Some entries use a slightly different structure that emerged organically:

```yaml
- id: GOTCHA-NNN
  date: YYYY-MM-DD
  area: component-or-domain
  severity: high | medium | low
  summary: "One-line description"
  detail: |
    Full explanation of the problem and how to avoid it.
  source: Where this was discovered
  applies_to:
    - file or context where this applies
```

### Rules

- Append only — rarely if ever deleted
- Sequential IDs (GOTCHA-001, GOTCHA-002)
- These represent permanent institutional knowledge
- AI agents read this at session start to avoid known pitfalls
- Discovered through the reflection questions at the end of each Claude Code task

---

## Blueprint.yaml

**Location:** `.forge/blueprint/Blueprint.yaml`
**Write behavior:** Manual edit (updated during planning sessions)

### Purpose

The full architecture specification for the project. Contains database schemas, processing pipelines, system design, feature specifications, and technical decisions. This file is often the largest in the project (2,000+ lines).

### Rules

- Never auto-read by AI agents (explicitly blocked in CLAUDE.md)
- The captain (Claude Web) reads it and extracts surgical sections for focused prompts
- May include version numbers (Blueprint.v8.0.yaml)
- No fixed schema — structure varies by project needs

---

## Blueprint-manifest.yaml

**Location:** `.forge/blueprint/Blueprint-manifest.yaml`
**Write behavior:** Update as features are completed

### Purpose

Tracks implementation progress against the blueprint. Maps blueprint sections to completion status.

---

## Spec Files

**Location:** `.forge/specs/[name].yaml`
**Write behavior:** Manual edit (updated as the domain evolves)

### Standard Specs

Every project should have these four:

| File | Purpose |
|------|---------|
| api-spec.yaml | API routes, request/response schemas, auth patterns |
| deployment.yaml | Environments, hosting, CI/CD, infrastructure config |
| integrations.yaml | External services, credentials, SDK usage, third-party connections |
| testing.yaml | Test strategy, coverage targets, QA patterns |

### Project-Specific Specs

Additional specs are added as needed. Examples from real projects:

- `local-processing.yaml` — Shared contract for local metadata extraction
- `dji-sidecar-discovery.yaml` — Hardware-specific data extraction specs

### Rules

- No fixed schema — structure should match the domain
- Read only when the current task touches that domain
- The captain references specific sections in focused prompts

---

## tokens.yaml

**Location:** `.forge/style/tokens.yaml`
**Write behavior:** Manual edit (updated during design sessions)

### Schema

```yaml
meta:
  project: project-name
  brand_philosophy: "Brief brand description"
  personality: Adjectives describing the brand feel
  visual_strategy: Core visual approach

colors:
  light:
    core:
      primary:
        value: "#hexcolor"
        usage: Where this color is used
    backgrounds: {}
    text: {}
    semantic: {}
  dark: {}

typography:
  fonts: {}
  scale: {}
  rules: []

spacing:
  base: 8px
  scale: {}

border_radius: {}
shadows: {}
motion: {}
components: {}

accessibility:
  standard: "WCAG 2.1 AA"
  contrast_ratios: []
  focus_state: {}
```

### Rules

- Read only during UI/styling work
- Defines the design system that AI agents should follow when building components
- Structure is flexible — include what's relevant to the project

---

## Initialization Templates

When creating a new Forge Flow project, files that don't yet have content should be initialized with these minimal templates:

```yaml
# session-state.yaml
session_date: null
project: null
milestones: []
decisions: []
blockers: []
next_steps: []
context: ""
```

```yaml
# active-bugs.yaml
schema_version: "1.0"
session_date: null
project: null
active_bugs: []
```

```yaml
# session-history.yaml
sessions: []
```

```yaml
# backlog.yaml
in_progress: []
backlog: []
```

```yaml
# GOTCHAS.yaml
# Lessons learned for future Claude Code sessions in this repo
```

```yaml
# CHANGELOG.yaml
entries: []
```
