# RENDER PROCEDURE — how Claude Web renders one repo from the ForgeFlow master

Blueprint v1.2, Section 6 and Principle P9. Written so a fresh Claude Web session can execute it cold.
Claude Web runs `master/render.py` in its own sandbox; GitHub is only ever read and written through the GitHub MCP.

STATUS (2026-09-05, master v1.1.0): the master is REPAIRED (RULING-009/010/011 — see CHANGELOG v1.1.0). The seven
repos rendered from v1.0.0 (seogeo, chromasmith-saas-starter, forgeflow, chromaqa, synclips-platform, chromasync,
dv-captain) all came up dispatch-OFF because no harness was installed and nothing said so; each RE-RENDERS from
v1.1.0 on Matt's go, AFTER its harness is installed (step 0b). Fixture test 47/47. Lesson from the first render,
kept here because it will recur: a repo the sandbox cannot clone (private, no credential) is detected from a tree
skeleton rebuilt from the GitHub listing — create the exact paths render.py's detect() looks for, nothing else —
and since v1.1.0 the skeleton MUST carry the real content of `.github/workflows/claude.yml` when it exists (fetch it
through the GitHub MCP), because render.py reads the `--allowed-tools` list out of it; the report says so.

## 0. Preconditions
- The GitHub MCP is connected. Ask Matt whether a Claude Code session is active on the TARGET repo, and whether
  another Claude Web session is mid-render or about to wrap (GOTCHA-002/004), before step 7.
- LIST THE TARGET TREE FIRST (GOTCHA-003): `.github/workflows/`, `.chromaqa/`, `.seogeo/`, `package.json`,
  `vercel.json`, `.gitattributes`, `CLAUDE.md`. Write the ruling and the config from what the tree shows.
- The target repo has `.forge/protocol-config.yaml` (repo-facing form: `profile` + `repo` + `overrides`). If it
  does not, write one from the profile that fits (`standard`, `legacy-local`, `docs-only`) and commit it FIRST.

## 0b. Dispatch harness — INSTALL BEFORE RENDERING (v1.1.0, RULING-009/011)
Dispatch defaults ON. If the tree has no `.github/workflows/claude.yml`, the render will come out dispatch-OFF with
a header shout and S-092 — legal, but it is the exact state v1.1.0 exists to end, so install first unless Matt says
this repo is dispatch-off by choice (then `execution.dispatch.enabled: false` goes in the config, with the reason).
THIS IS THE STANDARD FOR EVERY REPO THAT JOINS THE MASTER, new or existing: no repo is rendered dispatch-off by
accident again. Three steps, one at a time, each confirmed before the next. Matt does 1 and 3 himself; step 2 is
one Claude Code prompt and Matt never handles the token.

1. **Workflow file (Matt, GitHub web editor).** Claude Web hands him the pre-filled link
   `https://github.com/<org>/<repo>/new/main?filename=.github/workflows/claude.yml` and the COMPLETE content of
   `master/assets/claude.yml` in one copyable block (never "copy from line X"). The connector cannot write workflows.
   Confirm the commit landed: the file's blob SHA on GitHub must equal `git hash-object master/assets/claude.yml`
   (an uncompleted web-editor commit dialog is silently lost). A repo needing extra runner tools (database reads)
   OVERLAYS on the asset at the marked lines; it never forks the generic part.
2. **Secret — ONE command, from 1Password, in a Claude Code prompt.** The token lives in vault "Chromasmith Keys",
   item `CLAUDE_CODE_OAUTH_TOKEN`, field `credential` (created 2026-09-05 with `claude setup-token`; a Claude
   subscription token, NEVER `ANTHROPIC_API_KEY`, which bills per token). The prompt runs, in PowerShell:
       (op read "op://Chromasmith Keys/CLAUDE_CODE_OAUTH_TOKEN/credential").Trim() | gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo chromasmith/<repo>
   then proves it with `gh secret list --repo chromasmith/<repo>` (name and UTC date only; values are never shown).
   Readiness checks: `gh auth status` (signed in as chromasmith, repo scope) and `op vault list` — NEVER `op whoami`,
   which reports "not signed in" on Surface 12 even when the CLI works. Several repos can be done in one prompt, one
   attempt each, no retries without Matt's word. The value is never printed, echoed or written into a repo. `chromasmith`
   is a personal GitHub account: there are no organization-level secrets; every repo needs its own. To ROTATE the token
   later: `claude setup-token` again, `op item edit CLAUDE_CODE_OAUTH_TOKEN --vault "Chromasmith Keys" credential=<new>`
   (Matt pastes into the Claude Code prompt, which passes it on without displaying it), then re-run the one command per
   repo — `gh secret set` overwrites.
3. **Branch protection (Matt, GitHub web).** On the default branch, with "include administrators" UNTICKED
   (RULING-011): runners cannot push main; Matt, his local Claude Code and Claude Web's connector (acting as Matt)
   still can. Claude Web proves the bypass with a one-line docs commit before the first dispatch; a rejection means the
   box is ticked.
Then re-list the tree, confirm the workflow is there, and continue at step 1.

## 1. Fetch the master into the sandbox
```
mkdir -p /home/claude/ff && cd /home/claude/ff
mkdir -p master/profiles master/assets
for f in render.py protocol-config.schema.yaml CHANGELOG.yaml start-protocol.master.yaml end-protocol.master.yaml claude-md.house-block.master.md assets/claude.yml; do
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
enabled without a complete mirror, `execution.dispatch.harness_installed` is overridden true while the tree has no
workflow, a declared `allowed_tools` differs from the workflow's `--allowed-tools`, a `{{placeholder}}` cannot be resolved, a block fence is malformed, the block
manifest does not partition the master, or a forbidden cross-reference phrase survives. Read the one-line reason,
fix the CONFIG or the MASTER (never the output), re-run.

## 4. Prove byte-stability
Run step 3 a second time into a different `--out` with the same `--date`; `diff -r` the two output trees. Any
difference is a renderer bug; do not push.

## 5. Measure
`wc -l /home/claude/out/.forge/protocols/*.yaml`. Compare against the S4 ceilings in `BLUEPRINT.yaml`
`rendering.file_ceilings` (start 1650, dispatch start 650, end 1400, dispatch end 150). A file over its ceiling is not
pushed; apply replace-to-add (P11) in the master.

## 6. Diff and summarize
`diff` each rendered file against the repo's current copy. Write Matt a plain-English summary (adds X, removes the
stale Y wording, unifies Z). For a FIRST render of a repo that is a master lineage, a large unexpected diff is a
renderer bug; for SYN/CC2-lineage repos an additive diff of the eleven promoted rules is expected.

## 7. Push
- Ask whether a Claude Code session is active on the target repo. If yes, deliver as a PR; if no, a direct commit is allowed for a single-repo render.
- Read the rendered header's `knobs:` line aloud to Matt in one sentence before pushing — especially `dispatch=`.
  `dispatch=OFF(harness-not-installed)` on a repo Matt expects to dispatch from means go back to step 0b, not push.
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
