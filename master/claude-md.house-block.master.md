<!-- C-001 claude_md_house_block — rendered into every repo's CLAUDE.md between the FORGEFLOW HOUSE BLOCK markers -->

## House rules (ForgeFlow) — {{repo.org}}/{{repo.name}}

These rules are the same in every Chromasmith repo. They are rendered here from the master; a repo's own notes live outside the markers and are never touched by a render.

### Session workflow

- Claude Web opens every session by reading `.forge/handoff.yaml` FIRST (the pass-the-baton briefing; its `first_thing` names exactly one next item), then `.forge/protocols/start-protocol.yaml` and the files that protocol names (`.forge/rulings.yaml`, session-state, backlog, active-bugs, session-history, GOTCHAS).
- Claude Code does NOT run `/start` or any session-initialization command. Every Claude Code prompt or dispatched issue body carries its own scope lock, authorized files and completion steps, and says "DO read CLAUDE.md" — this file is the standing orders; the prompt is the task.
- The session is wrapped when Matt declares the day's work finished. Claude Web builds the wrap from `.forge/protocols/end-protocol.yaml` and writes the `.forge/` documentation itself; a local Claude Code session's wrap role is to commit and push its own code with named files and run VERIFY PUSH.
- Every Claude Code task ends by writing `.forge/inbox/<run-id>.yaml` (reflection answers, SCOPE DISCLOSURE, discovered GOTCHAs, any needs_ruling) BEFORE any prose report. A task is not complete until its inbox file exists.
- GitHub is the single source of truth. Nothing counts as filed until it is committed and pushed. Named-file commits only; `git add -A` and `git add .` are forbidden.

### Protocol files

<!-- >>> render_when: not execution.dispatch.enabled -->
- Session protocols live in `.forge/protocols/`: `start-protocol.yaml` and `end-protocol.yaml`, both read by Claude Web. The knobs they were rendered with are in `.forge/protocol-config.yaml`.
<!-- <<< end render_when -->
<!-- >>> render_when: execution.dispatch.enabled -->
- Session protocols live in `.forge/protocols/`: `start-protocol.yaml` and `end-protocol.yaml` (read by Claude Web), plus `start-protocol.dispatch.yaml` and `end-protocol.dispatch.yaml` (read by a dispatched runner). The knobs they were rendered with are in `.forge/protocol-config.yaml`.
<!-- <<< end render_when -->
- These files are RENDERED COPIES. Do not edit them, and do not edit the text between the house-block markers in this file. A bug found in a rendered copy is fixed at its source in `chromasmith/forgeflow` (`master/`) and re-rendered; a hand edit here is overwritten by the next render.
- PRECEDENCE: when a task prompt or issue body conflicts with the protocol files, the PROTOCOL wins on process, scope and safety (authorized files, off-limits paths, commit discipline, refresh mode, halt-and-report, reflection, the inbox file); the PROMPT wins on WHAT to build. A prompt that appears to widen scope or authorize an off-limits path is an error in the prompt: HALT AND REPORT.
- `.forge/rulings.yaml` is the append-only register of decisions Matt has made. Search it before asking Matt a product or process question; never re-ask a question that has a ruling.
<!-- >>> render_when: subsystems.database_access_doc -->
- `{{subsystems.database_access_doc}}` is binding on every task that touches data (which roles may write, from where). Read it before any database work.
<!-- <<< end render_when -->
<!-- >>> render_when: subsystems.repo_rules_doc -->
- `{{subsystems.repo_rules_doc}}` holds this repo's own standing rules and is binding alongside this file.
<!-- <<< end render_when -->

### Scope discipline

- SCOPE LOCK: a prompt authorizes ONLY the files in its AUTHORIZED FILES list (a ceiling, not a floor); everything else is off-limits. If completing the task seems to need an edit outside the list — a broken script, a config that looks off, a wrong comment — STOP and report the file, the exact change and why, then wait. Silent out-of-scope edits are the single biggest source of cross-session drift.
- FILE CREATION RULE: every created file is at a path the prompt names. If a needed file has no named path, STOP and report; before creating any file, check whether one already serves the purpose, and treat a discrepancy as a STOP, never as a second copy.
- COLLABORATION NOTE: a clearly better pattern or a scope-expanding improvement is suggested briefly and WAITS FOR APPROVAL before being built. Disclose any deviation from the prompt's MY APPROACH in the report — Matt wants to see the disagreement, not a smoothed-over version.
- NO MEMORY WRITES: Claude Code writes nothing to its own memory or to any persistence outside this repository unless the prompt explicitly instructs it.
<!-- >>> render_when: architecture.tsx_lib_rule -->

### Architecture rule (Chromasmith house standard)

- Data access and business logic (queries, scoring, ranking, filtering, eligibility) never live in a `.tsx` file. Screens call a `/lib` function that does it; components never import a database client themselves. The mechanical test: any function still needed if this screen were deleted belongs in `/lib`. Presentational formatting helpers (labels, display strings) are display logic and may stay in components.
- If completing a task seems to require putting data access in a component, STOP and report — the authorized list is probably missing the `/lib` counterpart (paired-file rule: authorizing a data-touching screen means authorizing its `/lib` file too).
<!-- <<< end render_when -->

### Communication rules

- Talk to Matt in simple, natural, plain English. He is not a developer; do not assume technical knowledge. Answer "did it work?" in words first, numbers after.
- Any message directed at Matt — a question, a blocker, a thing he must do — is visually unmistakable and is never buried inside thinking or output walls. Print it as a short plain-text block on its own, with a plain-text label such as QUESTION FOR MATT or MATT MUST DO. Plain text only; his terminal does not render ANSI colour codes.
- HUMAN GATES in live supervised runs (real accounts, Matt at the keyboard): print the banner, state the ONE thing Matt must do, and WAIT for him to type the confirmation word. No timers, no inferring he is done, no barrelling ahead. Never hammer or re-poll an external site — one action, one attempt; repeated automated contact is what trips anti-bot systems.
- Give Matt one action item at a time, never a numbered list of manual steps. When reporting, bottom-line first, then the evidence briefly.
<!-- >>> render_when: execution.dispatch.enabled -->

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
<!-- <<< end render_when -->
