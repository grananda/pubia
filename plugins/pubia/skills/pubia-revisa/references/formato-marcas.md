# Formato del JSON de marcas

Contrato entre la skill (que decide qué marcar) y `anota_docx.py` (que lo pinta).
El cuerpo del `.docx` se construye con el texto de `*.fuente.json`; aquí solo se
dice **dónde** y **qué** anotar.

```json
{
  "meta": {
    "novela": "Almenara",
    "capitulo": "Capítulo 12 — El regreso",
    "revision": "v1",
    "fecha": "2026-11-09",
    "revisor": "pubia",
    "notas": "Primera pasada contra la biblia v3. Faltan las escenas del telégrafo."
  },
  "marcas": [
    {
      "parrafo": 4,
      "tipo": "correccion",
      "buscar": "dió",
      "ocurrencia": 1,
      "propuesta": "dio",
      "categoria": "tilde",
      "nota": "Monosílabo: sin tilde desde 1959."
    },
    {
      "parrafo": 4,
      "tipo": "supresion",
      "buscar": "el ",
      "ocurrencia": 2,
      "categoria": "omision",
      "nota": "Artículo duplicado: «en el el almacén»."
    },
    {
      "parrafo": 4,
      "tipo": "sugerencia",
      "buscar": ", pero el pueblo no se había movido ni un dedo",
      "categoria": "redaccion",
      "nota": "Repite con otras palabras la idea de la frase anterior."
    },
    {
      "parrafo": 5,
      "tipo": "sugerencia",
      "buscar": "la lana la lavaba",
      "propuesta": "lavaba la lana",
      "categoria": "cacofonia",
      "nota": "Tropieza al leerlo en voz alta."
    },
    {
      "parrafo": 2,
      "tipo": "comentario",
      "buscar": "El caballo relinchó",
      "categoria": "continuidad",
      "texto": "En el cap. 4 este animal es una yegua llamada Brisa."
    },
    {
      "parrafo": 7,
      "tipo": "comentario",
      "categoria": "claridad",
      "texto": "No queda claro si «él» es Tomás o el mayordomo: los dos acaban de hablar."
    }
  ]
}
```

## Campos

| Campo | Obligatorio | Significado |
|---|---|---|
| `parrafo` | sí | `id` del párrafo en `*.fuente.json`. |
| `tipo` | sí | `correccion` o `supresion` (rojo), `comentario` (azul) o `sugerencia` (violeta). |
| `buscar` | sí en `correccion` y `supresion`; opcional en `comentario` y `sugerencia` | Fragmento **literal** del párrafo. Sin `buscar`, un comentario o una sugerencia anclan el párrafo entero. |
| `ocurrencia` | no (1) | Cuál de las apariciones de `buscar` en ese párrafo. |
| `propuesta` | sí en `correccion`; opcional en `sugerencia` | Texto que sustituye a `buscar`. En una sugerencia aparece entre corchetes tras el fragmento, como opción. |
| `categoria` | sí | Ver taxonomía. Sale en el comentario y en la tabla resumen. |
| `nota` | sí en `sugerencia`; opcional en el resto | El por qué. En una corrección o supresión genera además un comentario al margen; en una sugerencia **es** el comentario. |
| `texto` | sí en `comentario` | El comentario. Es lo que leerá el autor en el margen de Word. |

## Taxonomía

**Correcciones (rojo, en línea). Solo lo objetivo:**
`ortografia`, `tilde`, `puntuacion`, `tipografia`, `gramatica`, `concordancia`,
`verbo`, `preposicion`, `dialogo`, `numero`, `tratamiento` (fuga de *vosotros*
donde la variedad pide *ustedes*), `nombre` (grafía de un nombre, rango o
referente ya establecido), `omision` (palabra omitida o duplicada), `paronimo`
(*infligir/infringir*).

`lexico` **no es categoría de ningún nivel**: cambiar una palabra por otra mejor
es una preferencia, y las preferencias no se marcan.

**Comentarios (azul, margen o cuerpo). Umbral alto, exigen detenerse:**
`continuidad`, `cronologia`, `personaje`, `trama`, `historia` (anacronismo o
inexactitud **comprobada**), `incertidumbre` (las fuentes no concluyen),
`verosimilitud` (plausible no demostrable), `ambiguedad`, `claridad`, `logica`,
`punto-de-vista`, `voz`, `duda`.

**Sugerencias (violeta). Opcionales, el autor las toma o las deja:**
`cacofonia`, `repeticion` (misma palabra muy cerca, sin función retórica),
`redaccion`, `ritmo`. El fragmento va en violeta con subrayado punteado, la
propuesta (si la hay) entre corchetes, y la `nota` al margen. Una categoría de
sugerencia en un `comentario` se rechaza: lo opcional no va en azul.

Una `supresion` también es rojo, así que usa **la misma lista cerrada** que una
`correccion`: se borra una palabra duplicada (`omision`), una coma normativamente
incorrecta (`puntuacion`). Borrar una frase porque sobra es criterio: va como
`sugerencia` de `redaccion`, y el autor decide.

El script lo comprueba en los tres niveles: una marca con una categoría que no es
de su nivel —o inventada— no se pinta. Por defecto aborta; con `--tolerante` la
omite y la lista.

En los comentarios de investigación, abrir el texto con la etiqueta del hallazgo:
`COMPROBADO:`, `INCERTIDUMBRE REAL:`, `PLAUSIBLE NO DEMOSTRABLE:`. Una
`LICENCIA NARRATIVA` no se comenta.

## Reglas que evitan el 90% de los fallos del script

1. `buscar` debe ser **literal**: el mismo texto, con sus tildes, comillas y rayas, copiado del párrafo de `*.fuente.json`. Si lo reescribes, no ancla.
2. Dos correcciones del mismo párrafo **no pueden solaparse**. Si vas a suprimir una frase, no corrijas una falta dentro de ella: desaparece con la frase.
3. Un comentario sí puede abarcar una corrección: su anclaje se ensancha solo si hace falta (el script avisa).
4. El `id` de párrafo es el de la fuente, no el número de párrafo del capítulo en Scrivener.
5. La numeración `#n` de las marcas la pone el script por posición en el texto; no la escribas tú.

## Impresión como lector

No es una marca. Va en su propio fichero y se pasa con `--impresion`; el script
la añade como última sección del `.docx`, titulada «Impresión como lector» y
marcada como ajena a la corrección. Texto corrido, con `- ` para listas cortas.

## Modos de comentario

`--comentarios margen` (por defecto) genera comentarios reales de Word, anclados
al fragmento, con la etiqueta en el color de su nivel. `inline` los escribe en el
cuerpo, en cursiva y cuerpo menor, con el formato `COMENTARIO #n CATEGORIA — sobre
«frase exacta»: explicación` en azul (o `SUGERENCIA #n …` en violeta).
`ambos` hace las dos cosas. La tipografía por defecto es Times New Roman 11.

## Convención de nombres

```
revisiones/
  cap-12/
    cap-12.fuente.json        <- texto canónico extraído (se regenera)
    cap-12-v1.marcas.json     <- esta pasada
    cap-12-v1.docx            <- entregable para el autor
    cap-12-v1.impresion.md    <- impresión como lector (entra en el .docx)
    cap-12-v1.resumen.md      <- tabla de marcas en texto, para pubia-decisiones
    cap-12-v1.resueltas.json  <- marcas ancladas y numeradas (lo lee pubia-decisiones)
    cap-12-v2.marcas.json     <- la siguiente pasada, sin tocar la v1
```
