#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["striprtf>=0.0.26"]
# ///
"""Extrae el texto de un manuscrito (Scrivener) a un JSON de parrafos numerados.

Es el primer paso de `pubia revisa`: produce la fuente canonica sobre la que se
anota. El texto del .docx de revision sale SIEMPRE de este JSON, nunca de un
texto reescrito por el modelo, para garantizar que la revision es sobre el
manuscrito real.

Uso:
  uv run leer_manuscrito.py --fuente <fichero-o-carpeta> --salida fuente.json
  uv run leer_manuscrito.py --fuente Novela-sync/Draft --filtro "cap-12" --salida f.json

Formatos de entrada: .rtf (Scrivener), .txt, .md. Si --fuente es una carpeta se
usa su subcarpeta Draft/ cuando existe (estructura de "Sincronizar con carpeta
externa" de Scrivener) y se ordenan los ficheros por el prefijo numerico que
Scrivener anade.

Solo lectura: este script nunca escribe en la ruta de origen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

EXTENSIONES = {".rtf", ".txt", ".md", ".markdown", ".text"}
SEPARADORES = {"#", "##", "###", "*", "**", "***", "* * *", "- - -", "---", "~~~", "§"}
RE_PREFIJO_NUM = re.compile(r"^\s*(\d+)")
RE_ESPACIOS = re.compile(r"[ \t ]+")


def descomprimir_rtf(ruta: Path) -> str:
    from striprtf.striprtf import rtf_to_text

    return rtf_to_text(ruta.read_text(encoding="utf-8", errors="replace"), errors="ignore")


def leer_fichero(ruta: Path) -> str:
    if ruta.suffix.lower() == ".rtf":
        return descomprimir_rtf(ruta)
    return ruta.read_text(encoding="utf-8", errors="replace")


def orden_natural(ruta: Path) -> tuple:
    m = RE_PREFIJO_NUM.match(ruta.stem)
    return (0, int(m.group(1)), ruta.stem) if m else (1, 0, ruta.stem)


def recoger_ficheros(fuente: Path, filtro: str | None) -> list[Path]:
    if fuente.is_file():
        ficheros = [fuente]
    else:
        raiz = fuente / "Draft" if (fuente / "Draft").is_dir() else fuente
        ficheros = [
            p
            for p in raiz.rglob("*")
            if p.is_file()
            and p.suffix.lower() in EXTENSIONES
            and not p.name.startswith(".")
            and "Trash" not in p.parts
            and "Notes" not in p.parts
        ]
        ficheros.sort(key=orden_natural)
    if filtro:
        aguja = filtro.lower()
        ficheros = [p for p in ficheros if aguja in str(p).lower()]
    return ficheros


def normalizar(texto: str) -> str:
    """Normaliza invisibles sin tocar la ortografia ni la tipografia del autor."""
    texto = unicodedata.normalize("NFC", texto)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = texto.replace("\u200b", "").replace("\ufeff", "")
    return texto


def trocear(texto: str, modo: str) -> list[str]:
    texto = normalizar(texto)
    if modo == "bloques":
        crudos = re.split(r"\n\s*\n", texto)
    else:  # lineas: un parrafo por linea, como exporta Scrivener
        crudos = texto.split("\n")
    salida = []
    for bruto in crudos:
        limpio = RE_ESPACIOS.sub(" ", bruto.replace("\n", " ")).strip()
        if limpio:
            salida.append(limpio)
    return salida


def clasificar(parrafo: str) -> str:
    desnudo = parrafo.strip()
    if desnudo in SEPARADORES or re.fullmatch(r"[\*\-_~ ]{3,}", desnudo):
        return "separador"
    if desnudo.startswith("#"):
        return "titulo"
    if re.match(r"^[—–-]\s*\S", desnudo):
        return "dialogo"
    return "narracion"


def contar_palabras(texto: str) -> int:
    return len(re.findall(r"\b[\wÀ-ɏ'’-]+\b", texto, flags=re.UNICODE))


def main() -> int:
    ap = argparse.ArgumentParser(description="Extrae el manuscrito a JSON de parrafos.")
    ap.add_argument("--fuente", required=True, help="Fichero .rtf/.txt/.md o carpeta de sincronizacion de Scrivener")
    ap.add_argument("--salida", required=True, help="Ruta del JSON de fuente a generar")
    ap.add_argument("--filtro", help="Subcadena para quedarse solo con los ficheros que la contienen")
    ap.add_argument("--parrafos", choices=["lineas", "bloques"], default="lineas",
                    help="lineas (por defecto, Scrivener) o bloques separados por linea en blanco")
    ap.add_argument("--titulo", help="Titulo para la revision (por defecto, el nombre del fichero)")
    args = ap.parse_args()

    fuente = Path(args.fuente).expanduser()
    if not fuente.exists():
        print(f"ERROR: no existe la fuente: {fuente}", file=sys.stderr)
        return 2

    ficheros = recoger_ficheros(fuente, args.filtro)
    if not ficheros:
        print(f"ERROR: ningun fichero de texto en {fuente}" + (f" con filtro '{args.filtro}'" if args.filtro else ""),
              file=sys.stderr)
        return 2

    parrafos: list[dict] = []
    documentos: list[dict] = []
    sha = hashlib.sha256()
    siguiente = 1
    for ruta in ficheros:
        texto = leer_fichero(ruta)
        sha.update(texto.encode("utf-8", errors="replace"))
        trozos = trocear(texto, args.parrafos)
        primero = siguiente
        for trozo in trozos:
            parrafos.append({
                "id": siguiente,
                "documento": ruta.name,
                "tipo": clasificar(trozo),
                "palabras": contar_palabras(trozo),
                "texto": trozo,
            })
            siguiente += 1
        documentos.append({
            "fichero": str(ruta),
            "nombre": ruta.stem,
            "parrafos": [primero, siguiente - 1] if siguiente > primero else [],
            "palabras": sum(p["palabras"] for p in parrafos[primero - 1:siguiente - 1]),
        })

    if not parrafos:
        print("ERROR: la fuente no contiene texto aprovechable", file=sys.stderr)
        return 2

    salida = Path(args.salida).expanduser()
    salida.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "meta": {
            "titulo": args.titulo or (fuente.stem if fuente.is_file() else fuente.name),
            "fuente": str(fuente),
            "modo_parrafos": args.parrafos,
            "sha256": sha.hexdigest(),
            "documentos": documentos,
            "total_parrafos": len(parrafos),
            "total_palabras": sum(p["palabras"] for p in parrafos),
        },
        "parrafos": parrafos,
    }
    salida.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"OK  {salida}")
    print(f"    documentos: {len(documentos)}  parrafos: {len(parrafos)}  palabras: {datos['meta']['total_palabras']}")
    for d in documentos:
        rango = f"{d['parrafos'][0]}-{d['parrafos'][1]}" if d["parrafos"] else "vacio"
        print(f"    [{rango}] {d['nombre']} ({d['palabras']} palabras)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
