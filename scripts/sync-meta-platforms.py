#!/usr/bin/env python3
"""Sync galaxy_info.platforms in meta/main.yml from molecule/platforms.yml.

molecule/platforms.yml is the single source of truth for the platforms
this role officially supports. After editing it, run this script to
update meta/main.yml so Ansible Galaxy reflects the current list.
"""
from __future__ import annotations

import sys
from collections import OrderedDict
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent.parent
PLATFORMS_FILE = ROOT / "molecule" / "shared" / "platforms.yml"
META_FILE = ROOT / "meta" / "main.yml"


def main() -> int:
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True
    yaml.width = 4096

    with PLATFORMS_FILE.open() as f:
        platforms = yaml.load(f)["platforms"]

    grouped: OrderedDict[str, list[str]] = OrderedDict()
    for p in platforms:
        # Future / development branches omit `galaxy:` because Galaxy doesn't
        # accept their version strings (forky, sid, rawhide).
        g = p.get("galaxy")
        if not g:
            continue
        grouped.setdefault(g["name"], [])
        if g["version"] not in grouped[g["name"]]:
            grouped[g["name"]].append(g["version"])

    galaxy_platforms = [
        {"name": name, "versions": list(versions)}
        for name, versions in grouped.items()
    ]

    with META_FILE.open() as f:
        meta = yaml.load(f)
    meta["galaxy_info"]["platforms"] = galaxy_platforms

    with META_FILE.open("w") as f:
        yaml.dump(meta, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
