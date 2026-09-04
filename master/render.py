#!/usr/bin/env python3
"""
ForgeFlow MASTER renderer  (blueprint v1.2, Principle P9 / Board M5)

Turns  master/*.master.yaml  +  a repo's .forge/protocol-config.yaml
into complete, standalone protocol files for ONE repo — byte-exact, with a
header stamp, a block manifest and a real config hash.

Usage
  python3 render.py render  --config <repo>/.forge/protocol-config.yaml \
                            --master-dir master --out <dir> [--tree <repo checkout>] \
                            [--date YYYY-MM-DD] [--claude-md <repo>/CLAUDE.md]
  python3 render.py check   ... same flags ...  --against <dir with current rendered files>
  python3 render.py evidence <file-or-diff> [...]        # wrap companion check (M4/N3)
  python3 render.py explain --config ... --master-dir ... # print expanded config + which blocks render

Master block fence syntax (a fence is a full comment line):
  # >>> block S-001 | header_stamp_and_standalone_rule | reader: all | render_when: always
  ...block text...
  # <<< end S-001
Everything in a master file outside a block must be a comment or blank line.
Optional master directive (comment line, anywhere before the first block):
  # @reader-order cc-dispatch: S-030, S-038, W-003, S-048, S-074

Exit codes: 0 ok, 1 render/validation failure, 2 usage.
"""
import argparse, copy, datetime, hashlib, json, os, re, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("render.py needs PyYAML (pip install pyyaml --break-system-packages)")

# --------------------------------------------------------------------------- constants
MASTER_FILES = {
    "start": "start-protocol.master.yaml",
    "end":   "end-protocol.master.yaml",
}
RENDERED_NAME = {
    ("start", "cw"):          "start-protocol.yaml",
    ("end",   "cw"):          "end-protocol.yaml",
    ("start", "cc-dispatch"): "start-protocol.dispatch.yaml",
    ("end",   "cc-dispatch"): "end-protocol.dispatch.yaml",
}
# Which block reader-tags land in which rendered file (P7).
READER_ACCEPTS = {
    "cw":          {"cw", "cc", "cc-local", "cc-dispatch", "all"},   # the CW-read file carries everything
    "cc-dispatch": {"cc", "cc-dispatch", "all"},                      # the runner file carries only what a cold runner needs
}
CLAUDE_MD_MASTER = "claude-md.house-block.master.md"
CLAUDE_MD_OPEN  = "<!-- FORGEFLOW HOUSE BLOCK — rendered from forgeflow/master {version} — do not edit inside markers -->"
CLAUDE_MD_CLOSE = "<!-- END FORGEFLOW HOUSE BLOCK -->"
FORBIDDEN_PHRASES = [
    "see the local variant", "see the dispatch variant", "inherited from", "as in end-protocol",
    "as in start-protocol", "refer to master", "see the master", "see forgeflow", "render_when", ">>> block", "<<< end", "{{",
]
BLOCK_OPEN  = re.compile(r"^\s*#\s*>>>\s*block\s+(?P<id>[A-Z]-\d{3})\s*\|\s*(?P<name>[^|]+?)\s*\|\s*reader:\s*(?P<reader>[^|]+?)\s*\|\s*render_when:\s*(?P<cond>.+?)\s*$")
BLOCK_CLOSE = re.compile(r"^\s*#\s*<<<\s*end\s+(?P<id>[A-Z]-\d{3})\s*$")
ORDER_DIRECTIVE = re.compile(r"^\s*#\s*@reader-order\s+(?P<reader>[\w-]+)\s*:\s*(?P<ids>.+)$")
PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")

# --------------------------------------------------------------------------- helpers
class RenderError(Exception):
    pass

def fail(msg):
    raise RenderError(msg)

