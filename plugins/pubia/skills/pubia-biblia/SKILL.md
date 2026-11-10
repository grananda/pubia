---
name: pubia-biblia
description: PUBIA skill. Builds and maintains the novel bible via the command `pubia biblia`: the persistent memory that lets the corrector check continuity across a whole novel written over months. It reads the manuscript from the Scrivener sync folder and extracts into Markdown under biblia/ (personajes, cronologia, lugares, tramas, lexico-y-estilo, decisiones) every fact the text commits to -- exact spellings, physical traits, kinships, ages, dates, places and distances, objects, who knows what and since when, open plot threads, invented lexicon and style conventions -- each with the chapter it comes from, separating author canon from inferences still to confirm. It works incrementally by document fingerprint, never rewrites declared canon, and flags contradictions instead of picking a side. Use when the user says "actualiza la biblia", "pubia biblia", "extrae los personajes", "apunta esto como canon", "que sabemos de este personaje", or after writing new chapters.
metadata:
  author: Julio Fernández
  version: "0.2.0"
---

# pubia-biblia (PUBIA)

Use this skill when the bible needs creating or refreshing, or when they invoke:

- `pubia biblia` (incremental: only what changed)
- `pubia biblia completa` (rebuild from the whole manuscript)
- `pubia biblia cap 12` (absorb one chapter)
- `pubia biblia personaje "Marta"` (consolidate or query one entry)

Also "actualiza la biblia", "extrae los personajes", "apunta esto como canon", "que sabemos de Marta".

Write the bible in the author's language (Spanish by default). This SKILL.md is English/ASCII for portability.

## Why it exists

`pubia revisa` can only catch a continuity break if someone remembers chapter 4 while reading chapter 31. That memory is this bible: plain Markdown, versioned in git, readable and editable by the author. **Markdown is the single source of truth**; no database, no hidden state.

## Hard rules

1. **Read-only on the manuscript.** You write only inside `biblia/`.
2. **Every fact carries its origin**: `(cap. 4)`. A fact without a chapter cannot be used to contradict the author later.
3. **Canon vs inference.** What the author wrote in the text or declared explicitly is canon. What you deduced goes marked `[deducido]` until the author confirms it. Never promote your own inference to canon on your own.
4. **Do not erase the author's canon.** If the manuscript now contradicts something recorded, you do not overwrite it: you record both versions as a contradiction and tell the author. They decide which is true.
5. **No invention.** If the text does not say a character's eye colour, the bible does not say it either. An empty field is information; a made-up one is damage.

## Files under `biblia/`

| Fichero | Contenido |
|---|---|
| `00-indice.md` | Qué cubre la biblia (capítulos y su huella), fecha de la última actualización, resumen de la novela en diez líneas, y el índice de los demás ficheros. |
| `personajes.md` | Una ficha por personaje: nombre exacto y variantes, edad por fecha, físico, voz y registro, parentescos, qué quiere, qué sabe y desde cuándo, objetos propios, apariciones por capítulo. |
| `cronologia.md` | Época y marco histórico, línea temporal con fechas absolutas y relativas, duración de cada capítulo, saltos, edades derivadas. |
| `lugares.md` | Geografía de la novela: lugares, su disposición interna, distancias y tiempos de viaje, qué se ve desde dónde. |
| `tramas.md` | Hilos narrativos: qué se planta, dónde, y si se ha resuelto; promesas al lector pendientes; subtramas por personaje. |
| `lexico-y-estilo.md` | Variedad del español y tratamiento (ustedes/vosotros/voseo, quién trata a quién de qué), **formas orales y dialectales que son canon y no se corrigen** (*quedao*, *mi'jo*, *pa'*, el artículo ante nombre propio), léxico regional, términos inventados y su grafía canónica, topónimos, convenciones tipográficas (raya, comillas, cursiva para pensamientos, cifras), registro del narrador, tiempo verbal, punto de vista. |
| `investigacion.md` | Lo verificado sobre la época, la medicina, la ciencia o la técnica, **con su fuente** y su etiqueta (comprobado / incertidumbre real / plausible no demostrable). Evita repetir búsquedas y llegar a conclusiones distintas en cada capítulo. |
| `decisiones.md` | Lo que el autor ya rechazó, con fecha y motivo. **`pubia revisa` lo lee antes de marcar nada.** Lo mantiene `pubia decisiones`. |
| `contradicciones.md` | Las que no puedes resolver: dos capítulos que no pueden ser ciertos a la vez. |

`references/plantilla-biblia.md` tiene la estructura exacta de cada ficha.

## Workflow

1. **Load the config**: `pubia.json` (`scrivener_sync`, `biblia`, novel title, era). If missing, run `pubia setup`.
2. **Read `biblia/00-indice.md`** if it exists: which chapters are already absorbed and with what fingerprint.
3. **Extract the text** with the reader of `pubia-revisa` (same script, same canonical form):
   ```
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/pubia-revisa/scripts/leer_manuscrito.py \
     --fuente "<scrivener_sync>" --salida biblia/.cache/manuscrito.json
   ```
   Compare per-document fingerprints against the index to decide what to re-read. In `completa` mode, read everything.
4. **Read chapter by chapter, in story order**, and for each one note: new facts, facts that confirm existing ones, facts that contradict them, and what each character learns in that chapter (the knowledge state is the part nobody remembers and the part that breaks novels).
   Also collect, without judging them: every oral or dialect form the text uses (*quedao*, *pa'*, *mi'ja*, *usté*), the regional lexicon, and who addresses whom with which treatment. These go to `lexico-y-estilo.md` as canon, which is what stops the corrector from "fixing" the author's voice. A form that only appears once is still canon unless it clashes with the same character elsewhere -- in which case it is a contradiction, not an error to correct.
5. **Update the files**, preserving the author's wording in canonical entries, appending `(cap. N)` to every fact, and keeping entries alphabetical or chronological as the template says.
6. **Record contradictions** in `contradicciones.md` with both versions and their chapters. Do not choose.
7. **Update `00-indice.md`**: chapters covered, fingerprints, date, and a one-line changelog of this run.
8. **Report** in chat: what is new, what contradicts, and what you had to mark `[deducido]` and would like the author to confirm. Keep it to the things that need a human decision.

## Querying mode

`pubia biblia personaje "Marta"` does not rewrite anything: it reads the bible and answers what is known about that character, with chapter references, and says explicitly what is not recorded. Useful mid-writing, to avoid contradicting yourself in the first place.
