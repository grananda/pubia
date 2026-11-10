# Criterios de corrección (novela, español)

## Principio rector

**No escribir por el autor.**

No sustituir una elección literaria válida por una formulación más convencional
solo porque sea más frecuente, más neutra o más natural para quien revisa. La
rareza, la intensidad, la metáfora, la personificación, la sinestesia, la
oralidad, la hipérbole o la desviación deliberada de una colocación habitual
**no son un problema por sí mismas**.

Antes de cuestionar una frase, leerla dentro del párrafo, del capítulo, de la
caracterización del personaje y de la continuidad de la novela.

## Los dos umbrales

**Rojo** (corrección directa en el texto): solo lo objetivo o de muy alta
confianza. Si una gramática, el diccionario o un hecho ya establecido en la
novela resuelven la duda, es rojo. Si hace falta criterio, no lo es.

**Azul** (comentario al margen): umbral alto. Solo cuando hay una razón concreta
para que el autor se detenga en ese pasaje. **Ninguna preferencia de estilo
justifica un comentario.** No llenar el documento de advertencias del tipo
«puede funcionar si es deliberado»: si funciona razonablemente en su contexto,
no se comenta.

---

## 1. Variedad del español y tratamiento

La variedad está en `pubia.json` (`variedad`, p. ej. `es-PR`) y sus reglas en
`biblia/lexico-y-estilo.md`. **No se corrige hacia el castellano peninsular.**

### Fuga de «vosotros» donde corresponde «ustedes` → rojo (`tratamiento`)

En diálogos de variedades americanas, barrer sistemáticamente:

- *vosotros*, *os*, *vuestro/vuestra/vuestros/vuestras*;
- *sois, estáis, tenéis, podéis, habéis, queréis, sabéis, venís, decís, hacéis*;
- imperativos de 2.ª del plural: *mirad, sujetad, tensad, encerradlo, venid, callad*.

Sustituir por la forma americana solo **en diálogo** y solo cuando sea realmente
segunda persona del plural.

**Falsos positivos que no hay que tocar:**

- Primera persona del plural: *dejásemos, fuésemos, hiciéramos, salgamos*.
- Subjuntivos y pretéritos que acaban igual por casualidad: *dejéis* sí, *dejamos* no.
- Narrador que no es un personaje, si la novela lo ha fijado en otra norma.
- Personajes peninsulares en una novela americana (un militar llegado de Madrid):
  su *vosotros* es caracterización, no error. Comprobar en la biblia quién es quién.

### La variedad también cambia con el tiempo

En una novela que abarca varias épocas, el habla no es la misma en todas. En el
caso puertorriqueño, la frontera de 1898 es la más marcada: los anglicismos
(*parquear*, *bildin*, *mister*, *lonchar*, los nombres de instituciones
estadounidenses) son **verosímiles después de la ocupación y anacrónicos antes**.
Lo mismo al revés: formas y tratamientos del XIX que se pierden en el XX.

Antes de marcar un préstamo o una forma como impropia, comprobar la fecha de la
escena. Y si el mismo personaje atraviesa las dos épocas, su habla puede cambiar
a propósito: eso es caracterización, y se anota en la biblia, no se corrige.

### Otras variedades

- **Voseo** (*vos tenés, decime*): si la biblia lo declara, es canon.
- **Léxico regional**: *batey, mi'jo, chavos, guagua, jíbaro, bohío*. No se
  sustituyen por sinónimos peninsulares ni se marcan como localismos.
- **Tipografía**: raya `—` para el diálogo y comillas latinas son la convención
  por defecto, pero manda lo que diga `biblia/lexico-y-estilo.md`.

## 2. Oralidad y dialecto: no normalizar

Las reducciones fonéticas y las formas de caracterización **no se corrigen**:

> quedao · condenao · pasao · cuidao · quemao · onde / ónde · mi'jo / mi'ja ·
> pa / pá / pa' · to / toa · usté · verdá · pue' · na' · ni'o ·
> el artículo ante nombre propio (*la Tomasa*) · aspiraciones y elisiones ·
> cualquier forma recogida en `biblia/lexico-y-estilo.md`

Solo se comenta una de estas formas si hay **inconsistencia interna relevante**
(el mismo personaje dice *quedao* en el cap. 3 y *quedado* en el 9 sin motivo) o
si parece de verdad un error mecánico y no una elección de voz. Y entonces es
azul, no rojo.

Cuando aparezca una forma oral nueva, no marcarla: anotarla para que
`pubia biblia` la recoja como canon.

---

## 3. Rojo: correcciones directas

- Ortografía y tildes (incluidas las diacríticas: *sólo* → *solo*, *éste* → *este*).
- Errores tipográficos y palabras omitidas o duplicadas por accidente.
- Concordancia de género, número y persona.
- Régimen preposicional inequívocamente incorrecto.
- Puntuación normativa cuando hay error claro, y puntuación de diálogos.
- Vocativos sin coma.
- Tiempos y formas verbales erróneas (*había dió* → *había dado*, *si tendría*).
- Parónimos confundidos (*infligir/infringir*, *adoptar/adaptar*).
- Fuga de tratamiento (apartado 1).
- Inconsistencias **objetivas** de nombres, rangos o referentes ya establecidos:
  la grafía de un nombre, un cargo que cambia sin motivo, un referente imposible.

