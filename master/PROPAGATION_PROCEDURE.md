# PROPAGATION PROCEDURE — how one master change reaches every rendered repo

Blueprint v1.6, Section 7 (propagation, partial_propagation, drift_detection, atomic_propagation,
delivery_rule as amended by RULING-013) and Board N5. Written so a fresh Claude Web session can
execute it cold. A render of ONE repo follows RENDER_PROCEDURE.md; this file is for the pass that
follows a master change and touches EVERY registered repo.

STATUS (2026-09-06): master v1.2.0 is landed and rendered on forgeflow only (RULING-013 —
internal-only session). The v1.2.0 propagation to the other six registered repos is the FIRST run
of the one-prompt method below and is the next forgeflow session's single first_thing. Three of
those six (synclips-platform, chromasync, dv-captain) are still on v1.0.0 without a harness; their
step 2b must be finished by Matt before the pass renders them, or they are pinned for that pass.

## 0. What a propagation is, and is not
- A propagation is the act of taking every repo in `master/registered-repos.yaml` from the master
  version it was rendered from to the current master version, or pinning it with a written reason.
- A master change is NOT a propagation. Editing the master, bumping CHANGELOG.yaml and pushing is
  the change; the propagation is a separate act that Matt says go to, and it never starts on its own.
- A first render of a new repo is NOT a propagation either — that is RENDER_PROCEDURE.md, and it
  adds the repo's row to the registry when it lands.

## 1. Preconditions
- The master change is on GitHub: `master/CHANGELOG.yaml` top entry carries the new version, the
  fixture test passes (`python3 master/tests/test_render.py` from a fresh clone), and every fixture
  the change did not target renders byte-identical protocol text to the previous version.
- Matt has said go to the propagation itself, in this session.
- ONE concurrency question for the whole batch: ask Matt in one line whether a Claude Code session
  (or another Claude Web session mid-wrap) is active on ANY registered repo. A repo he names as busy
  is pinned for this pass (step 4) — the pass does not wait for it. Two writers on one repo is a
  collision; the propagation run works at the canonical checkouts `C:\Chromasmith\<repo>`, which are
  the same working trees a local Claude Code session uses.

## 2. Bump
The version to propagate is the top entry of `master/CHANGELOG.yaml`. It is already pushed. The
registry still names the OLD version for every row — that is correct until step 6.

## 2b. Harness before render (v1.1.0, RULING-009/011)
A repo re-renders with dispatch on only if its harness is installed — `.github/workflows/claude.yml`
(Matt, web editor, complete content of `master/assets/claude.yml`, blob SHA confirmed), the
`CLAUDE_CODE_OAUTH_TOKEN` secret, branch protection with administrators bypassing (RENDER_PROCEDURE
step 0b). A repo without a harness at pass time is NOT skipped and NOT failed: it renders
dispatch-OFF with the S-092 notice, exactly as the renderer is designed to do, and the report says
so; Matt installs the harness later and that repo re-renders alone under RENDER_PROCEDURE.md. A repo
Matt declares dispatch-off by choice carries `execution.dispatch.enabled: false` in its config.

## 3. Render every registered repo IN THE SANDBOX first (Claude Web)
For each row of `master/registered-repos.yaml` whose `state` is `current` and which is not pinned
for this pass: fetch the repo's `.forge/protocol-config.yaml`, current `.forge/protocols/*` and
`CLAUDE.md` through the connector (a shallow clone when the repo is public; a tree skeleton rebuilt
from the GitHub listing when it is private — say which in the report), render twice, diff for
byte-stability, measure against the S4 ceilings, diff against the repo's current copies and
summarize the change in plain English. Record, per repo, the `git hash-object` blob SHA of every
rendered file — these SHAs are what the run in step 5 must reproduce.

Do not dispatch the run until every repo has rendered cleanly in the sandbox. A renderer failure on
ANY repo stops the pass before anything is pushed anywhere (atomic_propagation).

