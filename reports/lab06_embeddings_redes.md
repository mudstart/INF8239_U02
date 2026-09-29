# U02.LAB06 · Embeddings y análisis de redes

Corpus: SMS Spam Collection (`data/raw/dataset.csv`, SHA-256 `c9ca2be9…a022d0`), 5.574
mensajes **sin deduplicar** (`embeddings_network.py` usa todas las filas).

## Paso 3 · Word2Vec

Comando: `uv run python scripts/embeddings_network.py --word call`

Configuración del script: `vector_size=60`, `window=5`, `min_count=1`, `epochs=30`,
`seed=42`, `workers=1`. Tokenización: minúsculas y palabras de 2 o más caracteres
alfanuméricos (`\b\w\w+\b`). Modelo guardado en `models/word2vec.model` (4,4 MB).

| Salida | Valor |
|---|---|
| Vocabulario | 8.713 términos |
| Cobertura de tokens | 1,0 (80.452 de 80.452 tokens) |
| Frecuencia de *call* | 593 apariciones |

**Vecinos de *call*** (similitud coseno):

| # | Vecino | Similitud | Tipo |
|---|---|---|---|
| 1 | [TELÉFONO] | 0,75 | número de tarificación adicional |
| 2 | quoting | 0,74 | "call … quoting [código]" |
| 3 | [TELÉFONO] | 0,74 | número |
| 4 | claims | 0,74 | "call to claim" |
| 5 | [TELÉFONO] | 0,73 | número |
| 6 | delivery | 0,72 | "call for delivery" |
| 7 | [TELÉFONO] | 0,72 | número |
| 8 | hava | 0,72 | jerga / error ortográfico |
| 9 | [TELÉFONO] | 0,71 | número |
| 10 | [TELÉFONO] | 0,71 | número |

*Los números de teléfono reales se sustituyeron por `[TELÉFONO]`.*

### Interpretación

**Vocabulario.** 8.713 términos no es pequeño para 5.574 SMS, pero está inflado: 4.404
términos (51 %) aparecen una sola vez y 6.855 (79 %) menos de cinco veces. Incluye 568
tokens numéricos, 253 de ellos con 10 o más dígitos (teléfonos). La jerga de SMS
multiplica las formas de una misma palabra ("later", "l8r").

**Cobertura.** El 1,0 es un resultado *por construcción*, no una evidencia de calidad:
con `min_count=1` todo token entra al vocabulario, así que ninguno queda fuera. El
problema no es la cobertura sino la calidad de los vectores raros: una palabra vista una
sola vez tiene un vector aprendido con un único contexto y es prácticamente ruido.

**Vecinos.** Los diez vecinos de *call* provienen del spam: seis son números de teléfono
y tres son términos de sus plantillas ("quoting", "claims", "delivery"). Word2Vec aprendió
el uso de *call* en el spam ("Call [TELÉFONO] to claim your prize"), aunque *call* aparece
también en muchos mensajes personales ("Sorry, I'll call later" ×30). Esto confirma desde
otra representación el error de ambigüedad del LAB05: en este corpus *call* está asociado
al spam, por eso "Please call me" se clasificaba como spam.

**Vecino extraño: "hava".** Aparece una sola vez en todo el corpus, en un spam: "If you
hava a match please call [TELÉFONO] quoting claim code…". Su vector se aprendió con ese
único contexto, que contiene precisamente *call*, *quoting* y *claim*; por eso queda cerca
de *call*. Es ruido de un error ortográfico, no una relación semántica.

**Similitud alta.** Una similitud de 0,75 entre *call* y un número de teléfono indica que
comparten contextos en *este* corpus, no que sean sinónimos ni que exista una relación
semántica general.

Comprobación adicional (no pedida por el manual):

| Palabra | Frec. | Vecinos más cercanos | Lectura |
|---|---|---|---|
| free | 284 | nokia, colour, ringtone, deliveredtomorrow, [código], tone | Contexto exclusivamente de spam (promociones de móviles y tonos) |
| love | 215 | kiss, miss, clean, jolt, without, heart | Contexto afectivo del ham, con ruido: "jolt" aparece solo 2 veces, ambas en mensajes románticos |
| later | 135 | aight, earlier, rush, brin, drove, tonight | Contexto temporal y conversacional del ham, con jerga ("aight", "brin") |

Las palabras del ham producen vecinos semánticamente coherentes; las del spam agrupan
números y productos. El embedding separa ambos registros, pero también aprende ruido de
mensajes repetidos.

