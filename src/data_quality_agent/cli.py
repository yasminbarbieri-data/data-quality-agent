
import argparse
from pathlib import Path

from data_quality_agent.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analisa a qualidade de arquivos CSV e Excel."
    )

    parser.add_argument(
        "arquivo",
        help="Caminho do arquivo CSV ou XLSX que sera analisado.",
    )

    parser.add_argument(
        "--saida",
        default="reports/issues.csv",
        help="Caminho do relatorio CSV de ocorrencias.",
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
    print(f"Ocorrencias encontradas: {summary['total_ocorrencias']}")

    print(
        f"Registros com problemas: "
        f"{summary['registros_com_problemas']} "
        f"({summary['percentual_registros_com_problemas']:.2f}%)"
    )

    print(
        f"Registros sem problemas detectados: "
        f"{summary['registros_sem_problemas']} "
        f"({summary['percentual_registros_sem_problemas']:.2f}%)"
    )

    print(f"Relatorio salvo em: {result['report_path']}")

    if summary["ocorrencias_por_regra"]:
        print("\nOcorrencias por regra:")

        for rule, count in sorted(
            summary["ocorrencias_por_regra"].items()
        ):
            print(f"  {rule}: {count}")

    top_rules = summary["regras_com_mais_ocorrencias"]

    if top_rules:
        print("\nRegras com mais ocorrencias:")

        for rule, count in sorted(top_rules.items()):
            print(f"  {rule}: {count}")


if __name__ == "__main__":
    main()