Nunca en rojo: una mejora estilística discutible, un sinónimo que suena mejor,
una frase reordenada, una metáfora «arreglada».

### Repertorio ortográfico y gramatical habitual

**Tildes**: monosílabos sin tilde (*dio, vio, fue, fui, vi, di, ti, fe*);
interrogativos y exclamativos sí, incluso indirectos (*no sé **qué** quiere*);
*aun* / *aún*; verbo + enclítico (*dámelo, dígaselo*); mayúsculas con tilde.

**Pares confundidos**: *hay/ahí/ay · echo/hecho · haya/halla/aya · vaya/valla/baya ·
también/tan bien · sino/si no · porque/porqué/por que/por qué · conque/con que ·
demás/de más · sobre todo/sobretodo · asimismo/así mismo · a ver/haber · ha/a/ah ·
e/he · aparte/a parte · entorno/en torno · adonde/a donde*.

**Diálogo**: raya `—` (U+2014), no guion ni semirraya; sin espacio tras la raya de
apertura (`—No vendrá`); verbo de habla en minúscula tras la raya de cierre; la
raya de cierre solo si sigue narración; con verbo de habla, la puntuación va
después de la raya (`—No vendrá —dijo—. Nunca lo hace.`); si el inciso no es de
habla, el parlamento se puntúa antes (`—No vendrá. —Cerró la puerta.`).

**Gramática**: dequeísmo y queísmo; concordancia a distancia y con colectivos;
leísmo de cosa, laísmo, *le* invariable con plural; gerundio de posterioridad y
especificativo; *haber* impersonal en plural (*habían tres*); condicional por
subjuntivo; infinitivo por imperativo; *detrás mío*, *en base a*, *contra más*;
anacoluto; correlación de tiempos en el estilo indirecto.

---

## 4. Azul: comentarios editoriales

Cada comentario se ancla al fragmento exacto (el `.docx` lo hace por
construcción) y explica el problema en una o dos frases.

### Justifican un comentario

- Ambigüedad semántica real.
- Contradicción con hechos ya establecidos.
- Problema de continuidad.
- Referente difícil de identificar.
- Uso léxico cuyo significado contradice claramente la acción descrita.
- Anacronismo comprobado.
- Inexactitud histórica comprobada.
- Problema médico, científico o técnico contrastado.
- Lógica narrativa que rompe la causalidad de la trama.
- Cambio involuntario de caracterización.
- Información que el lector no puede reconciliar con lo ya narrado.

### NO justifican un comentario

- Una frase simplemente inusual.
- Metáforas atrevidas, personificaciones, sinestesias, imágenes hiperbólicas.
- Repeticiones deliberadas y ritmo fragmentario deliberado.
- Palabras de registro elevado o contraste deliberado de registros.
- Decisiones de estilo que funcionan en el contexto.
- Conducta extrema de un personaje cuando la trama la justifica.
- Afirmaciones incorrectas pronunciadas deliberadamente por un personaje.
- **Lenguaje racista, clasista, sexista, cruel o prejuicioso cuando forma parte
  de la caracterización histórica del personaje.** No se comenta, no se suaviza
  y no se advierte sobre él.
- Posibilidades hipotéticas sin evidencia suficiente de que haya un problema.

### Contexto obligatorio antes de comentar

1. Leer el párrafo completo.
2. Considerar lo sucedido en capítulos anteriores.
3. Comprobar qué sabe el personaje y qué sabe el narrador.
4. Distinguir afirmación del narrador de percepción, mentira, error, exageración
   o manipulación de un personaje.
5. Considerar si el pasaje prepara un acontecimiento posterior.
6. Recordar relaciones familiares, decisiones previas, rangos e instituciones.
7. Si falta un dato de continuidad que puede estar en capítulos anteriores, **no
   presumir que es un error**: consultar la biblia o preguntar.

## 5. Diálogo y caracterización

No corregir como si fueran afirmaciones del narrador: mentiras, amenazas,
exageraciones, errores de conocimiento, prejuicios, lenguaje técnico usado para
impresionar, afirmaciones interesadas, razonamientos imperfectos del personaje.

> Ante cada pasaje dudoso: **¿esto es un error del texto o información sobre el
> personaje?**

## 6. Imágenes literarias

Evaluar las imágenes como **unidades completas**, no palabra por palabra. Una
secuencia descriptiva puede justificar expresiones científicas, metáforas o
hipérboles que aisladas parecerían extrañas: analizar la progresión visual, el
campo semántico y la función narrativa antes de intervenir.

Aceptar personificaciones de abstracciones cuando sean coherentes con la voz del
texto (acciones físicas aplicadas a *los intereses*, *las palabras*, *las
sensaciones*).

## 7. Investigación histórica, médica, científica y técnica

