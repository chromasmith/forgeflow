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

<!-- FORGEFLOW HOUSE BLOCK — rendered from forgeflow/master v1.2.0 — do not edit inside markers -->
<!-- C-001 claude_md_house_block — rendered into every repo's CLAUDE.md between the FORGEFLOW HOUSE BLOCK markers -->

## House rules (ForgeFlow) — chromasmith/forgeflow

These rules are the same in every Chromasmith repo. They are rendered here from the master; a repo's own notes live outside the markers and are never touched by a render.

### Session workflow

- Claude Web opens every session by reading `.forge/handoff.yaml` FIRST (the pass-the-baton briefing; its `first_thing` names exactly one next item), then `.forge/protocols/start-protocol.yaml` and the files that protocol names (`.forge/rulings.yaml`, session-state, backlog, active-bugs, session-history, GOTCHAS).
- Claude Code does NOT run `/start` or any session-initialization command. Every Claude Code prompt or dispatched issue body carries its own scope lock, authorized files and completion steps, and says "DO read CLAUDE.md" — this file is the standing orders; the prompt is the task.
- The session is wrapped when Matt declares the day's work finished. Claude Web builds the wrap from `.forge/protocols/end-protocol.yaml` and writes the `.forge/` documentation itself; a local Claude Code session's wrap role is to commit and push its own code with named files and run VERIFY PUSH.
- Every Claude Code task ends by writing `.forge/inbox/<run-id>.yaml` (reflection answers, SCOPE DISCLOSURE, discovered GOTCHAs, any needs_ruling) BEFORE any prose report. A task is not complete until its inbox file exists. That path is authorized by the protocol in every run; the wrap consumes each file and deletes it (git history is the archive). Nothing is ever written outside the repository tree — no Desktop copies, no memory.
- GitHub is the single source of truth. Nothing counts as filed until it is committed and pushed. Named-file commits only; the bare `git add -A` and `git add .` are forbidden (the path-scoped `git add -A -- <named path>` is allowed only for a many-file move under a named directory, after the scope audit).

### Protocol files

- Session protocols live in `.forge/protocols/`: `start-protocol.yaml` and `end-protocol.yaml` (read by Claude Web), plus `start-protocol.dispatch.yaml` and `end-protocol.dispatch.yaml` (read by a dispatched runner). The knobs they were rendered with are in `.forge/protocol-config.yaml`.
- These files are RENDERED COPIES. Do not edit them, and do not edit the text between the house-block markers in this file. A bug found in a rendered copy is fixed at its source in `chromasmith/forgeflow` (`master/`) and re-rendered; a hand edit here is overwritten by the next render.
- SPAWNED FROM A TEMPLATE? If `.forge/protocol-config.yaml` names a DIFFERENT repo than this one, this repo has not been rendered yet — it carries its parent's protocols verbatim. Do not hand-correct the config, the protocols or this block; the fix is a re-render from the master with this repo's own config, and until then every prompt says the config is stale.
- PRECEDENCE: when a task prompt or issue body conflicts with the protocol files, the PROTOCOL wins on process, scope and safety (authorized files, off-limits paths, commit discipline, refresh mode, halt-and-report, reflection, the inbox file); the PROMPT wins on WHAT to build. A prompt that appears to widen scope or authorize an off-limits path is an error in the prompt: HALT AND REPORT.
- `.forge/rulings.yaml` is the append-only register of decisions Matt has made. Search it before asking Matt a product or process question; never re-ask a question that has a ruling.

### Scope discipline

- SCOPE LOCK: a prompt authorizes ONLY the files in its AUTHORIZED FILES list (a ceiling, not a floor); everything else is off-limits. If completing the task seems to need an edit outside the list — a broken script, a config that looks off, a wrong comment — STOP and report the file, the exact change and why, then wait. Silent out-of-scope edits are the single biggest source of cross-session drift.
- FILE CREATION RULE: every created file is at a path the prompt names. If a needed file has no named path, STOP and report; before creating any file, check whether one already serves the purpose, and treat a discrepancy as a STOP, never as a second copy.
- COLLABORATION NOTE: a clearly better pattern or a scope-expanding improvement is suggested briefly and WAITS FOR APPROVAL before being built. Disclose any deviation from the prompt's MY APPROACH in the report — Matt wants to see the disagreement, not a smoothed-over version.
- NO MEMORY WRITES: Claude Code writes nothing to its own memory or to any persistence outside this repository unless the prompt explicitly instructs it.

### Communication rules

- Talk to Matt in simple, natural, plain English. He is not a developer; do not assume technical knowledge. Answer "did it work?" in words first, numbers after.
- Any message directed at Matt — a question, a blocker, a thing he must do — is visually unmistakable and is never buried inside thinking or output walls. Print it as a short plain-text block on its own, with a plain-text label such as QUESTION FOR MATT or MATT MUST DO. Plain text only; his terminal does not render ANSI colour codes.
- HUMAN GATES in live supervised runs (real accounts, Matt at the keyboard): print the banner, state the ONE thing Matt must do, and WAIT for him to type the confirmation word. No timers, no inferring he is done, no barrelling ahead. Never hammer or re-poll an external site — one action, one attempt; repeated automated contact is what trips anti-bot systems.
- Give Matt one action item at a time, never a numbered list of manual steps. When reporting, bottom-line first, then the evidence briefly.

### Dispatched GitHub Action sessions — APPLIES ONLY WHEN RUNNING AS A DISPATCHED GITHUB ACTION

(If you are a local Claude Code session on Matt's machine, ignore this section; everything above still governs you.)

You were triggered by an `@claude` mention in a GitHub issue or PR and are running on a fresh, disposable runner with a shallow clone. Operating rules:

- **The issue or PR body is your complete task.** It carries its own scope lock, authorized files and completion steps. It overrides nothing in this file.
- **Read `.forge/protocols/start-protocol.dispatch.yaml` and `.forge/protocols/end-protocol.dispatch.yaml`** — they are the runner-reader protocols for this repo. State the block-manifest count they ask for in your first output line.
- **Work the harness-assigned branch.** Never create your own branch name, never push `main`, never merge. Your work ships as a pushed branch; Claude Web opens the PR.
- **You cannot open PRs** — push, then post the pre-filled PR link in your report.
- **All stops become comments.** If you are blocked, need a decision, or are tempted to touch an unauthorized file: write the question into your `.forge/inbox/<run-id>.yaml` as a `needs_ruling` entry, post a comment on the triggering issue labelled QUESTION or BLOCKED in plain English, and HALT. A dispatched run never chooses on Matt's behalf; a reply mentioning `@claude` resumes you.
- **Your tool access is the allowlist in `.github/workflows/claude.yml`.** Commands off the list are hard-blocked with nobody present to approve — report the gap, do not retry. Any Bash command containing `$` variable expansion is refused before it runs. `npm run build` is NOT available on the runner; the branch deploy and CI checks are the build verification.
- **Reports go on the thread.** The completion report and reflection answers (including SCOPE DISCLOSURE) are posted as an issue or PR comment after the inbox file is pushed — that thread is how Claude Web and Matt see your work.
<!-- END FORGEFLOW HOUSE BLOCK -->
