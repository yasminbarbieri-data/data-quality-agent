import pandas as pd
from pandas.testing import assert_frame_equal

from data_quality_agent.corrections import correct_dataframe
from data_quality_agent.validators import REQUIRED_COLUMNS


def valid_data():
    return pd.DataFrame({
        "id_produto": ["P001", "P002"],
        "nome_produto": [" Teclado USB ", "Mouse"],
        "categoria": ["perifericos", "Monitores"],
        "preco": [129.9, -10],
        "quantidade_estoque": [5, -2],
        "data_atualizacao": ["2026-10-01", "2026-10-02"],
    }, columns=REQUIRED_COLUMNS)


def test_corrections_return_copy_and_keep_original_unchanged():
    original = valid_data()
    corrected, log = correct_dataframe(original)

    assert original.loc[0, "nome_produto"] == " Teclado USB "
    assert corrected.loc[0, "nome_produto"] == "Teclado USB"
    assert corrected.loc[0, "categoria"] == "Perifericos"
    assert len(log) == 2


def test_ambiguous_or_invalid_business_values_are_not_invented():
    original = valid_data()
    corrected, _ = correct_dataframe(original)

    assert corrected.loc[1, "preco"] == -10
    assert corrected.loc[1, "quantidade_estoque"] == -2


def test_missing_required_columns_returns_unchanged_copy_and_empty_log():
    original = pd.DataFrame({"id_produto": ["P001"]})
    corrected, log = correct_dataframe(original)

    assert corrected.equals(original)
    assert log.empty


def test_identifiers_are_not_trimmed_automatically_to_avoid_creating_collisions():
    original = valid_data()
    original.loc[0, "id_produto"] = " P001 "
    corrected, log = correct_dataframe(original)

    assert corrected.loc[0, "id_produto"] == " P001 "
    assert "id_produto" not in log.get("coluna", pd.Series(dtype=str)).tolist()


def test_demo_file_contains_safe_corrections_and_keeps_ambiguous_issues():
    from pathlib import Path
    from data_quality_agent.validators import validate_dataframe
    from data_quality_agent.file_reader import load_file

    project_root = Path(__file__).resolve().parents[1]
    sample = load_file(project_root / "data" / "samples" / "products_with_issues.csv")
    original_snapshot = sample.copy(deep=True)
    corrected, log = correct_dataframe(sample)

    assert_frame_equal(sample, original_snapshot)
    assert len(log) == 2
    assert log["linha"].tolist() == [2, 2]
    assert log["coluna"].tolist() == ["nome_produto", "categoria"]
    assert log["valor_original"].tolist() == [" Teclado USB ", " perifericos "]
    assert log["valor_novo"].tolist() == ["Teclado USB", "Perifericos"]
    assert log["motivo"].str.contains("conteúdo preservado|Correspondência inequívoca", regex=True).all()
    assert sample.loc[0, "nome_produto"] == " Teclado USB "
    assert corrected.loc[0, "nome_produto"] == "Teclado USB"
    remaining_issues = validate_dataframe(corrected)
    assert len(remaining_issues) == 7
    assert sum(issue["regra"] == "R05" for issue in remaining_issues) == 1
    remaining_codes = {issue["regra"] for issue in remaining_issues}
    assert {"R01", "R02", "R03", "R04", "R05", "R06"}.issubset(remaining_codes)


def test_category_trim_and_case_normalization_are_one_auditable_change():
    original = valid_data()
    original.loc[0, "categoria"] = " perifericos "
    corrected, log = correct_dataframe(original)

    category_changes = log[log["coluna"] == "categoria"]
    assert len(category_changes) == 1
    assert category_changes.iloc[0]["valor_original"] == " perifericos "
    assert category_changes.iloc[0]["valor_novo"] == "Perifericos"
    assert corrected.loc[0, "categoria"] == "Perifericos"
    assert original.loc[0, "categoria"] == " perifericos "


def test_change_log_uses_physical_row_number_not_dataframe_index():
    original = valid_data()
    original.index = [100, 200]
    corrected, log = correct_dataframe(original)

    name_change = log[log["coluna"] == "nome_produto"].iloc[0]
    assert name_change["linha"] == 2
    assert corrected.loc[100, "nome_produto"] == "Teclado USB"
