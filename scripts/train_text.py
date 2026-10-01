from __future__ import annotations

import re
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, f1_score
from sklearn.model_selection import train_test_split

from inf8239_u02.config import ROOT, settings
from inf8239_u02.data import anonymize_text, load_dataset, validate_dataframe
from inf8239_u02.modeling import build_models


def keep_manual_review(errors: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Conserva la clasificación manual (y los [NOMBRE] puestos a mano) de errores repetidos."""
    errors = errors.assign(category="REVISAR")
    if not path.exists():
        return errors
    previous = pd.read_csv(path)
    rows = []
    for row in errors.to_dict("records"):
        for old in previous.to_dict("records"):
            pattern = re.escape(str(old["text"])).replace(re.escape("[NOMBRE]"), r"\w+")
            same = old["real"] == row["real"] and old["predicted"] == row["predicted"]
            if same and re.fullmatch(pattern, row["text"]):
                row = old
                break
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    df = load_dataset().dropna(subset=[settings.text_column, settings.target_column])
    df = df.drop_duplicates(subset=[settings.text_column])
    validate_dataframe(df, settings.text_column, settings.target_column)
    counts = df[settings.target_column].value_counts()
    stratify = df[settings.target_column] if counts.min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        df[settings.text_column], df[settings.target_column], test_size=0.25,
        random_state=settings.random_state, stratify=stratify,
    )
    models = build_models(settings.random_state)
    rows = []
    predictions = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        predictions[name] = pred
        score = f1_score(y_test, pred, average="macro")
        rows.append({"model": name, "f1_macro": score})
        print(f"\n{name} · F1 macro={score:.3f}")
        print(classification_report(y_test, pred, zero_division=0))
    reports = ROOT / "reports"
    models_dir = ROOT / "models"
    reports.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    pd.DataFrame(rows).sort_values("f1_macro", ascending=False).to_csv(reports / "text_metrics.csv", index=False)
    selected = models["logistic"]
    selected_pred = predictions["logistic"]
    ConfusionMatrixDisplay.from_predictions(y_test, selected_pred, xticks_rotation=45, cmap="Blues")
    plt.tight_layout()
    plt.savefig(reports / "confusion_text.png", dpi=170)
    errors = pd.DataFrame({"text": x_test, "real": y_test, "predicted": selected_pred})
    errors = errors[errors["real"] != errors["predicted"]].copy()
    errors["text"] = errors["text"].map(anonymize_text)
    errors_path = reports / "error_analysis.csv"
    errors = keep_manual_review(errors, errors_path)
    errors.to_csv(errors_path, index=False)
    print(f"Errores: {len(errors)} · pendientes de clasificar: {(errors['category'] == 'REVISAR').sum()}")
    joblib.dump(selected, models_dir / "text_model.joblib")
    print("\nArtefactos guardados en reports/ y models/")


if __name__ == "__main__":
    main()
