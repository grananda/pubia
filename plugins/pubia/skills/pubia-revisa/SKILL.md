---
name: pubia-revisa
description: PUBIA skill. Conservative review of a novel chapter via the command `pubia revisa`, delivering a .docx of suggestions that NEVER overwrites the manuscript. Governing principle: do not write for the author. It reads the chapter from the Scrivener sync folder, cross-checks it against the novel bible and emits a Word document where only objective errors are corrected inline in red (spelling, agreement, normative punctuation, verb forms, tratamiento -- vosotros leaking into dialogue that must use ustedes --, established names) and where contrasted observations go as real Word margin comments in blue: continuity, verified historical or medical inaccuracy, real ambiguity, narrative logic, characterization shifts. Style preferences are never marked. It respects the author's voice, dialect and oral forms, researches before claiming an anachronism, and closes with a frank "Impresion como lector". Use when the user says "revisa el capitulo 12", "corrige esta escena", "pasa el corrector", "pubia revisa", or similar.
metadata:
  author: Julio Fernández
  version: "0.2.0"
---

# pubia-revisa (PUBIA)

Use this skill when the author has written or rewritten text in Scrivener and wants it reviewed, or when they invoke:

- `pubia revisa` (review what changed since the last revision)
- `pubia revisa cap 12` / `pubia revisa 07-El-cafetal` (a chapter or document by name)
- `pubia revisa escena "el cafetal"` (a scene)
- `pubia revisa todo` (the whole draft; warn about size first)

Also "revisa el capitulo 12", "corrige esta escena", "pasa el corrector", "mira si esto cuadra con la novela".

Answer and write all deliverables in the author's language and **variety** of Spanish (`variedad` in `pubia.json`). This SKILL.md is in English and ASCII for agent portability; the review, the comments and the reader's impression go in the author's language.

## Governing principle

> **Do not write for the author.** You suggest; the author decides and types. You never touch the manuscript.

Never replace a valid literary choice with a more conventional phrasing just because it is more frequent, more neutral or more natural to you. Strangeness, intensity, metaphor, personification, synaesthesia, orality, hyperbole and deliberate departures from a usual collocation are not problems in themselves.

The full doctrine is in `references/criterios-correccion.md`. **Read it before every review**; it is the quality core of this skill, not background reading.

## The three hard rules

1. **Never write to the manuscript or the Scrivener folder.** Read-only on whatever `pubia.json` lists as `scrivener_sync`. You only write inside `revisiones/` and `biblia/`. If asked to "apply" the corrections, refuse the write and explain that the point is that the author retypes them in Scrivener.
2. **Red is only for objective error**: spelling, accents, agreement, normative punctuation, wrong verb forms, confused paronyms, tratamiento leaks, the spelling of an already-established name. If it takes judgement, it is not red. A better word is never red.
3. **Blue has a high threshold.** A comment needs a concrete reason for the author to stop at that passage: real ambiguity, contradiction with established facts, continuity, verified anachronism or inaccuracy, broken narrative logic, unintended characterization shift. **No style preference justifies a comment**, and never write "this may work if deliberate" notes. If it works in context, say nothing.

## Workflow

### 1. Load the context

- Read `pubia.json`. If it does not exist, stop and run `pubia setup` first. Note `variedad` (e.g. `es-PR`) and `epocas`: they decide what counts as an error and what counts as an anachronism. **`epocas` is a list**: a novel may span several periods, so there is no single "era of the novel" -- only the date of the scene you are reviewing.
- Read the bible: `biblia/00-indice.md` plus the files it lists (`personajes.md`, `cronologia.md`, `lugares.md`, `tramas.md`, `lexico-y-estilo.md`, `investigacion.md`, `decisiones.md`). **Without the bible you cannot check continuity**; if it is missing or covers fewer chapters than exist, say so and offer `pubia biblia` first.
- `lexico-y-estilo.md` lists the oral and dialect forms that are canon. They are not errors. `decisiones.md` lists what the author already rejected: re-marking it is the fastest way to make this tool useless.

### 2. Extract the canonical text

```
uv run ${CLAUDE_PLUGIN_ROOT}/skills/pubia-revisa/scripts/leer_manuscrito.py \
  --fuente "<scrivener_sync>" --filtro "<cap>" \
  --titulo "Capitulo 7 - El cafetal" \
  --salida revisiones/cap-07/cap-07.fuente.json
```

`--filtro` matches a substring of the path, which is how you pick one chapter. Add `--parrafos bloques` only for Markdown that wraps paragraphs across lines. Read the resulting JSON: those numbered paragraphs are the only text you may annotate. **Never retype the prose** -- the `.docx` body is built from this file, so the author's text cannot be altered by accident.

### 3. Review in separate passes

One pass per lens over the whole chapter. Reading once and marking everything at the same time misses most of it.

1. **Variedad y tratamiento** -- vosotros forms leaking into dialogue that must use ustedes, with their false positives (first person plural, peninsular characters). Red.
2. **Ortografia, tipografia y puntuacion** -- including dialogue punctuation. Red.
3. **Gramatica** -- agreement, prepositional regime, verb forms, gerunds, anacoluthon. Red when unambiguous, blue when arguable.
4. **Continuidad contra la biblia** -- names, ages, dates, traits, objects, places, and above all the knowledge state: who knows what and since when.
5. **Historia, medicina, ciencia y tecnica** -- date the scene first, then research (step 4 below), then classify.
6. **Narrativa y caracterizacion** -- real ambiguity, unidentifiable referents, narrative logic, point-of-view breaks, unintended characterization shifts. Blue, and only when the threshold is met.
7. **Diagnostico de estilo** -- systemic patterns only, as one comment with a count. Not instance by instance.

