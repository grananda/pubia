# Roadmap de features — pubia

Backlog vivo del marketplace y del plugin `pubia`. Cada entrada se registra aquí cuando surge la idea y se marca cuando se implementa. No es el roadmap de una novela: es el del propio producto.

Estados: `propuesta` → `aceptada` → `implementada` (con versión y commit) / `descartada` (con motivo).

| # | Feature | Skill(s) | Estado | Añadida | Versión |
|---|---------|----------|--------|---------|---------|
| F-01 | Lectura del manuscrito desde la carpeta de sincronización de Scrivener (RTF, TXT, MD) con orden del binder y huella SHA-256 | pubia-revisa | **implementada** | 2026-11-09 | 0.2.0 |
| F-02 | `.docx` anotado con comentarios OOXML reales al margen y correcciones en rojo tachado, construido desde el texto extraído y nunca desde prosa reescrita | pubia-revisa | **implementada** | 2026-11-09 | 0.2.0 |
| F-03 | Biblia de la novela en Markdown: personajes, cronología, lugares, tramas, léxico, con cada hecho acompañado de su capítulo | pubia-biblia | **implementada** | 2026-11-09 | 0.2.0 |
| F-04 | Ciclo de decisiones: lo que el autor rechaza se convierte en regla permanente y no se vuelve a marcar | pubia-decisiones | **implementada** | 2026-11-09 | 0.2.0 |
| F-05 | Auditoría transversal de la obra completa: cronología, estado de información, cabos sueltos, derivas de nombres y de habla | pubia-continuidad | **implementada** | 2026-11-09 | 0.2.0 |
| F-06 | Doctrina de corrección conservadora: principio rector, umbral del rojo y del azul, oralidad que no se normaliza | pubia-revisa | **implementada** | 2026-11-09 | 0.2.0 |
| F-07 | Variedad del español y tratamiento: caza la fuga de `vosotros` donde la novela pide `ustedes`, con sus falsos positivos | pubia-revisa, pubia-setup | **implementada** | 2026-11-09 | 0.2.0 |
| F-08 | Guardarraíl por código: el generador rechaza una corrección en rojo cuya categoría sea una preferencia de estilo | pubia-revisa | **implementada** | 2026-11-09 | 0.2.0 |
| F-09 | Protocolo de investigación con fuentes y etiqueta del hallazgo (comprobado / incertidumbre / plausible / licencia) | pubia-revisa | **implementada** | 2026-11-09 | 0.2.0 |
| F-10 | Impresión como lector al final del `.docx`, declarada ajena a la corrección | pubia-revisa | **implementada** | 2026-11-09 | 0.2.0 |
| F-11 | La época es propiedad de la escena y no de la novela: `epocas` como lista y vigencia por hallazgo | pubia-revisa, pubia-biblia | **implementada** | 2026-11-09 | 0.2.0 |
| F-12 | Diagrama autónomo del funcionamiento del marketplace en `docs/` | marketplace | **implementada** | 2026-11-10 | 0.2.1 |
| F-13 | Versión global, CI de validación y release idempotente por `VERSION` | marketplace | **implementada** | 2026-11-10 | 0.2.1 |
| F-14 | Notas de release con lo que rompe primero, portadas de aidd-marketplace, y comprobación de versión en los dos sentidos | marketplace | **implementada** | 2026-11-10 | 0.2.1 |
| F-15 | `pubia publica`: subir el `.docx` a Drive convertido, para leer la revisión fuera del escritorio o pasarla a un corrector humano | marketplace | propuesta | 2026-11-09 | — |
| F-16 | Informe HTML de la revisión como alternativa al `.docx`, con aceptar/rechazar por marca y sin salir de la máquina | pubia-revisa | propuesta | 2026-11-09 | — |
| F-17 | Investigación compartida entre novelas de la misma época mediante `investigacion_compartida` | pubia-revisa, pubia-biblia | propuesta | 2026-11-10 | — |
| F-18 | Diagrama del ciclo en Mermaid dentro del `README.md`, versionado junto al código | marketplace | **implementada** | 2026-11-10 | 0.2.2 |