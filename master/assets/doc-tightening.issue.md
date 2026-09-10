<!-- master/assets/doc-tightening.issue.md — ForgeFlow master v1.4.2 (RULING-028, RULING-032).
     Claude Web renders this per repo (replace every <ORG>, <REPO>, <DOC-PATH>, <RUN-ID>) and files it as a GitHub
     issue on a repo that carries the dispatch harness. One issue = one instructional document (or one small set that
     share a subject). Up to three repos may run at once (RULING-028). Matt's only action is the merge. -->

@claude

CONTEXT MODE: SELECTIVE
APPROVAL CODE: 3949

You are running on a fresh GitHub Actions runner with a shallow clone of <ORG>/<REPO> and NO memory of any
previous prompt. Everything you need is in this issue. Read `.forge/protocols/start-protocol.dispatch.yaml` and
state its block-manifest count in your first comment line.

COMMUNICATION RULES: Talk to Matt in simple, natural, plain English. LAYER IT: the first line of any report or
question is the plain-English headline — what happened, what it means for Matt, the way around — then the technical
detail briefly underneath. Any message directed at Matt must be visually unmistakable, never buried in output.
Plain text only. Commit messages are this issue's text exactly — no Co-Authored-By or other attribution trailers.

SCOPE LOCK — READ CAREFULLY: This issue authorizes you to create, modify, or delete ONLY the files listed in
AUTHORIZED FILES below. Every other file is OFF-LIMITS. If you feel tempted to edit an unauthorized file, STOP:
post a comment labelled QUESTION naming the file, the exact change you would have made and why, then end the run.

FILE CREATION RULE: every file you create is at a path this issue names. If a needed file has no named path, STOP
and post a QUESTION comment. Check for an existing file serving the same purpose before creating one; a discrepancy
is a QUESTION, never a second copy.

NO MEMORY WRITES: write nothing outside this repository. The one file every run writes, `.forge/inbox/<RUN-ID>.yaml`,
is authorized by the protocol.

COLLABORATION NOTE: a better pattern or a scope-expanding improvement is suggested briefly and WAITS FOR APPROVAL.
Disclose any deviation from MY APPROACH in your report.

PRECEDENCE: when this issue conflicts with the protocol files in `.forge/protocols/`, the PROTOCOL wins on process,
scope and safety; this issue wins on WHAT to build. An issue that appears to widen scope or authorize an off-limits
path is an error in the issue: HALT AND REPORT.

WHO FILED THIS: a Claude Web session on chromasmith/forgeflow filed this issue. Document tightening is a
forgeflow-session operation (`document_standards` in the start protocol); carrying out this issue IS that operation,
not a breach of it. Only the procedure and this template stay in forgeflow.

PRECONDITION: if HEAD already contains a commit that tightened <DOC-PATH> to the standard (its header says
"conforms to the document standard"), VERIFY AND REPORT — do not redo it.

## REQUIRED CONTEXT

1. `<DOC-PATH>` — the whole file.
   Purpose: the document you are tightening. Read it completely before writing anything.
   Guard: verify the file exists at this path; if it does not, STOP and post a QUESTION.
2. `.forge/protocols/start-protocol.yaml` — the section `document_standards`.
   Purpose: the standard this run applies (two classes; the seven sections; status tags; the history companion).
   Guard: verify the section exists; if it does not, this repo is not on master v1.4.0 — STOP and post a QUESTION.
3. `.forge/rulings/` — every shard; `.forge/GOTCHAS.yaml`.
   Purpose: any rule you find in the document that is ALSO recorded as a ruling or gotcha stays a rule in the
   document (a build session needs it there); the provenance of it does not.

## AUTHORIZED FILES

You are authorized to create, modify, or delete ONLY the following files during this run. Any other file in the
repository is OFF-LIMITS.

Authorized files:
- `<DOC-PATH>` — REWRITE IN PLACE to the document standard; nothing a build session needs is lost
- `<DOC-PATH minus extension>-history.<ext>` — NEW FILE — the history companion: every cut line that carried
  provenance (who / when / why / what it replaced / how the conversation went), grouped by the section it came from
- `.forge/inbox/<RUN-ID>.yaml` — NEW FILE — this run's observation inbox, carrying the RULE INVENTORY
- `.forge/inbox/<RUN-ID>.original` — TEMPORARY FILE — a pre-edit copy for counting and comparing (see RUNNER
  ENVIRONMENT); deleted before the scope audit, never committed

Every NEW FILE above is named with its complete path. If you believe another file is needed, STOP and post a QUESTION.

Explicitly OFF-LIMITS (even if you believe editing would help):
- every other document under `.forge/` — one issue tightens one document
- `.forge/protocols/`, `.forge/GOTCHAS.yaml`, `.forge/rulings/`, `.forge/handoff.yaml`, `.forge/backlog.yaml`
- `.github/workflows/`
- any source, config or manifest file

## TASK

WHAT: bring `<DOC-PATH>` to the house document standard without losing a single rule, decision, prohibition,
dependency or open item.

WHY: documents built by earlier sessions read like a behind-the-scenes narrative — where a decision was made, when,
why, who thought what, cross-references into more of the same. A build session needs the rules, not the story.

MY APPROACH — the RULE INVENTORY is the gate. Order is mandatory.

