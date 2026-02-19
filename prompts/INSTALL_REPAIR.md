# =============================================================================
# FORGE FLOW 10 — INSTALL & REPAIR PROMPT
# =============================================================================
# Usage: Paste into Claude Code on any machine, at any time.
# Purpose: Bring any project repo into Forge Flow 10 compliance.
# Spec reference: https://github.com/chromasmith/forgeflow
# Idempotent: Safe to run repeatedly. Skips anything already correct.
# =============================================================================

task: |
  Bring a project repo into Forge Flow 10 compliance. This means:
  - The .forge/ folder structure exists with all required files
  - Any duplicate/drifted files at root are consolidated into .forge/
  - CHANGELOG.yaml exists at repo root
  - CLAUDE.md exists at repo root with Forge Flow 10 section
  - No data is lost during consolidation
  Check what already exists before doing anything. Skip anything already correct.

spec_repo: https://github.com/chromasmith/forgeflow
org: chromasmith
rule: Use the Forge Flow 10 spec as the source of truth for file locations and schemas.

# =============================================================================
# PHASE 1: DETERMINE TARGET REPO
# =============================================================================

phase_1_target:
  logic: |
    First, check if you are currently inside a git repo (look for .git in
    the current directory or any parent directory).

    IF inside a repo:
      Ask the user: "I see we're currently in {repo_name}. Should I set up
      Forge Flow here, or would you like me to work on a different repo?
      (Or say 'skip' to cancel.)"
      Wait for the user's response before proceeding.

    IF NOT inside a repo:
      Ask the user: "Which repo should I set up Forge Flow on? Give me the
      repo name (e.g., synclips-platform) and I'll clone it from the
      chromasmith org. Or say 'skip' to cancel."
      Wait for the user's response before proceeding.

    IF user says skip:
      Report "No changes made." and stop.

  after_confirmation:
    action: |
      Ensure you're working with the latest code from GitHub.

      If the target repo is the one you're already inside of:
        Do a git pull to ensure you have the latest, then work in place.

      If the target repo is a different one:
        Clone it fresh: git clone git@github.com:chromasmith/{repo_name}.git /tmp/{repo_name}
        Work inside the clone. Push when done. Clean up after.

# =============================================================================
# PHASE 2: AUDIT CURRENT STATE
# =============================================================================

