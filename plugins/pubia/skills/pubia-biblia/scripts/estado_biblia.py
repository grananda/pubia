#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Que le falta a la biblia: los documentos nuevos o cambiados desde que se absorbieron.

Lo usan `pubia revisa` (antes de revisar un capitulo, para que la biblia cubra
todo lo anterior), `pubia continuidad` (antes de auditar) y `pubia biblia`
(para leer solo lo que cambio y, al terminar, apuntar lo absorbido).

Entradas:
  --manuscrito  JSON de leer_manuscrito.py sobre el manuscrito completo
  --huellas     biblia/huellas.json (si no existe, la biblia no ha absorbido nada)

Uso:
  # que falta antes del capitulo 12 (el 12 no entra: se absorbe ya corregido)
  uv run estado_biblia.py --manuscrito m.json --huellas biblia/huellas.json --antes-de 12
  # que falta en toda la novela
  uv run estado_biblia.py --manuscrito m.json --huellas biblia/huellas.json
  # apuntar lo absorbido (las huellas las escribe solo este script)
  uv run estado_biblia.py --manuscrito m.json --huellas biblia/huellas.json --marcar 10 11

Veredicto, en la ultima linea y en --salida:
  AL DIA       nada pendiente
  ACTUALIZAR   pendiente por debajo del umbral: se absorbe y se avisa
  PREGUNTAR    pendiente por encima del umbral: se pregunta al autor antes

Solo escribe en --huellas, y solo con --marcar o --marcar-pendientes.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

# El filtro de documento es el mismo que el de leer_manuscrito.py: `12` es el
# documento 12 del binder, no el 112. Se importa para que no diverjan.
_LECTOR = Path(__file__).resolve().parents[2] / "pubia-revisa" / "scripts" / "leer_manuscrito.py"
_spec = importlib.util.spec_from_file_location("leer_manuscrito", _LECTOR)
_lector = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lector)
patron_filtro = _lector.patron_filtro

UMBRAL_PALABRAS = 30_000  # el mismo tramo con el que pubia biblia lee una novela larga


def clave(doc: dict) -> str:
    """Identidad del documento: su ruta dentro del borrador (dos escenas pueden
    llamarse igual en carpetas distintas)."""
    return doc.get("ruta") or doc["nombre"]


def casa(doc: dict, filtro: str) -> bool:
    patron = patron_filtro(filtro)
    if filtro.strip().isdigit():
        return bool(patron.search(Path(doc.get("fichero", doc["nombre"])).name))
    return bool(patron.search(doc.get("ruta") or doc["nombre"]))


def main() -> int:
    ap = argparse.ArgumentParser(description="Que le falta a la biblia.")
    ap.add_argument("--manuscrito", required=True, help="JSON de leer_manuscrito.py, manuscrito completo")
    ap.add_argument("--huellas", required=True, help="biblia/huellas.json")
    ap.add_argument("--antes-de", help="Filtro del capitulo que se va a revisar: solo cuenta lo anterior")
    ap.add_argument("--umbral-palabras", type=int, default=UMBRAL_PALABRAS,
                    help=f"Por encima, PREGUNTAR en vez de ACTUALIZAR (por defecto {UMBRAL_PALABRAS})")
    ap.add_argument("--marcar", nargs="+", metavar="FILTRO",
                    help="Apuntar como absorbidos, con su huella actual, los documentos que casan")
    ap.add_argument("--marcar-pendientes", action="store_true",
                    help="Apuntar como absorbidos todos los pendientes del alcance")
    ap.add_argument("--salida", help="JSON opcional con el estado")
    args = ap.parse_args()

    manuscrito = json.loads(Path(args.manuscrito).read_text(encoding="utf-8"))
    documentos = manuscrito["meta"]["documentos"]
    if documentos and "sha256" not in documentos[0]:
        print("ERROR: el manuscrito no lleva huella por documento; vuelve a extraerlo con "
              "leer_manuscrito.py actualizado.", file=sys.stderr)
        return 2

    ruta_huellas = Path(args.huellas).expanduser()
    huellas: dict = (json.loads(ruta_huellas.read_text(encoding="utf-8"))
                     if ruta_huellas.exists() else {"documentos": {}})
    absorbidos: dict = huellas.setdefault("documentos", {})

    # Alcance: todo, o lo que va antes del primer documento del capitulo.
    alcance = documentos
    if args.antes_de:
        indice = next((i for i, d in enumerate(documentos) if casa(d, args.antes_de)), None)
        if indice is None:
            print(f"ERROR: ningun documento casa con --antes-de {args.antes_de!r}", file=sys.stderr)
            return 2
        alcance = documentos[:indice]

    pendientes = []
    for d in alcance:
        previo = absorbidos.get(clave(d))
        if previo is None:
            pendientes.append({**d, "estado": "nuevo"})
        elif previo.get("sha256") != d["sha256"]:
            pendientes.append({**d, "estado": "cambiado", "absorbido": previo.get("fecha", "")})

    # Absorbidos que ya no estan en el manuscrito: la biblia guarda hechos de un
    # capitulo que se ha borrado o renombrado. No bloquea, pero hay que decirlo.
    presentes = {clave(d) for d in documentos}
    desaparecidos = sorted(n for n in absorbidos if n not in presentes)

    if args.marcar or args.marcar_pendientes:
        elegidos = ([d for d in documentos if any(casa(d, f) for f in args.marcar)]
                    if args.marcar else pendientes)
        if args.marcar and not elegidos:
            print(f"ERROR: ningun documento casa con --marcar {args.marcar}", file=sys.stderr)
            return 2
        hoy = date.today().isoformat()
        for d in elegidos:
            absorbidos[clave(d)] = {"sha256": d["sha256"], "fecha": hoy, "palabras": d["palabras"]}
        ruta_huellas.parent.mkdir(parents=True, exist_ok=True)
        ruta_huellas.write_text(json.dumps(huellas, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8")
        print(f"OK  {len(elegidos)} documento(s) apuntados como absorbidos en {ruta_huellas}")
        for d in elegidos:
            print(f"    {d['nombre']} ({d['palabras']} palabras)")
        return 0

    palabras = sum(d["palabras"] for d in pendientes)
    if not pendientes:
        veredicto = "AL DIA"
    elif palabras <= args.umbral_palabras:
        veredicto = "ACTUALIZAR"
    else:
        veredicto = "PREGUNTAR"

    ambito = f"antes de {args.antes_de!r}" if args.antes_de else "en toda la novela"
    print(f"Biblia {ambito}: {len(alcance) - len(pendientes)} de {len(alcance)} documentos al dia.")
    for d in pendientes:
        extra = f", absorbido el {d['absorbido']}" if d.get("absorbido") else ""
        print(f"    {d['estado']:<9} {d['nombre']} ({d['palabras']} palabras{extra})")
    for n in desaparecidos:
        print(f"    AVISO     {n}: absorbido pero ya no esta en el manuscrito")
    print(f"{veredicto}: {len(pendientes)} documento(s), {palabras} palabras pendientes "
          f"(umbral {args.umbral_palabras}).")

    if args.salida:
        Path(args.salida).write_text(json.dumps({
            "veredicto": veredicto,
            "palabras_pendientes": palabras,
            "pendientes": [{k: d[k] for k in ("nombre", "estado", "palabras")} for d in pendientes],
            "desaparecidos": desaparecidos,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
