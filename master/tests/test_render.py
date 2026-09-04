#!/usr/bin/env python3
"""
Renderer proof — run from the forgeflow repo root:  python3 master/tests/test_render.py
Uses the miniature fixture master in master/tests/fixtures/fixture-master so the test
does not depend on the real master files being finished. Exit 0 = all checks passed.
"""
import filecmp, os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENDER = HERE.parent / "render.py"
FIX = HERE / "fixtures"
MASTER_VERSION = [l.split(":",1)[1].strip().strip('"') for l in (HERE.parent / "CHANGELOG.yaml").read_text().splitlines() if l.strip().startswith("- version:")][0]  # top entry = the version render.py stamps
FIXTURE_BLOCKS = FIX / "fixture-master"          # only the three fixture master files live here
REAL = HERE.parent                                # schema, CHANGELOG and profiles come from the REAL master, so the test cannot drift from them
DATE = "2026-09-04"
checks = []

def assemble_master(dest):
    """fixture master = real schema + real CHANGELOG + real profiles + miniature block files"""
    dest.mkdir(parents=True, exist_ok=True)
    for f in ("protocol-config.schema.yaml", "CHANGELOG.yaml"):
        shutil.copy(REAL / f, dest / f)
    shutil.copytree(REAL / "profiles", dest / "profiles")
    for f in FIXTURE_BLOCKS.iterdir():
        shutil.copy(f, dest / f.name)
    return dest

def run(*args, expect=0, **kw):
    r = subprocess.run([sys.executable, str(RENDER), *args], capture_output=True, text=True, **kw)
    ok = (r.returncode == expect)
    checks.append((ok, " ".join(args[:2]) + f" -> rc {r.returncode} (want {expect})", (r.stdout + r.stderr).strip()))
    return r

def render(cfg, out, extra=()):
    return run("render", "--config", str(FIX / cfg), "--master-dir", str(MASTER), "--out", str(out), "--date", DATE, *extra)

