---
name: research-question
description: "Transforma um tema em pergunta de pesquisa: constructos, população, desfechos, dados, hipóteses rotuladas e estratégias de identificação. Use para \"definir pergunta\", \"formular hipóteses\", \"PICO\"."
argument-hint: "[tema ou pergunta preliminar]"
---

# Research Question

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

**Regra específica:** hipóteses causais são **conjecturas a testar**, nunca fatos. Toda
hipótese recebe o rótulo `[HIPÓTESE]` e, se inspirada em literatura, a referência só é
citada depois de verificada; caso contrário, rotule como [INFERÊNCIA].

## Quando usar

- Tema ainda amplo ("efeito da regulação tarifária sobre eficiência energética").
- Precisa de pergunta respondível com dados disponíveis.
- Precisa escolher entre perguntas descritivas, associativas, causais ou normativas.

## Quando NÃO usar

- A pergunta já está fechada e o usuário quer buscar literatura → `literature-search`.
- O usuário quer avaliar um desenho já implementado → `methodology-review`.

## Inputs esperados

Tema; contexto (país, setor, regulador); finalidade (artigo, AIR, ARR, dissertação);
restrições de dados/prazo; opcionalmente literatura já conhecida.

## Workflow

1. **Classificar o tipo de pergunta**: descritiva · associativa · causal · preditiva ·
   normativa/regulatória · avaliativa (resultado de política/ARR). Explicar implicações.
2. **Decompor em elementos** (adaptar PICO/PECO ao contexto):
   | Elemento | Pergunta-guia |
   |---|---|
   | População / unidade de análise | Quem ou o quê? (consumidores, distribuidoras, municípios, contratos) |
   | Intervenção / exposição | Qual política, mecanismo, regra, evento? |
   | Comparação / contrafactual | Contra o quê? (sem política, antes, outro desenho) |
   | Desfechos (outcomes) | O que muda? Com qual métrica e unidade? |
   | Contexto | Jurisdição, setor, período, arranjo institucional |
   | Horizonte | Curto/longo prazo; defasagens esperadas |
3. **Constructos e operacionalização**: para cada constructo, possíveis métricas e
   fontes de dados (marcar fontes de dados como "a verificar" até confirmadas).
4. **Hipóteses** `[HIPÓTESE]` com mecanismo teórico explícito e sinal esperado; incluir
   hipóteses alternativas/rivais.
5. **Estratégias de identificação candidatas** (se pergunta causal): DiD/event study,
   controle sintético, RDD, IV, RCT/experimento natural, painel com efeitos fixos,
   matching — para cada uma: premissa-chave, variação exógena necessária, ameaça principal,
   dado mínimo necessário.
6. **Viabilidade**: dados existem? granularidade? período pré/pós suficiente? poder?
7. **Versões da pergunta**: proponha 2–3 formulações (ambiciosa, factível, mínima).
8. Salvar em `research/protocol.md` (seção "Pergunta") se o projeto existir;
   template: `${CLAUDE_PLUGIN_ROOT}/templates/research-protocol.md`.

## Output esperado

```markdown
## Pergunta de pesquisa (versão recomendada)
...
## Tipo: causal | associativa | ...
## Elementos (tabela)
## Constructos → métricas → dados (status de verificação da fonte de dados)
## Hipóteses [HIPÓTESE] + mecanismo + hipóteses rivais
## Estratégias de identificação candidatas (tabela premissa/ameaça/dado)
## Riscos e lacunas
## Próximo passo sugerido
```

## Critérios de qualidade

- Pergunta respondível, delimitada no tempo/espaço, com desfecho mensurável.
- Linguagem causal só se o desenho proposto puder identificar causalidade.
- Nenhuma afirmação empírica sem fonte verificada; sem fonte → [INFERÊNCIA].

## Situações de falha

- Tema amplo demais e usuário não fornece contexto → faça no máximo 3 perguntas objetivas.
- Dados necessários provavelmente inexistentes → diga explicitamente e proponha pergunta
  alternativa (ex.: descritiva) em vez de supor que os dados existem.
