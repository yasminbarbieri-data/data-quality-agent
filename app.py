"""Interface Streamlit do Data Quality Agent."""
from __future__ import annotations

from io import BytesIO
import pandas as pd
import streamlit as st

from data_quality_agent.ai_assistant import build_local_guidance
from data_quality_agent.corrections import correct_dataframe
from data_quality_agent.file_reader import load_uploaded_file
from data_quality_agent.reporting import build_summary, issues_to_dataframe
from data_quality_agent.validators import REQUIRED_COLUMNS, validate_dataframe, validate_structure

RULE_DESCRIPTIONS = {
    "R01": "Campo obrigatório vazio", "R02": "ID de produto duplicado",
    "R03": "Preço inválido", "R04": "Estoque inválido",
    "R05": "Categoria não permitida", "R06": "Data inválida",
    "R07": "Coluna obrigatória ausente",
}
DISPLAY_COLUMNS = {
    "linha": "Linha", "coluna": "Coluna", "regra": "Código",
    "valor_encontrado": "Valor encontrado", "descricao": "O que foi identificado",
}
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    """CSV com BOM para abrir corretamente no Excel em português."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def to_xlsx_bytes(dataframe: pd.DataFrame, sheet_name: str = "Dados") -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return output.getvalue()


def display_issues(issues: list[dict]) -> pd.DataFrame:
    return issues_to_dataframe(issues).rename(columns=DISPLAY_COLUMNS)


def filter_issues(dataframe: pd.DataFrame, selected_rules: list[str], selected_columns: list[str], search_text: str) -> pd.DataFrame:
    filtered = dataframe.copy()
    if selected_rules:
        filtered = filtered[filtered["Código"].isin(selected_rules)]
    if selected_columns:
        filtered = filtered[filtered["Coluna"].isin(selected_columns)]
    if search_text.strip():
        text = search_text.strip().casefold()
        searchable = filtered[["Coluna", "Código", "Valor encontrado", "O que foi identificado"]].fillna("").astype(str)
        matches = searchable.apply(lambda row: text in " ".join(row).casefold(), axis=1)
        filtered = filtered[matches]
    return filtered


def render_styles() -> None:
    st.markdown("""
    <style>
      :root { --navy:#102A43; --teal:#0F7C86; --ink:#172B3A; --muted:#5C7082; --line:#DCE6ED; }
      .stApp { background:#FFFFFF; }
      [data-testid="stHeader"] { background:rgba(255,255,255,.96); }
      .block-container {max-width:1380px; padding-top:1.35rem; padding-bottom:3rem;}
      section[data-testid="stSidebar"] {background:#F3F7FA; border-right:1px solid var(--line);}
      .hero {padding:2rem 2.1rem; border-radius:18px; background:linear-gradient(112deg,#102A43 0%,#174A72 62%,#0F7C86 100%); color:#fff; margin-bottom:1.35rem; box-shadow:0 12px 30px rgba(16,42,67,.12);}
      .hero-kicker {font-size:.74rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:#A9E0E3; margin-bottom:.7rem;}
      .hero h1 {font-size:clamp(1.75rem,3vw,2.45rem); line-height:1.14; color:#BFEDE8; background:linear-gradient(90deg,#BFEDE8 0%,#78D7C8 52%,#A7E8C8 100%); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; margin:0 0 .8rem 0;}
      .hero p {font-size:1rem; line-height:1.65; color:#EAF4F7; max-width:900px; margin:0;}
      [data-testid="stMetric"] {background:#fff; border:1px solid var(--line); padding:1.05rem 1.1rem; border-radius:14px; box-shadow:0 4px 14px rgba(16,42,67,.045); min-height:120px;}
      [data-testid="stMetricLabel"] {color:#526779; font-size:.88rem;}
      [data-testid="stMetricValue"] {color:var(--navy); font-weight:750;}
      h1,h2,h3 {color:var(--navy); letter-spacing:-.025em;}
      h2 {padding-top:.35rem;}
      .section-note {color:#526779; font-size:.94rem; line-height:1.6;}
      .eyebrow {color:#0F7C86; font-size:.75rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase;}
      div[data-testid="stDownloadButton"] button {width:100%; min-height:2.65rem; border-radius:9px; font-weight:600;}
      div.stButton > button[kind="primary"], div[data-testid="stDownloadButton"] button[kind="primary"] {background:#0F7C86; border-color:#0F7C86; color:#fff;}
      div[data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:10px; overflow:hidden;}
      div[data-testid="stAlert"] {border-radius:11px;}
      .step-title {color:#102A43; font-weight:750; font-size:1rem;}
      .step-card {background:#F6F9FB; border:1px solid #E1EAF0; border-radius:12px; padding:1rem; min-height:112px;}
      .stCaption {color:#607789;}
    </style>""", unsafe_allow_html=True)


def render_empty_state() -> None:
    st.markdown("## Da planilha ao diagnóstico, em poucos passos")
    st.markdown('<p class="section-note">Encontre inconsistências antes que elas se transformem em retrabalho, relatórios incorretos ou decisões baseadas em dados frágeis.</p>', unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    cards = [
        ("01 · Carregue", "Envie uma base em CSV ou Excel (.xlsx)."),
        ("02 · Entenda", "Veja indicadores, ocorrências e registros que merecem revisão."),
        ("03 · Trate com segurança", "Exporte o diagnóstico e baixe uma cópia com ajustes inequívocos."),
    ]
    for col, (title, body) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="step-card"><div class="step-title">{title}</div><p>{body}</p></div>', unsafe_allow_html=True)
    st.write("")
    with st.expander("Quais colunas são esperadas?"):
        st.code("\n".join(REQUIRED_COLUMNS), language=None)
        st.caption("A versão atual é especializada em bases de produtos. Campos ausentes ou ambíguos não são preenchidos por suposição.")
    st.info("Dica: comece pelos arquivos de demonstração em `data/samples/`.")


def render_ai_assistant(issues: list[dict]) -> None:
    """Mostra orientações locais sem depender de serviços externos."""
    st.markdown("## Assistente de análise")
    st.markdown(
        '<p class="section-note">Entenda os problemas encontrados e veja próximos passos. '
        'As orientações são geradas localmente; nenhum dado é enviado a serviços externos.</p>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown("**Orientações locais — disponíveis sem internet**")
        for item in build_local_guidance(issues):
            st.markdown(
                f"**{item['regra']} · {item['ocorrencias']} ocorrência(s)** — {item['orientacao']}"
            )


def render_analysis(dataframe: pd.DataFrame, file_name: str) -> None:
    st.caption(f"ARQUIVO ANALISADO  ·  **{file_name}**  ·  {len(dataframe):,} registros".replace(",", "."))
    structure_issues = validate_structure(dataframe)
    if structure_issues:
        st.error("A estrutura não corresponde à base de produtos esperada. Confira as colunas obrigatórias antes de continuar.")
        table = display_issues(structure_issues)
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.download_button("Baixar diagnóstico de estrutura (.csv)", to_csv_bytes(table), "diagnostico_estrutura.csv", "text/csv")
        return

    issues = validate_dataframe(dataframe)
    summary = build_summary(dataframe, issues)
    issue_table = display_issues(issues)
    corrected, change_log = correct_dataframe(dataframe)
    affected_pct = summary["percentual_registros_com_problemas"]

    if issues:
        st.warning(f"Foram encontradas **{len(issues)} ocorrências** em **{summary['registros_com_problemas']} registro(s)**. Confira o diagnóstico antes de usar os dados.")
    else:
        st.success("Nenhum problema foi identificado pelas regras de validação atuais.")

    st.markdown("## Resumo da qualidade")
    metrics = st.columns(4, gap="medium")
    metrics[0].metric("Registros analisados", f"{summary['total_registros']:,}".replace(",", "."))
    metrics[1].metric("Ocorrências", f"{summary['total_ocorrencias']:,}".replace(",", "."))
    metrics[2].metric("Registros para revisar", f"{summary['registros_com_problemas']:,}".replace(",", "."), f"{affected_pct:.1f}% da base".replace(".", ","))
    metrics[3].metric("Ajustes seguros", f"{len(change_log):,}".replace(",", "."), "Em uma cópia, nunca no original")

    left, right = st.columns([1.2, 1], gap="large")
    with left:
        st.markdown("### Onde estão os problemas")
        if not issue_table.empty:
            counts = issue_table.groupby("Código").size().rename("Ocorrências").reset_index()
            counts["Problema"] = counts["Código"].map(RULE_DESCRIPTIONS)
            counts = counts.sort_values("Ocorrências", ascending=True)
            st.bar_chart(counts, x="Problema", y="Ocorrências", color="#0F7C86", horizontal=True)
        else:
            st.caption("Nenhuma ocorrência para representar no gráfico.")
    with right:
        st.markdown("### Prioridades de revisão")
        if summary["regras_com_mais_ocorrencias"]:
            ordered = sorted(summary["ocorrencias_por_regra"].items(), key=lambda item: (-item[1], item[0]))
            for rule, count in ordered[:4]:
                st.markdown(f"**{RULE_DESCRIPTIONS.get(rule, rule)}**  \n{count} ocorrência(s) · {rule}")
                st.progress(min(count / max(summary["total_ocorrencias"], 1), 1.0))
        else:
            st.info("A base passou pelas regras de validação implementadas.")

    st.markdown("## Explorar e exportar")
    original_tab, diagnosis_tab, correction_tab = st.tabs(["Dados originais", "Diagnóstico", "Cópia tratada"])
    with original_tab:
        st.markdown('<p class="section-note">Prévia do arquivo carregado. Esta visualização não altera os dados de origem.</p>', unsafe_allow_html=True)
        st.dataframe(dataframe.head(100), use_container_width=True, hide_index=True)
        downloads = st.columns(2, gap="medium")
        downloads[0].download_button("Dados originais (.csv)", to_csv_bytes(dataframe), "dados_originais.csv", "text/csv", key="download_original_csv")
        downloads[1].download_button("Dados originais (.xlsx)", to_xlsx_bytes(dataframe, "Dados originais"), "dados_originais.xlsx", MIME_XLSX, key="download_original_xlsx")
    with diagnosis_tab:
        if issue_table.empty:
            st.success("Não há ocorrências para filtrar ou exportar.")
        else:
            filters = st.columns([1, 1, 1.4], gap="medium")
            rule_options = sorted(issue_table["Código"].unique())
            column_options = sorted(issue_table["Coluna"].unique())
            rules = filters[0].multiselect("Tipo de problema", rule_options, format_func=lambda value: f"{value} — {RULE_DESCRIPTIONS.get(value, value)}")
            columns = filters[1].multiselect("Coluna", column_options)
            search = filters[2].text_input("Buscar no diagnóstico", placeholder="Ex.: P003, preço, inválida")
            filtered = filter_issues(issue_table, rules, columns, search)
            st.caption(f"Exibindo {len(filtered)} de {len(issue_table)} ocorrências")
            st.dataframe(filtered, use_container_width=True, hide_index=True)
            downloads = st.columns(2, gap="medium")
            downloads[0].download_button("Diagnóstico completo (.csv)", to_csv_bytes(issue_table), "diagnostico_completo.csv", "text/csv", key="download_diagnosis_csv")
            downloads[1].download_button("Diagnóstico completo (.xlsx)", to_xlsx_bytes(issue_table, "Diagnóstico"), "diagnostico_completo.xlsx", MIME_XLSX, key="download_diagnosis_xlsx")
            downloads[0].download_button("Diagnóstico filtrado (.csv)", to_csv_bytes(filtered), "diagnostico_filtrado.csv", "text/csv", key="download_filtered_csv")
            downloads[1].download_button("Diagnóstico filtrado (.xlsx)", to_xlsx_bytes(filtered, "Diagnóstico filtrado"), "diagnostico_filtrado.xlsx", MIME_XLSX, key="download_filtered_xlsx")
    with correction_tab:
        st.markdown('<p class="section-note">A cópia tratada inclui apenas ajustes determinísticos e auditáveis. O arquivo original permanece intacto.</p>', unsafe_allow_html=True)
        if change_log.empty:
            st.info("Nenhuma correção determinística segura foi identificada. Valores ambíguos ou inválidos continuam para revisão humana.")
        else:
            st.success(f"{len(change_log)} ajuste(s) seguro(s) identificado(s). Confira o histórico antes de utilizar a cópia.")
            st.dataframe(change_log, use_container_width=True, hide_index=True)
            downloads = st.columns(2, gap="medium")
            downloads[0].download_button("Baixar cópia corrigida (.csv)", to_csv_bytes(corrected), "produtos_corrigidos.csv", "text/csv", type="primary")
            downloads[1].download_button("Baixar cópia corrigida (.xlsx)", to_xlsx_bytes(corrected, "Produtos"), "produtos_corrigidos.xlsx", MIME_XLSX)
            downloads = st.columns(2, gap="medium")
            downloads[0].download_button("Histórico de alterações (.csv)", to_csv_bytes(change_log), "historico_correcoes.csv", "text/csv", key="download_change_log_csv")
            downloads[1].download_button("Histórico de alterações (.xlsx)", to_xlsx_bytes(change_log, "Histórico"), "historico_correcoes.xlsx", MIME_XLSX, key="download_change_log_xlsx")
            remaining = validate_dataframe(corrected)
            st.caption(f"Após os ajustes seguros, {len(remaining)} ocorrência(s) continuam detectadas e podem exigir revisão manual.")
    if issues:
        render_ai_assistant(issues)


def main() -> None:
    st.set_page_config(page_title="Data Quality Agent", page_icon="🔎", layout="wide", initial_sidebar_state="expanded")
    render_styles()
    with st.sidebar:
        st.markdown("## Data Quality Agent")
        st.caption("Diagnóstico e tratamento seguro de bases de produtos")
        uploaded_file = st.file_uploader("Carregue sua planilha", type=["csv", "xlsx"], help="Formatos aceitos: CSV e Excel (.xlsx).")
        st.divider()
        st.markdown("**Regras verificadas**")
        st.caption("Campos obrigatórios · IDs duplicados · preço · estoque · categoria · data · estrutura")
        st.info("Use dados fictícios, anonimizados ou autorizados.")
        st.caption("O diagnóstico e as orientações locais funcionam sem serviços externos ou chaves de API.")
    st.markdown('<section class="hero"><div class="hero-kicker">Qualidade de dados · diagnóstico e ação</div><h1>Dados confiáveis começam com uma boa validação.</h1><p>Identifique inconsistências, entenda o impacto e exporte resultados. Ajustes seguros ficam registrados em uma cópia; decisões ambíguas continuam sob revisão humana.</p></section>', unsafe_allow_html=True)
    if uploaded_file is None:
        render_empty_state()
        return
    try:
        dataframe = load_uploaded_file(uploaded_file, uploaded_file.name)
    except (ValueError, OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        st.error(f"Não foi possível ler o arquivo: {error}")
        return
    render_analysis(dataframe, uploaded_file.name)


if __name__ == "__main__":
    main()
