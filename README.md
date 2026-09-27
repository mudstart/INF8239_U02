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

## Entrenamiento

```bash
uv run python scripts/train_text.py
uv run streamlit run app/streamlit_app.py
```

## Interpretación

Toda conclusión debe separar observación, evidencia, interpretación y decisión.
