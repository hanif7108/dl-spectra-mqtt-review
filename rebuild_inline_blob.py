#!/usr/bin/env python3
"""
rebuild_inline_blob.py
======================
Re-embed manuscript_en.md and manuscript_id.md into index.html as the
MANUSCRIPTS global JavaScript object. Run this after editing either
Markdown file, then commit index.html together with the updated manuscripts.

Usage
-----
    cd /path/to/dl-spectra-mqtt-review
    python3 rebuild_inline_blob.py

Exit codes
----------
    0  success
    1  MANUSCRIPTS const not found in index.html
    2  manuscript_en.md or manuscript_id.md missing
"""
from __future__ import annotations

import json
import pathlib
import re
import sys


def main() -> int:
    root = pathlib.Path(__file__).parent
    en_path = root / "manuscript_en.md"
    id_path = root / "manuscript_id.md"
    idx_path = root / "index.html"

    for p in (en_path, id_path, idx_path):
        if not p.exists():
            print(f"ERROR: missing file: {p}", file=sys.stderr)
            return 2

    en = en_path.read_text(encoding="utf-8")
    id_ = id_path.read_text(encoding="utf-8")
    blob = "const MANUSCRIPTS = " + json.dumps(
        {"en": en, "id": id_}, ensure_ascii=False
    ) + ";"

    html = idx_path.read_text(encoding="utf-8")
    pattern = re.compile(r"const MANUSCRIPTS = \{.*?\};", re.DOTALL)
    if not pattern.search(html):
        print("ERROR: MANUSCRIPTS const not found in index.html", file=sys.stderr)
        return 1

    new_html = pattern.sub(blob, html, count=1)
    idx_path.write_text(new_html, encoding="utf-8")
    kb = len(new_html) // 1024
    print(f"✓ Updated {idx_path} ({kb} KB · EN {len(en)} chars · ID {len(id_)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
