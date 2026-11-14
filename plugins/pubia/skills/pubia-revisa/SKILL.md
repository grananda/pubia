---
name: pubia-revisa
description: PUBIA skill. Conservative review of a novel chapter via the command `pubia revisa`, delivering a .docx of suggestions that NEVER overwrites the manuscript. Governing principle: do not write for the author. It reads the chapter from the Scrivener sync folder, cross-checks it against the novel bible and emits a Word document in three tiers: red inline only for crucial objective errors (spelling, grammar, gender and number agreement, dialogue dashes, tratamiento, established names); blue margin comments for what demands a stop (continuity, verified historical inaccuracy, real ambiguity, narrative logic); violet optional suggestions the author may take or leave (cacophony, close word repetition, clumsy wording, rhythm). Word preferences are never marked. It respects the author's voice and dialect, researches before claiming an anachronism, and closes with a frank "Impresion como lector". Use when the user says "revisa el capitulo 12", "corrige esta escena", "pasa el corrector", "pubia revisa", or similar.
metadata:
  author: Julio Fernández
  version: "0.3.0"
---

# pubia-revisa (PUBIA)

Use this skill when the author has written or rewritten text in Scrivener and wants it reviewed, or when they invoke:

- `pubia revisa` (review what changed since the last revision)
- `pubia revisa cap 12` / `pubia revisa 07-El-cafetal` (a chapter or document by name)
- `pubia revisa escena "el cafetal"` (a scene)
- `pubia revisa todo` (the whole draft; warn about size first)
- `pubia revisa parrafo 23` / "mira esta frase" / "¿esto cuadra con el cap. 4?" (a targeted question: see *Scope the work to the question*)

Also "revisa el capitulo 12", "corrige esta escena", "pasa el corrector", "mira si esto cuadra con la novela".

Answer and write all deliverables in the author's language and **variety** of Spanish (`variedad` in `pubia.json`). This SKILL.md is in English and ASCII for agent portability; the review, the comments and the reader's impression go in the author's language.

## Governing principle

> **Do not write for the author.** You suggest; the author decides and types. You never touch the manuscript.

Never replace a valid literary choice with a more conventional phrasing just because it is more frequent, more neutral or more natural to you. Strangeness, intensity, metaphor, personification, synaesthesia, orality, hyperbole and deliberate departures from a usual collocation are not problems in themselves.

The full doctrine is in `references/criterios-correccion.md`. **Read it before every review**; it is the quality core of this skill, not background reading.

## The hard rules

1. **Never write to the manuscript or the Scrivener folder.** Read-only on whatever `pubia.json` lists as `scrivener_sync`. You only write inside `revisiones/` and `biblia/`. If asked to "apply" the corrections, refuse the write and explain that the point is that the author retypes them in Scrivener.
2. **Three tiers, decided in this order.** For each finding ask, in order, and stop at the first yes:
   - **Red (`correccion` / `supresion`) -- does a norm or an established fact settle it?** Only the crucial and objective: spelling and accents, grammar, gender/number/person agreement, dialogue dashes and dialogue punctuation, verb forms, prepositional regime, confused paronyms, tratamiento leaks, the spelling of an already-established name, a word duplicated by accident. If it takes judgement, it is not red.
   - **Blue (`comentario`) -- must the author stop here?** Real ambiguity, contradiction with established facts, continuity, verified anachronism or inaccuracy, broken narrative logic, unintended characterization shift. High threshold; never "this may work if deliberate" notes.
   - **Violet (`sugerencia`) -- is there a concrete reading problem the author may or may not want to fix?** Cacophony and unintended rhyme, the same word repeated very close with no rhetorical function, a sentence that makes you re-read, a stretch whose rhythm stumbles. Optional by definition: say why in `nota`, offer a `propuesta` only if a minimal one exists, and never insist.
   - **Otherwise, nothing.** A word you like better, a smoother synonym, a reordered sentence, a "fixed" metaphor: not marked in any colour.

## Workflow

### 1. Load the context

- Read `pubia.json`. If it does not exist, stop and run `pubia setup` first. Note `variedad` (e.g. `es-PR`) and `epocas`: they decide what counts as an error and what counts as an anachronism. **`epocas` is a list**: a novel may span several periods, so there is no single "era of the novel" -- only the date of the scene you are reviewing.
- Read the bible **selectively** (see *Scope the work to the question*). Always read in full the short files that are rules: `biblia/00-indice.md`, `lexico-y-estilo.md` and `decisiones.md`. From `personajes.md`, `lugares.md`, `tramas.md`, `cronologia.md` and `investigacion.md`, read the entries this chapter touches -- search (`Grep`) for the characters, places, objects and dates it names, plus the timeline around the scene's date -- rather than whole files; if a file is short, just read it. **Without the bible you cannot check continuity**; if it is missing or covers fewer chapters than exist, say so and offer `pubia biblia` first.
- `lexico-y-estilo.md` lists the oral and dialect forms that are canon. They are not errors. `decisiones.md` lists what the author already rejected: re-marking it is the fastest way to make this tool useless.

