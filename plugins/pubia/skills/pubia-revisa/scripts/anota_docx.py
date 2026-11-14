#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.2.0"]
# ///
"""Genera el .docx de revision de un capitulo a partir de la fuente y las marcas.

Entradas:
  --fuente  JSON producido por leer_manuscrito.py (texto canonico del manuscrito)
  --marcas  JSON con las marcas de revision (ver references/formato-marcas.md)

Salida: un .docx con tres niveles, de mas a menos imperativo:
  - ROJO, en linea: el error objetivo y crucial (ortografia, gramatica,
    concordancia, raya de dialogo...). El original tachado y la propuesta en
    negrita a continuacion.
  - AZUL, comentario real de Word al margen: lo que exige detenerse
    (continuidad, historia comprobada, ambiguedad, logica narrativa...).
  - VIOLETA, sugerencia opcional: lo que puede o no cambiarse (cacofonia,
    repeticion cercana, redaccion, ritmo). El fragmento en violeta con subrayado
    punteado, la propuesta (si la hay) entre corchetes, y el motivo al margen.
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
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_UNDERLINE
from docx.shared import Cm, Pt, RGBColor

ROJO = RGBColor(0xC0, 0x00, 0x00)
AZUL = RGBColor(0x1F, 0x4E, 0x79)
VIOLETA = RGBColor(0x70, 0x30, 0xA0)  # distinguible del rojo tambien impreso y con daltonismo
GRIS = RGBColor(0x59, 0x59, 0x59)

TIPOS_CORRECCION = {"correccion", "supresion"}
TIPOS = TIPOS_CORRECCION | {"comentario", "sugerencia"}

# Rojo: solo lo objetivo y crucial. 'lexico' NO esta aqui: cambiar una palabra
# por otra mejor es una preferencia, y las preferencias van en violeta.
CAT_CORRECCION = {
    "ortografia", "tilde", "puntuacion", "tipografia", "gramatica",
    "concordancia", "verbo", "preposicion", "dialogo", "numero",
    "tratamiento",   # fuga de vosotros donde la variedad pide ustedes
    "nombre",        # grafia de un nombre, rango o referente ya establecido
    "omision",       # palabra omitida o duplicada por accidente
    "paronimo",      # confusion objetiva de palabras (infligir/infringir)
}
# Azul: lo que exige que el autor se detenga. Umbral alto.
CAT_COMENTARIO = {
    "continuidad", "cronologia", "personaje", "trama", "historia",
    "verosimilitud", "voz", "punto-de-vista", "claridad", "duda",
    "ambiguedad", "logica", "incertidumbre",
}
# Violeta: opcional. Lo que el autor puede o no querer tocar, incluida la
# palabra que sonaria mejor. Nunca contra la voz, la oralidad o el lexico de la
# novela: eso no se marca en ningun color.
CAT_SUGERENCIA = {
    "cacofonia",   # sonidos que tropiezan, rimas y ecos involuntarios
    "repeticion",  # la misma palabra muy cerca, sin funcion retorica
    "redaccion",   # frase torpe, que obliga a releer
    "ritmo",       # frase o tramo que se arrastra o se atropella
    "lexico",      # una palabra mas precisa o que suena mejor: opcion, no correccion
}
COLOR = {"correccion": ROJO, "supresion": ROJO, "comentario": AZUL, "sugerencia": VIOLETA}


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

def preparar(fuente: dict, marcas_json: dict, avisos: list[str],
             tolerante: bool = False) -> dict[int, list[dict]]:
    """Valida las marcas y las agrupa por parrafo, resueltas a offsets.

    Estricto por defecto: cualquier marca invalida aborta. Con `tolerante`, las
    marcas invalidas (y la segunda de cada par que se solapa) se omiten y se
    reportan en `avisos`; las validas se pintan igual.
    """
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
        # Guardarrail del rojo: lista PERMITIDA, no prohibida. Todo lo que va en
        # rojo (correccion o supresion) tiene que ser de una categoria objetiva;
        # una categoria inventada o de criterio no entra, ni como aviso.
        if tipo in TIPOS_CORRECCION and categoria not in CAT_CORRECCION:
            if categoria in CAT_SUGERENCIA or categoria == "estilo":
                destino = "es una preferencia: va como sugerencia opcional (tipo 'sugerencia', violeta)"
            elif categoria in CAT_COMENTARIO:
                destino = "exige criterio: va como comentario (tipo 'comentario', azul)"
            else:
                destino = "no es una categoria objetiva conocida"
            errores.append(
                f"{ref}: una {tipo} en rojo no puede ser de categoria '{categoria}': {destino}. "
                f"Categorias de rojo: {', '.join(sorted(CAT_CORRECCION))}. "
                f"Ver criterios-correccion.md, principio rector."
            )
            continue
        if tipo == "sugerencia" and categoria not in CAT_SUGERENCIA:
            errores.append(
                f"{ref}: una sugerencia no puede ser de categoria '{categoria}'. Categorias de "
                f"sugerencia: {', '.join(sorted(CAT_SUGERENCIA))}. "
                + ("Lo objetivo va en rojo (correccion); lo que exige detenerse, en azul (comentario)."
                   if categoria in CAT_CORRECCION | CAT_COMENTARIO else
                   "Si es cambiar una palabra por otra mejor, la categoria es 'lexico'.")
            )
            continue
        if tipo == "comentario" and categoria in CAT_SUGERENCIA:
            errores.append(
                f"{ref}: '{categoria}' es opcional para el autor: va como 'sugerencia' (violeta), "
                f"no como comentario en azul, que es para lo que exige detenerse."
            )
            continue
        if tipo == "comentario" and categoria not in CAT_COMENTARIO:
            avisos.append(f"{ref}: categoria '{categoria}' no es de las habituales para un comentario")

        buscar = bruta.get("buscar")
        try:
            if buscar:
                inicio, fin = localizar(parrafo["texto"], buscar, int(bruta.get("ocurrencia", 1)))
            elif tipo in ("comentario", "sugerencia"):
                inicio, fin = 0, len(parrafo["texto"])  # nota a todo el parrafo
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
        if tipo == "sugerencia" and not str(bruta.get("nota", "")).strip():
            errores.append(f"{ref}: una sugerencia necesita 'nota': el motivo es lo que le "
                           f"permite al autor decidir si la quiere")
            continue

        marcas.append({
            "ref": ref,
            "tipo": tipo,
            "parrafo": pid,
            "categoria": categoria,
            "inicio": inicio,
            "fin": fin,
            "anclada": bool(buscar),
            "buscar": buscar or parrafo["texto"],
            "propuesta": bruta.get("propuesta", ""),
            "nota": bruta.get("nota", ""),
            "texto": bruta.get("texto", ""),
        })

    if errores and not tolerante:
        raise ErrorDeMarcas("\n".join(errores))
    avisos.extend(f"OMITIDA {e}" for e in errores)

    marcas.sort(key=lambda m: (m["parrafo"], m["inicio"], 0 if m["tipo"] in TIPOS_CORRECCION else 1))

    # Las correcciones de un mismo parrafo no pueden solaparse entre si. Se
    # comprueba antes de numerar, para que la numeracion #n que ve el autor no
    # tenga huecos cuando el modo tolerante descarta alguna.
    choques: list[str] = []
    descartadas: set[int] = set()
    ultima: dict[int, dict] = {}
    for m in marcas:
        if m["tipo"] not in TIPOS_CORRECCION:
            continue
        a = ultima.get(m["parrafo"])
        if a is not None and m["inicio"] < a["fin"]:
            choques.append(
                f"parrafo {m['parrafo']}: {a['ref']} ({a['buscar']!r}) y {m['ref']} "
                f"({m['buscar']!r}) se solapan; separa los anclajes"
            )
            descartadas.add(id(m))
            continue
        ultima[m["parrafo"]] = m
    if choques and not tolerante:
        raise ErrorDeMarcas("\n".join(choques))
    avisos.extend(f"OMITIDA {c} (se conserva la primera)" for c in choques)
    marcas = [m for m in marcas if id(m) not in descartadas]

    agrupadas: dict[int, list[dict]] = {}
    for n, m in enumerate(marcas, start=1):
        m["n"] = n
        agrupadas.setdefault(m["parrafo"], []).append(m)

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

    Formato heredado de la revision conservadora: cursiva, mas pequeno y
    visualmente separado del texto del autor, en el color de su nivel.
    """
    color = COLOR[marca["tipo"]]
    prefijo = "SUGERENCIA" if marca["tipo"] == "sugerencia" else "COMENTARIO"
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Cm(1.0)
    par.paragraph_format.space_before = Pt(2)
    par.paragraph_format.first_line_indent = Cm(0)
    cab = par.add_run(f"{prefijo} #{marca['n']} {etiqueta(marca['categoria'])}")
    cab.bold = True
    cab.italic = True
    cab.font.size = Pt(9)
    cab.font.color.rgb = color
    resto = par.add_run(f" — sobre «{recorta(cita, 110)}»: {cuerpo}")
    resto.italic = True
    resto.font.size = Pt(9)
    resto.font.color.rgb = color


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
    # Comentarios y sugerencias se anclan igual: envuelven tramos del texto.
    comentarios = [m for m in grupo if m["tipo"] in ("comentario", "sugerencia")]
    sugerencias = [m for m in comentarios if m["tipo"] == "sugerencia"]

    # Un anclaje no puede partir una correccion: se ensancha.
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
            # Fragmento de una sugerencia anclada a una frase (no al parrafo
            # entero): violeta con subrayado punteado, sin tachar nada.
            if any(sg["inicio"] <= ini and fin <= sg["fin"] and sg["anclada"] for sg in sugerencias):
                run.font.color.rgb = VIOLETA
                run.font.underline = WD_UNDERLINE.DOTTED
            runs = [run]
            # La propuesta de la sugerencia, entre corchetes, justo detras.
            for sg in sugerencias:
                if sg["anclada"] and sg["fin"] == fin and sg["propuesta"]:
                    prop = p.add_run(f" [{sg['propuesta']}]")
                    prop.italic = True
                    prop.font.color.rgb = VIOLETA
                    runs.append(prop)
            tramos.append((ini, fin, runs))
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
        for sg in sugerencias:  # una sugerencia ensanchada que acaba aqui
            if sg["anclada"] and sg["fin"] == fin and sg["propuesta"]:
                prop = p.add_run(f" [{sg['propuesta']}]")
                prop.italic = True
                prop.font.color.rgb = VIOLETA
                runs.append(prop)
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
        if c["tipo"] == "sugerencia":
            cuerpo = c["nota"] + (f"  [propuesta opcional: {c['propuesta']}]" if c["propuesta"] else "")
        else:
            cuerpo = c["texto"]
        if modo in ("margen", "ambos"):
            comentar(doc, runs, c, cuerpo, autor, iniciales)
        pendientes.append((c, cuerpo, texto[c["inicio"]:c["fin"]]))

    if modo in ("inline", "ambos"):
        for marca, cuerpo, cita in sorted(pendientes, key=lambda x: x[0]["n"]):
            nota_inline(doc, marca, cuerpo, cita)


