
import pandas as pd

from data_quality_agent.reporting import build_summary, export_issues


def test_build_summary_counts_records_and_issues():
    df = pd.DataFrame({
        "id_produto": ["P001", "P002", "P003"],
    })

    issues = [
        {
            "linha": 2,
            "coluna": "preco",
            "regra": "R03",
            "valor_encontrado": "-10",
            "descricao": "O preço deve ser maior que zero.",
        },
        {
            "linha": 2,
            "coluna": "categoria",
            "regra": "R05",
            "valor_encontrado": "Eletronicos",
            "descricao": "Categoria não permitida.",
        },
        {
            "linha": 4,
            "coluna": "quantidade_estoque",
            "regra": "R04",
            "valor_encontrado": "-2",
            "descricao": "A quantidade não pode ser negativa.",
        },
    ]

    summary = build_summary(df, issues)

    assert summary["total_registros"] == 3
    assert summary["total_ocorrencias"] == 3
    assert summary["registros_com_problemas"] == 2
    assert summary["registros_sem_problemas"] == 1
    assert summary["ocorrencias_por_regra"] == {
        "R03": 1,
        "R05": 1,
        "R04": 1,
    }


def test_export_issues_creates_csv(tmp_path):
    issues = [
        {
            "linha": 2,
            "coluna": "preco",
            "regra": "R03",
            "valor_encontrado": "-10",
            "descricao": "O preço deve ser maior que zero.",
        }
    ]

    output = tmp_path / "reports" / "issues.csv"
    result = export_issues(issues, output)

    assert result.exists()

    exported = pd.read_csv(result)

    assert len(exported) == 1
    assert exported.loc[0, "regra"] == "R03"


def test_export_empty_issues_creates_csv_with_headers(tmp_path):
    output = tmp_path / "empty.csv"

    export_issues([], output)

    exported = pd.read_csv(output)

    assert len(exported) == 0
    assert "regra" in exported.columns
