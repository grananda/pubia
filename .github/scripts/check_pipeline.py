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

El mayordomo habia dio orden de encerrar a los peones en el almacen, pero nadie se habia movido.
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
        {"parrafo": 4, "tipo": "supresion", "buscar": ", pero nadie se habia movido",
         "categoria": "redaccion", "nota": "Repite la idea anterior."},
        {"parrafo": 2, "tipo": "comentario", "buscar": "cafe quemao", "categoria": "continuidad",
         "texto": "En el cap. 4 el cafetal esta abandonado: no hay quien queme cafe."},
        {"parrafo": 2, "tipo": "comentario", "categoria": "ritmo",
         "texto": "Comentario anclado a todo el parrafo."},
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
        if comentarios != 4:
            fallos.append(f"docx: esperaba 4 comentarios reales de Word y hay {comentarios}")
        elif tachados != 3:
            fallos.append(f"docx: esperaba 3 fragmentos tachados en rojo y hay {tachados}")
        elif vinetas != 2:
            fallos.append(f"docx: la impresion como lector no renderiza las vinetas ({vinetas})")
        elif not sidecar.exists():
            fallos.append("docx: no ha escrito el sidecar *.resueltas.json")
        elif [m["n"] for m in json.loads(sidecar.read_text(encoding="utf-8"))["marcas"]] != [1, 2, 3, 4, 5]:
            fallos.append("sidecar: la numeracion #n no es consecutiva por posicion")
        else:
            hechas.append("comentarios OOXML reales, rojo tachado, vinetas y sidecar")

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
                      {"parrafo": 4, "tipo": "supresion", "buscar": "habia dio orden",
                       "categoria": "redaccion"},
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
            # Numeracion esperada, por posicion en el texto: #1 y #2 comentarios
            # del parrafo 2, #3 el tratamiento del 3, #4 el verbo y #5 la
            # supresion del 4. El autor solo aplico el verbo.
            esperado = {1: "sin cambios", 2: "sin cambios", 3: "rechazada",
                        4: "aceptada", 5: "rechazada"}
            discrepan = {n: (dec.get(n), v) for n, v in esperado.items() if dec.get(n) != v}
            if discrepan:
                fallos.append(f"decisiones: deduccion inesperada (obtenido, esperado) -> {discrepan}")
            else:
                hechas.append("deduccion: 1 aceptada, 2 rechazadas y 2 sin cambios, "
                              "desde el manuscrito corregido")

if fallos:
    print("El pipeline tiene problemas:", file=sys.stderr)
    for f in fallos:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)
for h in hechas:
    print(f"  ok  {h}")
print(f"Pipeline correcto: {len(hechas)} comprobaciones.")
