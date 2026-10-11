# Data Quality Agent

Ferramenta em Python para validação da qualidade de dados tabulares em arquivos CSV e Excel (`.xlsx`). Identifica inconsistências por meio de regras determinísticas e gera relatórios CSV para apoiar a análise e a correção dos dados.

## Objetivo

Dados inconsistentes podem comprometer relatórios, indicadores e decisões de negócio. O Data Quality Agent automatiza verificações básicas de qualidade, facilitando a identificação e a investigação de problemas antes que os dados sejam utilizados em análises.

O projeto utiliza validações explícitas em Python. Os resultados não dependem de modelos de inteligência artificial.

## Funcionalidades

- Leitura de arquivos CSV e Excel (`.xlsx`).
- Verificação de campos obrigatórios vazios.
- Identificação de IDs de produtos duplicados.
- Validação de preços e quantidades em estoque.
- Verificação de categorias permitidas.
- Validação de datas, incluindo datas inexistentes no calendário.
- Verificação de colunas obrigatórias.
- Geração de relatórios CSV com as ocorrências identificadas.
- Resumo das ocorrências por regra.
- Testes automatizados com `pytest`.

## Tecnologias

- **Python:** implementação das regras e do fluxo de processamento.
- **pandas:** leitura e manipulação dos dados tabulares.
- **openpyxl:** suporte a arquivos Excel.
- **pytest:** testes automatizados.
- **Git e GitHub:** versionamento e publicação do projeto.

## Regras de validação

| Regra | Descrição |
|---|---|
| R01 | Campos obrigatórios ausentes ou vazios |
| R02 | IDs de produto duplicados |
| R03 | Preços ausentes, não numéricos, infinitos ou menores ou iguais a zero |
| R04 | Quantidades de estoque inválidas, negativas ou não inteiras |
| R05 | Categorias fora da lista permitida |
| R06 | Datas inválidas ou fora do formato esperado |
| R07 | Colunas obrigatórias ausentes |

## Estrutura do projeto

```text
data-quality-agent/
├── data/
│   └── samples/
├── docs/
│   └── validation_rules.md
├── reports/
├── src/
│   └── data_quality_agent/
│       ├── file_reader.py
│       ├── validators.py
│       ├── reporting.py
│       ├── pipeline.py
│       └── cli.py
├── tests/
├── .gitignore
├── README.md
└── pyproject.toml
```

## Instalação

É necessário ter Python instalado. Os comandos abaixo consideram o Windows e a execução a partir da raiz do projeto.

Clone o repositório:

```cmd
git clone https://github.com/yasminbarbieri-data/data-quality-agent.git
cd data-quality-agent
```

Crie e ative um ambiente virtual:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

Instale o projeto e as dependências de execução:

```cmd
python -m pip install -e .
```

Instale o `pytest` para executar os testes:

```cmd
python -m pip install pytest
```

## Execução

### 1. Analisar um arquivo com inconsistências

```cmd
python -m data_quality_agent.cli data/samples/products_with_issues.csv
```

Resultado observado durante o desenvolvimento:

```text
Registros analisados: 6
Ocorrências encontradas: 7
Registros com problemas: 5
Registros sem problemas detectados: 1
```

O resumo por regra identificou:

| Regra | Ocorrências |
|---|---:|
| R01 | 1 |
| R02 | 2 |
| R03 | 1 |
| R04 | 1 |
| R05 | 1 |
| R06 | 1 |

O relatório é salvo por padrão em `reports/issues.csv`.

### 2. Analisar um arquivo sem ocorrências detectadas

```cmd
python -m data_quality_agent.cli data/samples/products_valid.csv --saida reports/valid_issues.csv
```

Resultado observado durante o desenvolvimento:

```text
Registros analisados: 5
Ocorrências encontradas: 0
Registros com problemas: 0
Registros sem problemas detectados: 5
```

O relatório é salvo em `reports/valid_issues.csv`.

Os relatórios são gerados durante a execução e não são versionados pelo Git.

## Testes automatizados

Para executar todos os testes:

```cmd
python -m pytest -v
```

Na última execução da suíte durante o desenvolvimento, **24 testes passaram**. Eles cobrem funcionalidades de leitura de arquivos, validações, geração de relatórios e integração do fluxo de processamento.

Execute os testes novamente após alterações para confirmar o estado atual do projeto.

## Limitações atuais

- As regras de validação são definidas explicitamente no código.
- As categorias permitidas correspondem ao conjunto de dados de exemplo e precisam ser adaptadas a outros contextos.
- A ferramenta ainda não possui interface gráfica.
- Não há integração com modelos de inteligência artificial.
- A ausência de ocorrências significa apenas que os dados passaram pelas regras implementadas; não garante sua qualidade absoluta.

## Próximas evoluções

- Desenvolver uma interface com Streamlit.
- Tornar a configuração das regras mais flexível.
- Ampliar os testes para outros casos-limite.
- Avaliar uma camada de IA para explicar ocorrências em linguagem natural, mantendo as validações determinísticas como base da análise.

## Dados de exemplo e privacidade

Os arquivos de demonstração utilizam dados sintéticos. Para testes e demonstrações públicas, prefira dados fictícios ou devidamente anonimizados. Não publique informações pessoais, confidenciais ou dados internos de empresas.

## Licença

A licença do projeto ainda não foi definida. Até que uma licença seja escolhida e adicionada ao repositório, não declare o projeto como licenciado sob uma licença específica de código aberto.