phase_2_audit:
  purpose: |
    Before making ANY changes, map out what exists. This determines whether
    we're doing a fresh install, a repair, or skipping (already compliant).

  step_1_check_forge_directory:
    test: ls -la .forge/ 2>/dev/null
    outcomes:
      - ".forge/ does not exist → FRESH INSTALL path"
      - ".forge/ exists → check contents for REPAIR or COMPLIANT"

  step_2_check_forge_contents:
    condition: Only if .forge/ exists
    check_files:
      - .forge/backlog.yaml
      - .forge/session-state.yaml
      - .forge/session-history.yaml
      - .forge/active-bugs.yaml
      - .forge/GOTCHAS.yaml
      - .forge/blueprint/Blueprint.yaml
      - .forge/blueprint/Blueprint-manifest.yaml
      - .forge/specs/api-spec.yaml
      - .forge/specs/deployment.yaml
      - .forge/specs/integrations.yaml
      - .forge/specs/testing.yaml
      - .forge/style/tokens.yaml
    record: "For each file: EXISTS (N lines) or MISSING"

  step_3_check_root_duplicates:
    purpose: |
      Detect files at repo root that should live in .forge/ per Forge Flow 10.
      These are the most common drift pattern.
    check_files:
      - backlog.yaml
      - session-state.yaml
      - session-history.yaml
      - GOTCHAS.yaml
      - active-bugs.yaml
    record: "For each file: EXISTS AT ROOT (N lines) or NOT AT ROOT"

  step_4_check_root_required:
    purpose: Check for files that SHOULD be at repo root.
    check_files:
      - CHANGELOG.yaml
      - CLAUDE.md
    record: "For each file: EXISTS (N lines) or MISSING"

  step_5_check_stale_forge_changelog:
    purpose: |
      If CHANGELOG.yaml exists BOTH at root AND in .forge/, the .forge/
      copy is stale and should be deleted. CHANGELOG.yaml lives at root only.
    test: "[ -f CHANGELOG.yaml ] && [ -f .forge/CHANGELOG.yaml ]"
    record: "STALE COPY IN .forge/ or CLEAN"

  step_6_check_claude_md_forge_section:
    purpose: |
      Check if CLAUDE.md has the Forge Flow 10 documentation section.
      This section tells AI agents what .forge/ files exist and how to use them.
    test: |
      If CLAUDE.md exists, search for the marker:
      grep -q ".forge/ Documentation" CLAUDE.md
    outcomes:
      - "CLAUDE.md missing → will create with Forge Flow section"
      - "CLAUDE.md exists, Forge Flow section present → COMPLIANT"
      - "CLAUDE.md exists, Forge Flow section missing → will append"

  step_7_report_audit:
    action: |
      Present the audit results to the user in this format:

      FORGE FLOW 10 AUDIT: {repo_name}
      ════════════════════════════════

      .forge/ directory: [EXISTS / MISSING]

      .forge/ files:
        backlog.yaml:           [OK (N lines) / MISSING]
        session-state.yaml:     [OK (N lines) / MISSING]
        session-history.yaml:   [OK (N lines) / MISSING]
        active-bugs.yaml:       [OK (N lines) / MISSING]
        GOTCHAS.yaml:           [OK (N lines) / MISSING]
        blueprint/Blueprint.yaml:          [OK / MISSING]
        blueprint/Blueprint-manifest.yaml: [OK / MISSING]
        specs/api-spec.yaml:    [OK / MISSING]
        specs/deployment.yaml:  [OK / MISSING]
        specs/integrations.yaml:[OK / MISSING]
        specs/testing.yaml:     [OK / MISSING]
        style/tokens.yaml:      [OK / MISSING]

      Root-level duplicates (should be in .forge/ only):
        backlog.yaml:           [DUPLICATE (N lines) / CLEAN]
        session-state.yaml:     [DUPLICATE (N lines) / CLEAN]
        session-history.yaml:   [DUPLICATE (N lines) / CLEAN]
        GOTCHAS.yaml:           [DUPLICATE (N lines) / CLEAN]
        active-bugs.yaml:       [DUPLICATE (N lines) / CLEAN]

      Root-level required files:
        CHANGELOG.yaml:         [OK (N lines) / MISSING]
        CLAUDE.md:              [OK (N lines) / MISSING]

      CLAUDE.md Forge Flow section: [PRESENT / MISSING — will append / NO FILE — will create]

      Stale copies:
        .forge/CHANGELOG.yaml:  [STALE — will delete / CLEAN]

      DIAGNOSIS: [FRESH INSTALL / REPAIR NEEDED / ALREADY COMPLIANT]

      Then ask: "Here's what I found. Ready to proceed with [install/repair]?
      Or would you like to review anything first?"

      Wait for user confirmation before proceeding to Phase 3.

# =============================================================================
# PHASE 3: CONSOLIDATE DUPLICATES (repair path only)
# =============================================================================

phase_3_consolidate:
  condition: Only run if root-level duplicates were detected in Phase 2.
  purpose: |
    For each file that exists at BOTH root and .forge/, determine which
    version has more content and consolidate into .forge/. No data loss.

  logic_per_file: |
    For each duplicate file (backlog, session-state, session-history, GOTCHAS, active-bugs):

    1. Compare line counts: root version vs .forge/ version
    2. IF root has MORE lines (or equal):
       - Copy root version to .forge/ (replacing .forge/ version)
       - Delete root version
       - Record: "Consolidated {file} → .forge/ (root was newer: {N} vs {M} lines)"
    3. IF .forge/ has MORE lines:
       - Delete root version (keep .forge/ version as-is)
       - Record: "Kept .forge/{file} ({N} lines), deleted stale root copy ({M} lines)"

  stale_changelog:
    condition: If .forge/CHANGELOG.yaml exists
    action: |
      Delete .forge/CHANGELOG.yaml. The root CHANGELOG.yaml is the canonical
      location per Forge Flow 10. Do NOT move or merge — the root version
      is always the complete one.
    record: "Deleted stale .forge/CHANGELOG.yaml"

