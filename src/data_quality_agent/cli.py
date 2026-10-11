
import argparse
from pathlib import Path

from data_quality_agent.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analisa a qualidade de arquivos CSV e Excel."
    )

    parser.add_argument(
        "arquivo",
        help="Caminho do arquivo CSV ou XLSX que será analisado.",
    )

    parser.add_argument(
        "--saida",
        default="reports/issues.csv",
        help="Caminho do relatório CSV de ocorrências.",
    )

    args = parser.parse_args()

    try:
        result = run_pipeline(args.arquivo, args.saida)
    except (FileNotFoundError, ValueError, OSError) as error:
        parser.exit(1, f"Erro: {error}\n")

    summary = result["summary"]

    print("\n=== DATA QUALITY AGENT ===")
    print(f"Arquivo analisado: {Path(args.arquivo).name}")
    print(f"Registros analisados: {summary['total_registros']}")
    print(f"Ocorrências encontradas: {summary['total_ocorrencias']}")
    print(f"Registros com problemas: {summary['registros_com_problemas']}")
    print(f"Registros sem problemas detectados: {summary['registros_sem_problemas']}")
    print(f"Relatório salvo em: {result['report_path']}")

    if summary["ocorrencias_por_regra"]:
        print("\nOcorrências por regra:")

        for rule, count in sorted(
            summary["ocorrencias_por_regra"].items()
        ):
            print(f"  {rule}: {count}")


if __name__ == "__main__":
    main()
