
from pathlib import Path

import pandas as pd




def build_summary(df, issues) -> dict:
    """Resume os resultados da validacao de qualidade dos dados."""
    issues_by_rule = {}

    for issue in issues:
        rule = issue["regra"]
        issues_by_rule[rule] = issues_by_rule.get(rule, 0) + 1

    affected_rows = {
        issue["linha"]
        for issue in issues
        if issue["linha"] >= 2
    }

    total_records = len(df)
    records_with_issues = len(affected_rows)
    records_without_issues = total_records - records_with_issues

    if total_records > 0:
        percentage_with_issues = (
            records_with_issues / total_records
        ) * 100
        percentage_without_issues = (
            records_without_issues / total_records
        ) * 100
    else:
        percentage_with_issues = 0.0
        percentage_without_issues = 0.0

    if issues_by_rule:
        highest_count = max(issues_by_rule.values())
        top_rules = {
            rule: count
            for rule, count in issues_by_rule.items()
            if count == highest_count
        }
    else:
        top_rules = {}

    return {
        "total_registros": total_records,
        "total_ocorrencias": len(issues),
        "registros_com_problemas": records_with_issues,
        "registros_sem_problemas": records_without_issues,
        "percentual_registros_com_problemas": round(
            percentage_with_issues, 2
        ),
        "percentual_registros_sem_problemas": round(
            percentage_without_issues, 2
        ),
        "ocorrencias_por_regra": issues_by_rule,
        "regras_com_mais_ocorrencias": top_rules,
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
