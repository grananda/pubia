# Plantilla de la biblia

Estructura exacta de cada fichero de `biblia/`. Todo hecho lleva su capítulo.
Lo que no está en el texto no se escribe. Lo deducido se marca `[deducido]`
hasta que el autor lo confirme.

---

## `00-indice.md`

```markdown
# Biblia de «<Novela>»

- Actualizada: 2026-11-09
- Capítulos absorbidos: 1-14
- Fuente: <ruta de sincronización de Scrivener>

| Documento | Huella | Absorbido |
|---|---|---|
| 12-El-regreso | 891b08e1a11e939b | 2026-11-09 |

## La novela en diez líneas
<sinopsis real, no promocional: qué pasa, quién lo provoca, cómo acaba lo que ya está escrito>

## Marco
- Variedad: <español de Puerto Rico; diálogos en ustedes>
- Épocas que abarca: <1866-1873 (caps. 1-14) · 1898-1917 (caps. 15-28)>
- Lugar: <la isla; el cafetal de ...; Ponce; San Juan>
- Punto de vista: <3.ª limitada sobre Marta; cap. 7 y 11 sobre Tomás>
- Tiempo verbal: <pasado>

## Índice
- [Personajes](personajes.md) · [Cronología](cronologia.md) · [Lugares](lugares.md)
- [Tramas](tramas.md) · [Léxico y estilo](lexico-y-estilo.md)
- [Decisiones del autor](decisiones.md) · [Contradicciones](contradicciones.md)

## Cambios de la última pasada
- <una línea por cambio relevante>
```

---

## `personajes.md`

```markdown
## Marta Esteve

- **Nombre exacto**: Marta Esteve. Variantes en el texto: «Marta», «la hija del herrero» (cap. 2).
- **Primera aparición**: cap. 1.
- **Nacimiento**: 1876 [deducido: en el cap. 4 dice tener veinticinco años en la primavera de 1901].
- **Edad por fecha**: 21 en 1897 (cap. 4) · 25 en 1901 (cap. 12).
- **Físico**: manos quemadas de la forja (cap. 1); zurda (cap. 6).
- **Voz y registro**: habla corto; no usa diminutivos; trata de usted al cura y de tú a Tomás (cap. 3).
- **Habla**: dice «quedao», «pa'» y «mi'jo»; nunca «vosotros» (cap. 2, 7). **Formas canónicas, no corregir.**
- **Parentescos**: hija de Ramón Esteve (cap. 1); sin hermanos (cap. 4).
- **Quiere**: recuperar la herrería. **Teme**: volver a Almenara (cap. 12).
- **Objetos propios**: el candil del patio (cap. 12); la carta quemada (cap. 12).
- **Qué sabe y desde cuándo**:
  - Sabe que su padre vendió la herrería — desde cap. 4 (se lo cuenta Tomás).
  - **No** sabe que Tomás firmó la venta — a fecha de cap. 14.
- **Apariciones**: 1, 2, 4, 6, 12, 14.
- **Pendiente de confirmar**: ¿sigue siendo zurda en el cap. 12? Allí sostiene el candil con la derecha.
```

---

## `cronologia.md`

```markdown
# Cronología

## Épocas de la novela
| Época | Años | Capítulos | Marco |
|---|---|---|---|
| colonial | 1866-1873 | 1-14 | gobernadores con facultades omnímodas; Lares 1868; abolición 1873 |
| ocupación | 1898-1917 | 15-28 | administración estadounidense; cambio de moneda; primeros anglicismos |

**Toda escena debe poder fecharse.** Las que no, van listadas al final de este
fichero: son las que impiden juzgar un anacronismo.

## Marco histórico
<qué está pasando en el mundo de la novela en esos años y qué de ello toca a la trama>

## Línea temporal

| Fecha | Capítulo | Qué pasa | Quién está presente |
|---|---|---|---|
| otoño 1897 | cap. 4 (retrospección) | Marta se marcha de Almenara | Marta, Ramón |
| primavera 1901 | cap. 12 | Marta vuelve de noche | Marta |

## Duraciones y saltos
- Entre cap. 11 y 12 pasan tres años y medio (cap. 12 lo llama «tres años»: ver contradicciones).
- Cap. 12 cubre una noche y el amanecer siguiente.

## Edades derivadas
<tabla de edad de cada personaje en cada fecha clave, para detectar imposibles>
```

---

## `lugares.md`

```markdown
## Almenara (pueblo)

- **Primera aparición**: cap. 1.
- **Disposición**: la plaza, el pozo, la higuera, la herrería al norte (cap. 1, 12).
- **Qué se ve desde dónde**: desde el patio se ve la torre del reloj (cap. 12).
- **Distancias y tiempos**: de la estación al pueblo, media hora a pie (cap. 13).
- **Detalles sensoriales comprometidos**: olor a tomillo (cap. 12).
```