## Paso 4 · Cambio de un parámetro con hipótesis

**Parámetro modificado:** solo `min_count`, de 1 a 5 (`window=5` y el resto sin cambios).

**Hipótesis.** Con `min_count=1`, el 51 % del vocabulario aparece una sola vez, y esos
vectores se aprenden con un único contexto (caso "hava"). Si se exige que una palabra
aparezca al menos 5 veces, desaparecerán los teléfonos únicos y los errores ortográficos,
y los vecinos de *call* serán más palabras y menos números, a costa de cobertura.

| Métrica | `min_count=1` | `min_count=5` |
|---|---|---|
| Vocabulario | 8.713 | 1.858 (−79 %) |
| Cobertura de tokens | 1,000 | 0,867 |
| Teléfonos (≥10 dígitos) en el vocabulario | 253 | 7 |
| Teléfonos entre los 10 vecinos de *call* | 6 | 1 |
| "hava" en el vocabulario | sí | no |

**Vecinos de *call*:**

| # | `min_count=1` | `min_count=5` |
|---|---|---|
| 1 | [TELÉFONO] 0,75 | [TELÉFONO] 0,67 |
| 2 | quoting 0,74 | quoting 0,64 |
| 3 | [TELÉFONO] 0,74 | delivery 0,62 |
| 4 | claims 0,74 | **speak** 0,62 |
| 5 | [TELÉFONO] 0,73 | **landline** 0,62 |
| 6 | delivery 0,72 | **ring** 0,61 |
| 7 | [TELÉFONO] 0,72 | **tells** 0,61 |
| 8 | hava 0,72 | match 0,61 |
| 9 | [TELÉFONO] 0,71 | **cal** 0,59 |
| 10 | [TELÉFONO] 0,71 | matches 0,59 |

**Resultado.** La hipótesis se confirma. Con `min_count=5` aparecen vecinos
semánticamente relacionados con la acción de llamar (*speak*, *landline*, *ring*, *tells*)
y una variante ortográfica frecuente (*cal*). Sigue quedando un teléfono (una plantilla de
spam repetida al menos 5 veces) y términos de concursos (*quoting*, *match*, *matches*),
así que *call* sigue sesgada hacia el spam, pero ahora también refleja su sentido
conversacional. Las similitudes bajan (0,75 → 0,67) porque ya no hay vectores de un solo
contexto que se "peguen" artificialmente a *call*.

Otras palabras: *free* conserva vecinos de spam (nokia, ringtone, unlimited, video);
*later* gana vecinos conversacionales (tonight, meeting, somethin) y pierde ruido
(brin, drove, rush).

