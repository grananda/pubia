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

Uso normal, desde la carpeta de la novela:
  uv run leer_manuscrito.py --config pubia.json --filtro 12 --salida fuente.json

La carpeta de sincronizacion de Scrivener la da el autor una vez, en `pubia
setup`, y queda en `scrivener_sync` de pubia.json: es la fuente estandar y no se
vuelve a pedir. Dentro, el texto esta en `Draft/`, que es la estructura que crea
"Sincronizar con carpeta externa"; si falta, la sincronizacion no se ha hecho o no
incluye el borrador, y el script se para en vez de leer otra cosa.

--fuente sirve para casos sueltos (un fichero, otra carpeta) y manda sobre
pubia.json. Formatos: .rtf (Scrivener), .txt, .md, ordenados por el prefijo
numerico que Scrivener anade.

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


def patron_filtro(filtro: str) -> re.Pattern:
    """Compila el filtro de documento.

    - Solo cifras (`7`, `07`): el documento cuyo prefijo numerico del binder es
      ese numero. `7` no casa con `17` ni con `70`.
    - Cualquier otro texto: subcadena sin distinguir mayusculas, pero un numero
      en los bordes no se prolonga: `cap 1` no casa con `cap 12`.
    """
    filtro = filtro.strip()
    if filtro.isdigit():
        return re.compile(rf"^\s*0*{int(filtro)}(?!\d)")
    patron = re.escape(filtro)
    if filtro[:1].isdigit():
        patron = r"(?<!\d)" + patron
    if filtro[-1:].isdigit():
        patron += r"(?!\d)"
    return re.compile(patron, re.IGNORECASE)


def recoger_ficheros(fuente: Path, filtro: str | None, borrador: str = "Draft") -> list[Path]:
    if fuente.is_file():
        ficheros = [fuente]
        raiz = fuente.parent
    else:
        raiz = fuente / borrador if (fuente / borrador).is_dir() else fuente
        ficheros = [
            p
            for p in raiz.rglob("*")
            if p.is_file()
            and p.suffix.lower() in EXTENSIONES
            and not p.name.startswith(".")
            # Relativo a la raiz: una ruta de usuario como ~/Notes/Novela-sync
            # no debe dejar fuera todo el manuscrito.
            and "Trash" not in p.relative_to(raiz).parts
            and "Notes" not in p.relative_to(raiz).parts
        ]
        ficheros.sort(key=orden_natural)
    if filtro:
        patron = patron_filtro(filtro)
        if filtro.strip().isdigit():
            ficheros = [p for p in ficheros if patron.search(p.name)]
        else:
            # Se busca en la ruta relativa a la raiz, no en la absoluta: si no,
            # `--filtro sync` casaria con todo.
            ficheros = [p for p in ficheros if patron.search(str(p.relative_to(raiz)))]
    return ficheros


def cargar_config(ruta: str | None) -> dict:
    if not ruta:
        return {}
    p = Path(ruta).expanduser()
    if not p.exists():
        print(f"AVISO: no existe {p}; se usan los valores por defecto", file=sys.stderr)
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


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
    ap.add_argument("--fuente", help="Fichero .rtf/.txt/.md o carpeta; por defecto, scrivener_sync de --config")
    ap.add_argument("--salida", required=True, help="Ruta del JSON de fuente a generar")
    ap.add_argument("--filtro",
                    help="Documento a extraer: un numero (`7`) casa con el prefijo del binder; "
                         "un texto casa como subcadena sin prolongar numeros (`cap 1` no es `cap 12`)")
    ap.add_argument("--config", help="pubia.json de la novela: aporta scrivener_sync (la fuente estandar) "
                                     "y modo_parrafos")
    ap.add_argument("--borrador", help=argparse.SUPPRESS)  # Draft es el estandar de Scrivener
    ap.add_argument("--parrafos", choices=["lineas", "bloques"],
                    help="lineas (por defecto, Scrivener) o bloques separados por linea en blanco")
    ap.add_argument("--titulo", help="Titulo para la revision (por defecto, el nombre del fichero)")
    args = ap.parse_args()

    # La linea de comandos manda sobre pubia.json, y pubia.json sobre los defectos.
    config = cargar_config(args.config)
    args.borrador = args.borrador or config.get("subcarpeta_borrador") or "Draft"
    args.parrafos = args.parrafos or config.get("modo_parrafos") or "lineas"
    if args.parrafos not in ("lineas", "bloques"):
        print(f"ERROR: modo_parrafos invalido en {args.config}: {args.parrafos!r}", file=sys.stderr)
        return 2

    desde_config = not args.fuente
    if desde_config:
        if not config.get("scrivener_sync"):
            print("ERROR: falta la carpeta de sincronizacion de Scrivener. Pasa --config pubia.json "
                  "con 'scrivener_sync' (lo escribe `pubia setup`) o --fuente.", file=sys.stderr)
            return 2
        args.fuente = config["scrivener_sync"]

    fuente = Path(args.fuente).expanduser()
    if not fuente.exists():
        print(f"ERROR: no existe la fuente: {fuente}", file=sys.stderr)
        return 2
    # La carpeta estandar tiene que tener la estructura estandar: sin Draft/ no
    # se adivina, porque leer la raiz mezclaria Notes/ y lo que haya suelto.
    # Si scrivener_sync apunta ya a la propia Draft/, se acepta tal cual.
    if desde_config and fuente.name != args.borrador and not (fuente / args.borrador).is_dir():
        print(f"ERROR: {fuente} no tiene la subcarpeta {args.borrador}/ que crea Scrivener al "
              f"sincronizar. Sincroniza desde Scrivener (Archivo > Sincronizar > Con carpeta externa, "
              f"con 'Sincronizar el contenido del borrador') o corrige scrivener_sync en pubia.json.",
              file=sys.stderr)
        return 2

    ficheros = recoger_ficheros(fuente, args.filtro, args.borrador)
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
