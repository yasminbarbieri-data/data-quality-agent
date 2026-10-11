
from pathlib import Path

from data_quality_agent.file_reader import load_file
from data_quality_agent.reporting import build_summary, export_issues
from data_quality_agent.validators import validate_dataframe, validate_structure


def run_pipeline(
    input_path: str | Path,
    output_path: str | Path = "reports/issues.csv",
) -> dict:
    df = load_file(input_path)

    structure_issues = validate_structure(df)

    if structure_issues:
        missing_columns = [
            issue["coluna"] for issue in structure_issues
        ]
        raise ValueError(
            "Arquivo com estrutura inválida. "
            f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
        )

    issues = validate_dataframe(df)
    summary = build_summary(df, issues)
    report_path = export_issues(issues, output_path)

    return {
        "summary": summary,
        "report_path": report_path,
    }
