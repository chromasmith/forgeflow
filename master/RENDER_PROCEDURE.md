# RENDER PROCEDURE — how Claude Web renders one repo from the ForgeFlow master

Blueprint v1.2, Section 6 and Principle P9. Written so a fresh Claude Web session can execute it cold.
Claude Web runs `master/render.py` in its own sandbox; GitHub is only ever read and written through the GitHub MCP.

STATUS (2026-09-04, end of step 3): renderer, schema, profiles, fixture test AND both master protocol files are
built. `start-protocol.master.yaml` (89 blocks) and `end-protocol.master.yaml` (46 blocks) render byte-stable for the
three fixture profiles and for the real convergible-sandbox knob set (`tests/fixtures/config-sandbox-real.yaml`,
rendered inside forgeflow only). Per RULING-001 no repo is rendered until Matt names it. Still to land before the first
real render: `claude-md.house-block.master.md`, `PROPAGATION_PROCEDURE.md`, `registered-repos.yaml`, the S4 ceilings
in BLUEPRINT.yaml, and the CHANGELOG bump to v1.0.0.

## 0. Preconditions
- The GitHub MCP is connected. Ask Matt whether a Claude Code session is active on the TARGET repo before step 7.
- The target repo has `.forge/protocol-config.yaml` (repo-facing form: `profile` + `repo` + `overrides`). If it
  does not, write one from the profile that fits (`standard`, `legacy-local`, `docs-only`) and commit it FIRST.

## 1. Fetch the master into the sandbox
```
mkdir -p /home/claude/ff && cd /home/claude/ff
for f in render.py protocol-config.schema.yaml CHANGELOG.yaml start-protocol.master.yaml end-protocol.master.yaml claude-md.house-block.master.md; do
  curl -sfL https://raw.githubusercontent.com/chromasmith/forgeflow/main/master/$f -o master/$f || echo "MISSING $f"
done
for p in standard legacy-local docs-only; do curl -sfL https://raw.githubusercontent.com/chromasmith/forgeflow/main/master/profiles/$p.yaml -o master/profiles/$p.yaml; done
```
Compare each file's `git hash-object` with the blob SHA the GitHub MCP reports for the same path. A mismatch means the fetch is stale; stop.

## 2. Fetch the target repo's inputs
- `.forge/protocol-config.yaml` (required), `CLAUDE.md` (if present), and the current `.forge/protocols/*` files (for the diff).
- For detection (P3), a shallow clone of the target into the sandbox is best: `git clone --depth 1 https://github.com/<org>/<repo> /home/claude/target`.
  Pass it as `--tree /home/claude/target`. Without a tree, every `detected: true` field takes its default or override — say so in the summary.

## 3. Render
```
python3 master/render.py render --config /home/claude/target/.forge/protocol-config.yaml \
        --master-dir master --tree /home/claude/target --claude-md /home/claude/target/CLAUDE.md \
        --out /home/claude/out --date $(date -u +%F)
```
render.py refuses to write when: an unknown config field is present, a required field has no value, dispatch is
enabled without a complete mirror, a `{{placeholder}}` cannot be resolved, a block fence is malformed, the block
manifest does not partition the master, or a forbidden cross-reference phrase survives. Read the one-line reason,
fix the CONFIG or the MASTER (never the output), re-run.

## 4. Prove byte-stability
Run step 3 a second time into a different `--out` with the same `--date`; `diff -r` the two output trees. Any
difference is a renderer bug; do not push.

## 5. Measure
`wc -l /home/claude/out/.forge/protocols/*.yaml`. Compare against the S4 ceilings in `BLUEPRINT.yaml` once they are
written (until then: report the numbers). A file over its ceiling is not pushed; apply replace-to-add (P11) in the master.

## 6. Diff and summarize
`diff` each rendered file against the repo's current copy. Write Matt a plain-English summary (adds X, removes the
stale Y wording, unifies Z). For a FIRST render of a repo that is a master lineage, a large unexpected diff is a
renderer bug; for SYN/CC2-lineage repos an additive diff of the eleven promoted rules is expected.

## 7. Push
- Ask whether a Claude Code session is active on the target repo. If yes, deliver as a PR; if no, a direct commit is allowed for a single-repo render.
- Push exactly these files: `.forge/protocol-config.yaml` (now carrying the effective-values comment block),
  `.forge/protocols/start-protocol.yaml`, `.forge/protocols/end-protocol.yaml`, and — only when dispatch is enabled —
  `.forge/protocols/start-protocol.dispatch.yaml`, `.forge/protocols/end-protocol.dispatch.yaml`; plus `CLAUDE.md` if the house block changed.
- Prove the push: the blob SHA the API returns for each file must equal `git hash-object` of the sandbox output.
- Then run `python3 master/render.py check --against <fetched copy> ...` to confirm the committed files are byte-identical to the render.

## 8. Record
Update `master/registered-repos.yaml` (the single authority on versions) LAST, after the push has landed: repo,
config path, master version, render date, config_hash. If this render is part of a propagation, follow
PROPAGATION_PROCEDURE.md instead of editing the registry per repo.

## Manual fallback
Only if code execution is unavailable in the session. Render by hand from the master, stamp `render_method: manual`
in the header, and never propagate a manual render to more than one repo; re-render by code at the next opportunity.

## Companion check for wraps (M4 / N3)
`python3 master/render.py evidence <the wrap's changed .forge files or their diff>` prints
`N claims verified by ID, M reported unverified, K unmarked`. K must be 0 before the wrap is written; the N/M line
goes at the end of the wrap commit message.
