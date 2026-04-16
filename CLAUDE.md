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

<!-- <scope-discipline v1> -->
<!-- DO NOT EDIT BETWEEN THESE MARKERS BY HAND -->
<!-- This block is managed by install-scope-discipline-repo.yaml -->
<!-- To update: edit the installer prompt, then re-run the installer -->

## Scope Discipline

Every Claude Code session in a Chromasmith project operates under a scope lock.
The prompt that kicked off this session named the files you are authorized to
create, modify, or delete. Every other file in the repository is off-limits for
this session, regardless of how tempting it is to edit.

**The rule:** If during execution you feel tempted to edit a file that was not
on the authorized list — to fix a script that won't run, to patch a helper that
looks broken, to adjust a config that seems off, to update a comment that's
wrong, to "just fix" something small while you're in the area — STOP. Do not
edit it. Instead, report:

1. The unauthorized file you wanted to edit
2. The exact change you would have made
3. Why you believed it was necessary

Then wait for instructions. Matt will either authorize the edit or redirect.

**Why this matters:** Silent edits to unauthorized files produce uncommitted
working-tree state that doesn't match what's in git, entangled commits where
code changes hide inside docs commits, and git history that lies about when
behavior changed. These failures compound across sessions and across machines.
A session that drifts silently poisons the reproducibility of every session
that follows.

**What "use the existing helpers" means:** When a prompt or a CLAUDE.md
instruction says "use the existing X helper" or "follow the pattern in Y" —
"use" means READ and CALL, never edit. "Follow the pattern" means STUDY and
REPLICATE, never edit the pattern source. If the helper has a genuine bug or
the pattern is broken, that is a STOP-and-report moment, not a fix-in-passing
moment.

**Before committing any session:**

1. Run `git status --porcelain` and compare against the authorized file list
   from the prompt.
2. If any file shows as modified/added/deleted that is not on the authorized
   list, STOP. Do not commit. Report the drift.
3. If the working tree is clean of drift, commit using NAMED FILES only.
   Never use `git add -A` or `git add .` — name every file explicitly. This
   makes silent scope drift structurally impossible to hide in a commit.

**The scope disclosure question:** At the end of every session, before
announcing done, answer honestly: "Did I modify, create, or delete any file
that was not on the authorized list?" If yes, list every such file and
explain why. If approval was obtained mid-session, note that. If no, say
so plainly. This question is non-negotiable.

Scope discipline is the single most important behavior in the Chromasmith
workflow. It is what makes multi-session, multi-machine work reproducible.
Hold the line.

<!-- </scope-discipline v1> -->