def load_yaml(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as ex:
        fail(f"{path} is not valid YAML: {ex}")

def is_field_spec(node):
    return isinstance(node, dict) and "type" in node and isinstance(node["type"], str)

def walk_schema(schema, prefix=""):
    """Yield (dotted_path, spec) for every field spec in the schema."""
    for key, node in schema.items():
        path = f"{prefix}{key}"
        if is_field_spec(node):
            yield path, node
        elif isinstance(node, dict):
            yield from walk_schema(node, path + ".")
        else:
            fail(f"schema: {path} is neither a field spec nor a group")

def get_path(d, dotted, default=None):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def set_path(d, dotted, value):
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
        if not isinstance(cur, dict):
            fail(f"config: {dotted} collides with a scalar at {part}")
    cur[parts[-1]] = value

def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        p = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, p + "."))
        else:
            out[p] = v
    return out

# --------------------------------------------------------------------------- config expansion
def expand_config(repo_cfg, schema, master_dir, tree=None):
    """
    repo-facing form  {profile, repo:{org,name}, overrides:{dotted: value}, ...}
    -> expanded nested config validated against the schema (Section 5 S2).
    """
    specs = dict(walk_schema(schema))
    known = set(specs)

    # 1. defaults
    eff = {}
    for path, spec in specs.items():
        if spec.get("set_by") == "renderer":
            continue
        if "default" in spec:
            set_path(eff, path, copy.deepcopy(spec["default"]))

    # 2. profile
    profile = repo_cfg.get("profile")
    if profile:
        pfile = Path(master_dir) / "profiles" / f"{profile}.yaml"
        if not pfile.exists():
            fail(f"config: profile '{profile}' has no file at {pfile}")
        for path, value in (load_yaml(pfile) or {}).items():
            if path not in known:
                fail(f"profile {profile}: unknown field {path}")
            set_path(eff, path, value)

    # 3. detection from the repo tree (P3) — fills detected fields; overrides still win
    if tree:
        for path, value in detect(tree).items():
            set_path(eff, path, value)

    # 4. explicit repo fields + overrides
    for key in ("repo", "north_star_doc", "companion_repos", "hardware", "protected", "ids", "thresholds", "subsystems"):
        if key in repo_cfg and key != "overrides":
            node = repo_cfg[key]
            if isinstance(node, dict):
                for p, v in flatten(node, key + ".").items():
                    if p not in known:
                        fail(f"config: unknown field {p}")
                    set_path(eff, p, v)
            else:
                if key not in known:
                    fail(f"config: unknown field {key}")
                set_path(eff, key, node)
    for path, value in (repo_cfg.get("overrides") or {}).items():
        if path not in known:
            fail(f"config: unknown override {path}")
        set_path(eff, path, value)
    for key in repo_cfg:
        if key not in ("profile", "overrides", "repo", "north_star_doc", "companion_repos", "hardware", "protected", "ids", "thresholds", "subsystems", "schema_version"):
            fail(f"config: unknown top-level key '{key}' (repo-facing form is profile + repo + overrides)")

    # 5. required fields present, enums legal
    for path, spec in specs.items():
        if spec.get("set_by") == "renderer":
            continue
        val = get_path(eff, path, KeyError)
        if val is KeyError:
            fail(f"config: required field {path} is missing and has no default")
        if spec["type"] == "enum" and val is not None and val not in spec.get("values", []):
            fail(f"config: {path}={val!r} not in {spec['values']}")
        if spec["type"] == "boolean" and not isinstance(val, bool):
            fail(f"config: {path} must be true/false, got {val!r}")
        if spec["type"] == "integer" and not isinstance(val, int):
            fail(f"config: {path} must be an integer, got {val!r}")
        if spec["type"] == "list" and not isinstance(val, list):
            fail(f"config: {path} must be a list, got {val!r}")

    # 6. Section 5 validation rules
    if get_path(eff, "execution.dispatch.enabled") and not get_path(eff, "mirror.github_is_complete_mirror"):
        fail("config: execution.dispatch.enabled requires mirror.github_is_complete_mirror: true")
    if not get_path(eff, "build.surfaces"):
        fail("config: build.surfaces must contain at least one entry")
    if get_path(eff, "execution.dispatch.enabled") and tree:
        missing = [r for r in [".github/workflows/claude.yml"] if not (Path(tree) / r).exists()]
        if missing:
            fail(f"config: dispatch enabled but the tree lacks {missing} (one-time install still owed)")
    gi = set(get_path(eff, "mirror.gitignored_local_only_paths") or [])
    for p in get_path(eff, "protected.never_touch_paths") or []:
        if p not in gi:
            print(f"note: protected.never_touch_paths entry {p} is not in gitignored_local_only_paths — treated as TRACKED", file=sys.stderr)

    # 7. resolve placeholders inside defaults (e.g. canonical_checkout)
    flat = flatten(eff)
    for path, val in list(flat.items()):
        if isinstance(val, str) and "{{" in val:
            set_path(eff, path, substitute(val, eff, where=f"config default {path}"))
    return eff

