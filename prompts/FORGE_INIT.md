# FORGE_INIT Prompt

This prompt initializes the `.forge/` structure in any project repo. It is non-destructive — it only creates files and folders that don't already exist.

## Usage

Copy the prompt below and send it to Claude Code. It will ask which repository to target.

## Prompt

    CONTEXT MODE: SELECTIVE
    APPROVAL CODE: 3949
    Do NOT run /start or any session initialization commands.

    ## TASK: Initialize Forge Flow Structure

    Ask me which repository to work in (org/repo-name), then:

    1. Clone or pull the repository
    2. Create the following files and folders ONLY IF THEY DON'T ALREADY EXIST
    3. Skip any file or folder that already exists — do not overwrite
    4. Commit all new files in a single commit

    ### Structure to Create

    **Root level:**
    - CHANGELOG.yaml

    **.forge/ folder:**
    - .forge/backlog.yaml
    - .forge/session-state.yaml
    - .forge/session-history.yaml
    - .forge/active-bugs.yaml
    - .forge/GOTCHAS.yaml

    **.forge/blueprint/ subfolder:**
    - .forge/blueprint/Blueprint.yaml
    - .forge/blueprint/Blueprint-manifest.yaml

    **.forge/specs/ subfolder:**
    - .forge/specs/api-spec.yaml
    - .forge/specs/deployment.yaml
    - .forge/specs/integrations.yaml
    - .forge/specs/testing.yaml

    **.forge/style/ subfolder:**
    - .forge/style/tokens.yaml

    ### File Templates

    Use these exact contents for new files:

    **CHANGELOG.yaml:**
    ```yaml
    # CHANGELOG — Public-facing record of wins, features, and milestones
    # Append new entries after sessions with changelog-worthy work
    entries: []
    ```

    **.forge/backlog.yaml:**
    ```yaml
    # Work queue — prioritized tasks
    # Updated each session: completed items removed, new items added
    in_progress: []
    backlog: []
    ```

    **.forge/session-state.yaml:**
    ```yaml
    # Session state — overwritten each session with current snapshot
    session_date: null
    project: null
    milestones: []
    decisions: []
    blockers: []
    next_steps: []
    context: ""
    ```

    **.forge/session-history.yaml:**
    ```yaml
    # Session history — new entries appended after each session
    # Permanent record of completed work
    sessions: []
    ```

    **.forge/active-bugs.yaml:**
    ```yaml
    # Active bugs — overwritten each session with currently unresolved bugs only
    schema_version: "1.0"
    session_date: null
    project: null
    active_bugs: []
    ```

    **.forge/GOTCHAS.yaml:**
    ```yaml
    # GOTCHAS.yaml
    # Lessons learned for future Claude Code sessions in this repo
    ```

    **.forge/blueprint/Blueprint.yaml:**
    ```yaml
    # Blueprint — Full architecture specification
    # This file is large and should NEVER be auto-read by AI agents
    # The captain (Claude Web) extracts surgical sections for focused prompts
    project: null
    version: null
    created: null
    sections: []
    ```

    **.forge/blueprint/Blueprint-manifest.yaml:**
    ```yaml
    # Blueprint Manifest — Implementation tracking
    # Maps blueprint sections to completion status
    project: null
    sections: []
    ```

    **.forge/specs/api-spec.yaml:**
    ```yaml
    # API Specification
    # API routes, request/response schemas, auth patterns
    project: null
    base_path: /api
    routes: []
    ```

    **.forge/specs/deployment.yaml:**
    ```yaml
    # Deployment Specification
    # Environments, hosting, CI/CD, infrastructure
    project: null
    environments: {}
    ```

    **.forge/specs/integrations.yaml:**
    ```yaml
    # Integrations Specification
    # External services, credentials, SDK usage
    project: null
    services: {}
    ```

    **.forge/specs/testing.yaml:**
    ```yaml
    # Testing Specification
    # Test strategy, coverage targets, QA patterns
    project: null
    strategy: null
    ```

    **.forge/style/tokens.yaml:**
    ```yaml
    # Design Tokens
    # Colors, typography, spacing, components, accessibility
    meta:
      project: null
      brand_philosophy: null
    colors: {}
    typography: {}
    spacing: {}
    ```

    ### Commit

    Commit all new files with:
    "chore: initialize .forge structure"

    ### Output

    When complete:
    ```bash
    echo -e "\033[32m✅✅✅ DONE: Forge Flow structure initialized ✅✅✅\033[0m"
    ```

    Then report:
    - ✅ Created: [list files created]
    - ⏭️ Skipped: [list files that already existed]

## Notes

- CLAUDE.md is NOT created by this prompt — it requires manual project-specific setup
- The prompt is idempotent — safe to run multiple times on the same repo
- Existing files are never modified or overwritten
