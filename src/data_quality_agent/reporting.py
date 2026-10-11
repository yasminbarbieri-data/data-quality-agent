
from pathlib import Path

import pandas as pd



def build_summary(df, issues) -> dict:
    """Resume os resultados sem confundir erros estruturais com registros."""
    issues_by_rule = {}

    for issue in issues:
        rule = issue["regra"]
        issues_by_rule[rule] = issues_by_rule.get(rule, 0) + 1

    affected_rows = {
        issue["linha"]
        for issue in issues
        if issue["linha"] >= 2
    }

    return {
        "total_registros": len(df),
        "total_ocorrencias": len(issues),
        "registros_com_problemas": len(affected_rows),
        "registros_sem_problemas": len(df) - len(affected_rows),
        "ocorrencias_por_regra": issues_by_rule,
    }



def export_issues(
    issues: list[dict],
    output_path: str | Path,
) -> Path:
    """Exporta as ocorrências para um arquivo CSV."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "linha",
        "coluna",
        "regra",
        "valor_encontrado",
        "descricao",
    ]

    df_issues = pd.DataFrame(issues, columns=columns)
    df_issues.to_csv(path, index=False, encoding="utf-8-sig")

    return path
