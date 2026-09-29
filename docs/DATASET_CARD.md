# Dataset Card

## Identificación
- Nombre: SMS Spam Collection
- Fuente original: UCI Machine Learning Repository — https://archive.ics.uci.edu/dataset/228/sms+spam+collection (descarga: https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip)
- Responsable: Tiago A. Almeida y José María Gómez Hidalgo (creadores); publicado y mantenido por UCI Machine Learning Repository
- Versión o fecha: versión única publicada en UCI, donada el 21/06/2012; DOI 10.24432/C5CC84. Hash SHA-256 del ZIP descargado: `1587ea43e58e82b14ff1f5425c88e17f8496bfcdb67a583dbff9eefaf9963ce3`; del CSV generado (`data/raw/dataset.csv`): `c9ca2be9b60921499e30de05a0350c9bee1ba7cfc98bc03d1547819938a022d0` (obtenidos el 27/09/2026 con `scripts/prepare_sms_spam.py`)
- Licencia: Creative Commons Attribution 4.0 International (CC BY 4.0). Permite descargar, analizar, adaptar y publicar resultados derivados con atribución.
- Idioma: inglés (variantes de Reino Unido y Singapur, con abundante jerga y abreviaturas de SMS)

Cita requerida: Almeida, T. & Hidalgo, J. (2011). *SMS Spam Collection* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CC84

## Propósito y variable objetivo
**Uso previsto:** entrenar y evaluar modelos de clasificación de texto (TF-IDF + Naive Bayes y modelo lineal en U02.LAB05) que distingan mensajes SMS legítimos de spam, con fines exclusivamente académicos.

**Pregunta:** ¿puede el contenido textual de un SMS predecir si es spam?

**Variable objetivo:** `label`, binaria:
- `ham`: mensaje legítimo.
- `spam`: mensaje comercial no solicitado o fraudulento.

**Unidad de análisis:** un mensaje SMS.

## Diccionario de datos

Archivo original `SMSSpamCollection`: texto plano, una línea por mensaje, separado por tabulador, **sin encabezado** (`etiqueta<TAB>mensaje`). Se convierte a `data/raw/dataset.csv` con las siguientes columnas:

| Columna | Tipo | Descripción | Valores o unidad |
|---|---|---|---|
| `label` | string (categórica) | Clase asignada al mensaje por los autores del corpus | `ham`, `spam` |
| `text` | string | Contenido crudo del SMS, sin normalizar (mayúsculas, signos, números y abreviaturas originales) | Texto libre; longitud en caracteres |

**Ejemplos anonimizados** (los números telefónicos, nombres y códigos se sustituyen por marcadores):

| label | text |
|---|---|
| ham | Lol your always so convincing. |
| ham | Ok lar... Joking wif u oni... |
| ham | [NOMBRE] is in hostel aha:-. |
| spam | Sunshine Quiz! Win a super Sony DVD recorder if you canname the capital of Australia? Text [CÓDIGO] to [NÚMERO]. |
| spam | URGENT! Your Mobile No was awarded a £2,000 Bonus Caller Prize on [FECHA]! This is our 2nd attempt to contact YOU! Call [TELÉFONO] [CÓDIGO] BT National Rate |

**Transformaciones realizadas:** (1) descompresión del ZIP oficial; (2) lectura del archivo separado por tabulador sin interpretar comillas; (3) asignación de nombres de columna `label` y `text`; (4) escritura como CSV UTF-8. No se modifica el contenido de los mensajes. `data/raw/` no se edita manualmente.

## Procedimiento de obtención
1. Configurar `.env`: `DATA_SOURCE=local`, `DATASET_PATH=data/raw/dataset.csv`, `TEXT_COLUMN=text`, `TARGET_COLUMN=label`.
2. Ejecutar `uv run python scripts/prepare_sms_spam.py`: descarga el ZIP oficial de UCI a `data/raw/sms_spam_collection.zip`, convierte `SMSSpamCollection` a `data/raw/dataset.csv` con las transformaciones descritas e imprime el SHA-256 del ZIP y del CSV. Si el ZIP ya existe se reutiliza; `--force` vuelve a descargarlo.
3. Comparar los hashes con los registrados en la sección Identificación; si difieren, la fuente cambió.
4. Ejecutar `uv run python scripts/download_data.py` (en modo `local` solo confirma la ruta configurada).
5. Ejecutar `uv run python scripts/audit_data.py` y copiar los resultados en la sección siguiente.
6. Los datos no se suben a Git (`data/raw/*` está en `.gitignore`); el README explica cómo obtenerlos.

**Composición según la documentación de la fuente:**

| Origen | ham | spam |
|---|---|---|
| Foro Grumbletext (Reino Unido), extracción manual | — | 425 |
| NUS SMS Corpus (Universidad Nacional de Singapur), muestra aleatoria | 3.375 | — |
| Tesis doctoral de Caroline Tagg | 450 | — |
| SMS Spam Corpus v.0.1 Big (Gómez Hidalgo) | 1.002 | 322 |
| **Total** | **4.827** | **747** |

## Calidad observada
Según la fuente: 5.574 registros, sin valores faltantes; los mensajes no están ordenados cronológicamente.