# =============================================================================
# PHASE 4: CREATE MISSING .forge/ FILES
# =============================================================================

phase_4_create:
  purpose: |
    Create any .forge/ files and directories that don't exist yet.
    Non-destructive: skip anything already in place.

  directories:
    create_if_missing:
      - .forge
      - .forge/blueprint
      - .forge/specs
      - .forge/style

  files:
    note: |
      For each file below, ONLY create it if it does not already exist.
      Use these exact templates for new files.

    - path: .forge/backlog.yaml
      skip_if: exists
      template: |
        # Work queue — prioritized tasks
        # Updated each session: completed items removed, new items added
        in_progress: []
        backlog: []

    - path: .forge/session-state.yaml
      skip_if: exists
      template: |
        # Session state — overwritten each session with current snapshot
        session_date: null
        project: null
        milestones: []
        decisions: []
        blockers: []
        next_steps: []
        context: ""

    - path: .forge/session-history.yaml
      skip_if: exists
      template: |
        # Session history — new entries appended after each session
        # Permanent record of completed work
        sessions: []

    - path: .forge/active-bugs.yaml
      skip_if: exists
      template: |
        # Active bugs — overwritten each session with currently unresolved bugs only
        schema_version: "1.0"
        session_date: null
        project: null
        active_bugs: []

    - path: .forge/GOTCHAS.yaml
      skip_if: exists
      template: |
        # GOTCHAS.yaml
        # Lessons learned for future Claude Code sessions in this repo

    - path: .forge/blueprint/Blueprint.yaml
      skip_if: exists
      template: |
        # Blueprint — Full architecture specification
        # This file is large and should NEVER be auto-read by AI agents
        # The captain (Claude Web) extracts surgical sections for focused prompts
        project: null
        version: null
        created: null
        sections: []

    - path: .forge/blueprint/Blueprint-manifest.yaml
      skip_if: exists
      template: |
        # Blueprint Manifest — Implementation tracking
        # Maps blueprint sections to completion status
        project: null
        sections: []

    - path: .forge/specs/api-spec.yaml
      skip_if: exists
      template: |
        # API Specification
        # API routes, request/response schemas, auth patterns
        project: null
        base_path: /api
        routes: []

    - path: .forge/specs/deployment.yaml
      skip_if: exists
      template: |
        # Deployment Specification
        # Environments, hosting, CI/CD, infrastructure
        project: null
        environments: {}

    - path: .forge/specs/integrations.yaml
      skip_if: exists
      template: |
        # Integrations Specification
        # External services, credentials, SDK usage
        project: null
        services: {}

    - path: .forge/specs/testing.yaml
      skip_if: exists
      template: |
        # Testing Specification
        # Test strategy, coverage targets, QA patterns
        project: null
        strategy: null

    - path: .forge/style/tokens.yaml
      skip_if: exists
      template: |
        # Design Tokens
        # Colors, typography, spacing, components, accessibility
        meta:
          project: null
          brand_philosophy: null
        colors: {}
        typography: {}
        spacing: {}

    - path: CHANGELOG.yaml
      location: repo root
      skip_if: exists
      template: |
        # CHANGELOG — Public-facing record of wins, features, and milestones
        # Append new entries after sessions with changelog-worthy work
        entries: []

# =============================================================================
# PHASE 5: CLAUDE.MD — CREATE OR UPDATE
# =============================================================================

