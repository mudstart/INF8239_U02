# INF-8239 · Unidad 02 · Proyecto NLP

Autor académico: Edwin Ramón José Nolasco

Proyecto base para LAB04–LAB06. No sustituya la comprensión por ejecución mecánica.

## Inicio rápido

```bash
uv python install 3.12
uv sync
uv run pytest -q
uv run python scripts/prepare_sms_spam.py
uv run python scripts/audit_data.py
```

Copie `.env.example` como `.env` y configure el dataset aprobado.

## Dataset

Corpus seleccionado: **SMS Spam Collection** (UCI id 228, CC BY 4.0). Los datos no se versionan;
para obtenerlos y verificarlos (LAB04, paso 6):

```bash
uv run python scripts/prepare_sms_spam.py
uv run python scripts/download_data.py
uv run python scripts/audit_data.py
```

| Script | Qué hace | Salida clave |
|---|---|---|
| `prepare_sms_spam.py` | Descarga el ZIP oficial de UCI y lo convierte a `data/raw/dataset.csv` (`label`, `text`) | SHA-256 del ZIP y del CSV |
| `download_data.py` | Con `DATA_SOURCE=local` solo confirma la ruta configurada; no descarga, porque UCI publica un ZIP y no un CSV directo | Ruta del dataset |
| `audit_data.py` | Audita el CSV | SHA-256 del CSV, filas, nulos, duplicados, clases y longitudes |

Los hashes deben coincidir con los registrados en `docs/DATASET_CARD.md`; si difieren, la fuente
cambió. La ficha, el diccionario, la licencia y el procedimiento completo están en
`docs/DATASET_CARD.md`.
El archivo `data/sample/demo_text.csv` solamente comprueba la arquitectura.

## Alcance del modelo

> **El modelo solo funciona con SMS en inglés.** Está entrenado con SMS Spam Collection:
> mensajes de Reino Unido y Singapur recogidos hasta 2011 y etiquetados como `ham`
> (legítimo) o `spam`.

Quien replique el proyecto debe tener en cuenta que:

- **No sirve para español ni para otros idiomas.** Con un spam en español
  ("Felicidades, ganaste un premio… Llama ahora") el modelo predice `ham`, porque de ese
  texto solo reconoce palabras como "un", "de" y "al". Para usarlo en República Dominicana
  u otro contexto hispanohablante hay que reentrenarlo con un corpus en español.
- **No cubre otros canales ni el spam actual:** WhatsApp, RCS, correo, *phishing*
  bancario, enlaces acortados o estafas de paquetería no están representados.
- **Los resultados son válidos solo para este corpus.** F1 macro 0,956 en la partición de
  prueba (regresión logística); las métricas completas y el análisis de errores están en
  `reports/lab05_lectura_metricas.md`.
- **La predicción no es una decisión.** Debe presentarse como "posible spam", no usarse
  para bloquear mensajes. Límites y usos prohibidos: `docs/DATASET_CARD.md`.

## Entrenamiento

```bash
uv run python scripts/train_text.py
uv run streamlit run app/streamlit_app.py
```

## Resultados y conclusión (LAB05)

Detalle de métricas, matriz de confusión y análisis de errores: `reports/lab05_lectura_metricas.md` y `reports/error_analysis.csv`.

### Cierre interpretativo

**Resultado principal:** la regresión logística sobre TF-IDF (unigramas y bigramas)
clasifica SMS en inglés como `ham` o `spam` con F1 macro 0,956 en la partición de prueba
(1.293 mensajes), frente a 0,926 de Complement Naive Bayes y 0,466 del baseline.

**Modelo seleccionado y evidencia:** regresión logística. Supera al baseline por 0,49 de
F1 macro y a Naive Bayes por 0,030; la mejora se concentra en la clase minoritaria:
recall de spam 0,93 frente a 0,80 (12 falsos negativos frente a 33), a cambio de 7
falsos positivos más (13 frente a 6). Ambos modelos son lineales, así que la mejora no
añade complejidad.

**Clase con mayor dificultad:** `spam`, con recall 0,93 frente a 0,99 de `ham` y la menor
precisión (0,92): de 164 mensajes marcados como spam, 13 eran legítimos.

