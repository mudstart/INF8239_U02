# INF-8239 · Unidad 02 · Proyecto NLP

Autor académico: Edwin Ramón José Nolasco

Proyecto base para LAB04–LAB06. No sustituya la comprensión por ejecución mecánica.

## Inicio rápido

```bash
cp .env.example .env
uv python install 3.12
uv sync
uv run pytest -q
uv run python scripts/prepare_sms_spam.py
uv run python scripts/audit_data.py
```

`.env.example` ya apunta al corpus aprobado (`data/raw/dataset.csv`); en PowerShell use
`Copy-Item .env.example .env`. El archivo `.env` no se versiona.

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

`train_text.py` regenera `reports/error_analysis.csv` (textos anonimizados) y conserva la
clasificación manual (`category`, `note`) de los errores que ya estaban revisados; los
errores nuevos quedan como `REVISAR`.

## Notebook ejecutado

`notebooks/ejercicio03.ipynb` reúne la evidencia del Ejercicio 03 con salidas y gráficos:
trazabilidad (SHA-256), auditoría, duplicados y prevención de fuga, baseline y dos
pipelines, matrices de confusión y análisis de los 25 errores. Usa el paquete
`inf8239_u02`, no modifica ningún artefacto y comprueba que sus resultados coinciden con
`reports/`. Para reejecutarlo (requiere `data/raw/dataset.csv`):

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/ejercicio03.ipynb
```

## Dependencias

`uv.lock` es la fuente de verdad. `requirements.txt` es su exportación, para entornos sin
uv (`pip install -r requirements.txt`); se regenera con
`uv export --format requirements.txt --no-hashes --output-file requirements.txt`.
`requirements-cloud.txt` (con hashes) es la versión para publicar la app y
`requirements-colab.txt` la mínima para Google Colab.

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

## Resultados y cierre (LAB06 · Embeddings y redes)

```bash
uv run python scripts/embeddings_network.py --word call --network-demo
```

Detalle de los pasos 3 a 8: `reports/lab06_embeddings_redes.md`. Configuración de
Word2Vec: `vector_size=60`, `window=5`, `min_count=5`, `epochs=30`, `seed=42`, `workers=1`.

### Cierre interpretativo

**Resultado de embeddings:** Word2Vec entrenado sobre los 5.574 SMS asocia *call* con el
contexto del spam. Con `min_count=1`, los 10 vecinos más cercanos provenían del spam (6
eran números de teléfono). Con `min_count=5`, queda 1 teléfono y aparecen vecinos
relacionados con llamar (*speak*, *landline*, *ring*, *cal*), aunque persisten términos de
concursos (*quoting*, *match*). Esto confirma desde otra representación el error de
ambigüedad del LAB05, donde "Please call me" se clasificaba como spam.

**Evidencia de cobertura:** con `min_count=1` la cobertura es 1,0 por construcción (todo
token entra al vocabulario), pero el 51 % de los 8.713 términos aparece una sola vez. Con
`min_count=5` el vocabulario baja a 1.858 términos y la cobertura a 0,867: el 13,3 % de
los tokens (teléfonos, códigos, jerga y palabras raras) queda sin vector a cambio de
vecinos más interpretables.

**Resultado estructural de la red:** la red de demostración (club de karate de Zachary)
tiene 34 nodos, 78 aristas no dirigidas y densidad 0,139. El algoritmo detecta 3
comunidades con modularidad 0,411, que separan casi perfectamente las dos facciones reales
del club (2 nodos mal agrupados de 34) pero parten una de ellas en dos.

**Dos métricas comparadas:** grado e intermediación. Los nodos 3 y 31 tienen el mismo
grado (6 conexiones), pero el 31 tiene una intermediación 11 veces mayor (0,138 frente a
0,012), porque une al nodo 0 con otra comunidad, mientras que los vecinos del 3 están en
su propio grupo y conectados entre sí.

**Interpretación permitida:** "El nodo 0 tiene la mayor intermediación (0,438): en
promedio está en el 44 % de los caminos mínimos entre otros nodos, calculado sin pesos".
"*call* y *landline* aparecen en contextos similares en este corpus de SMS".

**Interpretación que NO puede sostenerse:** que el nodo 0 o el 33 sea "la persona más
influyente" o "el líder"; que el nodo 31 "controla la comunicación"; que las comunidades
sean identidades sociales; que *call* y un número de teléfono tengan relación semántica, o
que los vecinos de una palabra valgan fuera de este corpus de SMS en inglés de 2011.

**Siguiente experimento:** entrenar Word2Vec sobre el corpus deduplicado y con los números
sustituidos por un marcador (`<TELÉFONO>`), para comprobar si *call* deja de estar sesgada
por plantillas de spam repetidas y si su vecindario pasa a ser mayoritariamente
conversacional. En la red, recalcular las centralidades usando los pesos (1–7) y comparar
si cambian los nodos con mayor intermediación.

## Uso de herramientas de IA

**Herramienta:** Claude Code (Anthropic), modelo Claude Opus 5.5, en la aplicación de
escritorio de Claude, con acceso al repositorio y a la terminal.

**Uso:** apoyo para revisar el proyecto base frente a los manuales de LAB04 y LAB05,
proponer y escribir código, ejecutar comandos, redactar borradores de documentación y
detectar errores. El estudiante decidió el corpus, aprobó cada cambio, ejecutó los
comandos del manual en su propia terminal para comprobar los resultados y es responsable
de los datos, el código, las referencias y las conclusiones.

**Prompts relevantes** (resumidos):

- "Analízame este folder y dame un reporte."
- "Estas son las indicaciones del trabajo; valida que los pasos se cumplem
- "Crea el script que recomiendas" (descarga y conversión del ZIP de UCI).
- "Haz un doble check en la verificacion."

**Partes elaboradas con apoyo de IA:** `scripts/prepare_sms_spam.py`, la función
`anonymize_text`, `keep_manual_review` y sus pruebas, el aviso de alcance de la app, `notebooks/ejercicio03.ipynb`,
`reports/lab05_lectura_metricas.md`, la clasificación propuesta de los 25 errores y los
borradores del cierre interpretativo y la conclusión.

**Verificaciones realizadas:**

- Los hashes SHA-256 del ZIP y del CSV coinciden con la ficha en varias ejecuciones,
  incluidas copias limpias del repositorio siguiendo solo este README.
- Las métricas (F1 macro 0,466 / 0,926 / 0,956) se reprodujeron en la terminal, en la copia limpia y en el notebook, y coinciden con `reports/text_metrics.csv`.
- Los cinco ejemplos de la ficha se buscaron en el corpus y son únicos.
- Las cifras sobre el corpus incluidas en los reportes se comprobaron contra los datos.

**Correcciones realizadas durante el trabajo:**

- El ejemplo 5 de la ficha no coincidía con el mensaje real (marcador `[TELÉFONO]` donde
  no había número, `L2,000` en lugar de `£2,000`); se corrigió.
- Un ejemplo de la ficha estaba duplicado en el corpus; se sustituyó por uno único.
- `reports/error_analysis.csv` y un reporte contenían teléfonos y un nombre reales; se
  anonimizaron y se añadió `anonymize_text` para que no se repita.
- Reentrenar borró la clasificación de errores; se restauró, se verificó que corresponde
  a los mismos 25 errores del modelo y `train_text.py` ahora la conserva al reentrenar.
- `.env.example` y `.python-version` estaban excluidos por `.gitignore` y `.env.example`
  apuntaba al archivo de demostración, por lo que un clon nuevo no era reproducible; se
  corrigió y se comprobó con una copia limpia.
- Se retiraron afirmaciones de los borradores que no pudieron comprobarse con los datos.

## Interpretación

Toda conclusión debe separar observación, evidencia, interpretación y decisión.