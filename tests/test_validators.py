from data_quality_agent.validators import (
    validate_categories,
    validate_duplicate_ids,
    validate_dates,
    validate_prices,
    validate_required_fields,
    validate_stock,
)
import pandas as pd

from data_quality_agent.validators import (
    validate_duplicate_ids,
    validate_required_fields,
)

from data_quality_agent.validators import (
    validate_categories,
    validate_dataframe,
    validate_duplicate_ids,
    validate_dates,
    validate_prices,
    validate_required_fields,
    validate_stock,
)
def test_required_field_empty():
    df = pd.DataFrame({
        "id_produto": ["P001", "P002"],
        "nome_produto": ["Teclado", ""],
    })

    issues = validate_required_fields(df)

    assert len(issues) == 1
    assert issues[0]["linha"] == 3
    assert issues[0]["coluna"] == "nome_produto"
    assert issues[0]["regra"] == "R01"


def test_duplicate_ids_marks_both_rows():
    df = pd.DataFrame({
        "id_produto": ["P001", "P003", "P003", "P004"],
    })

    issues = validate_duplicate_ids(df)

    assert len(issues) == 2
    assert {issue["linha"] for issue in issues} == {3, 4}
    assert all(issue["regra"] == "R02" for issue in issues)


def test_empty_ids_are_not_reported_as_duplicates():
    df = pd.DataFrame({
        "id_produto": ["P001", "", None],
    })

    issues = validate_duplicate_ids(df)

    assert issues == []

def test_negative_price_is_detected():
    df = pd.DataFrame({"preco": [100.0, -50.0]})

    issues = validate_prices(df)

    assert len(issues) == 1
    assert issues[0]["linha"] == 3
    assert issues[0]["regra"] == "R03"


def test_negative_or_fractional_stock_is_detected():
    df = pd.DataFrame({"quantidade_estoque": [5, -4, 2.5]})

    issues = validate_stock(df)

    assert len(issues) == 2
    assert {issue["linha"] for issue in issues} == {3, 4}


def test_unknown_category_is_detected():
    df = pd.DataFrame({
        "categoria": ["Perifericos", "Eletronicos"]
    })

    issues = validate_categories(df)

    assert len(issues) == 1
    assert issues[0]["linha"] == 3
    assert issues[0]["regra"] == "R05"


def test_invalid_calendar_date_is_detected():
    df = pd.DataFrame({
        "data_atualizacao": ["2026-10-05", "2026-02-30"]
    })

    issues = validate_dates(df)

    assert len(issues) == 1
    assert issues[0]["linha"] == 3
    assert issues[0]["regra"] == "R06"

def test_validate_dataframe_consolidates_rules():
    df = pd.DataFrame({
        "id_produto": ["P001", "P001"],
        "nome_produto": ["Teclado", ""],
        "categoria": ["Perifericos", "Eletronicos"],
        "preco": [100.0, -10.0],
        "quantidade_estoque": [5, -2],
        "data_atualizacao": ["2026-10-01", "2026-02-30"],
    })

    issues = validate_dataframe(df)

    rules_found = {issue["regra"] for issue in issues}

    assert {"R01", "R02", "R03", "R04", "R05", "R06"} <= rules_found
    assert issues == sorted(
        issues,
        key=lambda issue: (
            issue["linha"],
            issue["regra"],
            issue["coluna"],
        ),
    )

def test_missing_required_column_is_detected():
    from data_quality_agent.validators import validate_dataframe

    df = pd.DataFrame({
        "id_produto": ["P001"],
        "nome_produto": ["Teclado USB"],
        "categoria": ["Perifericos"],
        "quantidade_estoque": [10],
        "data_atualizacao": ["2026-10-01"],
    })

    issues = validate_dataframe(df)

    assert len(issues) == 1
    assert issues[0]["regra"] == "R07"
    assert issues[0]["coluna"] == "preco"

def test_infinite_price_is_detected():
    df = pd.DataFrame({
        "id_produto": ["P001"],
        "nome_produto": ["Teclado USB"],
        "categoria": ["Perifericos"],
        "preco": [float("inf")],
        "quantidade_estoque": [10],
        "data_atualizacao": ["2026-10-01"],
    })

    issues = validate_dataframe(df)

    price_issues = [
        issue for issue in issues
        if issue["regra"] == "R03"
    ]

    assert len(price_issues) == 1

def test_issue_line_number_uses_dataframe_position():
    df = pd.DataFrame({
        "id_produto": ["P001", "P002"],
        "nome_produto": ["Teclado USB", "Mouse sem fio"],
        "categoria": ["Perifericos", "Perifericos"],
        "preco": [129.90, -10.00],
        "quantidade_estoque": [35, 50],
        "data_atualizacao": ["2026-10-01", "2026-10-02"],
    }, index=[10, 20])

    issues = validate_dataframe(df)

    price_issue = next(
        issue for issue in issues
        if issue["regra"] == "R03"
    )

    assert price_issue["linha"] == 3
