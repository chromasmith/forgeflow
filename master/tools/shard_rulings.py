#!/usr/bin/env python
# shard_rulings.py — split a legacy single-file rulings register into twenty-entry shards (ForgeFlow v1.4.0, E-003).
#   python master/tools/shard_rulings.py <repo>/.forge/rulings.yaml [--keep]
# Writes <repo>/.forge/rulings/001-020.yaml, 021-040.yaml, ... with every entry byte-identical to the original and
# the original header comment repeated in each shard; deletes the original unless --keep. Prints a proof line
# (entry count in == entries out, ids in order) and exits non-zero on any mismatch. No YAML library needed; entries
# are sliced on the "  - id: " boundary so the bytes are untouched.
import io, os, re, sys

SHARD = 20

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    keep = "--keep" in sys.argv
    if len(args) != 1:
        sys.exit("usage: shard_rulings.py <path/to/.forge/rulings.yaml> [--keep]")
    src = args[0]
    if not os.path.isfile(src):
        sys.exit("not a file: " + src)
    outdir = os.path.join(os.path.dirname(src), "rulings")
    if os.path.isdir(outdir) and os.listdir(outdir):
        sys.exit("refusing: " + outdir + " already exists and is not empty (register already sharded?)")
    with io.open(src, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    key = "rulings:" + nl
    k = text.find(key)
    if k < 0:
        sys.exit("no 'rulings:' key found in " + src)
    header = text[:k]                       # comment lines before the list key, kept verbatim in every shard
    body = text[k + len(key):]
    starts = [m.start() for m in re.finditer(r"(?m)^  - id: ", body)]
    if not starts:
        sys.exit("no entries found")
    entries = [body[starts[i]:(starts[i + 1] if i + 1 < len(starts) else len(body))] for i in range(len(starts))]
    ids = [re.match(r"  - id: (\S+)", e).group(1) for e in entries]
    os.makedirs(outdir, exist_ok=True)
    written = []
    for i in range(0, len(entries), SHARD):
        first, last = i + 1, i + SHARD
        name = "%03d-%03d.yaml" % (first, last)
        path = os.path.join(outdir, name)
        shard_note = "# Shard %s of the rulings register — twenty rulings per file; the newest shard takes appends. Other shards live beside this one in .forge/rulings/.%s" % (name, nl)
        content = header + shard_note + key + "".join(entries[i:i + SHARD])
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        written.append((path, len(entries[i:i + SHARD])))
    # proof: re-slice the shards and compare bytes + ids
    back = []
    for path, _ in written:
        with io.open(path, "r", encoding="utf-8", newline="") as f:
            t = f.read()
        b = t[t.find(key) + len(key):]
        s2 = [m.start() for m in re.finditer(r"(?m)^  - id: ", b)]
        back += [b[s2[j]:(s2[j + 1] if j + 1 < len(s2) else len(b))] for j in range(len(s2))]
    if back != entries:
        sys.exit("PROOF FAILED: shard entries differ from the original bytes")
    if not keep:
        os.remove(src)
    print("sharded %d rulings (%s .. %s) into %d file(s):" % (len(entries), ids[0], ids[-1], len(written)))
    for path, n in written:
        print("  %s  (%d entries)" % (path, n))
    print("proof: every entry byte-identical; original " + ("kept" if keep else "deleted"))

if __name__ == "__main__":
    main()