**Tipo de error más frecuente:** ambigüedad por vocabulario compartido (12 de 25 errores y
9 de los 13 falsos positivos). Mensajes legítimos con *call*, *free*, *offer* o
*account* se confunden con spam; también fallan avisos de seguridad que describen un
fraude.

**Impacto en el contexto:** un falso positivo hace que el usuario pierda un mensaje
personal, un aviso de pago o una alerta de seguridad sin enterarse; un falso negativo lo
expone a llamadas o respuestas con tarificación adicional. En un filtro, el primero es
más grave porque es invisible.

**Limitación del dataset:** SMS en inglés de Reino Unido y Singapur recogidos hasta 2011,
con ham y spam procedentes de fuentes distintas. No representa el español ni el spam
actual: un spam en español se clasificó como `ham`. Además, 77 casi duplicados y 3
etiquetas discutibles pueden inflar o distorsionar las métricas.

**Decisión antes del despliegue:** publicar solo como demostración académica, con
advertencia explícita de alcance (implementada en la app y el README), presentando la
salida como "posible spam" y nunca como bloqueo. No usarlo con usuarios reales sin
reentrenarlo con SMS en español y del contexto local.

---

### Conclusión

Este laboratorio partió del corpus SMS Spam Collection auditado en LAB04: 5.574 mensajes,
sin nulos, con 403 duplicados exactos y un desbalance de 86,6 % ham frente a 13,4 % spam.
Tras eliminar los duplicados antes de dividir los datos, quedaron 5.171 mensajes, y se
entrenaron tres pipelines con una única partición estratificada y semilla 42.

El baseline mostró por qué la *accuracy* no basta: al predecir siempre `ham` obtuvo 87,4 %
de *accuracy* sin detectar un solo spam, con F1 macro 0,466. Complement Naive Bayes subió
el F1 macro a 0,926 y la regresión logística a 0,956. La diferencia entre ambos modelos
parece pequeña, pero no lo es en la clase que importa: la regresión logística recupera el
93 % del spam frente al 80 % de Naive Bayes, es decir, 21 mensajes fraudulentos menos que
llegan al usuario, a cambio de 7 falsas alarmas adicionales. Por eso se seleccionó.

La matriz de confusión muestra 13 mensajes legítimos marcados como spam y 12 spam que
pasaron como legítimos. El análisis de los 25 errores explica su origen. La categoría
dominante es la ambigüedad: 9 de los 13 falsos positivos son mensajes personales que usan
palabras como *call* o *free*, muy frecuentes en el spam del corpus. El modelo no ve el
contexto: en el spam, *call* suele ir seguido de un número de tarificación adicional,
pero cada número es un token distinto y esa combinación no se aprende. Los falsos
negativos, en cambio, corresponden a spam escrito como un mensaje informal, con jerga de
SMS, o a subtemas poco representados como el contenido adulto. Tres errores tienen
etiquetas discutibles, lo que recuerda que parte del error medido pertenece al corpus y
no al modelo.

Estos errores tienen costos distintos. Un falso negativo expone al usuario a gastos por
llamadas premium, pero lo ve y puede ignorarlo. Un falso positivo es invisible: el
usuario no sabe qué mensaje no le llegó. Entre los casos observados hay una alerta de
seguridad bancaria, justamente el tipo de mensaje que protege contra el fraude que el
filtro intenta evitar.

La principal limitación es el alcance. El corpus contiene SMS en inglés de Reino Unido y
Singapur hasta 2011. En la aplicación, un spam en español se clasificó como `ham` porque
el modelo solo reconoció palabras como "un" y "de". Tampoco representa WhatsApp, el
*phishing* bancario actual ni el contexto dominicano. Además, 77 casi duplicados, sobre
todo plantillas de spam que solo cambian el número, pueden aparecer en entrenamiento y
prueba e inflar ligeramente el recall de spam.

La decisión es publicar el modelo únicamente como demostración académica, con la
advertencia de que solo funciona con SMS en inglés, y presentar su salida como
sugerencia, no como bloqueo. La hipótesis para el siguiente experimento es verificable:
sustituir los números por marcadores y añadir n-gramas de caracteres debería reducir los
falsos positivos por ambigüedad sin aumentar los falsos negativos. Se comprobará con la
misma partición y midiendo esa categoría de error, no solo el F1 macro.

## Interpretación

Toda conclusión debe separar observación, evidencia, interpretación y decisión.
