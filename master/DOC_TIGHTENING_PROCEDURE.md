# DOC TIGHTENING PROCEDURE — how a forgeflow session brings a legacy document to the document standard

Master v1.4.2 (RULING-028, RULING-029, RULING-030, RULING-032). Conforms to the document standard (v1.4.0). Supersedes in full the
"session opened on the target repo" lane of RULING-028 and the inline procedure text of backlog item FF-020.
Status legend: RATIFIED, PROPOSED, DEFERRED (with trigger), RETIRED.

## rules

- RATIFIED — Tightening is a FORGEFLOW-SESSION operation, like a render: Claude Web works in a session opened on
  chromasmith/forgeflow; the target repo is never opened for it.
- RATIFIED — Matt names the target repo and the document(s); nothing is tightened that he has not named.
- RATIFIED — One dispatched issue tightens ONE instructional document (or one small set sharing a subject). The
  issue body is `master/assets/doc-tightening.issue.md` with every placeholder replaced; nothing else is added.
- RATIFIED — The template and this procedure live in forgeflow only. The rendered start protocol of every repo
  carries one line saying so (S-093); the template itself is never propagated, copied or committed into a target.
- RATIFIED — The RULE INVENTORY is the acceptance gate: the run lists every binding item before editing and maps
  each to the new document; a PR with an unmapped item is not merged.
- RATIFIED — Up to THREE issues run at once, on up to three repos or three documents of one repo, when no two
  touch the same document. Linear is the default for anything else.
- RATIFIED — Claude Web reviews the PR against the inventory and recommends; the merge gate is Matt's yes in chat;
  Claude Web merges (squash, house method). Runner branches auto-delete at merge (RULING-023).
- RATIFIED — Fallback lane: when the target repo cannot dispatch (harness off or broken), the same template runs
  as ONE local Claude Code prompt, opened with STEP 0 for that repo, same authorized files, same inventory gate.
- RATIFIED — In scope: instructional documents — blueprints, specs, plans, guides, READMEs, instructions,
  procedures (`.forge/strategy/`, `.forge/specs/`, `.forge/plans/`, `docs/`, README files).
- RATIFIED — Out of scope: record files (handoff, rulings, GOTCHAS, session-history, backlog), rendered protocol
  files under `.forge/protocols/`, source, config and manifests. Rulings entries are append-only and never rewritten.
- RATIFIED — Progress per repo is a DONE / NEXT inventory (RULING-030): every instructional document in the repo is
  listed under its FF-021 entry in forgeflow `.forge/backlog.yaml`, marked done (merge SHA) or next; a resuming
  session states "done / next" from that list, never from a tree scan.
- RATIFIED — A tightened document's patch version goes up by one and its date becomes the tightening date; the old
  version is never kept (RULING-032).

## data_model

