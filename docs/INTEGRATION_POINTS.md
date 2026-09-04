> **SUPERSEDED (2026-09-04).** This document describes the legacy Forge Flow 10 methodology. The live system is the **ForgeFlow Master** in [`master/`](../master/) — one master rendered per repo by `master/render.py`; see `master/BLUEPRINT.yaml`, `master/RENDER_PROCEDURE.md` and `master/registered-repos.yaml`. This file is kept for the record and is not maintained.

# Integration Points

Forge Flow is a folder convention and workflow specification. It does not own or define the external tools that interact with it. This document maps the touchpoints — which Forge Flow files each tool reads from and writes to — so the systems can coexist without stepping on each other.

## ChromaQA

**What it is:** A quality gate system that runs automated checks (TypeScript, ESLint, secret scanning, RLS verification, dependency audits) before and after build sessions.

**How it connects to Forge Flow:**

| Touchpoint | Direction | Details |
|-----------|-----------|---------|
| chromaqa-check.sh | Reads codebase | Script lives at repo root, runs quality checks |
| .chromaqa/CQA-debt.jsonl | Writes output | ChromaQA logs soft warnings here |
| .chromaqa/CQA-debt.jsonl | Read by Captain | Focused Build Protocol checks debt count at session start (threshold: 25) |
| CLAUDE.md | Referenced | Build commands section includes ChromaQA invocation syntax |

**What Forge Flow does NOT do:**
- Does not define ChromaQA's check logic
- Does not manage the .chromaqa/ directory
- Does not own the chromaqa-check.sh script

**Boundary:** ChromaQA is an independent system. Forge Flow simply knows it exists and checks its output at session start.

---

## GOTCHAS System

**What it is:** A lightweight institutional memory system that captures friction lessons from build sessions so future stateless AI agents don't repeat the same mistakes.

**How it connects to Forge Flow:**

| Touchpoint | Direction | Details |
|-----------|-----------|---------|
| .forge/GOTCHAS.yaml | Write (append) | New entries added when friction is discovered |
| .forge/GOTCHAS.yaml | Read by Agent | Claude Code reads at session start |
| .forge/GOTCHAS.yaml | Read by Captain | Claude Web reviews during planning |
| Reflection questions | Input source | Agent's answers feed the GOTCHAS system |

**The GOTCHAS lifecycle:**

1. Agent completes a task and answers two reflection questions
2. User reads the "Did you encounter anything..." answer
3. If worth preserving, user triggers logging
4. Entry is appended to `.forge/GOTCHAS.yaml` with sequential ID
5. Future sessions read the file at start, avoiding the same friction

**What Forge Flow owns:** The file location, entry schema, and read/write behavior.
**What Forge Flow does NOT own:** The LOG_FRICTION prompt or the decision of what qualifies.

### Cross-Project GOTCHAS (SolutionPatterns)

Some friction lessons apply across all projects, not just one repo. These are tracked in `SolutionPatterns.yaml` in the Forge Flow spec repo itself, using a different schema:

```yaml
- trigger: When/where does this occur
  symptom: What it looks like when it happens
  fix: What to do instead (one line)
  tags: [tag1, tag2, tag3]
  details: |
    Specific steps, commands, config snippets
```

---

## ChromaSwarm

**What it is:** A multi-agent orchestration system that coordinates specialized Claude Code instances (Prospector, Blacksmith, Crucible, Hallmark) for complex build sessions.

**How it connects to Forge Flow:**

| Touchpoint | Direction | Details |
|-----------|-----------|---------|
| .forge/chromaswarm.yaml | Read by Swarm | Agents read for repo-specific config |
| .forge/GOTCHAS.yaml | Read by Prospector | Reconnaissance agent reads friction lessons |
| .forge/session-state.yaml | Read by Prospector | Agent reads for current context |
| .forge/backlog.yaml | Read by Prospector | Agent reads for work queue |
| CLAUDE.md | Read by All Agents | Single source of truth for conventions |
| .forge/style/tokens.yaml | Read by Blacksmith | Builder agent reads for design consistency |
| chromaswarm-friction-journal.yaml | Write (append) | System-level friction logged at repo root |

**Status:** ChromaSwarm is in beta. It is not part of the standard Forge Flow workflow. Projects that use it include `chromaswarm.yaml` in `.forge/`; projects that don't simply omit the file.

---

## Prompt Library

The user maintains a library of carefully crafted prompts that drive the Forge Flow workflow. These prompts are not stored in the repo — they live in the user's prompt management system.

**Key prompts that interact with Forge Flow:**

| Prompt | What It Does | Forge Flow Files Touched |
|--------|-------------|-------------------------|
| Focused Build Protocol | Defines the captain/agent workflow | Reads all .forge/ session files at start |
| End Session | Captures state across all status files | Writes/updates 6 files |
| LOG_FRICTION | Logs a GOTCHA entry | Appends to .forge/GOTCHAS.yaml |
| FORGE_INIT | Scaffolds .forge/ structure in a new repo | Creates all files with init templates |

---

## Integration Boundary Principle

Forge Flow's role with external tools follows a consistent principle:

> **Forge Flow defines the files. The tools define the behavior.**

Forge Flow specifies where files live, what they contain, and how they're updated. External tools define their own logic, protocols, and workflows. The integration happens at the file level — structured YAML files with documented schemas that both sides understand.

This keeps Forge Flow stable even as the external tools evolve.
