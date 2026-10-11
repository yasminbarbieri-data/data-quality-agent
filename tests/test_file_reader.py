
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest

from data_quality_agent.file_reader import load_file, load_uploaded_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"


def test_load_valid_csv():
    df = load_file(SAMPLES_DIR / "products_valid.csv")

    assert len(df) == 5
    assert "id_produto" in df.columns


def test_load_csv_with_issues():
    df = load_file(SAMPLES_DIR / "products_with_issues.csv")

    assert len(df) == 6
    assert "preco" in df.columns


def test_file_not_found():
    file_path = SAMPLES_DIR / "arquivo_inexistente.csv"

    with pytest.raises(FileNotFoundError):
        load_file(file_path)


def test_load_uploaded_csv():
    content = BytesIO(
        b"id_produto,nome_produto\nP001,Teclado USB\n"
    )

    result = load_uploaded_file(content, "produtos.csv")

    assert result.to_dict("records") == [
        {"id_produto": "P001", "nome_produto": "Teclado USB"}
    ]


def test_load_uploaded_xlsx():
    content = BytesIO()
    pd.DataFrame({"id_produto": ["P001"]}).to_excel(
        content,
        index=False,
    )

    result = load_uploaded_file(content, "produtos.xlsx")

    assert result["id_produto"].tolist() == ["P001"]


def test_uploaded_file_rejects_unsupported_extension():
    with pytest.raises(ValueError, match="Formato não suportado"):
        load_uploaded_file(BytesIO(b"texto"), "produtos.txt")


def test_load_valid_xlsx(tmp_path):
    input_file = tmp_path / "products.xlsx"

    expected = pd.DataFrame({
        "id_produto": ["P001", "P002"],
        "nome_produto": ["Teclado USB", "Mouse sem fio"],
        "categoria": ["Perifericos", "Perifericos"],
        "preco": [129.90, 89.90],
        "quantidade_estoque": [35, 50],
        "data_atualizacao": ["2026-10-01", "2026-10-02"],
    })

    expected.to_excel(input_file, index=False)

    result = load_file(input_file)

    assert len(result) == 2
    assert list(result.columns) == list(expected.columns)
    assert result["id_produto"].tolist() == ["P001", "P002"]
