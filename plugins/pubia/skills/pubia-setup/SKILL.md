---
name: pubia-setup
description: PUBIA skill. Prepares a novel's working folder for the rest of PUBIA via the command `pubia setup`: asks for the Scrivener sync folder, verifies it can actually read the draft, writes pubia.json (novel, author, language, era, paths, typographic conventions), creates the biblia/ and revisiones/ layout with the bible skeleton, adds a .gitignore, and explains step by step how to set up "Sync with External Folder" in Scrivener so the text flows out without copy-paste and nothing is ever written back into the project. It also states the read-only guarantee: PUBIA only writes inside biblia/ and revisiones/. Use when the user says "pubia setup", "configura la novela", "empezamos con una novela nueva", "donde pongo el manuscrito", or when another PUBIA skill finds no pubia.json.
metadata:
  author: Julio Fernández
  version: "0.2.0"
---

# pubia-setup (PUBIA)

Use this skill on a new novel folder, or when another PUBIA skill reports a missing `pubia.json`. Commands: `pubia setup`, `pubia setup <ruta-de-sincronizacion>`.

Talk to the author in their language (Spanish by default).

## What you must find out

Ask only what you cannot deduce, in one go:

1. **Título de la novela** y **autor** (para la portada de las revisiones).
2. **Las épocas y el lugar.** En plural: una novela puede cruzar varios períodos, y lo que es cierto en uno es falso en otro. Pregunta por los tramos de años y qué capítulos caen en cada uno (p. ej. `1866-1873, caps. 1-14` y `1898-1917, caps. 15-28`). Si todavía no está decidido, se deja la lista vacía y se rellena cuando la cronología exista; sin fecha de escena, el corrector no afirma anacronismos, los pregunta.
3. **Variedad del español y tratamiento.** Es la pregunta que más errores evita: ¿español de España, de Puerto Rico, de Argentina…? ¿Los diálogos van en **ustedes** o en **vosotros**? ¿Hay voseo? ¿Hay personajes de otra variedad cuyo habla distinta es caracterización y no error? Sin esto, el corrector normaliza la novela hacia el castellano peninsular, que es el peor daño que puede hacer.
4. **Ruta de la carpeta de sincronización de Scrivener** (ver abajo cómo crearla).
5. **Convenciones tipográficas** si el autor ya las tiene decididas (raya de diálogo, comillas, pensamientos en cursiva, cifras). Si no, se dejan las habituales del español y se anotan en la biblia cuando se vean en el texto.
6. **Formato del entregable**, si tiene preferencia: comentarios al margen de Word (por defecto), comentarios en el cuerpo en azul y cursiva, o ambos; tipografía y cuerpo (por defecto Times New Roman 11).
7. **Si escribe más de una novela en la misma época y lugar**, ofrécele una carpeta de investigación compartida (`investigacion_compartida` en `pubia.json`): lo verificado sobre el período y el habla se acumula ahí y sirve para las demás novelas, en vez de investigarse otra vez desde cero. Si solo hay una novela, déjalo en `null`.

## Scrivener: sincronización con carpeta externa

Explícaselo así (Scrivener 3):

1. En Scrivener: **Archivo → Sincronizar → Con carpeta externa…** (*File → Sync → With External Folder*).
2. **Carpeta compartida**: elige una carpeta nueva, p. ej. `~/Documentos/<Novela>-sync`.
3. Marca **Sincronizar el contenido del borrador** (*Sync the contents of the Draft folder*). Las notas y la papelera no hacen falta.
4. **Formato**: RTF (por defecto) o texto plano. PUBIA lee los dos.
5. Marca **Sincronizar automáticamente al abrir y cerrar el proyecto** si quieres olvidarte del paso manual.
6. Pulsa **Sincronizar**. Aparecerá `<Novela>-sync/Draft/` con un fichero por documento, numerado en el orden del binder.

Avísale de dos cosas:

- PUBIA **solo lee** esa carpeta. No escribe en ella, así que Scrivener nunca va a re-importar nada de PUBIA. Las correcciones las teclea el autor en Scrivener.
- Cada vez que escriba, debe sincronizar antes de pedir una revisión (o dejar la sincronización automática activada). Si no, se revisa texto viejo. `pubia revisa` avisa de la fecha del fichero que ha leído.

## What you create

In the novel's folder (not in the plugin):

```
pubia.json
biblia/
  00-indice.md  personajes.md  cronologia.md  lugares.md
  tramas.md     lexico-y-estilo.md  investigacion.md
  decisiones.md contradicciones.md
revisiones/
.gitignore
```

- `pubia.json`: copy `${CLAUDE_PLUGIN_ROOT}/skills/pubia-setup/assets/pubia.ejemplo.json` and fill it in with the answers. Use an absolute path for `scrivener_sync`.
- The bible files: create them with the headings of `${CLAUDE_PLUGIN_ROOT}/skills/pubia-biblia/references/plantilla-biblia.md` and **empty of content** — do not invent facts. `pubia biblia` fills them from the manuscript.
- The one exception: in `lexico-y-estilo.md`, write down the **variety and treatment** the author just told you (variety, ustedes/vosotros/voseo, which characters are exceptions). That is a declaration, not an inference, and the corrector needs it from the very first review. Leave the table of oral forms empty with its headings: `pubia biblia` fills it from the text.
- `.gitignore`: add `biblia/.cache/` and, if the author's sync folder happens to live inside the repo, the folder itself (the manuscript belongs to Scrivener, not to this repo).

## Verify before declaring it done

1. Run the reader against the configured folder and show the author what came out:
   ```
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/pubia-revisa/scripts/leer_manuscrito.py \
     --fuente "<scrivener_sync>" --salida biblia/.cache/manuscrito.json
   ```
   The output lists documents, paragraphs and words per document. If it finds nothing, the sync is not done or the path is wrong: fix it before going on.
2. Confirm that `uv` is available (the scripts declare their own dependencies and resolve them on the fly; nothing is installed globally).
3. Tell the author the next step: `pubia biblia` to build the memory of what is already written, and then `pubia revisa cap N` for each new chapter.

Do not run `pubia biblia` yourself unless asked; on a long novel it is a heavy read and the author should decide when.
