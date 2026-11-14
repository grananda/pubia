---
name: pubia-continuidad
description: PUBIA skill. Cross-novel continuity audit via the command `pubia continuidad`: unlike `pubia revisa`, which works chapter by chapter, this one reads the whole manuscript against the bible and hunts what is only visible from above -- timeline impossibilities and derived ages, knowledge state (a character using a fact they cannot have yet, or asking about what they were already told), threads planted and never resolved and resolutions never planted, name drift, traits and objects that mutate between distant chapters, repeated scene beats, stalled arcs, accumulated anachronisms. It delivers a prioritized Markdown report with chapter references and quotes; it corrects no prose and proposes no style. Use when the user says "pubia continuidad", "revisa la coherencia de la novela", "que cabos sueltos tengo", "cuadra la cronologia", or before closing a draft.
metadata:
  author: Julio Fernández
  version: "0.3.0"
---

# pubia-continuidad (PUBIA)

Use this skill for a whole-novel pass, or when they invoke:

- `pubia continuidad` (everything written so far)
- `pubia continuidad cap 1-14` (a stretch)
- `pubia continuidad cronologia` / `saber` / `tramas` (one lens only)
- "¿puede Marta saber lo de la venta en el cap. 9?" (one question: answer it, do not audit the novel)

Also "revisa la coherencia de la novela", "que cabos sueltos tengo", "cuadra la cronologia", "esto hay que mirarlo antes de mandarlo".

Write in the author's language (Spanish by default).

## How it differs from `pubia revisa`

`pubia revisa` corrects a chapter: it works line by line and delivers a `.docx`. `pubia continuidad` never touches a line. It reads the whole thing and answers a different question: **does this novel hold together?** The deliverable is a report, because the fixes are decisions about the plot, not edits to a sentence.

## Workflow

0. **Size the job to the question.** A single question needs the bible entries it names and the chapters it cites, nothing else: grep the bible, extract those chapters with `--filtro`, quote, answer in chat. A single lens needs that lens. Only a full audit reads everything, and even then the bible goes first and the text only to confirm (step 3). Loading more than the question needs does not make the answer safer; it buries it.
1. Read `pubia.json` and the bible (the whole bible for a full audit; the relevant files or entries for a lens or a question). If the bible does not cover every chapter, run `pubia biblia` first — auditing against an outdated bible produces false findings, which is worse than no audit.
2. Extract the full manuscript:
   ```
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/pubia-revisa/scripts/leer_manuscrito.py \
     --config pubia.json --salida revisiones/continuidad/manuscrito.json
   ```
3. Audit one lens at a time, over the whole text. Never try to hold them all at once.
   **On a long novel, the bible is the map and the text is the evidence.** Past roughly 30 000 words, do not read the whole manuscript per lens. Build each lens from the bible first (the timeline from `cronologia.md`, the knowledge state from `personajes.md`, the threads from `tramas.md`): that is where the cross-chapter view already lives. Then go to the text only to confirm or refute each candidate finding, reading just the paragraphs involved (the `documentos` ranges in the JSON tell you where each chapter starts). Lenses the bible does not cover well (`Estructura y repeticion`) go stretch by stretch, writing interim notes to `revisiones/continuidad/` between stretches. A finding is only reported once you have quoted the text, never from the bible alone.
4. Write `revisiones/continuidad/continuidad-<fecha>.md`, prioritized.
5. Report in chat only the blocking findings; the rest is in the file.

## The lenses

**Cronología.** Absolute and relative dates, elapsed time between chapters, derived ages, seasons and weather, days of the week when named, journey durations, pregnancies, mournings and other clocks the text started. Build the timeline and look for the impossible, not the improbable.

**Estado de información (`saber`).** Per character, what they know and from which chapter. Then find: a character acting on something they cannot know yet; a character asking about what they were already told; a secret the reader was told to care about that everyone seems to have forgotten; a revelation that arrives with no scene behind it. This is the lens that catches the breaks readers write letters about.

**Tramas.** Every thread planted: where it was planted, whether it paid off, where. Chekhov's guns still hanging. Resolutions with no setup. Subplots that start and evaporate. Promises the opening made that the ending does not keep.

**Personajes.** Name and spelling drift, traits that mutate (eyes, handedness, scars, accent), objects that reappear after being lost, registers that slip (someone who used *usted* suddenly using *tú* with no scene to justify it), arcs that stop advancing for ten chapters.

**Geografía.** Distances, internal layout of houses and towns, what can be seen from where, how long it takes to get between places.

**Época.** Anachronisms accumulated across the whole novel, including lexical ones, and inconsistencies in the era's own rules (what one chapter says is forbidden, another allows with no comment).

**Estructura y repetición.** Scenes that repeat the same beat, chapters that open the same way, a resource used so often it has become a tic (the same gesture, the same weather, the same kind of cliffhanger).

## Report format

```markdown
# Continuidad — <Novela> — 2026-11-09
Cubre caps. 1-14 · biblia a 2026-11-09 · 61 400 palabras

## Bloqueantes
### B-01 · Marta sabe lo de la venta antes de que se lo cuenten
- **Dónde**: cap. 9 («ya sabía quién había firmado») vs cap. 11 (Tomás se lo cuenta).
- **Por qué rompe**: el cap. 11 pierde su función; la escena deja de ser una revelación.
- **Opciones**: mover la revelación al 9 y reconvertir el 11 en confirmación; o quitar la frase del 9.
- **Decide el autor**: cuál de las dos escenas quieres que cargue con el giro.

## Importantes
...
## Cabos sueltos
| Hilo | Plantado | Estado |
|---|---|---|
| El telegrama | cap. 12 | sin recoger a fecha de cap. 14 |

## Línea temporal reconstruida
<tabla de fechas, capítulos y edades, con las imposibilidades marcadas>

## Dudas para el autor
<lo que no puedes resolver leyendo: intenciones, no datos>
```

## Rules

- **Investigar antes de afirmar.** Un anacronismo o una inexactitud histórica solo entra en el informe si está verificado, con su fuente, y se anota en `biblia/investigacion.md`. Lo que las fuentes no concluyen va como incertidumbre, nunca como hallazgo. Lo que el autor se aparta del hecho a sabiendas y funciona es licencia narrativa: no es un hallazgo.
- **Evidence or nothing.** Every finding cites the chapters that clash and quotes the minimum needed. A continuity finding without a quote is a guess.
- **Do not propose prose.** You name the problem and the options; you do not write the fix. The author decides and writes.
- **Do not confuse ambiguity with error.** What the text leaves deliberately open is not a loose end. If you cannot tell, it goes under "Dudas para el autor".
- **Respect `biblia/decisiones.md`.** What the author declared intentional is not a finding.
- **Prioritize honestly.** Blocking means a reader will notice and the book is damaged. Three real blocking findings are worth more than forty nits.
- Record in `biblia/contradicciones.md` anything that remains unresolved, so the next pass does not rediscover it from scratch.
