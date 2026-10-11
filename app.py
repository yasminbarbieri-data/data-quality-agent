"""Interface Streamlit do Data Quality Agent."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data_quality_agent.file_reader import load_uploaded_file
from data_quality_agent.reporting import build_summary, issues_to_dataframe
from data_quality_agent.validators import (
    REQUIRED_COLUMNS,
    validate_dataframe,
    validate_structure,
)


RULE_DESCRIPTIONS = {
    "R01": "Campo obrigatório vazio",
    "R02": "ID de produto duplicado",
    "R03": "Preço inválido",
    "R04": "Quantidade em estoque inválida",
    "R05": "Categoria fora da lista permitida",
    "R06": "Data inválida ou fora do formato AAAA-MM-DD",
    "R07": "Coluna obrigatória ausente",
}

DISPLAY_COLUMNS = {
    "linha": "Linha do arquivo",
    "coluna": "Coluna",
    "regra": "Regra",
    "valor_encontrado": "Valor encontrado",
    "descricao": "Descrição",
}


def to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    """Gera um CSV compatível com programas de planilha no Windows."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def display_issues(issues: list[dict]) -> pd.DataFrame:
    """Converte as ocorrências do núcleo para os rótulos da interface."""
    return issues_to_dataframe(issues).rename(columns=DISPLAY_COLUMNS)


def filter_issues(
    dataframe: pd.DataFrame,
    selected_rules: list[str],
    selected_columns: list[str],
    search_text: str,
) -> pd.DataFrame:
    """Aplica os filtros do painel sem alterar o relatório completo."""
    filtered = dataframe.copy()

    if selected_rules:
        filtered = filtered[filtered["Regra"].isin(selected_rules)]

    if selected_columns:
        filtered = filtered[filtered["Coluna"].isin(selected_columns)]

    if search_text.strip():
        text = search_text.strip().casefold()
        searchable = filtered[
            ["Coluna", "Regra", "Valor encontrado", "Descrição"]
        ].fillna("").astype(str)
        matches = searchable.apply(
            lambda row: text in " ".join(row).casefold(),
            axis=1,
        )
        filtered = filtered[matches]

    return filtered


