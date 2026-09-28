# U02.LAB05 · Paso 4 · Lectura de métricas

Corpus: SMS Spam Collection (`data/raw/dataset.csv`, SHA-256 `c9ca2be9…a022d0`).
Tras eliminar 403 duplicados exactos quedan 5.171 mensajes. Partición estratificada única,
`test_size=0.25`, semilla 42:

| Conjunto | ham | spam | Total |
|---|---|---|---|
| Entrenamiento | 3.388 | 490 | 3.878 |
| Prueba | 1.130 | 163 | 1.293 |

## Resultados en prueba

| Modelo | F1 macro | Accuracy | Precisión spam | Recall spam | Recall ham |
|---|---|---|---|---|---|
| Dummy (baseline) | 0,466 | 0,874 | 0,00 | 0,00 | 1,00 |
| Complement Naive Bayes | 0,926 | 0,970 | 0,96 | 0,80 | 0,99 |
| **Regresión logística** | **0,956** | **0,981** | 0,92 | **0,93** | 0,99 |

Matrices de confusión (filas = real, columnas = predicho):

| Modelo | ham→ham | ham→spam (FP) | spam→ham (FN) | spam→spam |
|---|---|---|---|---|
| Dummy | 1.130 | 0 | 163 | 0 |
| Naive Bayes | 1.124 | 6 | 33 | 130 |
| Regresión logística | 1.117 | 13 | 12 | 151 |

*FP y FN se definen respecto a la clase `spam`.*

## Respuestas a las preguntas del manual

**¿Supera el baseline?** Sí, con amplio margen. El Dummy obtiene 87,4 % de *accuracy*
sin detectar un solo spam (F1 macro 0,466). Naive Bayes sube el F1 macro a 0,926 y la
regresión logística a 0,956. La mejora de la regresión logística sobre Naive Bayes
(+0,030) parece pequeña, pero se concentra en la clase minoritaria: recupera 21 spam más
(FN baja de 33 a 12) a cambio de 7 falsos positivos adicionales (de 6 a 13). Ambos
modelos son lineales sobre la misma matriz TF-IDF, por lo que la mejora no implica mayor
complejidad.

**¿Qué clase se pierde?** `spam`, en ambos modelos. Con regresión logística su recall es
0,93 frente a 0,99 de `ham`: 12 de 163 spam se clasifican como ham (fila `spam` de la
matriz). Con Naive Bayes la pérdida es mayor: 33 de 163 (recall 0,80).

**¿Qué predicción es poco confiable?** La predicción `spam` de la regresión logística
tiene la menor precisión (0,92): de 164 mensajes marcados como spam, 13 eran legítimos
(columna `spam` de la matriz). Naive Bayes es más conservador (precisión 0,96, solo 6 FP),
pero deja pasar casi tres veces más spam.

**¿Existe desbalance?** Sí. El *support* en prueba es 1.130 ham frente a 163 spam
(87,4 % / 12,6 %). Por eso la *accuracy* aislada engaña: el Dummy ya alcanza 0,874 y la
diferencia entre modelos (0,970 vs 0,981) parece mínima, mientras que el recall de spam
revela una diferencia de 13 puntos. Se usan F1 macro y métricas por clase.

**¿Puede generalizar?** Solo dentro del alcance del corpus: SMS en inglés de Reino Unido
y Singapur, recogidos hasta 2011, con ham y spam procedentes de fuentes distintas. No hay
evidencia sobre SMS en español, mensajería actual (WhatsApp, RCS) ni spam moderno
(*phishing* bancario, enlaces acortados). Además, tras la deduplicación exacta quedan 77
casi duplicados (59 de ellos spam, plantillas que solo cambian números), que pueden
aparecer a ambos lados de la partición e inflar ligeramente las métricas de spam.

## Explicación según el modelo del manual

