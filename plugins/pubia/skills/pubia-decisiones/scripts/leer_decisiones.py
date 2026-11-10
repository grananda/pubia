#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.2.0"]
# ///
"""Cierra el ciclo de una revision: que acepto y que rechazo el autor.

Dos fuentes de verdad, combinables:

1. La columna "Decision" de la tabla resumen del .docx, si el autor la ha
   rellenado en Word (--docx).
2. El manuscrito despues de las correcciones manuales (--nueva-fuente): se
   comprueba, marca a marca, si el texto original sigue ahi o si la propuesta
   aparece ya en el texto. Es la via automatica y no requiere que el autor
   anote nada.

Salida: una tabla por consola y, con --salida, un JSON para que la skill
actualice biblia/decisiones.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ACEPTA = {"si", "sí", "ok", "acepto", "aceptada", "aceptado", "aplicada", "aplicado", "x", "v", "✓", "sip"}
RECHAZA = {"no", "rechazo", "rechazada", "rechazado", "nope", "n"}


def leer_tabla_docx(ruta: Path) -> dict[int, str]:
    from docx import Document

    doc = Document(str(ruta))
    if not doc.tables:
        return {}
    tabla = doc.tables[-1]
    cabecera = [c.text.strip().lower() for c in tabla.rows[0].cells]
    if not cabecera or not cabecera[0].startswith("#"):
        return {}
    try:
        col = next(i for i, c in enumerate(cabecera) if c.startswith("decis"))
    except StopIteration:
        return {}
    decisiones: dict[int, str] = {}
    for fila in tabla.rows[1:]:
        celdas = fila.cells
        try:
            n = int(celdas[0].text.strip())
        except (ValueError, IndexError):
            continue
        valor = celdas[col].text.strip() if col < len(celdas) else ""
        if valor:
            decisiones[n] = valor
    return decisiones


def normaliza_decision(valor: str) -> str:
    bruto = " ".join(valor.split()).strip().lower().rstrip(".")
    if bruto in ACEPTA:
        return "aceptada"
    if bruto in RECHAZA:
        return "rechazada"
    if not bruto:
        return "sin decidir"
    # El autor rara vez escribe solo "no": lo normal es "no, porque...".
    primera = bruto.replace(",", " ").replace(":", " ").split()[0]
    if primera in RECHAZA:
        return "rechazada"
    if primera in ACEPTA:
        return "aceptada"
    return "comentada"


def texto_completo(fuente: dict) -> str:
    return "\n".join(p["texto"] for p in fuente["parrafos"])


def inferir(marca: dict, antes: str, despues: str) -> tuple[str, str]:
    """Deduce que paso con una marca comparando el texto antes y despues."""
    buscar = marca.get("buscar") or ""
    propuesta = (marca.get("propuesta") or "").strip()
    tipo = marca.get("tipo")

    if not buscar:
        return "sin rastro", "comentario a todo el parrafo: no se puede deducir"

    sigue = buscar in despues
    if tipo == "correccion":
        if not sigue and propuesta and propuesta in despues:
            return "aceptada", "el original ya no esta y la propuesta si"
        if not sigue:
            return "reescrita", "el original ya no esta, pero tampoco la propuesta literal"
        return "rechazada", "el original sigue en el manuscrito"
    if tipo == "supresion":
        return ("aceptada", "el fragmento ya no esta") if not sigue else ("rechazada", "el fragmento sigue")
    # comentario
    if sigue:
        return "sin cambios", "el pasaje comentado sigue igual"
    return "atendida", "el pasaje comentado ha cambiado"


def main() -> int:
    ap = argparse.ArgumentParser(description="Lee las decisiones del autor sobre una revision.")
    ap.add_argument("--resueltas", required=True,
                    help="JSON *.resueltas.json que genero anota_docx.py junto al .docx")
    ap.add_argument("--docx", help=".docx de la revision, si el autor relleno la columna Decision")
    ap.add_argument("--fuente", help="JSON de fuente con el que se genero la revision")
    ap.add_argument("--nueva-fuente", help="JSON de fuente re-extraido tras las correcciones manuales")
    ap.add_argument("--salida", help="Ruta de un JSON con el resultado")
    args = ap.parse_args()

    marcas_json = json.loads(Path(args.resueltas).read_text(encoding="utf-8"))
    marcas = marcas_json.get("marcas", [])
    if not marcas or "n" not in marcas[0]:
        print("ERROR: --resueltas debe apuntar al *.resueltas.json generado junto al .docx "
              "(lleva la numeracion #n que ve el autor).", file=sys.stderr)
        return 2

    anotadas = leer_tabla_docx(Path(args.docx)) if args.docx else {}

    antes = despues = ""
    if args.nueva_fuente:
        if not args.fuente:
            print("ERROR: --nueva-fuente necesita tambien --fuente", file=sys.stderr)
            return 2
        antes = texto_completo(json.loads(Path(args.fuente).read_text(encoding="utf-8")))
        despues = texto_completo(json.loads(Path(args.nueva_fuente).read_text(encoding="utf-8")))

    filas = []
    for marca in sorted(marcas, key=lambda m: m["n"]):
        decision = normaliza_decision(anotadas.get(marca["n"], ""))
        nota_autor = anotadas.get(marca["n"], "")
        inferida, motivo = ("", "")
        if despues:
            inferida, motivo = inferir(marca, antes, despues)
        filas.append({
            "n": marca["n"],
            "parrafo": marca.get("parrafo"),
            "tipo": marca.get("tipo"),
            "categoria": marca.get("categoria"),
            "buscar": marca.get("buscar", ""),
            "propuesta": marca.get("propuesta", ""),
            "comentario": marca.get("texto", ""),
            "decision_autor": decision,
            "nota_autor": nota_autor,
            "decision_inferida": inferida,
            "motivo": motivo,
        })

    ancho = 58
    print(f"{'#':>3}  {'tipo':<11} {'categoria':<13} {'autor':<12} {'inferida':<12} texto")
    print("-" * 110)
    for f in filas:
        muestra = " ".join((f["buscar"] or f["comentario"]).split())[:ancho]
        print(f"{f['n']:>3}  {f['tipo']:<11} {f['categoria']:<13} "
              f"{f['decision_autor']:<12} {f['decision_inferida']:<12} {muestra}")

    rechazadas = [f for f in filas if f["decision_autor"] == "rechazada" or f["decision_inferida"] == "rechazada"]
    print("-" * 110)
    print(f"total {len(filas)}  ·  rechazadas {len(rechazadas)}  ·  "
          f"aceptadas {sum(1 for f in filas if 'aceptada' in (f['decision_autor'], f['decision_inferida']))}")
    if not anotadas and not despues:
        print("AVISO: sin --docx anotado ni --nueva-fuente no hay nada que deducir; "
              "pasa al menos uno de los dos.")

    if args.salida:
        ruta = Path(args.salida).expanduser()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps({"meta": marcas_json.get("meta", {}), "decisiones": filas},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"JSON: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
