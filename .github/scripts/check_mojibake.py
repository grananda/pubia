#!/usr/bin/env python3
"""Caza mojibake en los ficheros de texto del repo.

Este marketplace escribe en espanol y los criterios de correccion estan llenos
de tildes, enies y comillas latinas. Un UTF-8 releido como latin-1 convierte la
doctrina en basura ilegible, y en un diff largo no se ve.

La deteccion no busca una lista de palabras rotas, sino la firma del error: un
byte de cabecera UTF-8 (0xC2, 0xC3, 0xE2) seguido de un byte de continuacion
(0x80-0xBF), que es lo que aparece cuando el texto se decodifica como latin-1.
Los patrones se construyen con chr() para que este fichero no contenga el
propio mojibake que persigue.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CABECERAS = chr(0xC2) + chr(0xC3) + chr(0xE2)
CONTINUACION = chr(0x80) + "-" + chr(0xBF)
FIRMA = re.compile("[" + CABECERAS + "][" + CONTINUACION + "]")
BOM = chr(0xFEFF)

EXTENSIONES = {".md", ".py", ".json", ".yml", ".yaml", ".html", ".txt"}

fallos: list[str] = []
revisados = 0

for ruta in sorted(ROOT.rglob("*")):
    if not ruta.is_file() or ".git" in ruta.parts or ruta.suffix not in EXTENSIONES:
        continue
    try:
        texto = ruta.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        fallos.append(f"{ruta.relative_to(ROOT)}: no es UTF-8 valido")
        continue
    revisados += 1
    rel = ruta.relative_to(ROOT)
    for n, linea in enumerate(texto.splitlines(), 1):
        if BOM in linea:
            fallos.append(f"{rel}:{n}: marca de orden de bytes (BOM) suelta en el texto")
            continue
        m = FIRMA.search(linea)
        if m:
            visible = m.group(0).encode("unicode_escape").decode()
            fallos.append(f"{rel}:{n}: firma de mojibake ({visible}) en: {linea.strip()[:70]}")

if fallos:
    print("Mojibake o codificacion rota:", file=sys.stderr)
    for f in fallos:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)
print(f"Codificacion correcta en {revisados} ficheros.")
