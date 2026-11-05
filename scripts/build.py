#!/usr/bin/env python3
"""Build the static site into _site/ (index.html + data.json).

    python scripts/build.py            # writes _site/
    python -m http.server -d _site     # preview at http://localhost:8000
"""
import json
import shutil
import sys
from pathlib import Path

from curedata import ROOT, compile_site, load_all, validate

out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
data = load_all()
errors = validate(data)
if errors:
    print("Validation failed; run scripts/validate.py for details.")
    sys.exit(1)
out.mkdir(parents=True, exist_ok=True)
site = compile_site(data)
(out / "data.json").write_text(json.dumps(site, ensure_ascii=False, separators=(",", ":"), default=str), encoding="utf-8")
for f in (ROOT / "site").iterdir():
    if f.is_file():
        shutil.copy2(f, out / f.name)
print(f"Built {len(site['diseases'])} diseases and {len(site['gates'])} pipeline stages into {out}")
