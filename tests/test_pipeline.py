
import pandas as pd
import pytest

from data_quality_agent.pipeline import run_pipeline


def test_pipeline_processes_valid_file(tmp_path):
    input_file = "data/samples/products_valid.csv"
    output_file = tmp_path / "valid_issues.csv"

    result = run_pipeline(input_file, output_file)

    assert result["summary"]["total_registros"] == 5
    assert result["summary"]["total_ocorrencias"] == 0
    assert result["summary"]["registros_sem_problemas"] == 5
    assert output_file.exists()


def test_pipeline_finds_issues(tmp_path):
    input_file = "data/samples/products_with_issues.csv"
    output_file = tmp_path / "issues.csv"

    result = run_pipeline(input_file, output_file)

    assert result["summary"]["total_registros"] == 6
    assert result["summary"]["total_ocorrencias"] == 8
    assert result["summary"]["registros_com_problemas"] == 6
    assert result["summary"]["ocorrencias_por_regra"] == {
        "R01": 1,
        "R02": 2,
        "R03": 1,
        "R04": 1,
        "R05": 2,
        "R06": 1,
    }
    assert output_file.exists()


def test_pipeline_rejects_file_with_missing_required_column(tmp_path):
    input_file = tmp_path / "missing_column.csv"
    output_file = tmp_path / "report.csv"

    pd.DataFrame({
        "id_produto": ["P001"],
        "nome_produto": ["Teclado USB"],
        "categoria": ["Perifericos"],
        "quantidade_estoque": [10],
        "data_atualizacao": ["2026-10-01"],
    }).to_csv(input_file, index=False)

    with pytest.raises(ValueError, match="estrutura inválida"):
        run_pipeline(input_file, output_file)

    assert not output_file.exists()
