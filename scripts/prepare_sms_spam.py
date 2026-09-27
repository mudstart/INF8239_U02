"""Descarga SMS Spam Collection (UCI id 228) y la convierte a data/raw/dataset.csv.

Transformaciones (ver docs/DATASET_CARD.md): descomprimir el ZIP oficial, leer
SMSSpamCollection (etiqueta<TAB>mensaje, sin encabezado, sin interpretar comillas),
nombrar las columnas label/text y escribir CSV UTF-8. El contenido no se modifica.
"""

from __future__ import annotations

import argparse
import zipfile

import pandas as pd
import requests

from inf8239_u02.config import ROOT, settings
from inf8239_u02.data import sha256

ZIP_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
ZIP_PATH = ROOT / "data/raw/sms_spam_collection.zip"
MEMBER = "SMSSpamCollection"


def download(force: bool) -> None:
    if ZIP_PATH.exists() and not force:
        print(f"ZIP existente, se reutiliza: {ZIP_PATH.relative_to(ROOT)}")
        return
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(ZIP_URL, timeout=60)
    response.raise_for_status()
    ZIP_PATH.write_bytes(response.content)
    print(f"Descargado: {ZIP_URL}")


def convert() -> pd.DataFrame:
    with zipfile.ZipFile(ZIP_PATH) as archive:
        raw = archive.read(MEMBER).decode("utf-8")
    rows = [line.split("\t", 1) for line in raw.splitlines() if line]
    return pd.DataFrame(rows, columns=["label", "text"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Volver a descargar el ZIP")
    args = parser.parse_args()
    download(args.force)
    df = convert()
    output = settings.dataset_path
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False, encoding="utf-8")
    print(f"SHA-256 ZIP: {sha256(ZIP_PATH)}")
    print(f"Guardado: {output.relative_to(ROOT)} · filas={len(df)}")
    print(f"SHA-256 CSV: {sha256(output)}")


if __name__ == "__main__":
    main()
