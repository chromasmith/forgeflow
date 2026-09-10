# RENDER PROCEDURE — how Claude Web renders one repo from the ForgeFlow master

Blueprint v1.2, Section 6 and Principle P9. Written so a fresh Claude Web session can execute it cold.
Claude Web runs `master/render.py` in its own sandbox; GitHub is only ever read and written through the GitHub MCP.

STATUS (2026-09-10, master v1.4.2): ten repos rendered, all dispatch-ON with the harness installed by step 0b.
A repo the sandbox cannot clone (private, no credential) is detected from a tree skeleton rebuilt from the GitHub
listing — create the exact paths render.py's detect() looks for, nothing else — and the skeleton MUST carry the
real content of `.github/workflows/claude.yml` when it exists (fetch it through the GitHub MCP), because render.py
reads the `--allowed-tools` list out of it; the report says so. A rendered set over ~80 KB lands through ONE local
Claude Code run, never the connector (step 0b item 5).

## 0. Preconditions
- The GitHub MCP is connected. Ask Matt whether a Claude Code session is active on the TARGET repo, and whether
  another Claude Web session is mid-render or about to wrap (GOTCHA-002/004), before step 7.
- LIST THE TARGET TREE FIRST (GOTCHA-003): `.github/workflows/`, `.chromaqa/`, `.seogeo/`, `package.json`,
  `vercel.json`, `.gitattributes`, `CLAUDE.md`. Write the ruling and the config from what the tree shows.
- OPEN THE NORTH-STAR DOCUMENT before naming it in the config (GOTCHA-027): read its first 30 lines and confirm its
  own title or meta names the document its path claims. Two instructional files within a few bytes of each other in
  size are one document duplicated until their headers are read.
- The target repo has `.forge/protocol-config.yaml` (repo-facing form: `profile` + `repo` + `overrides`). If it
  does not, write one from the profile that fits (`standard`, `legacy-local`, `docs-only`) and commit it FIRST.

## 0b. Dispatch harness — INSTALL BEFORE RENDERING (v1.1.0 RULING-009/011; v1.4.0 RULING-022/023/024)
Dispatch defaults ON. If the tree has no `.github/workflows/claude.yml`, the render comes out dispatch-OFF with a
header shout and S-092 — legal, but the exact state v1.1.0 exists to end, so install first unless Matt says this
repo is dispatch-off by choice (then `execution.dispatch.enabled: false` goes in the config, with the reason).
THIS IS THE STANDARD FOR EVERY REPO THAT JOINS THE MASTER. TOOLS FIRST (RULING-024): every step below is done by
ONE local Claude Code run through `gh api` and `op`, in Git Bash syntax; Matt's only action is the `apply`
confirmation word after the run shows him what it is about to change. No dashboard clicking.

0. **Name and casing first (GOTCHA-017).** Read the repo's real name from the API — `gh api repos/<org>/<repo> --jq .name` —
   before writing the config. `repo.name` feeds `config_hash` and every path in both protocol files, and a
   case-only rename NO-OPS silently in GitHub Settings (it needs the two-step: `<name>-tmp`, then the final casing).
1. **Workflow file.** `master/assets/claude.yml`, byte-identical (a repo needing extra runner tools OVERLAYS on the
   asset at the marked lines; it never forks the generic part). Landing lane, in order of preference: the run writes
   it with `gh api -X PUT repos/<org>/<repo>/contents/.github/workflows/claude.yml` (Matt's `gh` token carries the
   `workflow` scope; the GitHub App connector does not); if that is refused, Claude Web hands Matt the pre-filled
   link `https://github.com/<org>/<repo>/new/main?filename=.github/workflows/claude.yml` and the complete file
   content. Either way prove the landing: the blob SHA on GitHub equals `git hash-object master/assets/claude.yml`.
2. **Secret — one command, from 1Password.** Vault "Chromasmith Keys", item `CLAUDE_CODE_OAUTH_TOKEN`, field
   `credential` (a Claude subscription token from `claude setup-token`; NEVER `ANTHROPIC_API_KEY`, which bills per
   token). Readiness: `gh auth status` and `op vault list` — never `op whoami`, which lies on Surface 12
   (GOTCHA-005). The first `op` call after idle can return an authorization timeout (GOTCHA-022): on a timeout run
   `op vault list` exactly once more before treating it as a sign-in gate. Git Bash form, one line per repo, no loop:
       op read "op://Chromasmith Keys/CLAUDE_CODE_OAUTH_TOKEN/credential" | tr -d "\r\n" | gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo <org>/<repo>
   Prove with `gh secret list --repo <org>/<repo>`. The value is never printed, echoed or written into a repo.
   `chromasmith` is a personal account: no organization secrets, every repo needs its own. ROTATE: `claude
   setup-token`, `op item edit CLAUDE_CODE_OAUTH_TOKEN --vault "Chromasmith Keys" credential=<new>`, re-run the line.
3. **Branch protection — the HOUSE SETTING (RULING-022), set by API.** Classic protection on the default branch:
   "Require a pull request before merging" ON, "Require approvals" UNTICKED (`required_approving_review_count: 0`
   — a required approval deadlocks every merge, because Matt cannot approve his own PR and Claude Web opens runner
   PRs as him), "Do not allow bypassing" UNTICKED (`enforce_admins: false` — administrators bypass, RULING-011).
       gh api -X PUT repos/<org>/<repo>/branches/main/protection --input protection.json
   with protection.json = `{"required_status_checks": null, "enforce_admins": false, "required_pull_request_reviews":
   {"required_approving_review_count": 0, "dismiss_stale_reviews": false, "require_code_owner_reviews": false},
   "restrictions": null}` written to the Windows temp folder, never into the repo tree. Read it back with
   `gh api repos/<org>/<repo>/branches/main/protection` and confirm the three values. Claude Web then proves the
   bypass with a one-line docs commit; a rejection means `enforce_admins` came back true.
4. **Auto-delete head branches (RULING-023).** `gh api -X PATCH repos/<org>/<repo> -f delete_branch_on_merge=true`
   so runner branches vanish at merge. Transport branches (`tmp/…`) are deleted by the run that used them with
   `gh api -X DELETE repos/<org>/<repo>/git/refs/heads/tmp/<name>`. Matt never deletes a branch by hand.
5. **Landing lane by rendered size (GOTCHA-008/017).** Decide BEFORE rendering: the config (small) lands through the
   connector; if `wc -c` of any rendered file exceeds ~80 KB, the whole rendered set lands through ONE local Claude
   Code run gated on a blob-SHA table, with the render `--date` passed explicitly (the date is stamped into the
   header, so today's date makes every hash miss). Never discover the ceiling mid-render.
Then re-list the tree, confirm the workflow is there, and continue at step 1.
FIRST PROOF (2026-09-05): chromasmith/forgeflow — secret set, claude.yml blob 4cccfbf = asset, protection on main with
admin bypass, proven by a direct docs commit. API-set protection first proven 2026-09-10 (run HARNESS-AUDIT-1).

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
`rendering.file_ceilings` (start 2000, dispatch start 650, end 1700, dispatch end 150 — re-measured 2026-09-07 on a
repo carrying both ChromaQA and SEO/GEO, RULING-020). A file over its ceiling is not
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
