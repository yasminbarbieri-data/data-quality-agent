"""Assistente opcional para explicar diagnósticos sem alterar dados.

A chamada externa é explicitamente acionada pela pessoa usuária. Somente um resumo
agregado das regras é enviado ao provedor; valores de células e linhas não são enviados.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RULE_GUIDANCE = {
    "R01": "Campo obrigatório vazio: recuperar o valor em uma fonte confiável; não inventar conteúdo.",
    "R02": "ID duplicado: comparar os registros e decidir se são duplicidade real ou itens distintos; não excluir automaticamente.",
    "R03": "Preço inválido: confirmar o preço em uma fonte oficial; não substituir por estimativa.",
    "R04": "Estoque inválido: conferir a origem do saldo e a regra de negócio; não arredondar ou zerar sem autorização.",
    "R05": "Categoria fora do padrão: mapear apenas quando houver correspondência inequívoca com a lista permitida.",
    "R06": "Data inválida: confirmar a data correta na origem; não adivinhar datas.",
    "R07": "Coluna obrigatória ausente: corrigir o mapeamento/estrutura do arquivo antes de analisar os registros.",
}


def build_local_guidance(issues: list[dict]) -> list[dict[str, str | int]]:
    """Produz orientações locais e determinísticas, sem conexão externa."""
    counts: dict[str, int] = {}
    for issue in issues:
        code = str(issue.get("regra", ""))
        counts[code] = counts.get(code, 0) + 1
    return [
        {"regra": code, "ocorrencias": count, "orientacao": RULE_GUIDANCE.get(code, "Revisar conforme a regra de validação.")}
        for code, count in sorted(counts.items())
    ]


def ask_ai_about_issues(issues: list[dict], api_key: str | None = None, model: str = "gpt-4.1-mini") -> str:
    """Pede explicação à API OpenAI usando apenas códigos, descrições e contagens agregadas.

    Não envia nomes de arquivo, valores encontrados, IDs ou conteúdo bruto da planilha.
    Requer consentimento explícito da pessoa usuária na interface e uma chave válida.
    """
    key = (api_key or os.getenv("OPENAI_API_KEY", "")).strip()
    if not key:
        raise ValueError("Informe uma chave de API para usar a assistência de IA.")

    counts: dict[str, int] = {}
    descriptions: dict[str, str] = {}
    for issue in issues:
        code = str(issue.get("regra", ""))
        counts[code] = counts.get(code, 0) + 1
        descriptions[code] = str(issue.get("descricao", RULE_GUIDANCE.get(code, "Regra de validação.")))
    safe_summary = [{"regra": code, "ocorrencias": count, "descricao_da_regra": descriptions.get(code, "")}
                    for code, count in sorted(counts.items())]
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": (
                "Você é um assistente de qualidade de dados. Explique em português brasileiro, "
                "com clareza para pessoas não técnicas. Receberá apenas códigos de regra, contagens "
                "e descrições, não os dados da planilha. Nunca invente valores corretos. Separe "
                "correções determinísticas de decisões que exigem revisão humana. Não afirme que "
                "alterou arquivos. Entregue: resumo, prioridades e próximos passos seguros."
            )},
            {"role": "user", "content": "Explique este resumo agregado do diagnóstico: " + json.dumps(safe_summary, ensure_ascii=False)},
        ],
    }
    request = Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=35) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise ValueError("A API recusou a chave informada. Confira as permissões e o saldo da conta.") from exc
        raise RuntimeError(f"A API de IA retornou um erro HTTP ({exc.code}).") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Não foi possível conectar à API de IA. Confira a conexão e tente novamente.") from exc
    try:
        return str(result["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("A resposta da API veio em um formato inesperado.") from exc
