# PROPAGATION PROCEDURE — how one master change reaches every rendered repo

Blueprint v1.3, Section 7 (propagation, partial_propagation, drift_detection, atomic_propagation,
delivery_rule) and Board N5. Written so a fresh Claude Web session can execute it cold.
A render of ONE repo follows RENDER_PROCEDURE.md; this file is for the pass that follows a
master change and touches EVERY registered repo.

STATUS (2026-09-04): first written at master v1.0.0, when the registry held one repo
(chromasmith/seogeo). No propagation pass has run yet.

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
- For every repo in the registry, ask Matt in one line whether a Claude Code session is active on
  it before the pass writes anything there. Two writers on one repo is a collision.

## 2. Bump
The version to propagate is the top entry of `master/CHANGELOG.yaml`. It is already pushed. The
registry still names the OLD version for every row — that is correct until step 5.

## 3. Render every registered repo
For each row of `master/registered-repos.yaml` whose `state` is `current`, run RENDER_PROCEDURE.md
steps 1–6 exactly: fetch the master, fetch the repo's `.forge/protocol-config.yaml`, current
`.forge/protocols/*` and `CLAUDE.md`, detect (a shallow clone when the repo is public; a tree
skeleton rebuilt from the GitHub listing when it is private — say which in the report), render
twice, diff for byte-stability, measure against the S4 ceilings, diff against the repo's current
copies and summarize the change in plain English.

For each row whose `state` is `pinned`, render nothing. Write the drift line (step 4) instead.

Do not push anything until every repo has rendered cleanly in the sandbox. A renderer failure on
ANY repo stops the pass before the first push (atomic_propagation).

## 4. Deliver
- Delivery is a PULL REQUEST per repo, always (delivery_rule). A bad render caught in PRs is a few
  closed tabs; caught in commits it is a chain of reverts Matt must authorize. Direct commit is for
  the single-repo case in RENDER_PROCEDURE.md only.
- Each PR carries exactly the render's file set: `.forge/protocol-config.yaml` (effective-values
  block refreshed), `.forge/protocols/start-protocol.yaml`, `.forge/protocols/end-protocol.yaml`,
  the two `.dispatch.yaml` files only where dispatch is enabled, and `CLAUDE.md` when the house block
  changed. Nothing else.
- PR title: `protocols: render from forgeflow master <version>`. Body: the plain-English diff
  summary from step 3 and the config hash.
- For a pinned repo, write ONE field into its `.forge/handoff.yaml` (a single-line commit, or a
  line in an existing PR): `protocol_drift: "repo on <old>; master is <new> — <reason from the
  registry>"`. The start protocol reads only files inside its own repo; this line is how it learns
  it lags. Never write a drift line into a repo that is being rendered in the same pass.
- Matt merges. After each merge, prove the landing exactly as RENDER_PROCEDURE.md step 7: every
  blob SHA equals the sandbox output; `render.py check --against` the fetched copies reports OK.

## 5. Record — registered-repos.yaml LAST
Only after every repo is either merged-and-proven or pinned-with-reason, update
`master/registered-repos.yaml`: each rendered row gets the new `master_version`, `rendered_on` and
`config_hash`; each pinned row keeps its old version with `state: pinned` and the reason. The
registry is the single authority on versions; the `protocol_drift` handoff line is a courtesy
notice derived from it, never a second record.

## 6. If the pass cannot finish
A propagation that cannot finish in its session is REVERTED, not left half-landed: close the
unmerged PRs, remove any `protocol_drift` lines this pass wrote, and roll the master version back
(a new CHANGELOG entry that supersedes the bump — never a history rewrite). The registry, untouched
since step 5 never ran, already describes the reverted state. "Mostly propagated" does not exist.

## 7. Report
One plain sentence per repo — rendered / PR open / merged and proven / pinned and why — then the
overall position of the protocol system in one sentence, then the next step as a verb and who
holds the ball.
