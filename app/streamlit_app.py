from pathlib import Path

import joblib
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models/text_model.joblib"

st.title("INF-8239 · Clasificador de texto")
st.caption("Demostración académica. La predicción no constituye una decisión automática.")
st.warning(
    "Alcance: modelo entrenado con SMS Spam Collection (UCI), mensajes SMS **en inglés** "
    "de Reino Unido y Singapur recogidos hasta 2011. Solo clasifica SMS en inglés como "
    "`ham` o `spam`; con textos en otro idioma (incluido el español) o de otro tipo, "
    "la predicción no es fiable."
)

if not MODEL_PATH.exists():
    st.error("No existe el modelo. Ejecute: uv run python scripts/train_text.py")
    st.stop()

model = joblib.load(MODEL_PATH)
text = st.text_area("Texto para clasificar")
if st.button("Clasificar"):
    if not text.strip():
        st.warning("Ingrese un texto.")
    else:
        prediction = model.predict([text])[0]
        st.metric("Clase predicha", str(prediction))
        st.info("Interprete la salida dentro del dominio y las limitaciones del dataset documentado.")