### 2. Extract the canonical text

```
uv run ${CLAUDE_PLUGIN_ROOT}/skills/pubia-revisa/scripts/leer_manuscrito.py \
  --config pubia.json --filtro "<cap>" \
  --titulo "Capitulo 7 - El cafetal" \
  --salida revisiones/cap-07/cap-07.fuente.json
```

`--filtro` picks the chapter. A bare number (`--filtro 7`) matches the binder's numeric prefix exactly, so `7` never pulls in `17` or `70`; prefer it. Text matches as a substring of the path inside the sync folder, and a number at its edge is not extended (`cap 1` does not match `cap 12`). A chapter split into several scene documents is fine as long as the filter catches all of them and nothing else. **Check the document list the script prints before going on**: if it caught a document that is not this chapter, or missed one, fix the filter. `--config pubia.json` supplies the sync folder (`scrivener_sync`, given once in `pubia setup`: never ask for it again) and `modo_parrafos`; if the script says `Draft/` is missing, the author has not synced from Scrivener yet. Read the resulting JSON: those numbered paragraphs are the only text you may annotate. **Never retype the prose** -- the `.docx` body is built from this file, so the author's text cannot be altered by accident.

### 3. Review in separate passes

One pass per lens over the whole chapter. Reading once and marking everything at the same time misses most of it.

1. **Variedad y tratamiento** -- vosotros forms leaking into dialogue that must use ustedes, with their false positives (first person plural, peninsular characters). Red.
2. **Ortografia, tipografia y puntuacion** -- including dialogue dashes and dialogue punctuation. Red.
3. **Gramatica** -- agreement, prepositional regime, verb forms, gerunds, anacoluthon. Red when unambiguous, blue when it changes the meaning and is arguable.
4. **Continuidad contra la biblia** -- names, ages, dates, traits, objects, places, and above all the knowledge state: who knows what and since when. Blue (red only for an established spelling).
5. **Historia, medicina, ciencia y tecnica** -- date the scene first, then research (step 4 below), then classify. Blue.
6. **Narrativa y caracterizacion** -- real ambiguity, unidentifiable referents, narrative logic, point-of-view breaks, unintended characterization shifts. Blue, and only when the threshold is met.
7. **Lectura en voz alta** -- cacophony, close repetition, sentences that make you re-read, stumbling rhythm. Violet, instance by instance only when it clearly grates; systemic patterns (comodin verbs, narrative filters, *-mente* adverbs) as one violet suggestion with a count.

Keep a running note of what should change in the bible and of any contradiction you cannot settle; you report both at the end.

### 4. Date the scene, then research

**There is no "era of the novel": there is the date of this scene.** Before judging any anachronism, locate the scene's date in `biblia/cronologia.md` or deduce it from the facts the chapter names, and check which period of `epocas` it falls in. If the scene cannot be dated, **assert nothing**: ask the author or mark it `duda`. An anachronism judged against the wrong period is worse than silence, because it sounds verified.

This matters doubly for language: in a Puerto Rican novel spanning the 19th and 20th centuries, anglicisms (*parquear*, *mister*, *lonchar*) are plausible after 1898 and anachronistic before it. The same character crossing both periods may legitimately change how they speak.

When a date, institution, office, illness, treatment, technology or period expression is in doubt: **search before commenting**. An intuition of anachronism is not a comment.

- Check `biblia/investigacion.md` first, and then `<investigacion_compartida>/investigacion.md` if `pubia.json` sets it: it may already be settled, with its source. Use a shared finding only if its validity range covers the scene's date.
- Use `WebSearch` / `WebFetch`, preferring primary sources, archives, academic institutions, official bodies or reliable historical bibliography. **Cite the source inside the comment.**
- For medical or scientific matters, separate today's knowledge from what was available in the period narrated.
- Label every finding: `COMPROBADO` (category `historia`), `INCERTIDUMBRE REAL` (`incertidumbre`), `PLAUSIBLE NO DEMOSTRABLE` (`verosimilitud`), or `LICENCIA NARRATIVA` -- which is **not commented at all**.
- A character may be wrong, exaggerate or lie: the character's inaccuracy is not the novel's inaccuracy.
- Append what you verified to `biblia/investigacion.md` with its source **and its period of validity** (the years the finding holds for). A finding without its validity range is a trap in a novel that spans two centuries. If `investigacion_compartida` is set in `pubia.json`, findings about the era and its speech (true for any novel set there) go to `<investigacion_compartida>/investigacion.md` instead, same format, so the author's other novels reuse them; findings about this novel's own invented facts stay in `biblia/investigacion.md`. Create the shared file with the template headings if it does not exist.

