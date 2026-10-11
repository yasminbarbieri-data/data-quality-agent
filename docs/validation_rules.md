# Data Quality Agent — Regras de Validação

## 1. Objetivo

Definir as regras usadas pelo Data Quality Agent para verificar a qualidade dos dados de produtos e estoque de uma distribuidora fictícia.

As regras são explícitas e determinísticas. A IA poderá explicar os problemas identificados em uma etapa futura, mas não será responsável por decidir sozinha se um registro é válido.

## 2. Estrutura esperada

O arquivo deve conter as seguintes colunas:

| Coluna | Tipo esperado | Regra |
|---|---|---|
| `id_produto` | Texto | Obrigatório e único |
| `nome_produto` | Texto | Obrigatório e não vazio |
| `categoria` | Texto | Obrigatória e pertencente às categorias permitidas |
| `preco` | Numérico | Obrigatório e maior que zero |
| `quantidade_estoque` | Inteiro | Obrigatória e maior ou igual a zero |
| `data_atualizacao` | Data | Obrigatória e válida |

## 3. Categorias permitidas

- `Perifericos`
- `Monitores`
- `Mobiliario`

Na primeira versão, os valores serão comparados com essa lista explícita.

## 4. Regras de validação

### R01 — Campos obrigatórios

Identificar valores ausentes ou vazios nas colunas obrigatórias.

### R02 — Identificadores duplicados

Identificar IDs de produto repetidos e registrar todas as linhas envolvidas.

### R03 — Preço válido

O preço deve ser numérico e maior que zero.

### R04 — Quantidade de estoque válida

A quantidade deve ser um número inteiro maior ou igual a zero.

### R05 — Categoria permitida

A categoria deve corresponder a um dos valores definidos na lista de categorias permitidas.

### R06 — Data válida

A data deve corresponder a uma data de calendário válida no formato `AAAA-MM-DD`.

### R07 — Estrutura do arquivo

Verificar a existência de todas as colunas obrigatórias. Se uma coluna estiver ausente ou o arquivo não puder ser interpretado, interromper a análise de forma controlada.

## 5. Limites do sistema

- O arquivo original não deve ser alterado.
- Os dados usados na demonstração devem ser fictícios.
- A ferramenta deve registrar as ocorrências sem corrigir automaticamente os valores.
- A IA, quando adicionada, poderá explicar os problemas e sugerir investigações, mas não deverá inventar informações nem substituir as regras de validação.
- Um registro sem problemas detectados não é necessariamente perfeito: ele apenas passou pelas verificações implementadas.

## 6. Critérios de qualidade

A ferramenta deverá identificar os problemas previstos nos testes, preservar os registros originais e gerar relatórios consistentes.

Os resultados serão comparados com os problemas conhecidos dos arquivos de teste para avaliar detecções corretas, problemas não detectados e falsos positivos.

## 7. Dados de teste

- `products_valid.csv`: contém cinco registros que devem passar pelas regras.
- `products_with_issues.csv`: contém problemas intencionais para verificar o funcionamento das validações.