import math

import pandas as pd


REQUIRED_COLUMNS = [
    "id_produto",
    "nome_produto",
    "categoria",
    "preco",
    "quantidade_estoque",
    "data_atualizacao",
]


def validate_structure(df: pd.DataFrame) -> list[dict]:
    """Identifica colunas obrigatórias ausentes no arquivo."""
    issues = []

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            issues.append({
                "linha": 0,
                "coluna": column,
                "regra": "R07",
                "valor_encontrado": "",
                "descricao": (
                    f"A coluna obrigatória '{column}' não existe no arquivo."
                ),
            })

    return issues

def validate_required_fields(df: pd.DataFrame) -> list[dict]:
    """Identifica campos obrigatórios ausentes ou vazios."""
    issues = []

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            continue

        missing = df[column].isna() | df[column].astype("string").str.strip().eq("")

        for index in df.index[missing]:
            issues.append({
                "linha": int(index) + 2,
                "coluna": column,
                "regra": "R01",
                "valor_encontrado": "",
                "descricao": f"O campo obrigatório '{column}' está vazio.",
            })

    return issues


def validate_duplicate_ids(df: pd.DataFrame) -> list[dict]:
    """Identifica todas as ocorrências de IDs de produto duplicados."""
    if "id_produto" not in df.columns:
        return []

    ids = df["id_produto"].astype("string").str.strip()
    duplicated = ids.notna() & ids.ne("") & ids.duplicated(keep=False)

    issues = []

    for index in df.index[duplicated]:
        issues.append({
            "linha": int(index) + 2,
            "coluna": "id_produto",
            "regra": "R02",
            "valor_encontrado": str(df.loc[index, "id_produto"]),
            "descricao": "O ID do produto aparece em mais de um registro.",
        })

    return issues

from datetime import datetime

ALLOWED_CATEGORIES = {
    "Perifericos",
    "Monitores",
    "Mobiliario",
}



def validate_prices(df: pd.DataFrame) -> list[dict]:
    """Identifica preços ausentes, não numéricos, infinitos ou menores ou iguais a zero."""
    issues = []

    if "preco" not in df.columns:
        return issues

    prices = pd.to_numeric(df["preco"], errors="coerce")

    for index, price in prices.items():
        invalid = (
            pd.isna(price)
            or not math.isfinite(price)
            or price <= 0
        )

        if invalid:
            issues.append({
                "linha": int(index) + 2,
                "coluna": "preco",
                "regra": "R03",
                "valor_encontrado": str(df.loc[index, "preco"]),
                "descricao": (
                    "O preço deve ser um número finito maior que zero."
                ),
            })

    return issues


def validate_stock(df: pd.DataFrame) -> list[dict]:
    """Identifica quantidades inválidas, negativas ou não inteiras."""
    issues = []

    if "quantidade_estoque" not in df.columns:
        return issues

    stock = pd.to_numeric(df["quantidade_estoque"], errors="coerce")

    for index, quantity in stock.items():
        invalid = (
            pd.isna(quantity)
            or quantity < 0
            or quantity % 1 != 0
        )

        if invalid:
            issues.append({
                "linha": int(index) + 2,
                "coluna": "quantidade_estoque",
                "regra": "R04",
                "valor_encontrado": str(df.loc[index, "quantidade_estoque"]),
                "descricao": (
                    "A quantidade deve ser um número inteiro "
                    "maior ou igual a zero."
                ),
            })

    return issues


def validate_categories(df: pd.DataFrame) -> list[dict]:
    """Identifica categorias fora da lista permitida."""
    issues = []

    if "categoria" not in df.columns:
        return issues

    for index, category in df["categoria"].items():
        if pd.isna(category) or str(category).strip() not in ALLOWED_CATEGORIES:
            issues.append({
                "linha": int(index) + 2,
                "coluna": "categoria",
                "regra": "R05",
                "valor_encontrado": str(category),
                "descricao": "A categoria não pertence à lista permitida.",
            })

    return issues


def validate_dates(df: pd.DataFrame) -> list[dict]:
    """Identifica datas inválidas ou fora do formato AAAA-MM-DD."""
    issues = []

    if "data_atualizacao" not in df.columns:
        return issues

    for index, value in df["data_atualizacao"].items():
        try:
            if pd.isna(value):
                raise ValueError

            datetime.strptime(str(value).strip(), "%Y-%m-%d")

        except (ValueError, TypeError):
            issues.append({
                "linha": int(index) + 2,
                "coluna": "data_atualizacao",
                "regra": "R06",
                "valor_encontrado": str(value),
                "descricao": (
                    "A data deve existir e estar no formato AAAA-MM-DD."
                ),
            })

    return issues



def validate_dataframe(df: pd.DataFrame) -> list[dict]:
    """Verifica a estrutura e executa as regras de validação."""

    structure_issues = validate_structure(df)

    if structure_issues:
        return structure_issues

    # Padroniza o índice para que ele corresponda à posição dos registros.
    df = df.reset_index(drop=True)

    validators = [
        validate_required_fields,
        validate_duplicate_ids,
        validate_prices,
        validate_stock,
        validate_categories,
        validate_dates,
    ]

    issues = []

    for validator in validators:
        issues.extend(validator(df))

    return sorted(
        issues,
        key=lambda issue: (
            issue["linha"],
            issue["regra"],
            issue["coluna"],
        ),
    )
