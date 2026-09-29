import pandas as pd
import pytest

from inf8239_u02.data import anonymize_text, validate_dataframe


def test_accepts_valid_dataframe():
    df = pd.DataFrame({"text": ["uno", "dos"], "label": ["a", "b"]})
    validate_dataframe(df, "text", "label")


def test_rejects_missing_target():
    df = pd.DataFrame({"text": ["uno"]})
    with pytest.raises(ValueError, match="Faltan columnas"):
        validate_dataframe(df, "text", "label")


def test_rejects_empty_text():
    df = pd.DataFrame({"text": [""], "label": ["a"]})
    with pytest.raises(ValueError, match="textos vacíos"):
        validate_dataframe(df, "text", "label")


def test_anonymize_text_replaces_phone_numbers_only():
    text = "Call 09061701461 or 0871-872-9755 before 02/09/03, code 84484, win £2,000"
    assert anonymize_text(text) == (
        "Call [TELÉFONO] or [TELÉFONO] before 02/09/03, code 84484, win £2,000"
    )