**Por qué el cambio modifica el tipo de contexto capturado.** Word2Vec elimina las
palabras poco frecuentes *antes* de construir las ventanas. Con `min_count=5`, los
teléfonos únicos, códigos y errores ortográficos desaparecen de las frases, por lo que
la ventana de 5 posiciones alrededor de *call* se llena con palabras frecuentes. El
modelo deja de aprender la coocurrencia "*call* + número concreto", que es específica de
un mensaje, y aprende contextos recurrentes del idioma ("call me", "speak to", "ring
me"). El costo es que el 13,3 % de los tokens (palabras raras, jerga y números) queda sin
vector.

**Valor seleccionado: `min_count=5`.** Se mantiene en `scripts/embeddings_network.py`
porque produce vecinos más interpretables y elimina vectores aprendidos con un único
contexto. La pérdida de cobertura se acepta: las 6.855 palabras excluidas aparecen menos
de 5 veces cada una (incluyen 246 teléfonos, códigos, jerga y errores ortográficos, pero
también palabras legítimas poco usadas), y sus vectores, aprendidos con 1 a 4 contextos,
no eran fiables. `models/word2vec.model`
corresponde a esta configuración.

## Paso 5 · Red de demostración

Comando: `uv run python scripts/embeddings_network.py --word call --network-demo`

Se añadió al script el cálculo de la densidad (`nx.density`), que el manual espera en la
salida y el script original no imprimía.

### Qué representa la red (antes de interpretar)

Red del club de karate de Zachary (1977), incluida en NetworkX (`nx.karate_club_graph()`).

| Elemento | Definición |
|---|---|
| **Nodo** | Un miembro de un club de karate universitario de EE. UU. (34 personas), identificado solo por un número 0–33 |
| **Arista** | Interacción observada por el investigador **fuera** de las clases del club durante unos dos años (1970–1972); no dirigida |
| **Peso** | Existe (1 a 7, número de contextos de interacción), pero **el script lo ignora**: todas las métricas se calculan sin pesos |
| **Atributo `club`** | Facción a la que se unió cada miembro tras la división del club (instructor "Mr. Hi" u "Officer"); el script no lo usa |

**Información no incluida:** la intensidad real, la frecuencia y el signo (amistad o
conflicto) de la relación; interacciones dentro de las clases; características de las
personas (edad, rango, antigüedad); la evolución en el tiempo (la red es una sola foto
agregada); y la dirección (quién busca a quién). Tampoco hay constancia del
consentimiento de los participantes para este uso; los nodos están anonimizados por
número y así deben mantenerse.

### Resultados

| Salida | Valor |
|---|---|
| Nodos | 34 |
| Aristas | 78 |
| Densidad | 0,139 |
| Comunidades (`greedy_modularity_communities`) | 3 |
| Modularidad | 0,411 |

Archivos generados: `reports/centralities.csv` (grado, intermediación y PageRank de los 34
nodos), `reports/network.png` (visualización coloreada por comunidad) y
`reports/social_network.graphml` (red completa, reutilizable en Gephi u otras
herramientas).

**Lectura.**
- **Densidad 0,139:** existen 78 de las 561 aristas posibles (13,9 %). Es una red dispersa:
  cada miembro se relaciona fuera de clase con unos 4,6 miembros en promedio.
- **Modularidad 0,411:** hay más aristas dentro de las comunidades de las que se
  esperarían al azar; valores por encima de ~0,3 suelen indicar estructura comunitaria
  apreciable. Mide la separación de *esta* partición según *este* algoritmo, no que los
  grupos existan como tales.
- **Comunidades frente a la división real.** Comparando con el atributo `club`:

  | Comunidad | Mr. Hi | Officer |
  |---|---|---|
  | 0 (17 nodos, incluye el 33) | 1 | 16 |
  | 1 (9 nodos) | 8 | 1 |
  | 2 (8 nodos, incluye el 0) | 8 | 0 |

  El algoritmo separa casi perfectamente las dos facciones (2 nodos mal agrupados de 34),
  pero divide el bando de Mr. Hi en dos subgrupos. Esto ilustra que la comunidad es una
  agrupación estructural producida por el algoritmo: coincide con la división social
  aquí, pero el número de grupos (3 frente a 2) lo decide la optimización, no la realidad.

## Paso 6 · Comparación de centralidades

Fuente: `reports/centralities.csv` (métricas sin pesos). Grado normalizado = conexiones /
33.

**Los 7 nodos con mayor grado:**

| Nodo | Comunidad | Conexiones | Grado | Intermediación | PageRank | Rango grado / interm. / PageRank |
|---|---|---|---|---|---|---|
| 33 | 0 | 17 | 0,515 | 0,304 | 0,097 | 1 / 2 / 1 |
| 0 | 2 | 16 | 0,485 | **0,438** | 0,089 | 2 / **1** / 2 |
| 32 | 0 | 12 | 0,364 | 0,145 | 0,076 | 3 / 3 / 3 |
| 2 | 1 | 10 | 0,303 | 0,144 | 0,063 | 4 / 4 / 4 |
| 1 | 1 | 9 | 0,273 | 0,054 | 0,057 | 5 / 7 / 5 |
| 3 | 1 | 6 | 0,182 | **0,012** | 0,037 | 6 / **15** / 8 |
| 31 | 0 | 6 | 0,182 | **0,138** | 0,042 | 6 / **5** / 6 |

Correlación de rangos (Spearman): grado–PageRank 0,94; grado–intermediación 0,91;
intermediación–PageRank 0,84. Las tres métricas coinciden en los extremos, pero se
separan en los nodos intermedios, que es donde aportan información distinta.

### Casos del manual

**Grado alto y betweenness baja → conexiones locales, no conecta regiones.**
Nodo **3**: 6 conexiones, pero intermediación 0,012 (puesto 15). Cinco de sus seis
vecinos (1, 2, 7, 12, 13) están en su misma comunidad y además conectados entre sí, así
que casi ningún camino mínimo necesita pasar por él. El nodo 23 muestra lo mismo: sus 5
vecinos están todos en su comunidad (intermediación 0,018).

**Grado moderado y betweenness alta → posible puente estructural.**
Nodo **31**: tiene exactamente el mismo grado que el nodo 3 (6 conexiones), pero su
intermediación es 11 veces mayor (0,138, puesto 5). La diferencia está en *a quién* se
conecta: une al nodo 0 (comunidad 2) con cinco nodos de la comunidad 0 (24, 25, 28, 32,
33). Es uno de los caminos cortos entre ambos lados de la red. La comparación 3 frente a
31 muestra que el número de conexiones no basta: importa su posición.

**PageRank alto → recibe conexiones de nodos también relevantes.**
Nodo **33** tiene el mayor PageRank (0,097) y el nodo 0 el segundo (0,089). El nodo 33
supera al 0 en PageRank y grado, pero no en intermediación: sus conexiones se concentran
en su propia comunidad, mientras que el nodo 0 conecta las tres (tiene vecinos en las
comunidades 0, 1 y 2). El nodo 23 es un caso intermedio: intermediación baja (puesto 13)
pero PageRank en el puesto 7, porque sus pocos vecinos incluyen a 32 y 33, los nodos más
conectados.

**Comunidad detectada → agrupación según el algoritmo y esta red.**
Las 3 comunidades de `greedy_modularity_communities` (modularidad 0,411) separan casi
perfectamente las dos facciones del club, pero parten una de ellas en dos. No son grupos
de identidad: otro algoritmo (por ejemplo, Louvain) o pequeños cambios en las aristas
podrían dar otra partición.

### Redacción permitida y no permitida

| No escribir | Escribir |
|---|---|
| "El nodo 0 es la persona más influyente." | "El nodo 0 tiene la mayor intermediación (0,438): en promedio, está en el 44 % de los caminos mínimos entre pares de otros nodos, sin considerar pesos." |
| "El nodo 33 es el líder del grupo." | "El nodo 33 tiene el mayor grado (17 conexiones, 0,515) y el mayor PageRank (0,097): es el nodo con más relaciones directas y está conectado a otros nodos muy conectados." |
| "El nodo 31 controla la comunicación entre los grupos." | "El nodo 31 tiene intermediación alta para su grado: une estructuralmente el nodo 0 con la comunidad 0. La red no muestra si esa posición se usó para transmitir información." |
| "El nodo 3 es poco importante." | "El nodo 3 tiene grado medio e intermediación baja: sus relaciones se concentran dentro de su comunidad." |

**Límites.** Las métricas ignoran los pesos (intensidad de 1 a 7), por lo que un contacto
ocasional vale lo mismo que uno frecuente. La red es una foto agregada de dos años sin
dirección: no permite saber quién influyó en quién ni en qué orden. Las centralidades
describen posiciones en el grafo, no roles, poder ni causalidad.

## Paso 8 · Portabilidad

| Comprobación | Estado | Evidencia |
|---|---|---|
| Modelos y reportes en rutas relativas | Cumple | `embeddings_network.py` escribe con `ROOT / "models/..."` y `ROOT / "reports/..."`, donde `ROOT` se calcula desde la ubicación del proyecto; no hay rutas `C:\Users\...` en `src/`, `scripts/`, `app/` ni `tests/` |
| Semilla y `workers=1` | Cumple | `Word2Vec(..., seed=42, workers=1)` y `spring_layout(seed=42)`. La ejecución en PowerShell y en Git Bash produjo exactamente el mismo vocabulario (1.858), cobertura (0,867) y vecinos con las mismas similitudes |
| Documentación de la red | Cumple (red de demostración) | Paso 5: nodos, aristas, dirección (no dirigida), peso (1–7, ignorado por el script), periodo (1970–1972) y consentimiento (sin constancia) |
| Visualización sin identificadores personales | Cumple | `network.png` y `social_network.graphml` identifican a los miembros solo con números 0–33; el único atributo por nodo es la facción (`club`) |

**Límite de la reproducibilidad.** La coincidencia se comprobó en una sola máquina
(Windows, Python 3.12.14, versiones fijadas por `uv.lock`). En otro sistema operativo o
con otras versiones de gensim/NumPy los vectores pueden variar ligeramente. Para
comprobarlo se comparan el vocabulario, la cobertura y los primeros vecinos, no los
bytes de `word2vec.model`.

**Si se usara una red real**, antes de publicar habría que documentar además cómo se
obtuvo cada arista, qué ventana temporal cubre, si hay pesos y dirección, y contar con el
consentimiento de las personas; los nodos se publicarían con identificadores
seudonimizados.
