"""Correções determinísticas e auditáveis para bases de produtos.

Somente ajustes sem ambiguidade são aplicados automaticamente. O DataFrame de
origem nunca é alterado. Cada célula alterada gera uma única linha de auditoria.
"""
from __future__ import annotations

import pandas as pd

from data_quality_agent.validators import ALLOWED_CATEGORIES, REQUIRED_COLUMNS, validate_structure

TEXT_COLUMNS = ("nome_produto", "categoria", "data_atualizacao")
CHANGE_LOG_COLUMNS = ("linha", "coluna", "valor_original", "valor_novo", "motivo")


def correct_dataframe(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (cópia tratada, histórico); não inventa valores nem resolve ambiguidades."""
    corrected = dataframe.copy(deep=True)
    log: list[dict[str, object]] = []

    if validate_structure(corrected):
        return corrected, pd.DataFrame(columns=CHANGE_LOG_COLUMNS)

    category_lookup = {category.casefold(): category for category in ALLOWED_CATEGORIES}

    # Use posição física da linha, não o índice pandas, para corresponder à planilha.
    for position, (index, row) in enumerate(corrected.iterrows(), start=2):
        for column in TEXT_COLUMNS:
            original = row[column]
            if pd.isna(original) or not isinstance(original, str):
                continue

            cleaned = original.strip()
            new_value = cleaned
            reason_parts: list[str] = []
            if cleaned != original:
                reason_parts.append("Remoção de espaços no início/fim")

            # A categoria só é normalizada quando há correspondência exata após
            # ignorar espaços externos e caixa; nenhuma categoria é inferida.
            if column == "categoria" and cleaned:
                canonical = category_lookup.get(cleaned.casefold())
                if canonical is not None and canonical != cleaned:
                    new_value = canonical
                    reason_parts.append("padronização de maiúsculas/minúsculas para categoria permitida")

            if new_value != original:
                corrected.at[index, column] = new_value
                if column == "categoria" and new_value in ALLOWED_CATEGORIES:
                    reason = "; ".join(reason_parts) + ". Correspondência inequívoca com a lista permitida."
                else:
                    reason = "; ".join(reason_parts) + "; conteúdo preservado."
                log.append({
                    "linha": position,
                    "coluna": column,
                    "valor_original": original,
                    "valor_novo": new_value,
                    "motivo": reason,
                })

    return corrected, pd.DataFrame(log, columns=CHANGE_LOG_COLUMNS)
