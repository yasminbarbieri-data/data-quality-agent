from io import BytesIO
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from app import filter_issues, to_csv_bytes


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_filter_issues_combines_rule_column_and_text_filters():
    issues = pd.DataFrame({
        "Linha do arquivo": [2, 3, 4],
        "Coluna": ["preco", "categoria", "preco"],
        "Regra": ["R03", "R05", "R03"],
        "Valor encontrado": ["-10", "Eletronicos", "0"],
        "Descrição": [
            "O preço deve ser maior que zero.",
            "A categoria não pertence à lista permitida.",
            "O preço deve ser maior que zero.",
        ],
    })

    result = filter_issues(issues, ["R03"], ["preco"], "-10")

    assert result["Linha do arquivo"].tolist() == [2]


def test_to_csv_bytes_preserves_columns_and_content():
    dataframe = pd.DataFrame({"Regra": ["R03"], "Coluna": ["preco"]})

    result = pd.read_csv(BytesIO(to_csv_bytes(dataframe)))

    assert result.to_dict("records") == [{"Regra": "R03", "Coluna": "preco"}]


def test_streamlit_app_renders_empty_state_without_exceptions():
    app = AppTest.from_file(PROJECT_ROOT / "app.py")
    app.run()

    assert not app.exception
    assert len(app.sidebar.file_uploader) == 1
