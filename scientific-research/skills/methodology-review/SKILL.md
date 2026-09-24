---
name: methodology-review
description: Avaliação crítica da metodologia de estudos empíricos — seleção, endogeneidade, causalidade reversa, viés de variável omitida, erro de mensuração, tendências paralelas, suporte comum, validade de instrumentos, robustez, heterogeneidade, poder estatístico, validade interna e externa — com justificativa técnica para cada problema apontado. Use para "avaliar metodologia", "risco de viés", "critical appraisal", "o desenho identifica causalidade?", "revisar estratégia empírica", "methodology review".
argument-hint: "[estudo/ficha S-0001 ou manuscrito] [--profundidade rapida|completa]"
---

# Methodology Review

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

- Após a extração, para qualificar o peso de cada estudo na síntese.
- Para revisar a metodologia do próprio manuscrito do usuário.

## Quando NÃO usar

- Só há abstract → no máximo uma **avaliação preliminar** rotulada como tal. Não avaliar
  o estudo com base apenas no abstract quando o texto integral estiver disponível.
- Verificação de números/tabelas do manuscrito → `manuscript-review`.

## Inputs esperados

Texto integral (preferível) ou ficha de extração; pergunta de pesquisa; opcional:
apêndices, código, dados.

## Regras específicas

1. **Toda crítica tem justificativa técnica e localização**: "o teste de tendências
   paralelas não é reportado (seção 4, Tabela 3 mostra só o pós-tratamento)" — nunca
   "o estudo tem problemas de endogeneidade" sem explicar o mecanismo.
2. **Distinguir**: (a) problema demonstrado no texto; (b) ameaça plausível não endereçada;
   (c) ameaça endereçada pelos autores (e como). Não atribuir falha que os autores já trataram.
3. Avaliar em relação à **pergunta do estudo**, não à pergunta do usuário (esta vai em
   "aplicabilidade").
4. Linguagem calibrada: "ameaça potencial", "não é possível descartar", "os autores não reportam".

## Checklist por desenho (aplicar o que couber)

| Tema | O que examinar |
|---|---|
| Seleção | quem entra na amostra/tratamento; auto-seleção; atrito |
| Endogeneidade | fonte de variação; simultaneidade; causalidade reversa |
| Variável omitida | confundidores plausíveis; efeitos fixos; controles "ruins" (pós-tratamento) |
| Mensuração | proxies; erro clássico vs. não clássico; savings "declaradas" vs. medidas (EM&V) |
| DiD / event study | tendências paralelas (pré-tendências), antecipação, tratamento escalonado (TWFE com efeitos heterogêneos — estimadores robustos?), clusterização |
| Matching / PSM | suporte comum, balanceamento pós-matching, seleção em não observáveis |
| IV | relevância (F de 1º estágio), exclusão, monotonicidade, LATE vs. ATE |
| RDD | manipulação (densidade), bandwidth, continuidade de covariáveis |
| Controle sintético | ajuste pré-tratamento, placebo, doadores |
| RCT | randomização, compliance, spillovers, atrito diferencial |
| Simulação / CBA ex ante | premissas, sensibilidade, origem dos parâmetros; **não identifica efeito observado** |
| Inferência | erros-padrão (cluster, heterocedasticidade), múltiplos testes, poder |
| Robustez | especificações alternativas, amostras, placebo, falsificação |
| Heterogeneidade | subgrupos pré-especificados vs. exploratórios |
| Validade externa | contexto institucional/regulatório, período, população |

Template: `${CLAUDE_PLUGIN_ROOT}/templates/methodology-appraisal.md`.

## Workflow

1. Identificar o desenho e a estimand (ATE, ATT, LATE, associação).
2. Aplicar o checklist; para cada item: `endereçado` · `parcialmente` · `não endereçado` ·
   `não aplicável` · `não verificável` — com localização e justificativa.
3. Julgamento global de risco de viés: `baixo` · `moderado` · `alto` · `não avaliável`,
   justificando os itens determinantes. Se houver ferramenta formal apropriada
   (ROBINS-I, RoB 2), indicar e usar seus domínios sem alegar aplicação formal se não
   foi aplicada integralmente.
4. **Implicação para a síntese**: que tipo de afirmação o estudo sustenta (causal,
   associativa, descritiva, projeção).
5. Salvar em `research/appraisal/<source_id>.md`.

Para avaliações independentes (ex.: dois avaliadores), use o subagente
`methodology-reviewer` e compare as avaliações.

## Output esperado

Tabela do checklist + julgamento global + "o que o estudo permite afirmar" + dúvidas
que só o texto integral/dados resolveriam.

## Critérios de qualidade

- Nenhuma crítica sem mecanismo e localização.
- Avaliação com abstract apenas é rotulada **preliminar**.
- Julgamento proporcional; pontos fortes também registrados.

## Situações de falha

- Métodos descritos de forma insuficiente → `não verificável`, recomendar `replication-check`.
- Fora da expertise (ex.: métodos de outra área) → declarar a limitação.
