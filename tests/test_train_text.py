import pandas as pd

from scripts.train_text import keep_manual_review


def test_keep_manual_review_preserves_classification_and_names(tmp_path):
    path = tmp_path / "error_analysis.csv"
    pd.DataFrame({
        "text": ["Hi [NOMBRE]'s rent is paid", "Call me later"],
        "real": ["ham", "ham"],
        "predicted": ["spam", "spam"],
        "category": ["ambigüedad", "texto insuficiente"],
        "note": ["dinero", "corto"],
    }).to_csv(path, index=False)
    errors = pd.DataFrame({
        "text": ["Hi Ana's rent is paid", "Win a prize now"],
        "real": ["ham", "spam"],
        "predicted": ["spam", "ham"],
    })
    result = keep_manual_review(errors, path)
    assert result["text"].tolist() == ["Hi [NOMBRE]'s rent is paid", "Win a prize now"]
    assert result["category"].tolist() == ["ambigüedad", "REVISAR"]


def test_keep_manual_review_without_previous_file(tmp_path):
    errors = pd.DataFrame({"text": ["x"], "real": ["ham"], "predicted": ["spam"]})
    result = keep_manual_review(errors, tmp_path / "missing.csv")
    assert result["category"].tolist() == ["REVISAR"]