def comentar(doc: Document, runs: list, marca: dict, cuerpo: str, autor: str, iniciales: str) -> None:
    comentario = doc.add_comment([runs[0], runs[-1]], text="", author=autor, initials=iniciales)
    par = comentario.paragraphs[0] if comentario.paragraphs else comentario.add_paragraph()
    color = COLOR[marca["tipo"]]
    prefijo = "SUGERENCIA · " if marca["tipo"] == "sugerencia" else ""
    cab = par.add_run(f"#{marca['n']} {prefijo}{etiqueta(marca['categoria'])}")
    cab.bold = True
    cab.font.color.rgb = color
    resto = par.add_run(f" — {cuerpo}")
    resto.font.color.rgb = color


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
    sugerencias = [m for m in todas if m["tipo"] == "sugerencia"]
    palabras = meta_f.get("total_palabras", 0) or 1
    filas = [
        ("Palabras revisadas", f"{meta_f.get('total_palabras', 0)} en {meta_f.get('total_parrafos', 0)} párrafos"),
        ("Correcciones en rojo", str(len(correcciones))),
        ("Comentarios en azul", str(len(comentarios))),
        ("Sugerencias opcionales en violeta", str(len(sugerencias))),
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
        (", correcciones directas: solo el error objetivo (ortografía, gramática, concordancia de género "
         "y número, puntuación y rayas de diálogo, tratamiento, grafía de un nombre ya establecido). El "
         "original queda tachado y la propuesta va en rojo y negrita. ", None, False),
        ("En azul", AZUL, True),
        (", observaciones que merecen que te detengas: continuidad, verosimilitud histórica comprobada, "
         "ambigüedad real, lógica narrativa, caracterización. ", None, False),
        ("En violeta", VIOLETA, True),
        (", sugerencias opcionales: cacofonías, repeticiones cercanas, redacción, ritmo y la palabra que "
         "podría sonar mejor. El fragmento va subrayado en punteado y la propuesta, si la hay, entre "
         "corchetes; puedes tomarla o dejarla. Cada marca lleva un número que coincide con la tabla final.",
         None, False),
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


def texto_derecha(m: dict) -> str:
    """La columna 'Propuesta o comentario' de la tabla y del resumen."""
    nota = f"  ({m['nota']})" if m["nota"] else ""
    if m["tipo"] == "correccion":
        return f"→ {m['propuesta']}{nota}"
    if m["tipo"] == "supresion":
        return f"suprimir{nota}"
    if m["tipo"] == "sugerencia":
        return (f"opcional: → {m['propuesta']}{nota}" if m["propuesta"]
                else f"opcional: {m['nota']}")
    return m["texto"]


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
        derecha = texto_derecha(m)
        valores = [str(m["n"]), str(m["parrafo"]), etiqueta(m["categoria"]).lower(),
                   recorta(m["buscar"], 70), recorta(derecha, 140), ""]
        for celda, valor in zip(celdas, valores):
            celda.text = valor
            for par in celda.paragraphs:
                for run in par.runs:
                    run.font.size = Pt(8.5)
                    if celda is celdas[2]:
                        run.font.color.rgb = COLOR[m["tipo"]]


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
        derecha = texto_derecha(m)
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
        agrupadas = preparar(fuente, marcas_json, avisos, tolerante=args.tolerante)
    except ErrorDeMarcas as exc:
        print("MARCAS INVÁLIDAS — no se ha generado nada:\n" + str(exc), file=sys.stderr)
        print("\nCorrige el JSON de marcas y vuelve a ejecutar "
              "(o usa --tolerante para omitir solo las marcas que fallan).", file=sys.stderr)
        return 1

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
    cuenta = {t: sum(1 for g in agrupadas.values() for m in g if m["tipo"] in t)
              for t in (("correccion", "supresion"), ("comentario",), ("sugerencia",))}
    print(f"    marcas aplicadas: {total}  (rojo {cuenta[('correccion', 'supresion')]}, "
          f"azul {cuenta[('comentario',)]}, violeta {cuenta[('sugerencia',)]})")
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