## 4. Pin what will not render this pass
A repo Matt named as busy in step 1, a repo whose render failed, or a repo deliberately lagging
(ChromaControl) is PINNED: it gets no render in this pass, and the run in step 5 writes ONE field
into its `.forge/handoff.yaml` in a single-line commit —
`protocol_drift: "repo on <old>; master is <new> — <reason>"` — unless the repo is busy, in which
case the drift line waits too and the registry reason says so. The start protocol reads only files
inside its own repo; this line is how it learns it lags. Never write a drift line into a repo that
is being rendered in the same pass.

## 5. Deliver — ONE local Claude Code prompt (RULING-013)
Delivery is a single local Claude Code run on Matt's canonical machine, written by Claude Web from
the standard prompt shape (STEP 0 on forgeflow, scope lock, AUTHORIZED FILES naming every repo's
file set by literal path, the PRECEDENCE paragraph, W-005 self-check applied). The run:
1. Refreshes `C:\Chromasmith\forgeflow` to origin/main (safety check first, as always) and confirms
   `master/CHANGELOG.yaml` top entry is the version being propagated.
2. For each repo in the prompt's list, in the order given: refresh its canonical checkout to
   origin/main (pre-refresh safety check; a dirty or unpushed checkout is a STOP for that repo,
   reported and skipped, never discarded); run `python master/render.py render` from the forgeflow
   checkout with `--tree` pointing at the repo and `--claude-md` at its CLAUDE.md; compare the
   `git hash-object` SHA of every rendered file with the SHA Claude Web supplied in the prompt —
   ANY mismatch is a HALT for that repo (render non-determinism is a master bug, reported as such);
   copy the rendered set into the checkout; commit the named files as ONE commit
   `protocols: render from forgeflow master <version> (config_hash <12 chars>)`; `git fetch`, push
   to the default branch (administrators bypass protection — a rejection means the rule has
   "include administrators" ticked and is a STOP with the repo named); VERIFY PUSH.
3. For each pinned repo the prompt names: write the drift line into `.forge/handoff.yaml` as a
   single-line commit and VERIFY PUSH.
4. Writes `.forge/inbox/PROPAGATE-<version>.yaml` in forgeflow (the run id is the version) and
   reports, per repo: pushed at <SHA> and verified / halted on <reason> / pinned. The registry is
   NOT touched by the run — step 6 is Claude Web's.
The run never edits a master file, never edits a repo's config knobs above the effective-values
marker (a config that fails validation is a HALT, not a fix), and never `git add -A` (the file set
is named).

## 6. Record — registered-repos.yaml LAST (Claude Web)
Only after the run's report is in hand and every landing is re-proven through the connector (blob
SHA of each pushed file equals the sandbox SHA; `render.py check --against` on the fetched copies is
OK), update `master/registered-repos.yaml`: each rendered row gets the new `master_version`,
`rendered_on`, `config_hash` and the landing commit; each pinned row keeps its old version with
`state: pinned` and the reason. The registry is the single authority on versions; the
`protocol_drift` handoff line is a courtesy notice derived from it, never a second record.

## 7. If the pass cannot finish
A propagation that cannot finish in its session is REVERTED, not left half-landed: any repo the run
pushed is re-rendered from the previous version by the same method (or its commit reverted with a
normal `git revert`, never a history rewrite), any `protocol_drift` lines this pass wrote are removed,
and the master version rolls back by a new CHANGELOG entry that supersedes the bump. The registry,
untouched since step 6 never ran, already describes the reverted state. "Mostly propagated" does not
exist. EXCEPTION recorded 2026-09-06 (RULING-013): a deliberately internal-only master change may
land on forgeflow alone, with every other row left at the previous version and the propagation
named as the next session's first_thing — that is a declared lag, visible in the registry, not a
half-landed pass.

## 8. Report
One plain sentence per repo — pushed and proven / halted and why / pinned and why — then the
overall position of the protocol system in one sentence, then the next step as a verb and who
holds the ball.
