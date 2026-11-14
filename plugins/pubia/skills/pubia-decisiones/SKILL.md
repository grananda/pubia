---
name: pubia-decisiones
description: PUBIA skill. Closes the loop of a revision via the command `pubia decisiones`: finds out which suggestions the author accepted and which they rejected, and records the rejections in biblia/decisiones.md so the corrector never marks them again. It reads the Decision column of the revision .docx if the author filled it in in Word, and/or re-extracts the manuscript after the manual corrections and deduces mark by mark whether the original text is still there or the proposal already made it in. The author can also just say it in chat ("rechazo la 2 y la 3"). Rejections become permanent rules, with their reason, so that recurring decisions about voice and style stop being re-litigated on every pass. Use when the user says "pubia decisiones", "ya he corregido el capitulo", "rechazo estas sugerencias", "apunta que esto no se toca", "esto es intencionado", or similar.
metadata:
  author: Julio Fernández
  version: "0.3.0"
---

# pubia-decisiones (PUBIA)

Use this skill after the author has worked through a revision, or when they invoke:

- `pubia decisiones cap 12` (last revision of that chapter)
- `pubia decisiones` (the most recent revision)
- `pubia decisiones "no vuelvas a marcar X"` (a permanent rule, with no revision involved)

Also "ya he corregido el capitulo", "rechazo la 2 y la 7", "esto es intencionado", "apunta que esto no se toca".

Write in the author's language (Spanish by default).

## Why it exists

A corrector that re-marks what the author already rejected becomes noise and gets switched off. Every rejection is information about the author's voice, and it belongs in the bible, with its reason, forever.

## A withdrawn comment is a rejection

When the author explains an intention that resolves a comment you raised -- in chat, mid-conversation, with no `.docx` involved -- that comment is **withdrawn**, not defended. Record it here like any other rejection, with the author's reason in their words. This is the main way the corrector learns the difference between the author's voice and an actual error.

## The three sources of a decision

1. **The author says it in chat.** The fastest route: `rechazo la 2 y la 3`. Take it, ask for the reason in one line if it is not obvious (the reason is what makes the rule reusable), and record it.
2. **The Decision column of the `.docx`.** If the author filled it in in Word and saved the file, read it. Free text is fine: `no, el enfado es la mirada de Marta` counts as a rejection with its reason.
3. **The corrected manuscript.** Re-sync Scrivener, re-extract, and deduce what was applied.

```
# re-extraer el capitulo ya corregido
uv run ${CLAUDE_PLUGIN_ROOT}/skills/pubia-revisa/scripts/leer_manuscrito.py \
  --config pubia.json --filtro "<cap>" \
  --salida revisiones/cap-12/cap-12.fuente-corregida.json

# cruzar las marcas de la revision con lo que de verdad cambio
uv run ${CLAUDE_PLUGIN_ROOT}/skills/pubia-decisiones/scripts/leer_decisiones.py \
  --resueltas revisiones/cap-12/cap-12-v1.resueltas.json \
  --docx revisiones/cap-12/cap-12-v1.docx \
  --fuente revisiones/cap-12/cap-12.fuente.json \
  --nueva-fuente revisiones/cap-12/cap-12.fuente-corregida.json \
  --salida revisiones/cap-12/cap-12-v1.decisiones.json
```

`--resueltas` is the sidecar that `anota_docx.py` wrote next to the `.docx`; it carries the `#n` numbering the author sees, so never renumber by hand.

**The inferred column is a hint, not a verdict.** It compares text, so it gets things wrong in predictable ways: a correction whose anchor also appears elsewhere in the chapter, a comment the author addressed by rewriting the whole paragraph, a rewrite that solves the problem another way. Where the author's own note and the inference disagree, the author wins. Where there is only an inference and it matters, ask.

## What you record

In `biblia/decisiones.md`:

- **One row per rejection**: date, chapter, mark number and category, what was proposed, and the decision with its reason, in the author's words where you have them.
- **A permanent rule** whenever the rejection generalises. This is the valuable part:
  - `No marcar la personificacion de animales en la voz de Marta: es su mirada, no un descuido.`
  - `«candil de patio» es lexico de la novela, no un error.`
  - A rule must be checkable by reading it, and narrow enough not to blind the corrector to real errors. If a rejection is one-off and local, record only the row, not a rule.
- **Violet suggestions are optional.** One the author left as it was is *descartada*, not rejected: count it, do not record a row or a rule. Only when the author says why (`no, es un leitmotiv`) or the same kind keeps being discarded (every `repeticion` of *tierra*, chapter after chapter) does it become a rule: `No sugerir la repeticion de «tierra»: es leitmotiv.`
- **Nothing about accepted suggestions**, beyond a count. The bible is not a scoreboard; what the corrector needs to remember is what *not* to say again.

If a rejection reveals something about the novel's canon (an invented word, a typographic convention, a trait), also send it to the right bible file — or tell the author that `pubia biblia` should absorb it.

## Report back

Short: how many accepted, how many rejected, which new permanent rules you wrote, and anything you could not classify and need the author to settle. If the rejection rate is high in one category, say so: the corrector is miscalibrated in that dimension and should ease off next pass. The same goes for violet: if most suggestions are discarded, the next review should raise the bar.