phase_5_claude_md:
  purpose: |
    CLAUDE.md is the entry point for AI agents. Forge Flow 10 requires it to
    contain a .forge/ Documentation section that tells agents what files exist,
    what to read, and what to avoid.

    This phase either creates a new CLAUDE.md or appends the Forge Flow section
    to an existing one. Existing content is NEVER modified or removed.

  if_claude_md_missing:
    action: |
      Create CLAUDE.md at repo root with this starter template.
      Replace {repo_name} with the actual repo name detected in Phase 1.
    template: |
      # {repo_name}
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
    record: "Created CLAUDE.md with Forge Flow 10 template"
    note_to_user: |
      After creation, report to the user:
      "I created a starter CLAUDE.md with the Forge Flow 10 section. The
      .forge/ Documentation and file location conventions are set. You'll
      want to update the placeholders (project description, stack, key paths,
      build commands, and conventions) when you get a chance."

  if_claude_md_exists_without_section:
    action: |
      CLAUDE.md exists but does not contain the Forge Flow section.
      APPEND the following block to the END of the existing file.
      Do NOT modify, reorder, or remove any existing content.
      Add a blank line before the new section for clean separation.
    append_content: |

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

      **FILE LOCATION RULES:**
      - Session files (backlog, session-state, active-bugs, GOTCHAS, session-history) live ONLY in .forge/ — never at repo root
      - CHANGELOG.yaml lives ONLY at repo root — never in .forge/
    record: "Appended Forge Flow 10 .forge/ Documentation section to existing CLAUDE.md"

  if_claude_md_exists_with_section:
    action: Skip — already compliant.
    record: "CLAUDE.md already has Forge Flow section — no changes needed"

# =============================================================================
# PHASE 6: VERIFY
# =============================================================================

phase_6_verify:
  action: |
    Run a final check to confirm compliance:

    ```bash
    echo "=== FORGE FLOW 10 VERIFICATION ==="
    echo ""

    PASS=0
    FAIL=0

    # Check .forge/ directory
    if [ -d ".forge" ]; then echo "✅ .forge/ directory exists"; PASS=$((PASS+1)); else echo "❌ .forge/ directory MISSING"; FAIL=$((FAIL+1)); fi

    # Check all required .forge/ files
    for f in backlog.yaml session-state.yaml session-history.yaml active-bugs.yaml GOTCHAS.yaml; do
      if [ -f ".forge/$f" ]; then echo "✅ .forge/$f exists ($(wc -l < ".forge/$f") lines)"; PASS=$((PASS+1)); else echo "❌ .forge/$f MISSING"; FAIL=$((FAIL+1)); fi
    done

    # Check subdirectories and files
    for f in blueprint/Blueprint.yaml blueprint/Blueprint-manifest.yaml specs/api-spec.yaml specs/deployment.yaml specs/integrations.yaml specs/testing.yaml style/tokens.yaml; do
      if [ -f ".forge/$f" ]; then echo "✅ .forge/$f exists"; PASS=$((PASS+1)); else echo "❌ .forge/$f MISSING"; FAIL=$((FAIL+1)); fi
    done

    # Check root CHANGELOG
    if [ -f "CHANGELOG.yaml" ]; then echo "✅ CHANGELOG.yaml at root ($(wc -l < "CHANGELOG.yaml") lines)"; PASS=$((PASS+1)); else echo "❌ CHANGELOG.yaml MISSING from root"; FAIL=$((FAIL+1)); fi

    # Check CLAUDE.md exists
    if [ -f "CLAUDE.md" ]; then echo "✅ CLAUDE.md exists ($(wc -l < "CLAUDE.md") lines)"; PASS=$((PASS+1)); else echo "❌ CLAUDE.md MISSING"; FAIL=$((FAIL+1)); fi

    # Check CLAUDE.md has Forge Flow section
    if [ -f "CLAUDE.md" ] && grep -q ".forge/ Documentation" CLAUDE.md; then echo "✅ CLAUDE.md has Forge Flow section"; PASS=$((PASS+1)); else echo "❌ CLAUDE.md missing Forge Flow section"; FAIL=$((FAIL+1)); fi

    # Check for root-level duplicates that shouldn't be there
    for f in backlog.yaml session-state.yaml session-history.yaml GOTCHAS.yaml active-bugs.yaml; do
      if [ -f "$f" ]; then echo "❌ $f still at root (should only be in .forge/)"; FAIL=$((FAIL+1)); fi
    done

    # Check for stale .forge/CHANGELOG.yaml
    if [ -f ".forge/CHANGELOG.yaml" ]; then echo "❌ .forge/CHANGELOG.yaml still exists (should only be at root)"; FAIL=$((FAIL+1)); fi

    echo ""
    echo "Results: $PASS passed, $FAIL failed"
    if [ $FAIL -eq 0 ]; then
      echo "✅ FORGE FLOW 10 COMPLIANT"
    else
      echo "❌ ISSUES REMAIN — see failures above"
    fi
    ```

    If any checks fail, report them to the user and ask how to proceed.

