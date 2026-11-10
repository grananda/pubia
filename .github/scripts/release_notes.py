#!/usr/bin/env python3
"""Genera las notas de release.

A quien consume el marketplace solo le importa si tiene que reinstalar algo,
que version queda y que trae. Eso no se deduce de la lista de commits.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

mk = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
lineas = [f"## PUBIA {version}", ""]

for entrada in mk.get("plugins", []):
    pj = ROOT / entrada["source"] / ".claude-plugin" / "plugin.json"
    d = json.loads(pj.read_text(encoding="utf-8"))
    skills = sorted(p.parent.name for p in (ROOT / entrada["source"] / "skills").glob("*/SKILL.md"))
    lineas += [f"**{d['name']} {d['version']}** — {len(skills)} skills: " + ", ".join(f"`{s}`" for s in skills), ""]

anterior = subprocess.run(["git", "describe", "--tags", "--abbrev=0", f"v{version}^"],
                          capture_output=True, text=True, cwd=ROOT).stdout.strip()
if anterior:
    log = subprocess.run(["git", "log", "--pretty=- %s", f"{anterior}..HEAD"],
                         capture_output=True, text=True, cwd=ROOT).stdout.strip()
    # Fuera el ruido de mantenimiento: interesa lo que cambia para quien lo usa.
    utiles = [l for l in log.splitlines()
              if not re.match(r"- (chore|ci|docs?\(ci\)|merge)\b", l, re.I)]
    if utiles:
        lineas += [f"### Cambios desde {anterior}", "", *utiles, ""]

lineas += [
    "### Instalacion",
    "",
    "```",
    f"/plugin marketplace add {mk.get('repositorio', 'grananda/pubia')}",
    f"/plugin install pubia@{mk['name']}",
    "```",
    "",
    "Requiere `uv` en el PATH. Los scripts resuelven sus dependencias al ejecutarse.",
]
print("\n".join(lineas))
