#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.2.0"]
# ///
"""Genera el .docx de revision de un capitulo a partir de la fuente y las marcas.

Entradas:
  --fuente  JSON producido por leer_manuscrito.py (texto canonico del manuscrito)
  --marcas  JSON con las marcas de revision (ver references/formato-marcas.md)

Salida: un .docx donde
  - las correcciones van EN LINEA y en rojo: el original tachado y la propuesta
    en negrita a continuacion,
  - los comentarios (continuidad, trama, redaccion, ritmo...) van como
    COMENTARIOS REALES de Word en el margen, con la categoria en azul,
  - al final hay una tabla resumen con una columna "Decision" para que el autor
    marque que acepta y que rechaza.

El cuerpo del documento se construye SIEMPRE con el texto de --fuente, nunca con
texto reescrito: el .docx no puede alterar el manuscrito ni por accidente.

Por defecto es estricto: si una marca no ancla, no escribe nada y explica cual
falla, para que se corrija el JSON y se vuelva a ejecutar.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

ROJO = RGBColor(0xC0, 0x00, 0x00)
AZUL = RGBColor(0x1F, 0x4E, 0x79)
GRIS = RGBColor(0x59, 0x59, 0x59)

TIPOS_CORRECCION = {"correccion", "supresion"}
TIPOS = TIPOS_CORRECCION | {"comentario"}

# Rojo: solo lo objetivo. 'lexico' NO esta aqui a proposito: cambiar una palabra
# por otra mejor es una preferencia, y las preferencias van en azul.
CAT_CORRECCION = {
    "ortografia", "tilde", "puntuacion", "tipografia", "gramatica",
    "concordancia", "verbo", "preposicion", "dialogo", "numero",
    "tratamiento",   # fuga de vosotros donde la variedad pide ustedes
    "nombre",        # grafia de un nombre, rango o referente ya establecido
    "omision",       # palabra omitida o duplicada por accidente
    "paronimo",      # confusion objetiva de palabras (infligir/infringir)
}
CAT_COMENTARIO = {
    "continuidad", "cronologia", "personaje", "trama", "historia",
    "verosimilitud", "repeticion", "redaccion", "ritmo", "voz",
    "punto-de-vista", "claridad", "duda", "ambiguedad", "lexico",
    "logica", "incertidumbre",
}


class ErrorDeMarcas(Exception):
    pass


# ---------------------------------------------------------------- utilidades

def localizar(texto: str, buscar: str, ocurrencia: int) -> tuple[int, int]:
    """Devuelve (inicio, fin) de la ocurrencia n-esima de `buscar` en `texto`."""
    if not buscar:
        raise ErrorDeMarcas("'buscar' vacio")
    pos = -1
    for _ in range(ocurrencia):
        pos = texto.find(buscar, pos + 1)
        if pos == -1:
            total = texto.count(buscar)
            raise ErrorDeMarcas(
                f"no se encuentra la ocurrencia {ocurrencia} de {buscar!r} "
                f"(aparece {total} vez/veces en el parrafo)"
            )
    return pos, pos + len(buscar)


def etiqueta(categoria: str) -> str:
    return categoria.replace("-", " ").upper()


# ------------------------------------------------------------ preparar marcas

def preparar(fuente: dict, marcas_json: dict, avisos: list[str]) -> dict[int, list[dict]]:
    """Valida las marcas y las agrupa por parrafo, resueltas a offsets."""
    por_id = {p["id"]: p for p in fuente["parrafos"]}
    errores: list[str] = []
    marcas: list[dict] = []

    for i, bruta in enumerate(marcas_json.get("marcas", []), start=1):
        ref = f"marcas[{i}]"
        tipo = str(bruta.get("tipo", "")).strip().lower()
        if tipo not in TIPOS:
            errores.append(f"{ref}: tipo invalido {tipo!r} (usa: {', '.join(sorted(TIPOS))})")
            continue
        pid = bruta.get("parrafo")
        if pid not in por_id:
            errores.append(f"{ref}: el parrafo {pid!r} no existe en la fuente "
                           f"(rango valido 1-{fuente['meta']['total_parrafos']})")
            continue
        parrafo = por_id[pid]
        categoria = str(bruta.get("categoria", "")).strip().lower()
        if not categoria:
            errores.append(f"{ref}: falta 'categoria'")
            continue
        if tipo == "correccion" and categoria in ("lexico", "estilo", "redaccion", "ritmo", "voz"):
            errores.append(
                f"{ref}: una correccion en rojo no puede ser de categoria '{categoria}'. "
                f"Cambiar una palabra por otra mejor es una preferencia: va como comentario "
                f"(tipo 'comentario') o no va. Ver criterios-correccion.md, principio rector."
            )
            continue
        conocidas = (CAT_CORRECCION if tipo == "correccion"
                     else CAT_CORRECCION | CAT_COMENTARIO if tipo == "supresion"
                     else CAT_COMENTARIO)
        if categoria not in conocidas:
            avisos.append(f"{ref}: categoria '{categoria}' no es de las habituales para '{tipo}'")

        buscar = bruta.get("buscar")
        try:
            if buscar:
                inicio, fin = localizar(parrafo["texto"], buscar, int(bruta.get("ocurrencia", 1)))
            elif tipo == "comentario":
                inicio, fin = 0, len(parrafo["texto"])  # comentario a todo el parrafo
            else:
                raise ErrorDeMarcas("una correccion o supresion necesita 'buscar'")
        except ErrorDeMarcas as exc:
            errores.append(f"{ref} (parrafo {pid}): {exc}")
            continue

        if tipo == "correccion" and not str(bruta.get("propuesta", "")).strip():
            errores.append(f"{ref}: una correccion necesita 'propuesta' "
                           f"(para borrar sin sustituir usa tipo 'supresion')")
            continue
        if tipo == "comentario" and not str(bruta.get("texto", "")).strip():
            errores.append(f"{ref}: un comentario necesita 'texto'")
            continue

        marcas.append({
            "ref": ref,
            "tipo": tipo,
            "parrafo": pid,
            "categoria": categoria,
            "inicio": inicio,
            "fin": fin,
            "buscar": buscar or parrafo["texto"],
            "propuesta": bruta.get("propuesta", ""),
            "nota": bruta.get("nota", ""),
            "texto": bruta.get("texto", ""),
        })

    if errores:
        raise ErrorDeMarcas("\n".join(errores))

    marcas.sort(key=lambda m: (m["parrafo"], m["inicio"], 0 if m["tipo"] in TIPOS_CORRECCION else 1))
    for n, m in enumerate(marcas, start=1):
        m["n"] = n

    agrupadas: dict[int, list[dict]] = {}
    for m in marcas:
        agrupadas.setdefault(m["parrafo"], []).append(m)

    # Las correcciones de un mismo parrafo no pueden solaparse entre si.
    choques = []
    for pid, grupo in agrupadas.items():
        correcciones = [m for m in grupo if m["tipo"] in TIPOS_CORRECCION]
        for a, b in zip(correcciones, correcciones[1:]):
            if b["inicio"] < a["fin"]:
                choques.append(
                    f"parrafo {pid}: la marca #{a['n']} ({a['buscar']!r}) y la #{b['n']} "
                    f"({b['buscar']!r}) se solapan; separa los anclajes"
                )
    if choques:
        raise ErrorDeMarcas("\n".join(choques))

    return agrupadas


# ------------------------------------------------------------------ render

def estilo_base(doc: Document, tipografia: str = "Times New Roman", cuerpo: float = 11) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = tipografia
    normal.font.size = Pt(cuerpo)
    normal.paragraph_format.space_after = Pt(10)
    normal.paragraph_format.line_spacing = 1.4
    for seccion in doc.sections:
        seccion.top_margin = Cm(2.5)
        seccion.bottom_margin = Cm(2.5)
        seccion.left_margin = Cm(2.5)
        seccion.right_margin = Cm(4.0)  # aire para los comentarios del margen


def nota_inline(doc: Document, marca: dict, cuerpo: str, cita: str) -> None:
    """Comentario en el cuerpo del documento, citando la frase exacta.

    Formato heredado de la revision conservadora: azul, cursiva, mas pequeno y
    visualmente separado del texto del autor.
    """
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Cm(1.0)
    par.paragraph_format.space_before = Pt(2)
    par.paragraph_format.first_line_indent = Cm(0)
    cab = par.add_run(f"COMENTARIO #{marca['n']} {etiqueta(marca['categoria'])}")
    cab.bold = True
    cab.italic = True
    cab.font.size = Pt(9)
    cab.font.color.rgb = AZUL
    resto = par.add_run(f" — sobre «{recorta(cita, 110)}»: {cuerpo}")
    resto.italic = True
    resto.font.size = Pt(9)
    resto.font.color.rgb = AZUL


def parrafo_marcado(doc: Document, parrafo: dict, grupo: list[dict], autor: str,
                    iniciales: str, avisos: list[str], modo: str = "margen") -> None:
    texto = parrafo["texto"]
    tipo_p = parrafo["tipo"]

    p = doc.add_paragraph()
    if tipo_p == "titulo":
        p.paragraph_format.space_before = Pt(18)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        texto = texto.lstrip("# ").strip()
    elif tipo_p == "separador":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(0.8)

    correcciones = [m for m in grupo if m["tipo"] in TIPOS_CORRECCION]
    comentarios = [m for m in grupo if m["tipo"] == "comentario"]

    # Los comentarios no pueden partir una correccion: se ensancha su anclaje.
    for c in comentarios:
        for corr in correcciones:
            if corr["inicio"] < c["inicio"] < corr["fin"]:
                avisos.append(f"#{c['n']}: anclaje ampliado para no partir la correccion #{corr['n']}")
                c["inicio"] = corr["inicio"]
            if corr["inicio"] < c["fin"] < corr["fin"]:
                avisos.append(f"#{c['n']}: anclaje ampliado para no partir la correccion #{corr['n']}")
                c["fin"] = corr["fin"]

    cortes = {0, len(texto)}
    for m in grupo:
        cortes.add(m["inicio"])
        cortes.add(m["fin"])
    cortes = sorted(c for c in cortes if 0 <= c <= len(texto))

    por_corregir = {(m["inicio"], m["fin"]): m for m in correcciones}
    tramos: list[tuple[int, int, list]] = []  # (inicio, fin, runs)
    pendientes: list[tuple[dict, str, str]] = []  # (marca, cuerpo, cita) para modo inline

    for ini, fin in zip(cortes, cortes[1:]):
        if ini == fin:
            continue
        marca = por_corregir.get((ini, fin))
        if marca is None:
            run = p.add_run(texto[ini:fin])
            if tipo_p == "titulo":
                run.bold = True
                run.font.size = Pt(14)
            elif tipo_p == "separador":
                run.font.color.rgb = GRIS
            tramos.append((ini, fin, [run]))
            continue

        viejo = p.add_run(texto[ini:fin])
        viejo.font.strike = True
        viejo.font.color.rgb = ROJO
        runs = [viejo]
        if marca["tipo"] == "correccion":
            nuevo = p.add_run(" " + marca["propuesta"])
            nuevo.bold = True
            nuevo.font.color.rgb = ROJO
            runs.append(nuevo)
        tramos.append((ini, fin, runs))

        if marca["nota"]:
            cuerpo = f"{marca['nota']}"
            if marca["tipo"] == "correccion":
                cuerpo += f"  [propuesta: {marca['propuesta']}]"
            if modo in ("margen", "ambos"):
                comentar(doc, runs, marca, cuerpo, autor, iniciales)
            pendientes.append((marca, cuerpo, texto[ini:fin]))

    for c in comentarios:
        dentro = [t for t in tramos if t[0] >= c["inicio"] and t[1] <= c["fin"]]
        if not dentro:
            dentro = tramos or [(0, 0, [p.add_run("")])]
        runs = dentro[0][2] + dentro[-1][2]
        if modo in ("margen", "ambos"):
            comentar(doc, runs, c, c["texto"], autor, iniciales)
        pendientes.append((c, c["texto"], texto[c["inicio"]:c["fin"]]))

    if modo in ("inline", "ambos"):
        for marca, cuerpo, cita in sorted(pendientes, key=lambda x: x[0]["n"]):
            nota_inline(doc, marca, cuerpo, cita)


def comentar(doc: Document, runs: list, marca: dict, cuerpo: str, autor: str, iniciales: str) -> None:
    comentario = doc.add_comment([runs[0], runs[-1]], text="", author=autor, initials=iniciales)
    par = comentario.paragraphs[0] if comentario.paragraphs else comentario.add_paragraph()
    cab = par.add_run(f"#{marca['n']} {etiqueta(marca['categoria'])}")
    cab.bold = True
    cab.font.color.rgb = AZUL
    resto = par.add_run(f" — {cuerpo}")
    resto.font.color.rgb = AZUL


def portada(doc: Document, fuente: dict, marcas_json: dict, agrupadas: dict, autor: str) -> None:
    meta_f = fuente["meta"]
    meta_m = marcas_json.get("meta", {})
    todas = [m for g in agrupadas.values() for m in g]

    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("Revisión PUBIA")
    r.bold = True
    r.font.size = Pt(20)

    st = doc.add_paragraph()
    st.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs = st.add_run(" · ".join(x for x in [
        meta_m.get("novela", ""),
        meta_m.get("capitulo") or meta_f.get("titulo", ""),
        meta_m.get("revision", "v1"),
        meta_m.get("fecha") or date.today().isoformat(),
    ] if x))
    rs.font.size = Pt(11)
    rs.font.color.rgb = GRIS

    tabla = doc.add_table(rows=0, cols=2)
    tabla.style = "Table Grid"
    correcciones = [m for m in todas if m["tipo"] in TIPOS_CORRECCION]
    comentarios = [m for m in todas if m["tipo"] == "comentario"]
    palabras = meta_f.get("total_palabras", 0) or 1
    filas = [
        ("Palabras revisadas", f"{meta_f.get('total_palabras', 0)} en {meta_f.get('total_parrafos', 0)} párrafos"),
        ("Correcciones en rojo", str(len(correcciones))),
        ("Comentarios al margen", str(len(comentarios))),
        ("Densidad", f"{len(todas) * 1000 / palabras:.1f} marcas por 1000 palabras"),
        ("Fuente", ", ".join(d["nombre"] for d in meta_f.get("documentos", []))),
        ("Huella del texto revisado", meta_f.get("sha256", "")[:16]),
    ]
    for cat, grupo in sorted(agrupar_por_categoria(todas).items()):
        filas.append((f"  · {etiqueta(cat).lower()}", str(len(grupo))))
    for clave, valor in filas:
        fila = tabla.add_row().cells
        fila[0].text = clave
        fila[1].text = valor
        for par in fila[0].paragraphs:
            for run in par.runs:
                run.font.size = Pt(9)
        for par in fila[1].paragraphs:
            for run in par.runs:
                run.font.size = Pt(9)

    doc.add_paragraph()
    ley = doc.add_paragraph()
    for texto, color, negrita in [
        ("Cómo leer este documento. ", None, True),
        ("En rojo", ROJO, True),
        (", correcciones directas: solo lo objetivo (ortografía, concordancia, puntuación normativa, "
         "tratamiento, grafía de un nombre ya establecido). El original queda tachado y la propuesta va "
         "en rojo y negrita. ", None, False),
        ("En azul", AZUL, True),
        (", observaciones contrastadas que merecen que te detengas: continuidad, verosimilitud histórica "
         "comprobada, ambigüedad real, lógica narrativa, caracterización. Nada de preferencias de estilo. "
         "Cada marca lleva un número que coincide con la tabla final.", None, False),
    ]:
        run = ley.add_run(texto)
        run.bold = negrita
        run.font.size = Pt(9.5)
        if color is not None:
            run.font.color.rgb = color

    av = doc.add_paragraph()
    rav = av.add_run(
        f"Este documento no sustituye al manuscrito: es una propuesta de {autor}. "
        "Nada se ha aplicado en Scrivener; las correcciones las decides y las haces tú."
    )
    rav.italic = True
    rav.font.size = Pt(9.5)
    rav.font.color.rgb = GRIS

    if meta_m.get("notas"):
        nota = doc.add_paragraph()
        rn = nota.add_run(str(meta_m["notas"]))
        rn.font.size = Pt(9.5)
        rn.font.color.rgb = GRIS


def agrupar_por_categoria(marcas: list[dict]) -> dict[str, list[dict]]:
    salida: dict[str, list[dict]] = {}
    for m in marcas:
        salida.setdefault(m["categoria"], []).append(m)
    return salida


def recorta(texto: str, limite: int = 90) -> str:
    texto = " ".join(texto.split())
    return texto if len(texto) <= limite else texto[: limite - 1] + "…"


def tabla_resumen(doc: Document, agrupadas: dict) -> None:
    todas = sorted((m for g in agrupadas.values() for m in g), key=lambda m: m["n"])
    if not todas:
        return
    doc.add_page_break()
    cab = doc.add_paragraph()
    rc = cab.add_run("Resumen de marcas")
    rc.bold = True
    rc.font.size = Pt(15)
    sub = doc.add_paragraph()
    rsub = sub.add_run("Anota tu decisión en la última columna. `pubia decisiones` recoge lo que rechaces "
                       "para no volver a marcarlo en las siguientes pasadas.")
    rsub.font.size = Pt(9)
    rsub.font.color.rgb = GRIS

    tabla = doc.add_table(rows=1, cols=6)
    tabla.style = "Table Grid"
    for celda, titulo in zip(tabla.rows[0].cells, ["#", "Párr.", "Categoría", "Texto afectado", "Propuesta o comentario", "Decisión"]):
        celda.text = titulo
        for par in celda.paragraphs:
            for run in par.runs:
                run.bold = True
                run.font.size = Pt(9)

    for m in todas:
        celdas = tabla.add_row().cells
        if m["tipo"] == "correccion":
            derecha = f"→ {m['propuesta']}" + (f"  ({m['nota']})" if m["nota"] else "")
        elif m["tipo"] == "supresion":
            derecha = "suprimir" + (f"  ({m['nota']})" if m["nota"] else "")
        else:
            derecha = m["texto"]
        valores = [str(m["n"]), str(m["parrafo"]), etiqueta(m["categoria"]).lower(),
                   recorta(m["buscar"], 70), recorta(derecha, 140), ""]
        for celda, valor in zip(celdas, valores):
            celda.text = valor
            for par in celda.paragraphs:
                for run in par.runs:
                    run.font.size = Pt(8.5)
                    if celda is celdas[2] and m["tipo"] == "comentario":
                        run.font.color.rgb = AZUL
                    elif celda is celdas[2]:
                        run.font.color.rgb = ROJO


def seccion_impresion(doc: Document, texto: str) -> None:
    """Seccion final, independiente de la correccion: la lectura como lector.

    No lleva marcas ni propuestas. Es la opinion franca sobre el capitulo.
    """
    doc.add_page_break()
    cab = doc.add_paragraph()
    rc = cab.add_run("Impresión como lector")
    rc.bold = True
    rc.font.size = Pt(15)
    aviso = doc.add_paragraph()
    ra = aviso.add_run("Esta sección no forma parte de la corrección.")
    ra.italic = True
    ra.font.size = Pt(9)
    ra.font.color.rgb = GRIS

    for bloque in [b.strip() for b in texto.split("\n\n") if b.strip()]:
        lineas = [l.strip() for l in bloque.splitlines() if l.strip()]
        # Una lista es un bloque de varias lineas, cada una su propia vineta;
        # un parrafo normal se une en una sola linea.
        if any(l.startswith(("- ", "* ")) for l in lineas):
            unidades = lineas
        else:
            unidades = [" ".join(" ".join(lineas).split())]
        for unidad in unidades:
            par = doc.add_paragraph()
            if unidad.startswith("#"):
                run = par.add_run(unidad.lstrip("# ").strip())
                run.bold = True
                par.paragraph_format.space_before = Pt(10)
            elif unidad.startswith(("- ", "* ")):
                par.style = doc.styles["List Bullet"]
                par.add_run(unidad[2:].strip())
            else:
                par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                par.add_run(unidad)


def resumen_markdown(fuente: dict, marcas_json: dict, agrupadas: dict, docx: Path) -> str:
    meta_m = marcas_json.get("meta", {})
    todas = sorted((m for g in agrupadas.values() for m in g), key=lambda m: m["n"])
    lineas = [
        f"# Revisión — {meta_m.get('capitulo') or fuente['meta'].get('titulo', '')}",
        "",
        f"- Documento: `{docx}`",
        f"- Revisión: {meta_m.get('revision', 'v1')} · {meta_m.get('fecha') or date.today().isoformat()}",
        f"- Texto: {fuente['meta'].get('total_palabras', 0)} palabras, huella `{fuente['meta'].get('sha256', '')[:16]}`",
        f"- Marcas: {len(todas)}",
        "",
        "| # | Párr. | Tipo | Categoría | Texto afectado | Propuesta o comentario | Decisión |",
        "|---|-------|------|-----------|----------------|------------------------|----------|",
    ]
    for m in todas:
        derecha = (f"→ {m['propuesta']}" if m["tipo"] == "correccion"
                   else "suprimir" if m["tipo"] == "supresion" else m["texto"])
        if m["nota"] and m["tipo"] != "comentario":
            derecha += f" ({m['nota']})"
        celda = lambda t: recorta(t, 120).replace("|", "\\|")
        lineas.append(
            f"| {m['n']} | {m['parrafo']} | {m['tipo']} | {m['categoria']} | "
            f"{celda(m['buscar'])} | {celda(derecha)} |  |"
        )
    lineas.append("")
    return "\n".join(lineas)


# -------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="Genera el .docx de revision anotada.")
    ap.add_argument("--fuente", required=True, help="JSON de leer_manuscrito.py")
    ap.add_argument("--marcas", required=True, help="JSON de marcas de revision")
    ap.add_argument("--salida", required=True, help="Ruta del .docx a generar")
    ap.add_argument("--resumen", help="Ruta opcional de un resumen .md de las marcas")
    ap.add_argument("--autor", default=None, help="Autor de los comentarios (por defecto 'pubia')")
    ap.add_argument("--comentarios", choices=["margen", "inline", "ambos"], default="margen",
                    help="margen: comentarios reales de Word (por defecto); inline: en el cuerpo, "
                         "en azul y cursiva citando la frase; ambos: las dos cosas")
    ap.add_argument("--impresion", help="Fichero de texto con la seccion final 'Impresion como lector'")
    ap.add_argument("--tipografia", default="Times New Roman", help="Fuente del cuerpo")
    ap.add_argument("--cuerpo", type=float, default=11, help="Tamano del cuerpo en puntos")
    ap.add_argument("--tolerante", action="store_true",
                    help="No abortar si una marca no ancla: la omite y la reporta")
    args = ap.parse_args()

    fuente = json.loads(Path(args.fuente).read_text(encoding="utf-8"))
    marcas_json = json.loads(Path(args.marcas).read_text(encoding="utf-8"))
    autor = args.autor or marcas_json.get("meta", {}).get("revisor") or "pubia"
    iniciales = "".join(w[0] for w in autor.split()[:2]).upper() or "PB"

    avisos: list[str] = []
    try:
        agrupadas = preparar(fuente, marcas_json, avisos)
    except ErrorDeMarcas as exc:
        print("MARCAS INVÁLIDAS — no se ha generado nada:\n" + str(exc), file=sys.stderr)
        if not args.tolerante:
            print("\nCorrige el JSON de marcas y vuelve a ejecutar "
                  "(o usa --tolerante para omitir las marcas que fallan).", file=sys.stderr)
            return 1
        marcas_json = {**marcas_json, "marcas": []}
        agrupadas = preparar(fuente, marcas_json, avisos)

    doc = Document()
    estilo_base(doc, args.tipografia, args.cuerpo)
    portada(doc, fuente, marcas_json, agrupadas, autor)

    doc.add_page_break()

    documento_actual = None
    for parrafo in fuente["parrafos"]:
        if parrafo["documento"] != documento_actual and documento_actual is not None:
            doc.add_page_break()
        documento_actual = parrafo["documento"]
        parrafo_marcado(doc, parrafo, agrupadas.get(parrafo["id"], []), autor, iniciales, avisos,
                        args.comentarios)

    tabla_resumen(doc, agrupadas)

    if args.impresion:
        ruta_imp = Path(args.impresion).expanduser()
        if not ruta_imp.exists():
            print(f"ERROR: no existe el fichero de impresion: {ruta_imp}", file=sys.stderr)
            return 2
        seccion_impresion(doc, ruta_imp.read_text(encoding="utf-8"))

    salida = Path(args.salida).expanduser()
    salida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(salida))

    # Sidecar con las marcas ya ancladas y numeradas. Es el contrato con
    # pubia-decisiones: la numeracion #n depende de la posicion en el texto y
    # solo se conoce aqui, asi que se publica en lugar de recalcularse.
    resueltas = sorted((m for g in agrupadas.values() for m in g), key=lambda m: m["n"])
    sidecar = salida.with_suffix(".resueltas.json")
    sidecar.write_text(json.dumps({
        "meta": {**marcas_json.get("meta", {}),
                 "docx": str(salida),
                 "fuente": args.fuente,
                 "sha256_fuente": fuente["meta"].get("sha256", "")},
        "marcas": [{k: m[k] for k in ("n", "parrafo", "tipo", "categoria", "inicio", "fin",
                                      "buscar", "propuesta", "nota", "texto")} for m in resueltas],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = sum(len(g) for g in agrupadas.values())
    print(f"OK  {salida}")
    print(f"    marcas aplicadas: {total}  (comentarios reales de Word + correcciones en rojo)")
    print(f"    marcas resueltas: {sidecar}")
    print(f"    comentarios: {args.comentarios}"
          + ("  ·  con impresión como lector" if args.impresion else ""))
    if args.resumen:
        ruta = Path(args.resumen).expanduser()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(resumen_markdown(fuente, marcas_json, agrupadas, salida), encoding="utf-8")
        print(f"    resumen: {ruta}")
    for aviso in avisos:
        print(f"    AVISO {aviso}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