> La regresión logística obtuvo el mejor F1 macro (0,956 frente a 0,926 de Naive Bayes y
> 0,466 del baseline). Sin embargo, la clase **spam** presentó el menor recall (0,93), con
> **12 falsos negativos** de 163. En este contexto ese error implica que **mensajes
> fraudulentos o de cobro premium llegan al usuario como legítimos**; y el error inverso,
> 13 mensajes legítimos marcados como spam, implica **que el usuario puede perder mensajes
> personales**, lo que suele considerarse más grave en un filtro. Por ello proponemos,
> **antes de publicar**: (1) analizar los 25 errores por categoría (paso 6) para ver si
> los falsos positivos comparten un patrón (p. ej. ham que menciona premios, dinero o
> números); (2) evaluar el efecto de los casi duplicados con una partición que los
> agrupe; y (3) presentar la salida como sugerencia ("posible spam") y no como un bloqueo
> automático, dado que el corpus no representa el contexto local ni el spam actual.

# Paso 5 · Matriz de confusión (`reports/confusion_text.png`)

Modelo: regresión logística (el guardado en `models/text_model.joblib`). Filas = clase
real; columnas = clase predicha.

| Real \ Predicho | ham | spam | Total |
|---|---|---|---|
| **ham** | **1.117** | 13 | 1.130 |
| **spam** | 12 | **151** | 163 |

**Diagonal (aciertos por clase).** 1.117 de 1.130 ham (98,8 %) y 151 de 163 spam (92,6 %).
En total 1.268 aciertos de 1.293 (98,1 %). El color oscuro de la celda ham→ham refleja el
desbalance, no un mejor desempeño: la celda spam→spam es clara porque hay pocos spam, no
porque el modelo falle.

**Celda fuera de la diagonal con mayor frecuencia: ham → spam (13 mensajes).** Son mensajes
legítimos que el filtro marcaría como spam. Supera por un solo caso a spam → ham (12), por
lo que ambos errores tienen un peso casi igual y deben analizarse juntos.

**Qué contiene esa celda.** Los 13 falsos positivos comparten vocabulario típico del spam
del corpus: *call*, *free*, *offer*, *text*, *sms*. Se observan tres patrones:

- Peticiones cortas de llamada: "I'm at work. Please call", "I am waiting for your call sir.",
  "Are you free now?can i call now?". Para TF-IDF, *call* y *free* son de los términos
  más asociados a spam ("Call 0871…", "FREE entry").
- Avisos de seguridad legítimos que hablan de fraude: "Please protect yourself from
  e-threats… Never share your password", "Plz note: if anyone calling from a mobile Co. …
  Disconnect the call". Describen una estafa y por eso usan sus mismas palabras.
- Mensajes con etiqueta discutible: "I (Career Tel) have added u as a contact on
  INDYAROCKS.COM to send FREE SMS. To remove from phonebook - sms NO to…" tiene forma de
  publicidad automatizada aunque el corpus lo marca como ham.

**Costo real de la confusión.** En un filtro de SMS, un falso positivo significa que un
mensaje personal o de servicio no llega a la bandeja principal. Los casos observados no son
triviales: una persona que espera una llamada ("waiting for your call"), una notificación
de pago ("[NOMBRE]'s rent has been transfred to ur Acnt") o una alerta de seguridad del
banco. Perder la alerta de seguridad es especialmente costoso, porque justamente protege
al usuario contra el fraude que el filtro intenta evitar. El usuario no ve el error (no
sabe qué mensaje no le llegó), mientras que un spam que se cuela sí lo ve y puede
ignorarlo.