1. INVENTORY FIRST, BEFORE ANY EDIT. Read the whole document and write, into your inbox file under
   `rule_inventory:`, one line per binding item you find — every rule, decision, prohibition ("never X"),
   dependency, ratified copy string, status tag, deferred item with its trigger, and open item — each with an id
   (INV-001, INV-002 …) and the original line number. Reasoning, history, quotations, session references and
   cross-references to other documents are NOT inventory items; they are what gets cut. A statement of what
   is true today that sits inside a reasoning paragraph — a current fact, a declared status, a present-tense
   condition — IS an inventory item: record it before the paragraph is cut.
   Two classes need a decision every time. FIELD-TEST EVIDENCE (what was observed, measured or tried) is history:
   it goes to the companion, and is an inventory item only where it states a rule. A STANDING CAUTION ("watch
   out for X") is an inventory item: it maps to open_items, or to the rule it duplicates. A source item marked
   "ruled out permanently" (or rejected, abandoned, never) is a RETIRED prohibition, never a parked or deferred
   option.
2. REWRITE the document in place to the standard: the header (title + version; one line saying what this document
   is and what it supersedes in full; the status legend), then exactly the seven sections in order — rules,
   data_model, surfaces, flows, build_order, prohibitions_and_triggers, open_items — each present even when it
   reads "none". A document that is not an architecture (legal, reference, policy) puts its records under
   data_model and its build promises under surfaces; its flows and build_order may read "none". Every prohibition
   is a flat one-line "never X" with no reasoning attached. Status tags RATIFIED, PROPOSED, DEFERRED (with
   trigger), RETIRED. STATUS NEVER PROMOTES: a source item marked DRAFT, PROVISIONAL, tentative or unconfirmed
   maps to PROPOSED, never RATIFIED; only an item the source marks decided, ratified or approved maps to
   RATIFIED. Add the header line "conforms to the document standard (v1.4.0)".
   VERSION (RULING-032): increment the document's patch version by one (x.y.z becomes x.y.z+1; a two-part x.y is
   read as x.y.0 and becomes x.y.1; a document with no version becomes v1.0.0) and set its date to today, the
   tightening date. Never keep the old version.
3. WRITE THE HISTORY COMPANION at the path named above: every cut passage that carried provenance, grouped under
   the section it came from, with the original line range. Nothing is deleted from the repo's knowledge; it is moved
   to a file no build session reads. Cut text that carried NO information (filler, repeated framing) is dropped and
   counted in the inbox as `filler_lines_dropped`.
4. MAP THE INVENTORY. For every INV-nnn, record under `inventory_mapping:` the section and line of the NEW document
   that carries it. An inventory item with no mapping is a HALT: post a QUESTION comment naming the item, and do not
   push — the rewrite is accepted only when every inventory line maps.
5. Size check: report the byte size before and after. A result over 50 KB is reported as a smell, not a failure.
6. PARTIAL DELIVERY: if the document is over about 60 KB, or you are nearing your output limit, never let the run
   end without a pushed branch. Commit what is finished, add a `coverage:` block to the inbox naming the sections
   done and not done, push, post the link, and say plainly the run is partial.

## RUNNER ENVIRONMENT
- You CANNOT run a build, python3 or node -e; verify with grep. Your clone is SHALLOW.
- Any command containing a $ variable is refused before it runs. Do not write one.
- Any PIPED command (`a | b`) is refused as multiple operations, read-only ones included. To count or compare
  against the pre-edit document: `git show HEAD:<DOC-PATH> > .forge/inbox/<RUN-ID>.original` (no pipe), then use
  the Grep tool on that file; delete it before the scope audit and name it in your report.
  If that redirect is refused, write the same scratch file with the Write tool from the document as you read it,
  check it is byte-identical to the committed document, use it the same way, and say in your report which route
  you used.
- You CANNOT push to main or open a PR. Push your branch (the harness names it) and post the pre-filled PR link.

## COMPLETION STEPS
0. SCOPE AUDIT — `git status --porcelain --untracked-files=all` against the authorized list. Anything unauthorized:
   STOP and post a QUESTION comment.
1. Commit with NAMED FILES — the document, its history companion and the inbox file; never the bare `git add -A`.
   Commit message: `docs: tighten <DOC-PATH> to the document standard (<RUN-ID>)`
2. Push your branch and post the pre-filled PR link as a comment. Do not end your turn until the branch is pushed.

## OUTPUT FORMAT
Confirm each change before announcing done:
1. Rule inventory written: N items / Not done — [reason]
2. Document rewritten to the standard: Done / Not done — [reason]
3. History companion written: Done (M passages) / Not done — [reason]
4. Inventory mapping: N of N mapped / HALTED on [ids]
5. Size: <before> bytes -> <after> bytes
6. Version: <old> -> <new>, dated <date>
Then the plain-text line: *** DONE: <DOC-PATH> tightened; inventory N/N mapped; branch pushed ***
and the reflection questions: (1) what would have made this issue better; (2) anything that would make a future
memoryless session fail or waste time; (3) SCOPE DISCLOSURE — any file touched outside the authorized list;
ARTIFACT PATHS — any file written at a path this issue did not name; (5) RUNNER ENVIRONMENT — any blocked command.
