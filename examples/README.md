# Examples

This directory contains reference examples of Forge Flow in action.

## Scaffold Template

The files below show what a freshly initialized Forge Flow project looks like. These are the minimal templates created by the FORGE_INIT prompt.

### Directory structure after initialization:

    repo-root/
    ├── CLAUDE.md                          # Needs manual setup per project
    ├── CHANGELOG.yaml                     # Empty, ready for entries
    │
    └── .forge/
        ├── backlog.yaml                   # Empty work queue
        ├── session-state.yaml             # Empty session snapshot
        ├── session-history.yaml           # Empty history log
        ├── active-bugs.yaml               # Empty bug list
        ├── GOTCHAS.yaml                   # Empty friction log
        │
        ├── blueprint/
        │   ├── Blueprint.yaml             # Placeholder
        │   └── Blueprint-manifest.yaml    # Placeholder
        │
        ├── specs/
        │   ├── api-spec.yaml              # Placeholder
        │   ├── deployment.yaml            # Placeholder
        │   ├── integrations.yaml          # Placeholder
        │   └── testing.yaml               # Placeholder
        │
        └── style/
            └── tokens.yaml                # Placeholder

## FORGE_INIT Prompt

The initialization prompt creates all files and folders non-destructively (skipping anything that already exists). It asks which project repo to target, creates the structure, and commits with the message "chore: initialize .forge structure".

See [prompts/FORGE_INIT.md](../prompts/FORGE_INIT.md) for the complete prompt.

## Real-World Example: Synclips Platform

For a mature Forge Flow project with populated files, see the Synclips Platform repo (chromasmith/synclips-platform). Key stats after ~30 build sessions:

- GOTCHAS.yaml: 25 entries covering Supabase, React, CSS, and tooling friction
- session-history.yaml: 1,000+ lines documenting every session
- backlog.yaml: Active work queue with 10+ tasks across multiple priorities
- Blueprint.yaml: 2,200 lines of architecture specification
- style/tokens.yaml: 544 lines of design system tokens
- CHANGELOG.yaml: 778 lines of public-facing product wins
