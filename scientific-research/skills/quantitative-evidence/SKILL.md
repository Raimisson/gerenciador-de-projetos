---
name: quantitative-evidence
description: Localiza e extrai evidência quantitativa de estudos — equações, fórmulas, parâmetros, elasticidades, coeficientes, erros-padrão, intervalos, testes, resultados de regressão, relações custo-benefício, estatísticas descritivas — sempre com página/tabela/figura, unidade e especificação; também define regras para análises reproduzíveis de dados. Use para "extrair coeficientes", "elasticidade", "resultados de regressão", "tabela de resultados", "quanto reduziu", "custo por kWh economizado", "números do estudo", "quantitative evidence".
argument-hint: "[estudo/PDF/DOI] [--parametro nome]"
---

# Quantitative Evidence

<!-- integrity:start -->
## Regras de integridade (não negociáveis)

1. Não inventar artigos, DOI, autores, periódicos, páginas, datas, URLs, números ou resultados. Memória do modelo não é fonte.
2. Informação não confirmada → "Não foi possível verificar esta informação nas fontes consultadas."
3. Sem evidência quantitativa → "Não foi encontrada evidência quantitativa que permita estimar este parâmetro."
4. Campo ausente → `NR — não reportado`; nunca inferir sem rotular como [INFERÊNCIA].
5. Separar **[FONTE]**, **[AUTORES]** e **[INFERÊNCIA]**.
6. Status: `VERIFIED` · `PARTIALLY_VERIFIED` · `UNVERIFIED` · `CONTRADICTED` · `NOT_REPORTED`.
7. Texto integral prevalece sobre abstract; registrar página/tabela/figura ou declarar que a página não é identificável.

Referência completa: `${CLAUDE_PLUGIN_ROOT}/docs/scientific-method.md`.
<!-- integrity:end -->

## Quando usar

- O usuário quer números de estudos (efeitos, elasticidades, custos, parâmetros).
- Estudo com várias tabelas/especificações que exige extração cuidadosa.
- Preparar parâmetros para análise própria (ex.: calibração, AIR).

## Quando NÃO usar

- Ficha geral do estudo sem foco numérico → `evidence-extraction`.
- Combinar estimativas entre estudos → `evidence-synthesis` (portão de viabilidade).

## Inputs esperados

Texto integral (tabelas e apêndices), parâmetro de interesse, unidade desejada.

## Regras específicas

1. **Número como reportado**: sinal, casas decimais, unidade, escala (ex.: "×100",
   "em log", "US$ de 2010"). Converter só como [INFERÊNCIA] explícita, com fórmula.
2. **Especificação completa** para cada estimativa: variável dependente, explicativa,
   controles/efeitos fixos, amostra, período, estimador, cluster do EP, tratamento e
   controle, desenho de identificação.
3. **Denominador** sempre que houver taxa/percentual/"por cliente".
4. **Significância**: registrar a convenção do artigo (estrelas, p, IC). Estrelas sem
   p-valor → `p_value: "NR — não reportado"`, `significance: "*** (p<0.01, convenção do artigo)"`.
5. **Nunca** transformar descrição qualitativa em número.
6. Se não houver número: "Não foi encontrada evidência quantitativa que permita estimar este parâmetro."
7. Preferir a especificação que **os autores** apresentam como principal; outras vão
   como robustez, identificadas.

## Checklist de extração por estimativa

`estimate`, `unit`, `denominator`, `se`, `ci_low`/`ci_high` (nível do IC), `p_value`,
`significance`, `n` (e unidade de N: observações, clusters), `period`, `model`,
`specification`, `dependent_variable`, `explanatory_variable`, `treatment_group`,
`control_group`, `identification`, `location{page,table,figure,section}`, `excerpt`.

Equações: transcrever em LaTeX com numeração do artigo (ex.: "Eq. (3), p. 12") e
definir cada símbolo como o artigo define.

## Workflow

1. Mapear todas as tabelas/figuras com resultados; listar quais respondem à pergunta.
2. Extrair para `estimates[]` da ficha (`research/extraction/<S-id>.json`).
3. Validar (`srtool.py validate extraction`): checa localização, trecho e presença do
   número no trecho.
4. Registrar no ledger as estimativas que serão usadas.

## Análise de dados reproduzível (quando o usuário analisa dados próprios)

- Dados brutos em `research/data/raw/` são **imutáveis** (o hook do plugin pede
  confirmação antes de alterá-los). Transformações → `research/data/derived/` via script.
- Todo resultado gerado registra: script, insumos (com hash ou data), parâmetros, seed,
  versões (Python/R/pacotes), saída. Template: `${CLAUDE_PLUGIN_ROOT}/templates/analysis-run-log.md`.
- Nunca "limpar" outliers, imputar ou filtrar sem registrar critério e contagem afetada.

## Output esperado

Tabela de estimativas com localização + equações transcritas + lacunas (`NR`) +
observações sobre comparabilidade de unidades.

## Critérios de qualidade

- 100% das estimativas com localização, unidade e trecho.
- Nenhuma conversão silenciosa.
- Estimativas de robustez distinguidas da principal.

## Situações de falha

- Tabela ilegível/escaneada → não estimar valores; pedir versão legível.
- Unidade ambígua (ex.: moeda ausente no texto extraído) → `unit: "NR — não reportado"` +
  nota explicando a ambiguidade.
