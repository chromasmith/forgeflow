# forgeflow
[Project description — update this with your project's purpose]

**Owner:** Chromasmith LLC
**Stack:** [Update with actual tech stack]

---

## Key Paths
[Update with project-specific paths]

## Build Commands
[Update with project-specific build commands]

---

## .forge/ Documentation
This folder contains project specs and session documentation.

**DO NOT READ:**
- `.forge/blueprint/Blueprint.yaml` — Too large for agent context windows.

**SAFE TO READ (when relevant to your task):**
- `.forge/GOTCHAS.yaml` — Friction lessons. Check when you hit unexpected issues.
- `.forge/session-state.yaml` — Current session context
- `.forge/session-history.yaml` — Log of all past sessions
- `.forge/backlog.yaml` — Work queue
- `.forge/active-bugs.yaml` — Known bugs and their status
- `.forge/specs/api-spec.yaml` — API documentation
- `.forge/specs/deployment.yaml` — Deployment and infrastructure
- `.forge/specs/integrations.yaml` — Third-party services
- `.forge/specs/testing.yaml` — Test strategy
- `.forge/style/tokens.yaml` — Design system

**REPO ROOT (not in .forge/):**
- `CHANGELOG.yaml` — Public-facing record of product wins

---

## Conventions
- Session files (backlog, session-state, active-bugs, GOTCHAS, session-history) live ONLY in .forge/ — never at repo root
- CHANGELOG.yaml lives ONLY at repo root — never in .forge/
[Add project-specific conventions below]

---

## Current Status
[Update with current project status]