Resultados de `audit_data.py` (ejecutado el 27/09/2026 sobre el CSV con SHA-256 `c9ca2be9…a022d0`):

| Indicador | Valor |
|---|---|
| Filas / columnas | 5.574 / 2 |
| Nulos en `text` / `label` | 0 / 0 |
| Textos duplicados exactos | 403 (309 ham, 94 spam); ninguno con etiquetas contradictorias |
| Distribución de clases | ham 86,60 % (4.827) / spam 13,40 % (747) |
| Longitud p50 / p90 / p99 (caracteres) | 62 / 156 / 276 (mín. 2, máx. 910, media 80,5) |

Verificaciones complementarias: tras eliminar duplicados quedan 5.171 mensajes (ham 87,37 % / spam 12,63 %); mediana de longitud ham 52 vs. spam 149 caracteres; 12 mensajes de 3 caracteres o menos (p. ej. "Ok", "Okie").

**Interpretación:**
- **Desbalance:** un clasificador que siempre prediga `ham` obtendría ≈ 86,6 % de *accuracy*. Por eso se reportarán precisión, recall y F1 de la clase `spam`, y se usará partición estratificada.
- **Duplicados:** el 7,2 % de las filas repite un texto ya presente. Los más frecuentes son respuestas automáticas ("Sorry, I'll call later" ×30) y cadenas de spam. Deben eliminarse antes de dividir en entrenamiento y prueba para evitar fuga de información; `train_text.py` ya aplica `drop_duplicates` sobre `text`. Al no haber conflictos de etiqueta, eliminar duplicados no introduce ambigüedad.
- **Longitud:** el spam triplica la mediana del ham, por lo que la longitud es una señal fuerte y un posible atajo del modelo. No hay textos vacíos, pero sí mensajes muy cortos poco informativos.
- **Codificación:** algunos mensajes conservan entidades HTML sin decodificar (`&amp;`, `&lt;`). Se mantienen en `data/raw/`; cualquier normalización se hará en `data/processed/` y se documentará.

## Población cubierta y excluida
**Cubierta:** SMS en inglés de usuarios de Reino Unido (spam denunciado en un foro público) y de Singapur (mayoritariamente estudiantes universitarios que donaron sus mensajes de forma voluntaria), además de mensajes de corpus académicos previos. Periodo aproximado: hasta 2011.

**Excluida:**
- Otros idiomas, incluido el español, y otros países (no hay SMS de República Dominicana ni de Latinoamérica).
- Mensajería actual (WhatsApp, RCS, iMessage) y spam moderno: *phishing* bancario, enlaces acortados, estafas de paquetería, OTP falsos.
- Grupos de edad y perfiles socioeconómicos distintos de estudiantes universitarios, en la parte legítima.

## Riesgos, sesgos y usos prohibidos
**Riesgos**
- **Información personal:** algunos mensajes contienen números telefónicos, nombres propios y detalles de la vida privada. No se publican ejemplos sin anonimizar. `train_text.py` aplica `anonymize_text` (`src/inf8239_u02/data.py`) al escribir `reports/error_analysis.csv`, sustituyendo los números de 10 o más dígitos por `[TELÉFONO]`; los nombres propios no se detectan automáticamente y se revisan a mano (`[NOMBRE]`). Limitación: los vocabularios de `models/text_model.joblib` y `models/word2vec.model` conservan como tokens algunos números telefónicos del corpus (sin el mensaje asociado); eliminarlos exige reentrenar con los números sustituidos por un marcador.
- **Contenido ofensivo:** puede haber lenguaje vulgar o de contenido sexual, sobre todo en el spam.

**Sesgos previsibles**
- **Sesgo de origen:** ham y spam provienen de fuentes distintas (Singapur vs. Reino Unido). El modelo podría aprender diferencias de dialecto y de fuente, no de "spam", y sobrestimar su desempeño real.
- **Sesgo temporal:** el vocabulario del spam de 2012 (premios, tonos, concursos por SMS) difiere del spam actual.
- **Sesgo de selección:** el spam fue denunciado por usuarios; el spam que nadie reportó no está representado.

**Usos prohibidos**
- Desplegar el modelo para filtrar mensajes reales de usuarios sin revalidarlo con datos actuales y del contexto local.
- Intentar reidentificar a las personas que enviaron o recibieron los mensajes.
- Extraer o reutilizar números telefónicos del corpus.
- Generar mensajes de spam o evaluar técnicas para evadir filtros.

## Selección frente a la alternativa
Se comparó con **YouTube Spam Collection** (UCI id 380, CC BY 4.0, DOI 10.24432/C58885). Ambos tienen licencia clara, pero se descartó porque:
- Tiene solo 1.956 comentarios, procedentes de apenas 5 videos musicales (Psy, Katy Perry, LMFAO, Eminem y Shakira), por lo que su representatividad es muy estrecha.
- Incluye las columnas `AUTHOR` y `COMMENT_ID`, que identifican a usuarios y aumentan el riesgo de privacidad.
- Sus datos están repartidos en cinco CSV que hay que unir, lo que añade un paso de preparación.

SMS Spam Collection ofrece casi tres veces más observaciones, una única fuente versionada y una etiqueta equivalente, por lo que se aprueba.
