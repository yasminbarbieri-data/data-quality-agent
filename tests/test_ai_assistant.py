from data_quality_agent.ai_assistant import build_local_guidance


def test_local_guidance_summarizes_rules_without_external_ai():
    issues = [
        {"regra": "R02", "descricao": "ID duplicado"},
        {"regra": "R02", "descricao": "ID duplicado"},
        {"regra": "R03", "descricao": "Preço inválido"},
    ]
    result = build_local_guidance(issues)
    assert result == [
        {"regra": "R02", "ocorrencias": 2, "orientacao": "ID duplicado: comparar os registros e decidir se são duplicidade real ou itens distintos; não excluir automaticamente."},
        {"regra": "R03", "ocorrencias": 1, "orientacao": "Preço inválido: confirmar o preço em uma fonte oficial; não substituir por estimativa."},
    ]


def test_ai_requires_api_key_before_network_call():
    from data_quality_agent.ai_assistant import ask_ai_about_issues
    import pytest
    with pytest.raises(ValueError, match="chave de API"):
        ask_ai_about_issues([], api_key="")