### 5. Write the marks

Write `revisiones/<id>/<id>-vN.marcas.json` following `references/formato-marcas.md`.

- **Each tier has a closed list of categories**, and the script rejects a mark outside its list. Red (`correccion`, `supresion`): the objective ones. Violet (`sugerencia`): `cacofonia`, `repeticion`, `redaccion`, `ritmo`. Blue (`comentario`): the rest of the editorial ones. Deleting a duplicated word is red (`omision`); deleting a clause because it is redundant is a violet `redaccion` suggestion, never a red deletion.
- **Minimal anchor.** `buscar` is the shortest literal span that identifies the problem, copied exactly from the source JSON; add `ocurrencia` when it repeats. The script is strict and names any anchor that fails.
- **A reason always.** Every correction that is not a plain typo carries `nota`; every comment explains why and, where relevant, cites the bible chapter that contradicts it or the source that settles it.
- **Proportion.** Order of importance: continuity and plot > verified history > grammar and tratamiento > violet suggestions. Red has no quota: an error is an error. Violet does: past roughly 5 suggestions per thousand words, keep the ones that grate most and fold the rest into one systemic suggestion with a count; a document full of violet buries the red and the blue.
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

Options: `--comentarios margen` (default: real Word comments), `inline` (italic notes in the body, in the colour of their tier, citing the exact phrase) or `ambos`; `--tipografia` and `--cuerpo` (default Times New Roman 11). Honour `comentarios` and `tipografia` from `pubia.json` when present.

The script is strict on purpose: if an anchor does not resolve, two corrections overlap or a mark's category does not belong to its tier, it writes nothing and names the offending mark. Fix the JSON and run again; do not reach for `--tolerante` to silence it. (`--tolerante` exists for a human in a hurry: it drops only the failing marks and lists them, and the report must say which ones were dropped.)

Version with `vN`: never overwrite a previous revision of the same chapter.

### 8. Report back

Short and useful: where the `.docx` is, how many red corrections, blue comments and violet suggestions, the three or four findings that actually matter, what the bible should absorb (offer `pubia biblia`), and any contradiction you could not settle (offer `pubia continuidad`). Do not paste the mark list into chat; that is what the document is for.

## Scope the work to the question

Context is finite, and a bigger context does not make a better review: what matters gets diluted. Load what the question needs, and no more -- but never skip what the question depends on.

- **A full chapter review** needs the whole chapter text (that is the job) and the bible entries it touches, not the whole bible.
- **A targeted question** -- one paragraph, one sentence, "does this fit with chapter 4?", "is *parquear* OK in 1890?" -- needs only that span, and only the bible entries or research the question names. Extract with `--filtro` the one document, answer in chat, and skip the seven passes and the `.docx` unless the author asks for them. If the answer reveals a rejection or a canon fact, record it as usual.
- **When unsure whether something is relevant, grep before reading.** Searching the bible for a name costs little; reading all of `personajes.md` to check one eye colour costs a lot.
- **Do not trim what the verdict depends on.** If a continuity doubt needs an earlier chapter, extract that chapter (or the paragraphs involved) and quote it; asserting a contradiction from memory or from a partial read is worse than not asserting it.

## When the author pushes back on a comment

- Reconsider the passage using their explanation.
- If their intention resolves the problem, **withdraw the comment explicitly** and record it in `biblia/decisiones.md` (or offer `pubia decisiones`). Do not defend it out of inertia.
- Say clearly whether what you raised is a norm or a preference.
- Do not insist on an alternative just because it is more conventional.
- Be brief.

## Scope limits

- You review text; you do not rewrite the novel. No "here is the improved chapter".
- No corrections of substance disguised as style: if you think a scene should change, that is a blue comment, argued.
- Violet is not a back door for preferences: if the only reason is "I would say it differently", it is not marked.
- If the chapter is unfinished or carries author notes in brackets, review around them and say so; do not mark the notes as prose.
