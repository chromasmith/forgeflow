# Forge Flow 10

A specification for AI-assisted software development using natural language.

Forge Flow is not a framework, not a build system, not software you install. It is a **folder convention, a set of file schemas, and an operating methodology** for building production SaaS applications through conversational AI.

## What It Does

Forge Flow defines how project knowledge is organized so that AI coding agents (Claude Code, Claude Web, or any future LLM tool) can operate effectively on your codebase. It solves three problems:

1. **Session continuity** — AI agents are stateless. Forge Flow files carry context between sessions so work doesn't get lost or repeated.
2. **Information diet** — AI agents degrade when overloaded with context. Forge Flow uses a visibility tier system to control what an agent sees and when.
3. **Institutional memory** — Lessons learned, architectural decisions, and friction points are captured in structured files that persist across hundreds of sessions.

## How It Works

Every Forge Flow project has a `.forge/` directory containing structured YAML files that describe the project's architecture, current state, work queue, and accumulated knowledge. A `CLAUDE.md` file at the repo root serves as the entry point that tells AI agents what exists and what to read.

A human operator (the "captain") works with a planning AI (Claude Web) to craft surgical, context-minimal prompts that are handed to a coding AI (Claude Code) for execution. The coding agent reads only what it needs, builds what's asked, and reports back. At session end, all status files are updated to carry state forward.

## Specification

| Document | What It Covers |
|----------|---------------|
| [Folder Structure](docs/FOLDER_STRUCTURE.md) | Every file, where it lives, and why |
| [File Schemas](docs/FILE_SCHEMAS.md) | Complete schema for every Forge Flow file |
| [Visibility Tiers](docs/VISIBILITY_TIERS.md) | How information access is controlled |
| [Session Lifecycle](docs/SESSION_LIFECYCLE.md) | Start → Build → End session workflow |
| [Integration Points](docs/INTEGRATION_POINTS.md) | How external tools (ChromaQA, GOTCHAS, ChromaSwarm) connect |

## Quick Start

See [examples/](examples/) for a complete scaffolded project and the initialization prompt.

## Origin

Forge Flow emerged from hundreds of real build sessions across multiple SaaS products at Chromasmith LLC. Earlier versions were an ambitious module-based build system that proved too complex. Version 10 is a clean restart capturing only what survived and works daily: the folder structure, the file schemas, and the captain/agent workflow.

## License

Proprietary — Chromasmith LLC