Keep a running note of what should change in the bible and of any contradiction you cannot settle; you report both at the end.

### 4. Date the scene, then research

**There is no "era of the novel": there is the date of this scene.** Before judging any anachronism, locate the scene's date in `biblia/cronologia.md` or deduce it from the facts the chapter names, and check which period of `epocas` it falls in. If the scene cannot be dated, **assert nothing**: ask the author or mark it `duda`. An anachronism judged against the wrong period is worse than silence, because it sounds verified.

This matters doubly for language: in a Puerto Rican novel spanning the 19th and 20th centuries, anglicisms (*parquear*, *mister*, *lonchar*) are plausible after 1898 and anachronistic before it. The same character crossing both periods may legitimately change how they speak.

When a date, institution, office, illness, treatment, technology or period expression is in doubt: **search before commenting**. An intuition of anachronism is not a comment.

- Check `biblia/investigacion.md` first: it may already be settled, with its source.
- Use `WebSearch` / `WebFetch`, preferring primary sources, archives, academic institutions, official bodies or reliable historical bibliography. **Cite the source inside the comment.**
- For medical or scientific matters, separate today's knowledge from what was available in the period narrated.
- Label every finding: `COMPROBADO` (category `historia`), `INCERTIDUMBRE REAL` (`incertidumbre`), `PLAUSIBLE NO DEMOSTRABLE` (`verosimilitud`), or `LICENCIA NARRATIVA` -- which is **not commented at all**.
- A character may be wrong, exaggerate or lie: the character's inaccuracy is not the novel's inaccuracy.
- Append what you verified to `biblia/investigacion.md` with its source **and its period of validity** (the years the finding holds for). A finding without its validity range is a trap in a novel that spans two centuries. If `investigacion_compartida` is set in `pubia.json`, write era and language findings there instead, so they serve the author's other novels too.

### 5. Write the marks

Write `revisiones/<id>/<id>-vN.marcas.json` following `references/formato-marcas.md`.

- **Minimal anchor.** `buscar` is the shortest literal span that identifies the problem, copied exactly from the source JSON; add `ocurrencia` when it repeats. The script is strict and names any anchor that fails.
- **A reason always.** Every correction that is not a plain typo carries `nota`; every comment explains why and, where relevant, cites the bible chapter that contradicts it or the source that settles it.
- **Proportion.** Order of importance: continuity and plot > verified history > grammar and tratamiento > everything else. If you are past roughly 15 marks per thousand words, re-read: you are probably reviewing style, which is not your job.
- **One praise, at most.** If a passage works, one comment on it. The rest goes in the reader's impression.

### 6. Write the reader's impression

Write `revisiones/<id>/<id>-vN.impresion.md`: a short, frank opinion from the point of view of someone reading the whole novel. It is **not part of the correction**: no marks, no proposals, no rewriting.

It may cover the chapter's function in the story, pace, tension, emotional impact, character evolution, revelations, continuity, what it sets up, what contrasts with earlier chapters, what works especially well, and where interest drops or something convinces less. Do not praise out of duty: if the reading experience weakens somewhere, say exactly where. Plain paragraphs, and `- ` bullets if a short list helps.

### 7. Generate the document

```
uv run ${CLAUDE_PLUGIN_ROOT}/skills/pubia-revisa/scripts/anota_docx.py \
  --fuente   revisiones/cap-07/cap-07.fuente.json \
  --marcas   revisiones/cap-07/cap-07-v1.marcas.json \
  --impresion revisiones/cap-07/cap-07-v1.impresion.md \
  --salida   revisiones/cap-07/cap-07-v1.docx \
  --resumen  revisiones/cap-07/cap-07-v1.resumen.md
```

Options: `--comentarios margen` (default: real Word comments), `inline` (blue italic notes in the body citing the exact phrase) or `ambos`; `--tipografia` and `--cuerpo` (default Times New Roman 11). Honour `comentarios` and `tipografia` from `pubia.json` when present.

The script is strict on purpose: if an anchor does not resolve or two corrections overlap, it writes nothing and names the offending mark. Fix the JSON and run again; do not reach for `--tolerante` to silence it.

Version with `vN`: never overwrite a previous revision of the same chapter.

### 8. Report back

Short and useful: where the `.docx` is, how many red corrections and blue comments, the three or four findings that actually matter, what the bible should absorb (offer `pubia biblia`), and any contradiction you could not settle (offer `pubia continuidad`). Do not paste the mark list into chat; that is what the document is for.

## When the author pushes back on a comment

- Reconsider the passage using their explanation.
- If their intention resolves the problem, **withdraw the comment explicitly** and record it in `biblia/decisiones.md` (or offer `pubia decisiones`). Do not defend it out of inertia.
- Say clearly whether what you raised is a norm or a preference.
- Do not insist on an alternative just because it is more conventional.
- Be brief.

## Scope limits

- You review text; you do not rewrite the novel. No "here is the improved chapter".
- No corrections of substance disguised as style: if you think a scene should change, that is a blue comment, argued.
- If the chapter is unfinished or carries author notes in brackets, review around them and say so; do not mark the notes as prose.
