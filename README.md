# Data Quality Agent

Aplicação em Python e Streamlit para diagnosticar problemas de qualidade em bases de produtos, aplicar somente correções determinísticas auditáveis e exportar resultados para revisão.

## O que o projeto faz

- Lê arquivos CSV e Excel (`.xlsx`).
- Valida a estrutura e as regras R01–R07: campos obrigatórios vazios, IDs duplicados, preço inválido, estoque inválido, categoria não permitida, data inválida e coluna obrigatória ausente.
- Apresenta indicadores, gráfico de ocorrências, prioridades de revisão e diagnóstico filtrável por regra, coluna e texto.
- Permite exportar os dados originais, o diagnóstico completo, o diagnóstico filtrado, a cópia tratada e o histórico de alterações em CSV ou XLSX.
- Corrige apenas casos determinísticos, como espaços externos em campos textuais não identificadores e normalização inequívoca de maiúsculas/minúsculas em categorias permitidas.
- Inclui orientações locais gratuitas e um assistente de IA opcional para explicar o diagnóstico agregado.

## Limites e segurança

- A versão atual é especializada em bases de produtos e espera estas colunas exatas: `id_produto`, `nome_produto`, `categoria`, `preco`, `quantidade_estoque`, `data_atualizacao`.
- As categorias permitidas são `Perifericos`, `Monitores` e `Mobiliario`.
- O arquivo original nunca é sobrescrito. A cópia tratada é um resultado separado.
- As exportações são produzidas a partir da visualização atual, mas não modificam o arquivo nem o DataFrame recebido.
- O sistema não inventa valores para campos vazios, preços, IDs duplicados, estoque inválido ou datas ambíguas. Esses casos continuam para revisão humana.
- O aplicativo não depende de serviços externos nem de chaves de API. O assistente oferece orientações locais, inclusive sem internet.
- O processamento e as orientações acontecem localmente; nenhuma planilha ou resumo é enviado a uma API externa.
- As orientações são recomendações gerais baseadas nas regras detectadas. Revise os dados antes de utilizá-los.
- Use apenas dados fictícios, anonimizados ou autorizados.

## Instalação no Windows

Requer Python 3.11 ou superior. A interface usa Streamlit 1.65 ou superior.

1. Extraia o ZIP para uma pasta fácil de encontrar, por exemplo `Documentos\Projetos\data-quality-agent`.
2. Abra essa pasta no VS Code. **A pasta correta é aquela que contém `app.py` e `pyproject.toml`.**
3. Abra o terminal do VS Code em **Terminal → Novo Terminal**.
4. Crie e ative um ambiente virtual. No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, abra o terminal **Command Prompt (cmd)** e execute:

```cmd
.venv\Scripts\activate.bat
```

5. Instale o projeto e as dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

6. Inicie o aplicativo:

```powershell
streamlit run app.py
```

O navegador normalmente abrirá `http://localhost:8501`. Mantenha o terminal aberto enquanto utiliza a aplicação.

### Se o terminal abrir na pasta errada

Use o Explorer do VS Code: clique com o botão direito na pasta que contém `app.py` e escolha **Open in Integrated Terminal**. Não execute `pip install` na pasta externa que contém apenas a pasta do projeto.

## Executar os testes

Na pasta que contém `app.py`:

```powershell
python -m pytest -v
```

## Arquivos de demonstração

- `data/samples/products_with_issues.csv`: inconsistências intencionais e exemplos de ajustes seguros, como espaços externos e categoria em caixa diferente. A contagem esperada é explícita para evitar divergências entre a tela, os testes e a documentação:

| Regra | Ocorrências | Situação após ajustes seguros |
|---|---:|---:|
| R01 — campo obrigatório vazio | 1 | 1 permanece para revisão humana |
| R02 — ID duplicado | 2 | 2 permanecem para revisão humana |
| R03 — preço inválido | 1 | 1 permanece para revisão humana |
| R04 — estoque inválido | 1 | 1 permanece para revisão humana |
| R05 — categoria não permitida | 2 | 1 permanece; a outra é uma normalização inequívoca de `perifericos` para `Perifericos` |
| R06 — data inválida | 1 | 1 permanece para revisão humana |
| **Total** | **8** | **7 permanecem após 2 ajustes seguros** |

O outro ajuste seguro é a remoção dos espaços externos em `nome_produto`; ele é registrado no histórico, mas não elimina uma ocorrência porque o valor já não era considerado vazio.

- `data/samples/products_valid.csv`: base sem problemas detectáveis pelas regras implementadas.

## Acessibilidade e interface

- A interface usa tema de alto contraste, bordas visíveis e componentes nativos do Streamlit.
- Gráficos e tabelas recebem descrições curtas para tecnologias assistivas.
- Os controles mantêm rótulos visíveis e as ações de download identificam conteúdo e formato.

## Estrutura principal

```text
app.py
src/data_quality_agent/
  ai_assistant.py
  corrections.py
  file_reader.py
  pipeline.py
  reporting.py
  validators.py
tests/
data/samples/
```

## Escopo atual

O aplicativo é um protótipo funcional de validação de dados para catálogo de produtos. Ele não é um corretor genérico para qualquer planilha, não conecta automaticamente a bancos de dados e não deve ser usado como substituto de validação de negócio ou revisão humana.