- Placeholders in the template: `<ORG>`, `<REPO>`, `<DOC-PATH>`, `<RUN-ID>`, `<DOC-PATH minus extension>-history.<ext>`.
- RUN-ID: `TIGHTEN-<repo-short>-<nnn>` — repo-short is the repo name without `chromasmith/`, nnn counts up per
  repo across sessions (read the repo's `.forge/inbox/` history and backlog for the last used number).
- Issue title: `TIGHTEN <DOC-PATH> to the document standard (<RUN-ID>)`.
- Run outputs, all inside the target repo on the runner's branch: the rewritten document; the history companion
  at `<DOC-PATH minus extension>-history.<ext>`; `.forge/inbox/<RUN-ID>.yaml` carrying `rule_inventory:`
  (INV-nnn, original line), `inventory_mapping:` (INV-nnn to new section and line), `filler_lines_dropped:`,
  the size before and after, the reflection answers, scope disclosure and any `needs_ruling`.
- PR title: `docs: tighten <DOC-PATH> to the document standard (<RUN-ID>)`.
- Progress record: one block per target repo under FF-021 in forgeflow `.forge/backlog.yaml` — every instructional
  document in that repo on its own line, `done <merge SHA> <date>` or `next`; written at the repo's first tightening
  session, updated at every later wrap that lands a document there.

## surfaces

- Claude Web chat on chromasmith/forgeflow (planning, review, merge recommendation).
- GitHub issue on the target repo beginning `@claude` (the dispatched run); the PR Claude Web opens from the
  runner's branch; the issue and PR threads (reports, QUESTION / BLOCKED comments).
- Local Claude Code on Surface 12 — fallback lane only.

## flows

0. Matt names the repo and the document(s). Claude Web restates them and the lane in one line. If the repo has no
   inventory block under FF-021 yet, Claude Web lists every instructional document in its tree (the paths in the
   in-scope rule) and writes the block at this session's wrap with each marked next until landed; if the block
   exists, Claude Web reads it and states in one line what is done and what is next.
1. PREFLIGHT, per document, from the connector — every check silent when it passes:
   - the repo's row in `master/registered-repos.yaml` is `current` at v1.4.2 or later — an older render's
     `document_standards` can halt a cold runner (GOTCHA-025), so a lagging repo is rendered first (RENDER_PROCEDURE);
   - the repo's rendered start protocol header reads `dispatch=on` (else: fallback lane, said in one line);
   - the document exists at the exact path and is instructional (rules list above); a record file is declined;
   - no open PR touches the document; no other issue this session names it;
   - concurrency: Matt confirms in one line no Claude Code session is active on the target repo
     (a runner branch cannot collide with a local session until merge; the confirmation guards the merge).
2. RENDER THE ISSUE BODY in the sandbox from `master/assets/doc-tightening.issue.md`: replace every placeholder,
   grep the result for a leftover `<` placeholder, and confirm the RUN-ID is unused in the target repo.
3. FILE the issue(s) through the connector — one to three, each with its own RUN-ID. Confirm each run started
   (a workflow run exists for the issue), then HAND THE TURN BACK. No sleep-polling.
4. On any message from Matt, ADVANCE THE BOARD: read every run's comments; surface any QUESTION or `needs_ruling`
   as the decision it is with a recommendation attached; open a PR for every pushed branch that carries its inbox
   file (a branch without one gets a comment asking for it; if the run ended, the PR is opened marked
   "no inbox — inventory lost for this run" and is NOT recommended for merge).
5. REVIEW each PR against the inventory before recommending:
   - fetch `.forge/inbox/<RUN-ID>.yaml` from the branch; every INV-nnn has a mapping line;
   - spot-check at least three inventory items — the mapped line in the new document carries the same rule;
   - the new document has the header line "conforms to the document standard (v1.4.0)", the seven sections in
     order, flat one-line prohibitions, status tags, and no session references, quotations or reasoning;
   - the history companion exists at the named path and holds the cut provenance, field-test evidence included;
   - every source item "ruled out permanently" (or equivalent) is a RETIRED prohibition, not a parked option;
   - the version went up by one patch and the date is the tightening date (RULING-032);
   - the `.forge/inbox/<RUN-ID>.original` scratch file is absent from the PR;
   - the PR touches only the three committed authorized paths;
   - size before and after read from the inbox; over 50 KB after is named as a smell.
   Any failed check: a comment on the PR naming it, `@claude` to resume the run, no merge recommendation.
6. RECOMMEND in one plain sentence per PR; Matt's yes in chat; squash-merge through the connector; confirm the
   head branch is gone.
7. RECORD at the forgeflow wrap: in the repo's FF-021 inventory block, mark each landed document done with its merge
   SHA and date; the target repo's inbox file is consumed by that repo's own next wrap, not by forgeflow's.

## build_order

1. FF-020 — this procedure and the S-093 pointer line land in master v1.4.1 and propagate to every repo.
2. FF-021 — one repo per forgeflow session on Matt's schedule, up to three documents at a time.
3. The P11 prune session for the protocol files runs after the cleanups.

## prohibitions_and_triggers

- Never propagate, copy or commit the template or this procedure into a target repo.
- Never tighten a record file, a rendered protocol file, a source file or a manifest with this template.
- Never rewrite an existing rulings entry.
- Never file two issues that touch the same document, and never more than three at once.
- Never open a tightening issue against a document with an open PR.
- Never recommend a merge with an unmapped inventory item or a missing inbox file.
- Never edit the runner's output by hand to make the mapping pass; the fix is a comment and a resumed run.
- Trigger: the repo's header reads `dispatch=off`, or its dispatch is known broken — use the local prompt lane.
- Trigger: a run posts QUESTION or `needs_ruling` — surface it on the next board advance, never at the wrap.

## open_items

- DEFERRED (trigger: a third tightening session finds the by-hand mapping check too slow) — a sandbox tool that
  parses the inbox inventory and the new document and reports unmapped items mechanically.