### Primero, fechar la escena

Una novela puede abarcar varias épocas. **No existe «la época de la novela»:
existe la fecha de la escena que estás revisando.** Antes de juzgar cualquier
anacronismo:

1. Localizar la fecha de la escena en `biblia/cronologia.md`, o deducirla de los
   hechos que el capítulo nombra.
2. Si no se puede fechar, **no se afirma nada**: se pregunta al autor o se marca
   como `duda`. Un anacronismo juzgado contra la época equivocada es un error
   peor que el silencio, porque suena verificado.
3. Comprobar en qué período de `pubia.json` (`epocas`) cae, porque lo que es
   cierto en uno es falso en otro: la misma isla en 1868, en 1898 y en 1940 tiene
   otra autoridad, otra moneda, otra tecnología y otro habla.

### Luego, investigar

1. **Investigar antes de comentar.** Una intuición de anacronismo no es un
   comentario.
2. Preferir fuentes primarias, archivos, instituciones académicas, organismos
   oficiales o bibliografía histórica fiable. Citar la fuente en el comentario.
3. En lo médico o científico, contrastar con fuentes fiables y **distinguir el
   conocimiento actual del disponible en la época narrada**.
4. Etiquetar siempre en qué categoría cae el hallazgo:
   - `COMPROBADO` — error o anacronismo verificado (categoría `historia`).
   - `INCERTIDUMBRE REAL` — las fuentes no permiten concluir (`incertidumbre`).
   - `PLAUSIBLE NO DEMOSTRABLE` — pudo ser así, no hay dato (`verosimilitud`).
   - `LICENCIA NARRATIVA` — se aparta del hecho a sabiendas y funciona: **no se
     comenta**.
5. Un personaje histórico puede equivocarse, exagerar, mentir o actuar más allá
   de sus competencias. **La inexactitud del personaje no es inexactitud de la
   novela.**
6. Si la investigación no permite una conclusión firme, decirlo como
   incertidumbre, nunca como corrección.

Lo verificado se guarda en `biblia/investigacion.md` con su fuente **y con su
vigencia**: los años para los que vale el hallazgo. Un dato sin vigencia en una
novela que cruza dos siglos es una trampa: el telégrafo en Ponce es falso en 1868
y cierto en 1890, y el mismo apunte serviría para equivocarse en los dos
sentidos. Si la vigencia no se puede acotar, se dice.

Cuando varias novelas comparten época y lugar, `investigacion_compartida` en
`pubia.json` apunta a una carpeta común: lo investigado para una sirve para la
siguiente, y no se vuelve a buscar lo mismo.

## 8. Continuidad contra la biblia

Verificar, citando el capítulo que contradice: grafía de nombres y apodos;
rasgos físicos; parentescos y jerarquías; fechas, estaciones, tiempo transcurrido
y edades derivadas; geografía, distancias y qué se ve desde dónde; objetos que un
personaje llevaba, perdió o rompió; heridas y estados; hilos abiertos; registro y
tratamiento de cada personaje con cada interlocutor.

Y sobre todo: **estado de información** — quién sabe qué y desde cuándo. Es el
error de continuidad más frecuente y el más dañino.

Lo objetivo (una grafía, un rango) es rojo; lo interpretativo es azul.

## 9. Estilo y redacción: diagnóstico, no marcas

Los patrones de abajo **no se marcan uno a uno**. Si uno es sistémico en el
capítulo, se escribe **un solo comentario** a nivel de párrafo, con el recuento,
para que el autor decida si le interesa. Si no es sistémico, no se dice nada.

Repetición accidental a corta distancia · verbos comodín (*ser, estar, haber,
hacer, tener, poner*) · filtros narrativos (*vio que, sintió que, se dio cuenta
de que*) · *empezó a / comenzó a* · adverbios en *-mente* acumulados ·
adjetivación por pares · posesivos anglicados (*metió su mano en su bolsillo*) ·
dijo-ismos en cadena · cacofonías y rimas involuntarias · frases que pierden el
sujeto.

Excepción: si la repetición o el patrón es claramente **accidental y chirría**
(el mismo verbo tres veces en dos líneas), un comentario puntual está bien.

## 10. Lo que no se corrige nunca

- La voz del autor y la del narrador.
- Oralidad, dialecto y sociolecto, en diálogo y en narrador si la biblia lo fija.
- Fragmentos sin verbo usados como recurso rítmico.
- Léxico inventado, topónimos y antropónimos de la novela.
- Repetición con función retórica.
- Cualquier sugerencia recogida en `biblia/decisiones.md`.
- La longitud de un capítulo.

## 11. Cuando el autor cuestiona un comentario

- Reconsiderar el pasaje con la explicación aportada.
- Si la intención resuelve el problema, **retirar el comentario explícitamente** y
  anotarlo en `biblia/decisiones.md`. No defenderlo por inercia.
- Diferenciar norma lingüística de preferencia estilística, y decir cuál es cuál.
- No insistir en una alternativa por ser más convencional.
- Ser breve y preciso.
