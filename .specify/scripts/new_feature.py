#!/usr/bin/env python3
"""Scaffold specs/NNN-<name>/ from .specify/templates. Usage: new_feature.py 001-repo-and-ci "Repo and CI" """
import pathlib, sys
root = pathlib.Path(__file__).resolve().parents[2]
if len(sys.argv) < 3:
    sys.exit(__doc__)
fid, title = sys.argv[1], sys.argv[2]
dest = root / "specs" / fid
if dest.exists():
    sys.exit(f"{dest} already exists")
dest.mkdir(parents=True)
(dest / "contracts").mkdir()
for t in ("spec", "plan", "tasks"):
    text = (root / ".specify/templates" / f"{t}-template.md").read_text()
    text = text.replace("NNN-<name>", fid).replace("NNN", fid.split("-")[0]).replace("<Title>", title)
    (dest / f"{t}.md").write_text(text)
print(f"scaffolded {dest}")
