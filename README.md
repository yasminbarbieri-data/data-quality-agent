# Data Quality Agent

Ferramenta em Python para verificar a qualidade de dados tabulares em arquivos CSV e Excel, identificar inconsistências e gerar relatórios de ocorrências.

## Objetivo

Dados inconsistentes podem comprometer análises, relatórios e decisões de negócio. O Data Quality Agent automatiza verificações básicas de qualidade, tornando os problemas mais fáceis de identificar e investigar.

O projeto utiliza regras determinísticas: os resultados são produzidos por validações explícitas, sem depender de um modelo de inteligência artificial.

## Funcionalidades

- Leitura de arquivos CSV e Excel (`.xlsx`).
- Verificação de campos obrigatórios.
- Identificação de IDs duplicados.
- Validação de preços e quantidades em estoque.
- Verificação de categorias permitidas.
- Validação de datas.
- Verificação da presença das colunas obrigatórias.
- Geração de relatórios CSV.
- Resumo das ocorrências por regra.
- Testes automatizados com pytest.

## Tecnologias

- Python
- pandas
- openpyxl
- pytest
- Git

## Regras de validação

| Regra | Descrição |
|---|---|
| R01 | Campos obrigatórios vazios |
| R02 | IDs de produto duplicados |
| R03 | Preços ausentes, inválidos ou menores ou iguais a zero |
| R04 | Quantidades de estoque negativas, inválidas ou não inteiras |
| R05 | Categorias fora da lista permitida |
| R06 | Datas inválidas |
| R07 | Colunas obrigatórias ausentes |

## Estrutura do projeto

```text
data-quality-agent/
├── data/
│   └── samples/
├── docs/
├── reports/
├── src/
│   └── data_quality_agent/
├── tests/
├── .gitignore
└── pyproject.toml
```

## Instalação

Recomenda-se utilizar um ambiente virtual.

No Windows, a partir da raiz do projeto:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -e .
python -m pip install pytest
```

## Execução

Analise um arquivo com inconsistências:

```cmd
python -m data_quality_agent.cli data/samples/products_with_issues.csv
```

Analise um arquivo válido e defina o caminho do relatório:

```cmd
python -m data_quality_agent.cli data/samples/products_valid.csv --saida reports/valid_issues.csv
```

Os relatórios são gerados durante a execução e não são versionados pelo Git.

## Testes

Execute a suíte automatizada:

```cmd
python -m pytest -v
```

Na última execução registrada durante o desenvolvimento, os 21 testes passaram. Execute os testes novamente após alterações para confirmar o estado atual.

## Limitações atuais

- As regras são definidas explicitamente no código.
- As categorias permitidas são configuradas para o conjunto de dados de exemplo.
- A ferramenta ainda não possui interface gráfica.
- Não há integração com modelos de inteligência artificial.
- A ausência de ocorrências significa apenas que os dados passaram pelas regras implementadas; não garante a qualidade absoluta dos dados.

## Próximas evoluções

- Criar uma interface com Streamlit.
- Melhorar a configuração das regras.
- Ampliar os testes para outros casos-limite.
- Avaliar uma camada de IA para explicar as ocorrências em linguagem natural, sem substituir as validações determinísticas.

## Dados de exemplo

Os arquivos de demonstração utilizam dados sintéticos. Não utilize dados confidenciais ou pessoais nos exemplos publicados.

## Licença

A licença do projeto ainda não foi definida.