def detect(tree):
    """P3 — what can be read off the repo tree. Everything else is declared."""
    t = Path(tree)
    out = {}
    pkg_root = (t / "package.json").exists()
    apps = sorted(p.parent for p in t.glob("apps/*/package.json"))
    if pkg_root:
        out["shape.kind"] = "single-app"; out["shape.build_location"] = "."; out["build.validation"] = "npm-build"
    elif apps:
        out["shape.kind"] = "monorepo"; out["shape.build_location"] = str(apps[0].relative_to(t)).replace(os.sep, "/"); out["build.validation"] = "npm-build"
    elif (t / "pyproject.toml").exists() or (t / ".venv").exists():
        out["build.validation"] = "py-compile"
    out["subsystems.supabase"] = (t / "supabase").is_dir()
    out["subsystems.vercel"] = (t / ".vercel" / "project.json").exists() or (t / "vercel.json").exists()
    if out["subsystems.vercel"]:
        out["build.deploy"] = "vercel"
    wf = list(t.glob(".github/workflows/*.yml"))
    out["subsystems.ci_quality_gate"] = any(re.search(r"quality|gate|ci", p.name, re.I) for p in wf)
    out["subsystems.chromaqa"] = (t / ".chromaqa").is_dir()
    out["subsystems.ui_inventory"] = (t / ".forge" / "specs" / "ui-inventory.yaml").exists()
    out["subsystems.artifact_register"] = (t / ".forge" / "protocols" / "artifact-register.yaml").exists()
    out["architecture.tsx_lib_rule"] = any(t.glob("src/**/*.tsx")) or any(t.glob("app/**/*.tsx"))
    return out