---

## `tramas.md`

```markdown
## Hilo: la venta de la herrería

- **Plantado**: cap. 4 (Tomás lo insinúa).
- **Estado**: abierto a fecha de cap. 14.
- **Promesa al lector**: se sabrá quién firmó.
- **Hitos**: cap. 4 insinuación · cap. 12 la carta quemada · cap. 14 ?

## Hilos pendientes de resolver
- El telegrama del cap. 12: nadie vuelve a mencionarlo.

## Promesas cumplidas
- <hilo> → resuelto en cap. N.
```

---

## `lexico-y-estilo.md`

```markdown
# Léxico y estilo

## Variedad y tratamiento
- Variedad: español de Puerto Rico, 1868.
- Diálogos en **ustedes**. No hay «vosotros» salvo en personajes peninsulares
  (el capitán Lamadrid, cap. 9), donde es caracterización y no error.
- Narrador: norma culta sin marcas regionales fuertes.

## Formas orales y dialectales canónicas (NO corregir)
| Forma | Dónde | Quién / vigencia |
|---|---|---|
| quedao, quemao, pasao, cuidao | cap. 2, 7 | narrador y diálogo |
| parquear, mister, lonchar | cap. 19 | diálogo, **solo desde 1898** |
| mi'jo, mi'ja | cap. 7 | don Esteban |
| pa', pa | cap. 7 | todos los peones |
| la Tomasa (artículo ante nombre propio) | cap. 7 | uso del pueblo |
| usté, verdá | cap. 7 | diálogo |

## Léxico regional
- *batey*, *bohío*, *jíbaro*, *chavos*: léxico de la isla. No sustituir por
  equivalentes peninsulares.

## Grafía canónica
| Forma correcta | Variantes vistas en el texto | Nota |
|---|---|---|
| Almenara | «Almenarra» (cap. 9) | corregir la variante |

## Términos propios de la novela
- *candil de patio*: no es un farol; el autor lo usa así desde cap. 1. **No corregir.**

## Convenciones tipográficas de la novela
- Diálogo con raya `—`, sin espacio tras la apertura.
- Pensamiento en cursiva, sin comillas.
- Cifras: años en cifras; cantidades por debajo de cien, en letra.

## Voz del narrador
- 3.ª limitada, pasado, sin juicios del narrador.
- Léxico de época: evitar términos posteriores a 1901 (lista de los ya detectados).
```

---

## `decisiones.md`

```markdown
# Decisiones del autor

Lo que ya se propuso y el autor rechazó. `pubia revisa` no vuelve a marcarlo.

| Fecha | Capítulo | Marca | Qué se propuso | Decisión y motivo |
|---|---|---|---|---|
| 2026-11-09 | 12 | #2 lexico | «enfadado» → «irritado» | Rechazado: el animal sí se personifica, es la mirada de Marta. |

## Reglas permanentes
- No volver a marcar la repetición de «cuello» en el cap. 12: es intencionada.
```

---

## `contradicciones.md`

```markdown
# Contradicciones sin resolver

## C-01 · Tres años o tres años y medio
- **Versión A** (cap. 4): Marta se marcha en otoño de 1897.
- **Versión B** (cap. 12): «hacía tres años que no pisaba Almenara», en primavera de 1901.
- **Imposible**: son tres años y medio, casi cuatro.
- **Detectada**: 2026-11-09, pasada de `pubia revisa` del cap. 12.
- **Decisión del autor**: pendiente.
```

---

## `investigacion.md`

```markdown
# Investigación verificada

Lo que ya se comprobó, con su fuente. Antes de volver a investigar algo, mirar
aquí. Antes de comentar un anacronismo, dejarlo aquí.

## I-01 · Autoridad civil en Puerto Rico, 1868
- **Pregunta**: ¿mandaba el alcalde o el gobernador?
- **Hallazgo**: COMPROBADO. Régimen de gobernadores con facultades omnímodas
  (Ley de 1825); el alcalde no legislaba.
- **Vigencia**: 1825-1898. **No vale para los capítulos de la ocupación.**
- **Fuente**: <referencia concreta: archivo, boletín oficial, bibliografía>
- **Consecuencia en la novela**: la frase del cap. 7 es válida como opinión
  interesada de Esteban, no como afirmación del narrador.
- **Verificado**: 2026-11-09.

## I-02 · Telégrafo en Ponce
- **Hallazgo**: INCERTIDUMBRE REAL **para 1868**. No se ha podido confirmar
  servicio en esa fecha; el desarrollo documentado es posterior.
- **Vigencia del hallazgo**: la duda afecta solo a los capítulos anteriores a
  1880. En los de la ocupación el telégrafo no es problema.
- **Fuente**: <lo consultado y por qué no concluye>
- **Estado**: pendiente de que el autor decida si la trama depende de ello.
```
