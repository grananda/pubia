#!/usr/bin/env python3
"""Valida los HTML de docs/: cierre, anidamiento y SVG bien formado.

El diagrama se publica y se abre en local. Un SVG mal cerrado no da error
visible: deja de dibujar media figura y nadie se entera. Contar etiquetas no
basta, porque no detecta un anidamiento cruzado.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VACIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
          "meta", "param", "source", "track", "wbr"}


class Validador(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.pila: list[tuple[str, tuple[int, int]]] = []
        self.fallos: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VACIOS:
            self.pila.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VACIOS:
            return
        if self.pila and self.pila[-1][0] == tag:
            self.pila.pop()
            return
        for i in range(len(self.pila) - 1, -1, -1):
            if self.pila[i][0] == tag:
                colgando = ", ".join(f"<{t}> (linea {p[0]})" for t, p in self.pila[i + 1:])
                self.fallos.append(
                    f"linea {self.getpos()[0]}: </{tag}> cierra saltandose {colgando}")
                del self.pila[i:]
                return
        self.fallos.append(f"linea {self.getpos()[0]}: </{tag}> sin apertura")


def atributos_sin_comillas(s: str) -> list[str]:
    """Busca solo dentro del texto de las etiquetas, con los valores vaciados."""
    malos: list[str] = []
    for etiqueta in re.findall(r"<[a-zA-Z][^>]*>", s):
        desnuda = re.sub(r'"[^"]*"', '""', etiqueta)
        malos += re.findall(r'\s[\w-]+=([^"\s>][^\s>]*)', desnuda)
    return malos


fallos: list[str] = []
revisados = 0

for ruta in sorted(ROOT.glob("docs/*.html")):
    rel = ruta.relative_to(ROOT)
    s = ruta.read_text(encoding="utf-8")
    revisados += 1

    v = Validador()
    v.feed(s)
    v.close()
    fallos += [f"{rel}: {f}" for f in v.fallos]
    fallos += [f"{rel}: <{t}> abierto en linea {p[0]} y nunca cerrado" for t, p in v.pila]

    # Un SVG en linea tiene que ser XML bien formado: es el criterio real.
    for n, frag in enumerate(re.findall(r"<svg\b.*?</svg>", s, re.S), 1):
        limpio = re.sub(r"var\(--[a-z-]+\)", "black", frag).replace("url(#", "url(%23")
        try:
            ET.fromstring(limpio)
        except ET.ParseError as exc:
            fallos.append(f"{rel}: svg {n} no es XML bien formado ({exc})")

    ids = set(re.findall(r'\bid="([^"]+)"', s))
    refs = set(re.findall(r"url\(#([^)]+)\)", s)) | set(re.findall(r'href="#([^"]+)"', s))
    if refs - ids:
        fallos.append(f"{rel}: referencias internas sin destino: {sorted(refs - ids)}")
    if ids - refs:
        fallos.append(f"{rel}: ids definidos y nunca usados: {sorted(ids - refs)}")

    for bloque in re.findall(r"<style[^>]*>(.*?)</style>", s, re.S):
        if bloque.count("{") != bloque.count("}"):
            fallos.append(f"{rel}: llaves de CSS descompensadas")
    malos = atributos_sin_comillas(s)
    if malos:
        fallos.append(f"{rel}: atributos sin comillas: {malos[:5]}")
    for etiqueta in ("<!doctype html>", "<html", "</html>", "<head>", "</head>",
                     "<body>", "</body>", "<title>"):
        if etiqueta not in s.lower():
            fallos.append(f"{rel}: falta {etiqueta}")

if fallos:
    print("HTML con problemas:", file=sys.stderr)
    for f in fallos:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)
print(f"HTML correcto en {revisados} ficheros de docs/.")
