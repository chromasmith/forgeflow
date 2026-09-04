# ForgeFlow

Matt Fleming's operating system for building Chromasmith software with AI agents: Claude Web plans and
writes prompts, Claude Code builds, and a set of `.forge/` files in every repo carries state between
stateless sessions.

> **Where the live system is: [`master/`](master/).** Since 2026-09-04 every repo's session protocols
> are RENDERED from one master — `master/start-protocol.master.yaml`, `master/end-protocol.master.yaml`
> and the CLAUDE.md house block — by `master/render.py`, driven by a small `.forge/protocol-config.yaml`
> in each repo. Nothing in a rendered repo is hand-edited; a protocol bug is a master bug, fixed here
> and re-rendered.

## The ForgeFlow Master — start here

| File | What it is |
|------|------------|
| [`master/BLUEPRINT.yaml`](master/BLUEPRINT.yaml) | The design: principles, artifact set, config schema, rendering rules, propagation, session flow. Read the version notes at the top first. |
| [`master/RENDER_PROCEDURE.md`](master/RENDER_PROCEDURE.md) | How Claude Web renders ONE repo from the master, cold. |
| [`master/PROPAGATION_PROCEDURE.md`](master/PROPAGATION_PROCEDURE.md) | How a master change reaches EVERY registered repo (PR per repo, registry written last). |
| [`master/registered-repos.yaml`](master/registered-repos.yaml) | The single authority on which repos are rendered and from which master version. |
| [`master/CHANGELOG.yaml`](master/CHANGELOG.yaml) | Version history of the master itself. The top entry is the version every render stamps. |
| [`master/render.py`](master/render.py) | The deterministic renderer. `python3 master/tests/test_render.py` is its proof. |
| [`master/protocol-config.schema.yaml`](master/protocol-config.schema.yaml) · [`master/profiles/`](master/profiles/) | Every knob a repo config may set, with defaults; the three starting profiles (`standard`, `legacy-local`, `docs-only`). |
| [`master/LINEAGE_RECONCILIATION.yaml`](master/LINEAGE_RECONCILIATION.yaml) | How the three legacy protocol lineages were reconciled into one master, rule by rule. |

Session governance for THIS repo lives in [`.forge/handoff.yaml`](.forge/handoff.yaml) (read first) and
[`.forge/rulings.yaml`](.forge/rulings.yaml) (Matt's decisions — search before asking).

## Legacy: Forge Flow 10 (superseded)

The documents below describe the earlier Forge Flow 10 folder convention and captain/agent workflow. They
are kept for the record, each carries a "superseded" banner, and they are **not maintained**. The master
above absorbed what survived of them.

| Document | What It Covered |
|----------|-----------------|
| [Folder Structure](docs/FOLDER_STRUCTURE.md) | Every file, where it lives, and why |
| [File Schemas](docs/FILE_SCHEMAS.md) | Schema for every Forge Flow file |
| [Visibility Tiers](docs/VISIBILITY_TIERS.md) | How information access was controlled |
| [Session Lifecycle](docs/SESSION_LIFECYCLE.md) | Start → Build → End session workflow |
| [Integration Points](docs/INTEGRATION_POINTS.md) | How external tools (ChromaQA, GOTCHAS, ChromaSwarm) connected |
| [FORGE_INIT](prompts/FORGE_INIT.md) · [INSTALL_REPAIR](prompts/INSTALL_REPAIR.md) · [examples/](examples/) | Legacy prompts and the scaffold example |

## Origin

Forge Flow emerged from hundreds of real build sessions across multiple SaaS products at Chromasmith LLC.
Earlier versions were an ambitious module-based build system that proved too complex; Version 10 was a
clean restart. The ForgeFlow Master (2026-09-04) is the next step: one source of truth for the session
protocols, rendered per repo, so a fix lands once and everywhere.

## License

Proprietary — Chromasmith LLC