# =============================================================================
# PHASE 7: COMMIT AND PUSH
# =============================================================================

phase_7_commit:
  condition: Only if changes were made (not if already compliant).
  action: |
    Determine the appropriate commit message based on what was done:

    IF fresh install (no .forge/ existed before):
      Message: "chore: initialize Forge Flow 10 structure"

    IF repair (duplicates consolidated and/or missing files created):
      Message: "chore: Forge Flow 10 compliance — consolidate and repair .forge/ structure"

    IF only missing files added (no duplicates found):
      Message: "chore: add missing Forge Flow 10 files"

    IF only CLAUDE.md was created or updated:
      Message: "chore: add Forge Flow 10 section to CLAUDE.md"

    ```bash
    git add -A
    git commit -m "{appropriate message}"
    git push origin main
    ```

    If working in a temp clone, clean up after pushing.

# =============================================================================
# PHASE 8: REPORT
# =============================================================================

phase_8_report:
  format: |
    When finished, report exactly what happened:

    FORGE FLOW 10 — {repo_name}
    ════════════════════════════

    DIAGNOSIS: [FRESH INSTALL / REPAIR / ALREADY COMPLIANT]

    DUPLICATES CONSOLIDATED:
    - [file]: root (N lines) → .forge/ [or "none found"]
    [list each file that was consolidated, or "No duplicates found."]

    STALE COPIES REMOVED:
    - [file] [or "None."]

    FILES CREATED:
    - [file] [or "None — all files already existed."]

    FILES SKIPPED (already existed):
    - [file]
    [list each file that was skipped]

    CLAUDE.MD: [created from template / Forge Flow section appended / already compliant]
    [If created from template: "NOTE: Placeholders need project-specific updates (description, stack, paths, build commands, conventions)."]

    VERIFICATION: [ALL PASSED / issues found: details]

    COMMIT: [commit hash and message / no changes needed]

  completion:
    action: |
      ```bash
      echo -e "\033[32m✅✅✅ DONE: {repo_name} is Forge Flow 10 compliant ✅✅✅\033[0m"
      ```

# =============================================================================
# RULES
# =============================================================================

rules:
  - Always confirm the target repo with the user before making any changes.
  - Always work with the latest code from GitHub (pull or fresh clone).
  - Non-destructive by default. Never overwrite existing content without comparing first.
  - When consolidating duplicates, always keep the version with MORE content.
  - CLAUDE.md — if missing, create from template. If exists, ONLY append — never modify existing content.
  - Present the audit to the user and wait for confirmation before making changes.
  - One step at a time. Report what you're doing as you go.
  - If anything fails or looks unexpected, stop and report before continuing.
  - Push all changes back to GitHub when done.
  - If working in a temp clone, clean up after pushing.
  - approval_code: 3949

# =============================================================================
# END OF PROMPT
# =============================================================================
