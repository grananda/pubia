#!/usr/bin/env python3
"""Las rutas que un skill nombra resuelven donde el skill las busca.

Los skills se cargan en diferido: el agente lee un `references/*.md` solo cuando
el `SKILL.md` se lo dice. Una ruta que no resuelve **no da error**: el agente no
encuentra el fichero, sigue sin el, y la regla que contenia simplemente no se
aplica. Es el peor fallo posible aqui, porque se parece a que todo funciona.

Ya paso una vez en este repo: `pubia-biblia` invocaba el lector con
`${CLAUDE_PLUGIN_ROOT}/../pubia-revisa/scripts/...`, que no existe, porque la
raiz del plugin no es la carpeta del skill.

Convencion del repo:

| Destino | Forma |
|---|---|
| El mismo skill | `references/x.md`, `scripts/x.py` |
| Otro skill del plugin | `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/x.py` |

Y el reverso: un `references/*.md` o un `scripts/*.py` que nadie nombra no lo
lee ni lo ejecuta nadie, y parece documentacion vigente.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RAIZ = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)")
INTERNA = re.compile(r"`((?:references|scripts|assets)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`")

fallos: list[str] = []
resueltas = 0

for plugin in sorted(ROOT.glob("plugins/*")):
    if not (plugin / ".claude-plugin" / "plugin.json").is_file():
        continue
    for skill in sorted(plugin.glob("skills/*")):
        for fichero in sorted(skill.rglob("*.md")):
            rel = fichero.relative_to(ROOT)
            texto = fichero.read_text(encoding="utf-8")

            for ruta in RAIZ.findall(texto):
                destino = plugin / ruta
                if destino.is_file():
                    resueltas += 1
                else:
                    fallos.append(f"{rel}: ${{CLAUDE_PLUGIN_ROOT}}/{ruta} no existe "
                                  f"(se busca en {destino.relative_to(ROOT)})")

            for ruta in INTERNA.findall(texto):
                destino = skill / ruta
                if destino.is_file():
                    resueltas += 1
                else:
                    fallos.append(f"{rel}: `{ruta}` no existe dentro del skill "
                                  f"(se busca en {destino.relative_to(ROOT)})")

        # Huerfanos: ficheros del skill que ningun .md nombra.
        nombrados = " ".join(f.read_text(encoding="utf-8") for f in skill.rglob("*.md"))
        for recurso in sorted(list(skill.glob("references/*")) + list(skill.glob("scripts/*"))
                              + list(skill.glob("assets/*"))):
            if recurso.is_file() and recurso.name not in nombrados:
                fallos.append(f"{recurso.relative_to(ROOT)}: no lo nombra ningun .md del skill, "
                              f"asi que nadie lo lee ni lo ejecuta")

if fallos:
    print("Rutas de skills que no resuelven:", file=sys.stderr)
    for f in fallos:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)
print(f"Rutas correctas: {resueltas} referencias resueltas y ningun recurso huerfano.")