def config_hash(eff):
    canon = json.dumps(eff, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()

# --------------------------------------------------------------------------- conditions
def truthy(v):
    if v is None or v is False:
        return False
    if isinstance(v, (list, dict, str)):
        return len(v) > 0
    return bool(v)

def parse_literal(tok):
    tok = tok.strip()
    if tok in ("true", "True"):  return True
    if tok in ("false", "False"): return False
    if tok in ("none", "null", "None"): return None
    if re.fullmatch(r"-?\d+", tok): return int(tok)
    return tok.strip("'\"")

def eval_condition(cond, eff):
    """
    Tiny boolean language over config paths. Supported forms (joined by ' and ' / ' or '):
      always | never | <path> | not <path> | <path> == lit | <path> != lit
      <path> non-empty | <path> empty | len(<path>) > N | len(<path>) >= N | len(<path>) == N
    """
    cond = cond.strip()
    if " or " in cond:
        return any(eval_condition(c, eff) for c in cond.split(" or "))
    if " and " in cond:
        return all(eval_condition(c, eff) for c in cond.split(" and "))
    if cond == "always": return True
    if cond == "never":  return False
    m = re.fullmatch(r"len\(([a-zA-Z0-9_.]+)\)\s*(>=|==|>|<|<=)\s*(\d+)", cond)
    if m:
        v = get_path(eff, m.group(1)); n = len(v) if isinstance(v, (list, dict, str)) else 0; k = int(m.group(3))
        return {">": n > k, ">=": n >= k, "==": n == k, "<": n < k, "<=": n <= k}[m.group(2)]
    m = re.fullmatch(r"([a-zA-Z0-9_.]+)\s+(non-empty|empty)", cond)
    if m:
        return truthy(get_path(eff, m.group(1))) == (m.group(2) == "non-empty")
    m = re.fullmatch(r"([a-zA-Z0-9_.]+)\s*(==|!=)\s*(.+)", cond)
    if m:
        lhs = get_path(eff, m.group(1)); rhs = parse_literal(m.group(3))
        return (lhs == rhs) if m.group(2) == "==" else (lhs != rhs)
    m = re.fullmatch(r"not\s+([a-zA-Z0-9_.]+)", cond)
    if m:
        return not truthy(get_path(eff, m.group(1), KeyError if False else None))
    if re.fullmatch(r"[a-zA-Z0-9_.]+", cond):
        if get_path(eff, cond, KeyError) is KeyError:
            fail(f"render_when references unknown config path '{cond}'")
        return truthy(get_path(eff, cond))
    fail(f"cannot parse render_when condition: {cond!r}")

# --------------------------------------------------------------------------- master parsing
class Block:
    __slots__ = ("id", "name", "readers", "cond", "lines", "start_line")
    def __init__(self, id, name, readers, cond, start_line):
        self.id, self.name, self.readers, self.cond, self.start_line = id, name, readers, cond, start_line
        self.lines = []

def parse_master(path):
    """Returns (blocks_in_order, reader_orders{reader: [ids]}, preamble_comment_lines)."""
    text = Path(path).read_text(encoding="utf-8")
    if "\r" in text:
        fail(f"{path}: contains CR characters — the master must be pure LF")
    blocks, orders, preamble = [], {}, []
    cur = None
    seen = set()
    for n, line in enumerate(text.split("\n"), 1):
        mo = BLOCK_OPEN.match(line)
        mc = BLOCK_CLOSE.match(line)
        md = ORDER_DIRECTIVE.match(line)
        if mo:
            if cur: fail(f"{path}:{n}: block {mo.group('id')} opens inside {cur.id}")
            bid = mo.group("id")
            if bid in seen: fail(f"{path}:{n}: duplicate block id {bid}")
            seen.add(bid)
            readers = {r.strip() for r in re.split(r"[+,]", mo.group("reader")) if r.strip()}
            bad = readers - {"cw", "cc", "cc-local", "cc-dispatch", "all"}
            if bad: fail(f"{path}:{n}: unknown reader tag(s) {sorted(bad)}")
            cur = Block(bid, mo.group("name"), readers, mo.group("cond"), n)
        elif mc:
            if not cur or cur.id != mc.group("id"):
                fail(f"{path}:{n}: close fence for {mc.group('id')} does not match open block {cur.id if cur else None}")
            blocks.append(cur); cur = None
        elif cur:
            cur.lines.append(line)
        elif md:
            orders[md.group("reader")] = [i.strip() for i in md.group("ids").split(",") if i.strip()]
        elif line.strip() == "" or line.lstrip().startswith("#"):
            preamble.append(line)
        else:
            fail(f"{path}:{n}: content outside any block: {line[:60]!r}")
    if cur: fail(f"{path}: block {cur.id} never closed")
    if not blocks: fail(f"{path}: no blocks found")
    return blocks, orders, preamble

# --------------------------------------------------------------------------- substitution
def substitute(text, eff, where=""):
    def repl(m):
        v = get_path(eff, m.group(1), KeyError)
        if v is KeyError:
            fail(f"unresolved placeholder {{{{{m.group(1)}}}}} in {where}")
        if isinstance(v, list):
            return ", ".join(str(x) if not isinstance(x, dict) else x.get("name", json.dumps(x)) for x in v) if v else "(none)"
        if v is None:
            return "(none)"
        return str(v)
    return PLACEHOLDER.sub(repl, text)

# --------------------------------------------------------------------------- rendering one file
def order_blocks(included, reader, orders):
    """Stable IDs, per-reader ORDER (P7): directive IDs first in directive order, then master order."""
    first = [i for i in orders.get(reader, []) if i in {b.id for b in included}]
    rest  = [b for b in included if b.id not in set(first)]
    by_id = {b.id: b for b in included}
    return [by_id[i] for i in first] + rest

def knob_summary(eff):
    d = eff
    return (f"mirror={'complete(hard-reset)' if get_path(d,'mirror.github_is_complete_mirror') else 'partial(gentle-pull)'} "
            f"shape={get_path(d,'shape.kind')}@{get_path(d,'shape.build_location')} build={get_path(d,'build.validation')} "
            f"deploy={get_path(d,'build.deploy')} dispatch={'on' if get_path(d,'execution.dispatch.enabled') else 'off'} "
            f"surfaces={len(get_path(d,'build.surfaces') or [])} companions={len(get_path(d,'companion_repos') or [])} "
            f"supabase={get_path(d,'subsystems.supabase')} chromaqa={get_path(d,'subsystems.chromaqa')} "
            f"ui_inventory={get_path(d,'subsystems.ui_inventory')} tsx_lib_rule={get_path(d,'architecture.tsx_lib_rule')}")

def render_file(kind, reader, blocks, orders, eff, version, date, chash, method="code"):
    all_ids = [b.id for b in blocks]
    included, excluded = [], []      # excluded: (block, reason)
    for b in blocks:
        cond_ok = eval_condition(b.cond, eff)
        reader_ok = bool(b.readers & READER_ACCEPTS[reader])
        if cond_ok and reader_ok:
            included.append(b)
        elif not cond_ok:
            excluded.append((b, f"render_when false: {b.cond}"))
        else:
            excluded.append((b, f"reader {reader} does not read {'/'.join(sorted(b.readers))} blocks"))
    ordered = order_blocks(included, reader, orders)

    # manifest check: included + excluded == master, disjoint, every excluded really false/foreign
    inc_ids = [b.id for b in ordered]; exc_ids = [b.id for b, _ in excluded]
    if sorted(inc_ids + exc_ids) != sorted(all_ids) or set(inc_ids) & set(exc_ids):
        fail(f"{kind}/{reader}: manifest does not partition the master block set")
    for b, reason in excluded:
        if reason.startswith("render_when") and eval_condition(b.cond, eff):
            fail(f"{kind}/{reader}: {b.id} excluded but its condition evaluates true")

    companion = RENDERED_NAME[(kind, "cc-dispatch" if reader == "cw" else "cw")] if get_path(eff, "execution.dispatch.enabled") else "(none — dispatch not enabled)"
    head = [
        "# " + "=" * 77,
        f"# {kind.upper()} PROTOCOL — {get_path(eff,'repo.org')}/{get_path(eff,'repo.name')} — reader: {reader}",
        f"# source:         chromasmith/forgeflow master/{MASTER_FILES[kind]}",
        f"# master_version: {version}",
        f"# rendered_on:    {date}",
        f"# render_method:  {method}",
        f"# config_hash:    {chash}",
        f"# config_file:    .forge/protocol-config.yaml",
        f"# companion_file: .forge/protocols/{companion}",
        "# DO NOT EDIT THIS FILE — edit the master and re-render. A bug found here is a master bug.",
        f"# knobs:          {knob_summary(eff)}",
        "#",
        f"# BLOCK MANIFEST — included {len(inc_ids)}, excluded {len(exc_ids)}, master total {len(all_ids)}",
        "# included (in this file's order): " + ", ".join(inc_ids),
    ]
    for b, reason in excluded:
        head.append(f"# excluded {b.id} ({b.name}): {reason}")
    head.append("# " + "=" * 77)
    head.append("")

    body = []
    for b in ordered:
        body.append(f"# --- {b.id} {b.name} " + "-" * max(3, 70 - len(b.id) - len(b.name)))
        body.extend(substitute("\n".join(b.lines), eff, where=f"{kind} block {b.id}").split("\n"))
        body.append("")
    out = "\n".join(head + body).rstrip("\n") + "\n"
    standalone_check(out, f"{kind}/{reader}", skip_header_lines=len(head))
    return out, inc_ids, exc_ids

def standalone_check(text, label, skip_header_lines=0):
    lines = text.split("\n")
    for n, line in enumerate(lines, 1):
        if n <= skip_header_lines:
            continue
        low = line.lower()
        for ph in FORBIDDEN_PHRASES:
            if ph.lower() in low:
                fail(f"standalone check failed in {label} line {n}: contains {ph!r}: {line.strip()[:80]}")

def render_claude_md(master_dir, existing_text, eff, version, date):
    src = Path(master_dir) / CLAUDE_MD_MASTER
    if not src.exists():
        return None
    block = substitute(src.read_text(encoding="utf-8").rstrip("\n"), eff, where=CLAUDE_MD_MASTER)
    open_line = CLAUDE_MD_OPEN.format(version=version)
    rendered_block = f"{open_line}\n{block}\n{CLAUDE_MD_CLOSE}"
    if existing_text is None:
        return rendered_block + "\n"
    pat = re.compile(r"<!-- FORGEFLOW HOUSE BLOCK — rendered from forgeflow/master [^\n]*-->\n.*?\n" + re.escape(CLAUDE_MD_CLOSE), re.S)
    if pat.search(existing_text):
        return pat.sub(lambda m: rendered_block, existing_text, count=1)
    print("note: CLAUDE.md had no house-block markers — block appended at the end; Matt may want to reorder it", file=sys.stderr)
    return existing_text.rstrip("\n") + "\n\n" + rendered_block + "\n"

def effective_config_text(repo_cfg_text, eff):
    """Repo config with the effective values written back as a trailing comment block (S2)."""
    marker = "# --- effective values (written by render.py, do not edit) ---"
    base = repo_cfg_text.split(marker)[0].rstrip("\n")
    lines = [base, "", marker]
    for k, v in sorted(flatten(eff).items()):
        lines.append(f"# {k}: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"

# --------------------------------------------------------------------------- commands
def cmd_render(a, check_only=False):
    master_dir = Path(a.master_dir)
    schema = load_yaml(master_dir / "protocol-config.schema.yaml")
    repo_cfg_text = Path(a.config).read_text(encoding="utf-8")
    repo_cfg = yaml.safe_load(repo_cfg_text.split("# --- effective values")[0]) or {}
    eff = expand_config(repo_cfg, schema, master_dir, tree=a.tree)
    version = (load_yaml(master_dir / "CHANGELOG.yaml").get("entries") or [{}])[0].get("version") or fail("CHANGELOG.yaml has no top entry with a version")
    date = a.date or datetime.date.today().isoformat()
    for p in ("protocol.master_version", "protocol.rendered_on", "protocol.render_method"):
        set_path(eff, p, {"protocol.master_version": version, "protocol.rendered_on": date, "protocol.render_method": a.method}[p])
    chash = config_hash({k: v for k, v in eff.items() if k != "protocol"})
    set_path(eff, "protocol.config_hash", chash)

    outputs = {}
    readers = ["cw"] + (["cc-dispatch"] if get_path(eff, "execution.dispatch.enabled") else [])
    for kind, fname in MASTER_FILES.items():
        mpath = master_dir / fname
        if not mpath.exists():
            fail(f"master file missing: {mpath}")
        blocks, orders, _ = parse_master(mpath)
        for reader in readers:
            text, inc, exc = render_file(kind, reader, blocks, orders, eff, version, date, chash, a.method)
            outputs[f".forge/protocols/{RENDERED_NAME[(kind, reader)]}"] = text
            print(f"{kind}/{reader}: {len(inc)} blocks in, {len(exc)} out, {text.count(chr(10))} lines", file=sys.stderr)
    outputs[".forge/protocol-config.yaml"] = effective_config_text(repo_cfg_text, eff)
    if a.claude_md is not None:
        existing = Path(a.claude_md).read_text(encoding="utf-8") if Path(a.claude_md).exists() else None
        cm = render_claude_md(master_dir, existing, eff, version, date)
        if cm is not None:
            outputs["CLAUDE.md"] = cm

    if check_only:
        drift = []
        for rel, text in outputs.items():
            cur = Path(a.against) / rel
            if not cur.exists() or cur.read_text(encoding="utf-8") != text:
                drift.append(rel)
        if drift:
            print("DRIFT — committed files differ from the render of the committed config:\n  " + "\n  ".join(drift))
            return 1
        print(f"OK — {len(outputs)} files byte-identical to the render (config_hash {chash[:12]})")
        return 0

    out = Path(a.out)
    for rel, text in outputs.items():
        p = out / rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    print(f"rendered {len(outputs)} files to {out} — master {version}, config_hash {chash[:12]}")
    return 0

def cmd_explain(a):
    master_dir = Path(a.master_dir)
    schema = load_yaml(master_dir / "protocol-config.schema.yaml")
    repo_cfg = yaml.safe_load(Path(a.config).read_text(encoding="utf-8").split("# --- effective values")[0]) or {}
    eff = expand_config(repo_cfg, schema, master_dir, tree=a.tree)
    print(yaml.safe_dump(eff, sort_keys=True, allow_unicode=True))
    for kind, fname in MASTER_FILES.items():
        if (master_dir / fname).exists():
            blocks, _, _ = parse_master(master_dir / fname)
            for b in blocks:
                print(f"{kind} {b.id} {'IN ' if eval_condition(b.cond, eff) else 'out'} [{'/'.join(sorted(b.readers))}] {b.cond}")
    return 0

STATE_WORDS = re.compile(r"\b(complete|completed|shipped|merged|deployed|fixed|passing|landed|proven|live)\b", re.I)
ID_PATTERNS = re.compile(r"(\b[0-9a-f]{7,40}\b|#\d{2,}|\bPR\s*#?\d+|\brun[ _-]?id[:\s]*\S+|\bdpl_\w+|\bdeployment\s+\S*\d\S*|\bquery result\b|\bcommit\s+[0-9a-f]{7,})", re.I)
REPORTED = re.compile(r"\b(reported|unverified|not verified|claims)\b", re.I)

def cmd_evidence(a):
    """M4/N3 — count state-change lines and whether each carries an artifact identifier."""
    total = with_id = reported = 0
    offenders = []
    for f in a.files:
        for n, line in enumerate(Path(f).read_text(encoding="utf-8", errors="replace").split("\n"), 1):
            if line.startswith("-") and not line.startswith("---"):
                continue                      # diff removals do not count
            s = line[1:] if line.startswith("+") else line
            if s.lstrip().startswith("#"):
                continue
            if not STATE_WORDS.search(s):
                continue
            total += 1
            if ID_PATTERNS.search(s):
                with_id += 1
            elif REPORTED.search(s):
                reported += 1
            else:
                offenders.append(f"{f}:{n}: {s.strip()[:110]}")
    print(f"{with_id} claims verified by ID, {reported} reported unverified, {len(offenders)} unmarked")
    if offenders:
        print("FAIL — state-change lines with neither an identifier nor a 'reported' marker:")
        print("\n".join("  " + o for o in offenders))
        return 1
    if total == 0 and not a.allow_empty:
        print("WARNING — no state-change lines found; a wrap for a session that produced commits should record some (use --allow-empty to accept)")
        return 1
    return 0

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    def common(p):
        p.add_argument("--config", required=True); p.add_argument("--master-dir", default="master")
        p.add_argument("--tree", default=None, help="local checkout for detection (P3)")
        p.add_argument("--date", default=None); p.add_argument("--method", default="code", choices=["code", "manual"])
        p.add_argument("--claude-md", default=None, help="path to the repo's current CLAUDE.md (marker replacement)")
    r = sub.add_parser("render"); common(r); r.add_argument("--out", required=True)
    c = sub.add_parser("check");  common(c); c.add_argument("--against", required=True)
    e = sub.add_parser("explain"); common(e)
    v = sub.add_parser("evidence"); v.add_argument("files", nargs="+"); v.add_argument("--allow-empty", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "render":   return cmd_render(a)
        if a.cmd == "check":    return cmd_render(a, check_only=True)
        if a.cmd == "explain":  return cmd_explain(a)
        if a.cmd == "evidence": return cmd_evidence(a)
    except RenderError as ex:
        print(f"RENDER FAILED: {ex}", file=sys.stderr)
        return 1
    return 2

if __name__ == "__main__":
    sys.exit(main())