def read(p): return Path(p).read_text(encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    MASTER = assemble_master(td / "master")
    # 1. byte-stable: render twice, compare
    render("config-standard.yaml", td / "a"); render("config-standard.yaml", td / "b")
    same = all(read(td/"a"/f) == read(td/"b"/f) for f in [".forge/protocols/start-protocol.yaml", ".forge/protocols/end-protocol.yaml", ".forge/protocol-config.yaml"])
    checks.append((same, "byte-stable: two renders of the same inputs are identical", ""))
    # 2. no dispatch -> exactly two protocol files, dispatch blocks excluded with reason
    sp = read(td/"a"/".forge/protocols/start-protocol.yaml")
    checks.append((not (td/"a"/".forge/protocols/start-protocol.dispatch.yaml").exists(), "standard: no dispatch file rendered", ""))
    checks.append(("excluded S-002" in sp and "render_when false: execution.dispatch.enabled" in sp, "standard: S-002 excluded with its condition named", ""))
    checks.append(("excluded S-026" in sp and "hard reset to origin/main" in sp, "standard: S-026 excluded, S-034 hard-reset text present", ""))
    checks.append(("C:\\Chromasmith\\fixture-standard" in sp, "substitution: canonical_checkout default resolved from repo.name", ""))
    # 3. sandbox: dispatch file exists, fixed reader ordering, cw-only blocks excluded from runner file
    render("config-sandbox.yaml", td / "s")
    dsp = read(td/"s"/".forge/protocols/start-protocol.dispatch.yaml")
    inc_line = [l for l in dsp.split("\n") if l.startswith("# included")][0]
    checks.append((inc_line.split(": ",1)[1].startswith("S-030, S-038, S-074"), "dispatch reader: fixed ordering S-030, S-038, S-074 first", inc_line))
    checks.append(("excluded W-001" in dsp and "reader cc-dispatch does not read" in dsp, "dispatch reader: cw-only block excluded for reader reason", ""))
    checks.append(("excluded S-034" in dsp, "dispatch reader: cc-local block excluded", ""))
    cw = read(td/"s"/".forge/protocols/start-protocol.yaml")
    checks.append(("# --- S-002" in cw and "# --- S-074" in cw, "cw reader: dispatch blocks included", ""))
    ep = read(td/"s"/".forge/protocols/end-protocol.yaml")
    checks.append(("# --- E-018" in ep and "excluded E-020" in ep, "sandbox end: supabase block in, relay block out", ""))
    # manifest partition: included + excluded == total on every file
    for f in ["start-protocol.yaml", "start-protocol.dispatch.yaml", "end-protocol.yaml", "end-protocol.dispatch.yaml"]:
        t = read(td/"s"/".forge/protocols"/f)
        m = [l for l in t.split("\n") if l.startswith("# BLOCK MANIFEST")][0]
        nums = [int(x) for x in m.replace(",", "").split() if x.isdigit()]
        checks.append((nums[0] + nums[1] == nums[2], f"manifest partition holds for {f}", m))
    # 4. legacy: gentle pull (S-034 excluded), spike block in, relay block in with substitution
    render("config-legacy.yaml", td / "l")
    ls = read(td/"l"/".forge/protocols/start-protocol.yaml"); le = read(td/"l"/".forge/protocols/end-protocol.yaml")
    checks.append(("excluded S-034" in ls and "# --- S-026" in ls and "desktop, wsl-build, phone" in ls, "legacy: hard-reset out, spike in, surfaces substituted", ""))
    checks.append(("# --- E-020" in le and "synclips-relay" in le, "legacy: relay block in with companion name substituted", ""))
    # enum literal "none" is a STRING value (build.deploy: none), not YAML null — S-083/S-085 must render for it
    checks.append(("# --- S-085" in ls, "legacy: 'build.deploy == none' block INCLUDED (enum literal none is a string)", ""))
    checks.append(("excluded S-085" in sp and "build.deploy == none" in sp, "standard: 'build.deploy == none' block excluded for a vercel repo", ""))
    # 5. effective values written back into the config
    ec = read(td/"l"/".forge/protocol-config.yaml")
    checks.append(("# --- effective values" in ec and "# mirror.github_is_complete_mirror: false" in ec, "config: effective values comment block written", ""))
    # 6. CLAUDE.md marker replacement leaves the rest byte-identical
    shutil.copy(FIX / "CLAUDE.md", td / "CLAUDE.md")
    render("config-standard.yaml", td / "c", extra=("--claude-md", str(td / "CLAUDE.md")))
    cm = read(td/"c"/"CLAUDE.md")
    checks.append((cm.startswith("# CLAUDE.md for fixture\n\nProject notes stay untouched.") and cm.rstrip().endswith("Trailing notes stay untouched.") and "old block" not in cm and "chromasmith/fixture-standard" in cm and MASTER_VERSION in cm, "CLAUDE.md: only the marker interior replaced", ""))
    checks.append(("Dispatched runner rules" not in cm and "render_when" not in cm, "CLAUDE.md: dispatch-fenced lines dropped with their fences for a no-dispatch repo", ""))
    shutil.copy(FIX / "CLAUDE.md", td / "CLAUDE-s.md")
    render("config-sandbox.yaml", td / "cs", extra=("--claude-md", str(td / "CLAUDE-s.md")))
    cms = read(td/"cs"/"CLAUDE.md")
    checks.append(("Dispatched runner rules" in cms and "render_when" not in cms and cms.rstrip().endswith("Trailing notes stay untouched."), "CLAUDE.md: dispatch-fenced lines kept, fences removed, for a dispatch repo", ""))
    badmd = td / "badmd"; shutil.copytree(MASTER, badmd)
    f = badmd / "claude-md.house-block.master.md"; f.write_text(read(f).replace("<!-- <<< end render_when -->\n", ""), encoding="utf-8")
    r = run("render", "--config", str(FIX/"config-standard.yaml"), "--master-dir", str(badmd), "--out", str(td/"x5"), "--date", DATE, "--claude-md", str(td / "CLAUDE.md"), expect=1)
    checks[-1] = (r.returncode == 1 and "never closed" in r.stderr, "CLAUDE.md: unclosed fence fails the render", r.stderr.strip()[-120:])
    # 7. check mode: identical -> 0, then a hand-edit -> drift
    run("check", "--config", str(FIX/"config-standard.yaml"), "--master-dir", str(MASTER), "--against", str(td/"a"), "--date", DATE, expect=0)
    p = td/"a"/".forge/protocols/start-protocol.yaml"; p.write_text(read(p) + "# hand edit\n", encoding="utf-8")
    run("check", "--config", str(FIX/"config-standard.yaml"), "--master-dir", str(MASTER), "--against", str(td/"a"), "--date", DATE, expect=1)
    # 8. failure modes
    render("config-bad-unknown.yaml", td / "x1"); checks[-1] = (checks[-1][0] is False, "fails on unknown override field", checks[-1][2])
    render("config-bad-dispatch.yaml", td / "x2"); checks[-1] = (checks[-1][0] is False, "fails when dispatch enabled without complete mirror", checks[-1][2])
    # standalone check: inject a forbidden phrase and an unresolved placeholder into a copy of the fixture master
    bad = td / "badmaster"; shutil.copytree(MASTER, bad)
    f = bad / "end-protocol.master.yaml"; f.write_text(read(f).replace("only if migrations ran.", "only if migrations ran; see the master for details."), encoding="utf-8")
    r = run("render", "--config", str(FIX/"config-sandbox.yaml"), "--master-dir", str(bad), "--out", str(td/"x3"), "--date", DATE, expect=1)
    checks[-1] = (r.returncode == 1 and "standalone check failed" in r.stderr, "fails standalone check on 'see the master'", r.stderr.strip()[-120:])
    bad2 = td / "badmaster2"; shutil.copytree(MASTER, bad2)
    f = bad2 / "start-protocol.master.yaml"; f.write_text(read(f).replace("{{repo.org}}", "{{repo.orgg}}"), encoding="utf-8")
    r = run("render", "--config", str(FIX/"config-standard.yaml"), "--master-dir", str(bad2), "--out", str(td/"x4"), "--date", DATE, expect=1)
    checks[-1] = (r.returncode == 1 and "unresolved placeholder" in r.stderr, "fails on unresolved placeholder", r.stderr.strip()[-120:])
    # 9. evidence companion check
    r = run("evidence", str(FIX/"wrap-good.yaml"), expect=0); checks[-1] = (r.returncode == 0 and "2 claims verified by ID, 1 reported unverified" in r.stdout, "evidence: good wrap counts 2 verified / 1 reported", r.stdout.strip())
    r = run("evidence", str(FIX/"wrap-bad.yaml"), expect=1); checks[-1] = (r.returncode == 1 and "unmarked" in r.stdout, "evidence: bare 'shipped' line fails", r.stdout.strip()[:80])

fails = [c for c in checks if not c[0]]
for ok, name, detail in checks:
    print(("PASS " if ok else "FAIL ") + name + (("\n      " + detail) if (not ok and detail) else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} checks passed")
sys.exit(1 if fails else 0)