**Error inverso: spam → ham (12 mensajes).** Incluye spam de contenido sexual con número
de tarificación adicional ("Ring [TELÉFONO] now! Costs 20p/min", dos veces) y concursos
("Send A, B or C"). Su costo es económico directo: si el usuario responde o llama, paga
tarifas premium. Varios de estos mensajes están escritos en jerga informal ("wot do i do
next", "L8ER GOT MEGA BILL") que se parece al ham, y al menos uno ("Latest News! Police
station toilet stolen…") es un chiste cuya etiqueta spam es discutible.

**Conclusión del paso.** Los dos errores cuestan cosas distintas: el falso positivo cuesta
mensajes perdidos e invisibles; el falso negativo, dinero y exposición a fraude. Con 13 y
12 casos no hay un sesgo claro hacia uno de ellos, pero el falso positivo es más grave para
un filtro. Esto refuerza la decisión del paso 4 de no usar el modelo para bloquear, sino
para marcar "posible spam" y dejar la decisión final al usuario. La categorización
completa de los 25 errores se hace en el paso 6.

# Paso 6 · Análisis de errores (`reports/error_analysis.csv`)

Se clasificaron los **25 errores** de la regresión logística (13 falsos positivos y 12
falsos negativos). La columna `category` reemplaza el valor `REVISAR` y la columna `note`
justifica cada decisión. No se modificó ninguna predicción ni etiqueta.

| Categoría | ham→spam (FP) | spam→ham (FN) | Total |
|---|---|---|---|
| Ambigüedad (vocabulario compartido con la otra clase) | 9 | 3 | **12** |
| Dialecto (jerga y abreviaturas de SMS) | 0 | 3 | 3 |
| Tema fuera del dominio (spam adulto, subtema poco representado) | 0 | 3 | 3 |
| Texto insuficiente | 2 | 1 | 3 |
| Etiqueta discutible | 2 | 1 | 3 |
| Ironía | 0 | 1 | 1 |
| **Total** | **13** | **12** | **25** |

No se observaron errores por negación.

**Patrón dominante.** La ambigüedad explica casi la mitad de los errores (12/25) y 9 de
los 13 falsos positivos. En todos ellos el mensaje legítimo usa palabras que en el corpus
aparecen sobre todo en spam: *call*, *free*, *offer*, *reply*, *account*. Cuatro son
peticiones de llamada ("Please call", "waiting for your call") y dos son avisos de
seguridad que describen un fraude. El vectorizador solo ve palabras y pares de palabras
(`ngram_range=(1, 2)`), y cada número de teléfono es un token distinto que casi nunca se
repite; así, no distingue bien "call me when you're free" de "FREE entry, call 0871…":
en el spam, *call* suele ir acompañado de un número largo, y ese contexto se pierde.

**Falsos negativos.** Se reparten entre dialecto (3), spam adulto (3) y ambigüedad (3).
El spam que se escapa es el que *no* usa el vocabulario típico de premios y concursos:
está escrito como un mensaje personal ("wot do i do next", "B alone… 2day") o trata un
subtema poco frecuente en el corpus. Dos de los tres spam adultos son casi duplicados
entre sí ("Want explicit SEX in 30 secs?…") y el modelo falló en ambos.

**Etiquetas discutibles (3) e ironía (1).** Una cadena viral de advertencia y un aviso
automatizado de alta en un servicio de SMS están marcados como ham aunque tienen forma de
mensaje masivo, y una queja de un usuario sobre su factura está marcada como spam. Esto
confirma el riesgo de etiquetado documentado en la ficha: parte del error medido no es
error del modelo sino del corpus.

**Hipótesis verificable para el siguiente experimento.** Si los errores se deben a que el
modelo ve palabras aisladas sin su contexto, entonces una representación que capture
estructura del mensaje debería reducir los falsos positivos por ambigüedad sin aumentar
los falsos negativos. Experimentos concretos, comparados con la misma partición y semilla:

1. Sustituir números por marcadores (`<TELÉFONO>`, `<NUM>`) antes de vectorizar, para que
   el modelo aprenda "*call* + número largo" como señal en lugar de *call* sola.
2. Añadir n-gramas de caracteres (`analyzer="char_wb"`), que también deberían ayudar con
   las variantes de dialecto ("wot", "2day", "B").
3. Medir el cambio en los falsos positivos de la categoría ambigüedad, no solo el F1 macro.

# Paso 7 · Pruebas y modelo guardado

| Verificación | Resultado |
|---|---|
| `uv run pytest tests/test_text_model.py -q` | 1 prueba aprobada |
| Carga de `models/text_model.joblib` (1,26 MB) | Correcta; pipeline con pasos `tfidf` y `model`; clases `['ham', 'spam']` |
| `m.predict(['Excelente servicio'])` (comando del manual) | `['ham']` |

**Qué demuestra y qué no.** La prueba entrena los tres pipelines con cuatro frases de
juguete en español y comprueba que cada uno devuelve una predicción y conserva sus pasos
`tfidf` y `model`. Verifica la *estructura* del código, no la calidad del modelo guardado:
no carga `text_model.joblib` ni usa el corpus SMS. La calidad se sostiene con las
métricas, la matriz y el análisis de errores de los pasos 4 a 6.

**Lectura del comando del manual.** "Excelente servicio" está en español, fuera del
idioma del corpus. El modelo responde `ham` con probabilidad de spam 0,21: no reconoce
ninguna de las dos palabras, así que la predicción refleja sobre todo la clase mayoritaria
y no una comprensión del texto. Demuestra que el modelo carga y predice, no que funcione
en español.

Comprobación adicional con frases en inglés (probabilidad de spam entre paréntesis):

| Texto | Predicción |
|---|---|
| Are we still meeting for lunch tomorrow? | ham (0,13) |
| WINNER! You have won a 1000 cash prize. Call now to claim | spam (0,97) |
| Please call me when you are free | **spam (0,71)** |

El tercer caso reproduce fuera del conjunto de prueba el patrón de ambigüedad del paso 6:
una petición de llamada legítima se clasifica como spam por las palabras *call* y *free*.

# Paso 8 · Aplicación local

`uv run streamlit run app/streamlit_app.py` arranca en `http://localhost:8501`, carga
`models/text_model.joblib` y clasifica el texto ingresado. Pruebas realizadas en la
interfaz (la probabilidad de spam se calculó aparte con el mismo modelo, porque la app no
la muestra):

| Tipo de prueba | Texto | Predicción | P(spam) |
|---|---|---|---|
| Claramente de una clase | URGENT! You have won a 2000 cash prize. Call [TELÉFONO] now to claim, only 150p/min | spam | 0,98 |
| Ambigua | Hey, call me when you are free, I have some news about the prize money | ham | 0,49 |
| Fuera del dominio (español) | Felicidades, ganaste un premio de 5000 pesos. Llama ahora al [TELÉFONO] | **ham** | 0,30 |

**Lectura.**
- El texto típico de spam del corpus se reconoce con alta confianza.
- La frase ambigua mezcla una petición personal con *prize money*; el modelo queda
  prácticamente en el umbral (0,49). La etiqueta `ham` que muestra la app oculta que el
  modelo está indeciso.
- El spam en español pasa como `ham`. Del mensaje, el vocabulario del modelo solo reconoce
  "un", "de", "al" y "5000"; no entiende "premio", "ganaste" ni "llama". Es la
  limitación de idioma documentada en la ficha, vista en la aplicación: para un usuario
  dominicano el filtro no ofrece ninguna protección.

**Advertencias de alcance en la interfaz.** La app muestra dos avisos: "Demostración
académica. La predicción no constituye una decisión automática" (bajo el título) e
"Interprete la salida dentro del dominio y las limitaciones del dataset documentado"
(tras cada predicción). Cumplen el requisito de no presentar la etiqueta como verdad,
pero son genéricos: no dicen cuál es el dominio (SMS en inglés, Reino Unido/Singapur,
hasta 2011) ni muestran la confianza de la predicción, por lo que un usuario no sabría
que la frase en español o la ambigua son poco fiables.