def render_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container {max-width: 1180px; padding-top: 2.4rem; padding-bottom: 3rem;}
            [data-testid="stMetric"] {
                background: #f7f9fc;
                border: 1px solid #e4e9f2;
                border-radius: 14px;
                padding: 1rem;
            }
            .hero-eyebrow {
                color: #2463eb;
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.4rem;
            }
            .hero-copy {color: #52616b; font-size: 1.05rem; max-width: 730px;}
            .rule-card {
                background: #f7f9fc;
                border-left: 4px solid #2463eb;
                border-radius: 0 10px 10px 0;
                padding: 0.85rem 1rem;
                margin: 0.45rem 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.info("Envie um arquivo CSV ou XLSX na barra lateral para iniciar a análise.")
    st.subheader("Como a análise funciona")
    steps = st.columns(3)
    steps[0].markdown("**1. Envie a planilha**\n\nO arquivo não é alterado.")
    steps[1].markdown(
        "**2. Confira os indicadores**\n\nVeja o tamanho e o tipo dos problemas."
    )
    steps[2].markdown(
        "**3. Baixe o relatório**\n\nCompartilhe as ocorrências com quem fará a correção."
    )

    with st.expander("Estrutura esperada do arquivo"):
        st.write(
            "A versão atual valida uma base de produtos. Os nomes das colunas "
            "devem ser exatamente estes:"
        )
        st.code("\n".join(REQUIRED_COLUMNS), language=None)
        st.caption(
            "As regras verificam campos vazios, IDs duplicados, preço, estoque, "
            "categoria e data de atualização."
        )


def render_analysis(dataframe: pd.DataFrame, file_name: str) -> None:
    structure_issues = validate_structure(dataframe)
    st.caption(
        f"Arquivo analisado: **{file_name}** · {len(dataframe):,} registro(s)"
        .replace(",", ".")
    )

    if structure_issues:
        issue_table = display_issues(structure_issues)
        st.error(
            "Não foi possível executar as validações de conteúdo porque faltam "
            "colunas obrigatórias. Confira a estrutura e tente novamente."
        )
        st.dataframe(issue_table, use_container_width=True, hide_index=True)
        st.download_button(
            "Baixar relatório de estrutura (.csv)",
            data=to_csv_bytes(issue_table),
            file_name="relatorio_estrutura_invalida.csv",
            mime="text/csv",
        )
        return

    issues = validate_dataframe(dataframe)
    summary = build_summary(dataframe, issues)
    issue_table = display_issues(issues)

    if issues:
        st.warning(
            "A análise foi concluída. As ocorrências abaixo indicam pontos que "
            "merecem revisão antes do uso dos dados."
        )
    else:
        st.success(
            "Análise concluída: nenhum problema foi detectado pelas regras atuais."
        )

    st.subheader("Visão geral")
    metrics = st.columns(4)
    metrics[0].metric("Registros analisados", summary["total_registros"])
    metrics[1].metric("Ocorrências", summary["total_ocorrencias"])
    metrics[2].metric(
        "Registros com problemas",
        f"{summary['registros_com_problemas']} "
        f"({summary['percentual_registros_com_problemas']:.2f}%)",
    )
    metrics[3].metric(
        "Sem problemas detectados",
        f"{summary['registros_sem_problemas']} "
        f"({summary['percentual_registros_sem_problemas']:.2f}%)",
    )

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Ocorrências por regra")
        if issues:
            rule_counts = (
                issue_table.groupby("Regra", as_index=False)
                .size()
                .rename(columns={"size": "Ocorrências"})
                .sort_values("Ocorrências", ascending=False)
            )
            st.bar_chart(rule_counts, x="Regra", y="Ocorrências", color="#2463eb")
        else:
            st.caption("Não há ocorrências para exibir.")

    with right:
        st.subheader("O que revisar primeiro")
        if summary["regras_com_mais_ocorrencias"]:
            for rule, count in summary["regras_com_mais_ocorrencias"].items():
                st.markdown(
                    "<div class='rule-card'><strong>"
                    f"{rule} · {count} ocorrência(s)</strong><br>"
                    f"{RULE_DESCRIPTIONS.get(rule, 'Regra de validação')}"
                    "</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption(
                "Não há uma regra prioritária porque não foram detectadas ocorrências."
            )

    with st.expander("Prévia dos dados enviados"):
        st.dataframe(
            dataframe.head(20),
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Ocorrências detalhadas")
    if issue_table.empty:
        st.caption("Nenhuma ocorrência encontrada para filtrar ou baixar.")
        st.download_button(
            "Baixar relatório vazio (.csv)",
            data=to_csv_bytes(issue_table),
            file_name="relatorio_ocorrencias.csv",
            mime="text/csv",
        )
        return

    filter_columns = st.columns(3)
    selected_rules = filter_columns[0].multiselect(
        "Filtrar por regra",
        options=sorted(issue_table["Regra"].dropna().unique().tolist()),
    )
    selected_columns = filter_columns[1].multiselect(
        "Filtrar por coluna",
        options=sorted(issue_table["Coluna"].dropna().unique().tolist()),
    )
    search_text = filter_columns[2].text_input(
        "Buscar no relatório",
        placeholder="Ex.: preço, P003 ou inválida",
    )

    filtered = filter_issues(
        issue_table,
        selected_rules,
        selected_columns,
        search_text,
    )
    st.caption(f"Exibindo {len(filtered)} de {len(issue_table)} ocorrência(s).")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    downloads = st.columns(2)
    downloads[0].download_button(
        "Baixar relatório completo (.csv)",
        data=to_csv_bytes(issue_table),
        file_name="relatorio_ocorrencias.csv",
        mime="text/csv",
    )
    downloads[1].download_button(
        "Baixar resultado filtrado (.csv)",
        data=to_csv_bytes(filtered),
        file_name="relatorio_ocorrencias_filtrado.csv",
        mime="text/csv",
    )


def main() -> None:
    st.set_page_config(
        page_title="Data Quality Agent",
        page_icon="🔎",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_styles()

    with st.sidebar:
        st.title("🔎 Data Quality Agent")
        st.caption("Validação visual de dados para planilhas de produtos")
        uploaded_file = st.file_uploader(
            "Envie sua planilha",
            type=["csv", "xlsx"],
            help="Formatos aceitos: CSV e Excel (.xlsx).",
        )
        st.divider()
        st.markdown("**Antes de enviar**")
        st.caption(
            "Use dados fictícios, anonimizados ou autorizados para demonstrações."
        )
        st.markdown("**Regras disponíveis**")
        st.caption("R01–R07 · Estrutura, preenchimento, duplicidade e consistência.")

    st.markdown(
        "<p class='hero-eyebrow'>Qualidade de dados sem complicação</p>",
        unsafe_allow_html=True,
    )
    st.title("Encontre problemas antes que eles virem retrabalho")
    st.markdown(
        "<p class='hero-copy'>Envie uma planilha para identificar campos vazios, "
        "duplicidades e valores inconsistentes — e transforme a revisão em um "
        "relatório claro para quem toma ou executa decisões.</p>",
        unsafe_allow_html=True,
    )

    if uploaded_file is None:
        render_empty_state()
        return

    try:
        dataframe = load_uploaded_file(uploaded_file, uploaded_file.name)
    except (ValueError, OSError, pd.errors.ParserError) as error:
        st.error(f"Não foi possível ler o arquivo: {error}")
        return

    render_analysis(dataframe, uploaded_file.name)


if __name__ == "__main__":
    main()
