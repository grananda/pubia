#!/usr/bin/env python3
"""Prueba de extremo a extremo de los tres scripts del plugin.

Lo que de verdad se puede romper en este repo no es un manifiesto: es que un
anclaje deje de resolver, que el sidecar de marcas resueltas cambie de forma o
que el guardarrail del rojo deje de disparar. Esto lo ejercita en cada PR.

Requiere python-docx y striprtf instalados (la CI los instala con pip).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SK = ROOT / "plugins" / "pubia" / "skills"
LEER = SK / "pubia-revisa" / "scripts" / "leer_manuscrito.py"
ANOTA = SK / "pubia-revisa" / "scripts" / "anota_docx.py"
DECIDE = SK / "pubia-decisiones" / "scripts" / "leer_decisiones.py"

CAPITULO = """# Capitulo 7 - El cafetal

Don Esteban cruzo el batey antes de que aclarara. El olor a cafe quemao le llego desde el rancho.

-Mi'jo, vengan aca -dijo-. ¿Vosotros sabeis lo que paso anoche?

El mayordomo habia dio orden de encerrar a los los peones en el almacen, pero nadie se habia movido.
"""

fallos: list[str] = []
hechas: list[str] = []


def corre(argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *argv], capture_output=True, text=True)


def espera_exito(nombre: str, argv: list[str]) -> subprocess.CompletedProcess:
    r = corre(argv)
    if r.returncode != 0:
        fallos.append(f"{nombre}: esperaba exito y salio {r.returncode}\n{r.stderr.strip()}")
    else:
        hechas.append(nombre)
    return r


def espera_fallo(nombre: str, argv: list[str], en_stderr: str, no_debe_existir: Path) -> None:
    r = corre(argv)
    if r.returncode == 0:
        fallos.append(f"{nombre}: esperaba que fallara y salio 0")
    elif en_stderr.lower() not in r.stderr.lower():
        fallos.append(f"{nombre}: fallo, pero sin explicar '{en_stderr}'\n{r.stderr.strip()}")
    elif no_debe_existir.exists():
        fallos.append(f"{nombre}: fallo pero dejo escrito {no_debe_existir.name}")
    else:
        hechas.append(nombre)


with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp)
    (t / "sync" / "Draft").mkdir(parents=True)
    (t / "sync" / "Draft" / "07-El-cafetal.txt").write_text(CAPITULO, encoding="utf-8")
    (t / "sync" / "Draft" / "08-La-carta.rtf").write_text(
        r"{\rtf1\ansi\deff0 Marta hab\'eda vuelto en tren.\par}", encoding="utf-8")
    (t / "sync" / "Notes").mkdir()
    (t / "sync" / "Notes" / "no-leer.txt").write_text("esto no debe aparecer\n", encoding="utf-8")

    fuente = t / "fuente.json"
    espera_exito("extraccion desde carpeta de sincronizacion",
                 [str(LEER), "--fuente", str(t / "sync"), "--salida", str(fuente)])

    if fuente.exists():
        d = json.loads(fuente.read_text(encoding="utf-8"))
        tipos = [p["tipo"] for p in d["parrafos"]]
        textos = " ".join(p["texto"] for p in d["parrafos"])
        if "no debe aparecer" in textos:
            fallos.append("extraccion: ha leido la carpeta Notes/, que debe ignorarse")
        elif "titulo" not in tipos or "dialogo" not in tipos:
            fallos.append(f"extraccion: no clasifica titulo/dialogo (tipos: {tipos})")
        elif "vuelto en tren" not in textos:
            fallos.append("extraccion: no ha decodificado el .rtf de Scrivener")
        elif d["meta"]["sha256"] == "":
            fallos.append("extraccion: sin huella sha256")
        else:
            hechas.append("clasificacion, orden del binder, .rtf y huella")

    def marcas(ruta: Path, lista: list[dict]) -> Path:
        ruta.write_text(json.dumps(
            {"meta": {"novela": "prueba", "capitulo": "cap 7", "revision": "v1"}, "marcas": lista},
            ensure_ascii=False), encoding="utf-8")
        return ruta

    buenas = marcas(t / "ok.json", [
        {"parrafo": 3, "tipo": "correccion", "buscar": "¿Vosotros sabeis lo que paso anoche?",
         "propuesta": "¿Ustedes saben lo que paso anoche?", "categoria": "tratamiento",
         "nota": "La variedad de la novela pide ustedes."},
        {"parrafo": 4, "tipo": "correccion", "buscar": "habia dio", "propuesta": "habia dado",
         "categoria": "verbo"},
        {"parrafo": 4, "tipo": "supresion", "buscar": "los ", "ocurrencia": 2,
         "categoria": "omision", "nota": "Articulo duplicado."},
        {"parrafo": 2, "tipo": "comentario", "buscar": "cafe quemao", "categoria": "continuidad",
         "texto": "En el cap. 4 el cafetal esta abandonado: no hay quien queme cafe."},
        {"parrafo": 2, "tipo": "comentario", "categoria": "claridad",
         "texto": "Comentario anclado a todo el parrafo."},
        {"parrafo": 2, "tipo": "sugerencia", "buscar": "antes de que aclarara",
         "propuesta": "antes del alba", "categoria": "cacofonia",
         "nota": "Tres -a- seguidas tropiezan al leerlo en voz alta."},
    ])
    impresion = t / "impresion.md"
    impresion.write_text("Primer parrafo de la impresion.\n\n- una vineta\n- otra vineta\n",
                         encoding="utf-8")
    docx = t / "cap-07-v1.docx"
    espera_exito("generacion del .docx",
                 [str(ANOTA), "--fuente", str(fuente), "--marcas", str(buenas),
                  "--salida", str(docx), "--resumen", str(t / "r.md"),
                  "--impresion", str(impresion)])

    sidecar = docx.with_suffix(".resueltas.json")
    if docx.exists():
        from docx import Document  # noqa: E402

        doc = Document(str(docx))
        comentarios = len(doc.comments)
        tachados = sum(1 for p in doc.paragraphs for r in p.runs if r.font.strike)
        vinetas = sum(1 for p in doc.paragraphs if p.style.name == "List Bullet")
        violeta = [r.text for p in doc.paragraphs for r in p.runs
                   if r.font.color.rgb is not None and str(r.font.color.rgb) == "7030A0"]
        punteado = [r.text for p in doc.paragraphs for r in p.runs
                    if r.font.underline is not None and r.font.underline is not True
                    and r.font.underline is not False and "DOTTED" in str(r.font.underline)]
        if comentarios != 5:
            fallos.append(f"docx: esperaba 5 comentarios reales de Word y hay {comentarios}")
        elif punteado != ["antes de que aclarara"] or " [antes del alba]" not in violeta:
            fallos.append(f"docx: la sugerencia no sale en violeta punteado con su propuesta "
                          f"(punteado {punteado}, violeta {violeta})")
        elif tachados != 3:
            fallos.append(f"docx: esperaba 3 fragmentos tachados en rojo y hay {tachados}")
        elif vinetas != 2:
            fallos.append(f"docx: la impresion como lector no renderiza las vinetas ({vinetas})")
        elif not sidecar.exists():
            fallos.append("docx: no ha escrito el sidecar *.resueltas.json")
        elif [m["n"] for m in json.loads(sidecar.read_text(encoding="utf-8"))["marcas"]] != [1, 2, 3, 4, 5, 6]:
            fallos.append("sidecar: la numeracion #n no es consecutiva por posicion")
        else:
            hechas.append("comentarios OOXML reales, rojo tachado, violeta punteado, vinetas y sidecar")

    espera_fallo("anclaje que no resuelve",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "mal.json", [
                      {"parrafo": 2, "tipo": "correccion", "buscar": "palabra que no existe",
                       "propuesta": "x", "categoria": "tilde"}])),
                  "--salida", str(t / "no.docx")],
                 "no se encuentra", t / "no.docx")

    espera_fallo("dos correcciones que se solapan",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "sol.json", [
                      {"parrafo": 4, "tipo": "correccion", "buscar": "habia dio orden",
                       "propuesta": "habia dado orden", "categoria": "verbo"},
                      {"parrafo": 4, "tipo": "correccion", "buscar": "habia dio",
                       "propuesta": "habia dado", "categoria": "verbo"}])),
                  "--salida", str(t / "no2.docx")],
                 "solapan", t / "no2.docx")

    # El principio rector, comprobado por la maquina: una preferencia de estilo
    # no puede entrar en rojo.
    espera_fallo("guardarrail del rojo: categoria de preferencia",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "lex.json", [
                      {"parrafo": 2, "tipo": "correccion", "buscar": "quemao",
                       "propuesta": "quemado", "categoria": "lexico"}])),
                  "--salida", str(t / "no3.docx")],
                 "preferencia", t / "no3.docx")

    # El guardarrail es una lista permitida: tampoco entra en rojo una supresion
    # por criterio ni una categoria inventada.
    espera_fallo("guardarrail del rojo: supresion por redaccion",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "sup.json", [
                      {"parrafo": 4, "tipo": "supresion", "buscar": ", pero nadie se habia movido",
                       "categoria": "redaccion"}])),
                  "--salida", str(t / "no4.docx")],
                 "preferencia", t / "no4.docx")
    espera_fallo("guardarrail del rojo: categoria inventada",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "inv.json", [
                      {"parrafo": 2, "tipo": "correccion", "buscar": "quemao",
                       "propuesta": "quemado", "categoria": "mejora"}])),
                  "--salida", str(t / "no5.docx")],
                 "no es una categoria objetiva", t / "no5.docx")

    # Tercer nivel: lo opcional va en violeta y solo con sus categorias.
    # La palabra que suena mejor es violeta: se acepta como sugerencia...
    espera_exito("violeta: la palabra que suena mejor es sugerencia",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "lx.json", [
                      {"parrafo": 4, "tipo": "sugerencia", "buscar": "encerrar",
                       "propuesta": "recluir", "categoria": "lexico",
                       "nota": "Mas preciso para peones en un almacen."}])),
                  "--salida", str(t / "lx.docx")])
    # ...pero una categoria que no es de ningun nivel no se pinta.
    espera_fallo("violeta: categoria inventada",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "sl.json", [
                      {"parrafo": 2, "tipo": "sugerencia", "buscar": "batey",
                       "propuesta": "patio", "categoria": "estilo", "nota": "Suena mejor."}])),
                  "--salida", str(t / "no6.docx")],
                 "no puede ser de categoria", t / "no6.docx")
    espera_fallo("violeta: lo opcional no va en azul",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "ca.json", [
                      {"parrafo": 4, "tipo": "comentario", "buscar": "habia movido",
                       "categoria": "repeticion", "texto": "Repite 'habia'."}])),
                  "--salida", str(t / "no7.docx")],
                 "sugerencia", t / "no7.docx")
    espera_fallo("violeta: una sugerencia sin motivo",
                 [str(ANOTA), "--fuente", str(fuente),
                  "--marcas", str(marcas(t / "sn.json", [
                      {"parrafo": 2, "tipo": "sugerencia", "buscar": "antes de que aclarara",
                       "categoria": "cacofonia"}])),
                  "--salida", str(t / "no8.docx")],
                 "nota", t / "no8.docx")

    # --tolerante omite SOLO las marcas que fallan; las buenas se pintan.
    tol = t / "tol.docx"
    r = espera_exito("tolerante: genera con las marcas validas",
                     [str(ANOTA), "--fuente", str(fuente), "--tolerante",
                      "--marcas", str(marcas(t / "tol.json", [
                          {"parrafo": 4, "tipo": "correccion", "buscar": "habia dio",
                           "propuesta": "habia dado", "categoria": "verbo"},
                          {"parrafo": 4, "tipo": "correccion", "buscar": "habia dio orden",
                           "propuesta": "habia dado orden", "categoria": "verbo"},
                          {"parrafo": 2, "tipo": "correccion", "buscar": "no existe",
                           "propuesta": "x", "categoria": "tilde"},
                          {"parrafo": 2, "tipo": "comentario", "buscar": "cafe quemao",
                           "categoria": "continuidad", "texto": "Comentario valido."}])),
                      "--salida", str(tol)])
    if r.returncode == 0:
        quedan = [(m["n"], m["buscar"]) for m in
                  json.loads(tol.with_suffix(".resueltas.json").read_text(encoding="utf-8"))["marcas"]]
        if quedan != [(1, "cafe quemao"), (2, "habia dio")]:
            fallos.append(f"tolerante: esperaba conservar 2 marcas numeradas sin huecos y quedan {quedan}")
        elif r.stdout.count("OMITIDA") != 2:
            fallos.append(f"tolerante: no reporta las 2 marcas omitidas\n{r.stdout}")
        else:
            hechas.append("tolerante: omite solo las 2 invalidas y numera sin huecos")

    # Filtro de documento: `7` no es `17`, `cap 1` no es `cap 12`.
    f = t / "filtro" / "Draft"
    f.mkdir(parents=True)
    for nombre in ("07-El-cafetal.txt", "17-El-regreso.txt", "70-Final.txt",
                   "Capitulo 1.txt", "Capitulo 12.txt"):
        (f / nombre).write_text(f"Texto de {nombre}.\n", encoding="utf-8")

    def docs(filtro: str, fuente_dir: Path = t / "filtro", extra: list[str] | None = None) -> list[str]:
        out = t / "f.json"
        r = corre([str(LEER), "--fuente", str(fuente_dir), "--filtro", filtro,
                   "--salida", str(out), *(extra or [])])
        if r.returncode != 0:
            return []
        return [d["nombre"] for d in json.loads(out.read_text(encoding="utf-8"))["meta"]["documentos"]]

    casos = {"7": ["07-El-cafetal"], "07": ["07-El-cafetal"], "17": ["17-El-regreso"],
             "Capitulo 1": ["Capitulo 1"], "capitulo 12": ["Capitulo 12"], "cafetal": ["07-El-cafetal"]}
    malos = {k: (docs(k), v) for k, v in casos.items() if docs(k) != v}
    if malos:
        fallos.append(f"filtro: documentos inesperados (obtenido, esperado) -> {malos}")
    else:
        hechas.append("filtro: numero exacto del binder y bordes numericos")

    # La carpeta de sincronizacion se da una vez en pubia.json y es la fuente
    # estandar: sin --fuente, con su Draft/, y una carpeta Notes en la ruta del
    # usuario no deja fuera el manuscrito.
    base = t / "Notes" / "Novela-sync"
    (base / "Draft").mkdir(parents=True)
    (base / "Draft" / "01-Uno.txt").write_text("Dentro del borrador.\n", encoding="utf-8")
    (base / "suelto.txt").write_text("Fuera del borrador.\n", encoding="utf-8")
    cfg = t / "pubia.json"
    cfg.write_text(json.dumps({"scrivener_sync": str(base), "modo_parrafos": "lineas"}),
                   encoding="utf-8")
    out = t / "cfg.json"
    r = corre([str(LEER), "--config", str(cfg), "--salida", str(out)])
    if r.returncode != 0:
        fallos.append(f"config: la extraccion desde scrivener_sync fallo\n{r.stderr.strip()}")
    else:
        textos = " ".join(p["texto"] for p in json.loads(out.read_text(encoding="utf-8"))["parrafos"])
        if "Dentro del borrador" not in textos or "Fuera del borrador" in textos:
            fallos.append(f"config: Draft/ o Notes/ en la ruta mal resueltos ({textos!r})")
        else:
            hechas.append("config: scrivener_sync como fuente estandar, Draft/ y Notes/ solo dentro")

    # Una carpeta estandar sin Draft/ es una sincronizacion que no se ha hecho:
    # se para en vez de leer lo que haya suelto.
    sin_draft = t / "sin-draft"
    sin_draft.mkdir()
    (sin_draft / "suelto.txt").write_text("Texto suelto.\n", encoding="utf-8")
    cfg2 = t / "pubia2.json"
    cfg2.write_text(json.dumps({"scrivener_sync": str(sin_draft)}), encoding="utf-8")
    espera_fallo("config: scrivener_sync sin Draft/",
                 [str(LEER), "--config", str(cfg2), "--salida", str(t / "nodraft.json")],
                 "Draft/", t / "nodraft.json")

    # Ciclo de decisiones: el autor aplica una correccion y rechaza otra.
    corregido = (t / "sync" / "Draft" / "07-El-cafetal.txt")
    corregido.write_text(CAPITULO.replace("habia dio", "habia dado"), encoding="utf-8")
    nueva = t / "nueva.json"
    espera_exito("re-extraccion tras las correcciones a mano",
                 [str(LEER), "--fuente", str(t / "sync"), "--filtro", "07-", "--salida", str(nueva)])
    if sidecar.exists() and nueva.exists():
        r = espera_exito("lectura de decisiones",
                         [str(DECIDE), "--resueltas", str(sidecar), "--fuente", str(fuente),
                          "--nueva-fuente", str(nueva), "--salida", str(t / "dec.json")])
        if r.returncode == 0:
            datos = json.loads((t / "dec.json").read_text(encoding="utf-8"))["decisiones"]
            dec = {d["n"]: d["decision_inferida"] for d in datos}
            # Numeracion esperada, por posicion en el texto: #1 comentario a
            # todo el parrafo 2, #2 la sugerencia y #3 el comentario del mismo
            # parrafo, #4 el tratamiento del 3, #5 el verbo y #6 la supresion
            # del 4. El autor solo aplico el verbo: la sugerencia que dejo tal
            # cual es "descartada", no "rechazada".
            esperado = {1: "sin cambios", 2: "descartada", 3: "sin cambios",
                        4: "rechazada", 5: "aceptada", 6: "rechazada"}
            discrepan = {n: (dec.get(n), v) for n, v in esperado.items() if dec.get(n) != v}
            if discrepan:
                fallos.append(f"decisiones: deduccion inesperada (obtenido, esperado) -> {discrepan}")
            else:
                hechas.append("deduccion: 1 aceptada, 2 rechazadas, 1 sugerencia descartada y "
                              "2 sin cambios, desde el manuscrito corregido")

if fallos:
    print("El pipeline tiene problemas:", file=sys.stderr)
    for f in fallos:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)
for h in hechas:
    print(f"  ok  {h}")
print(f"Pipeline correcto: {len(hechas)} comprobaciones.")
