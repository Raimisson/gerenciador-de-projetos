---
name: evidence-synthesis
description: "Síntese da literatura por desfecho, força da evidência e portão de viabilidade de meta-análise (sem combinar coeficientes incompatíveis). Use para \"sintetizar a literatura\", \"o que a evidência diz\", \"meta-análise?\"."
argument-hint: "[pergunta] [--meta-feasibility]"
---

# Evidence Synthesis

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

- Há matriz de evidências e avaliações metodológicas; é preciso dizer o que o conjunto mostra.
- O usuário pergunta se é possível fazer meta-análise.

## Quando NÃO usar

- Sem extração/ledger → primeiro `evidence-extraction` e `evidence-ledger`.
- Redação final do texto → `scientific-writing` (usa esta síntese como insumo).

## Inputs esperados

`research/matrix/*`, `research/ledger/evidence.jsonl`, `research/appraisal/*`, pergunta.

## Workflow

1. **Agrupar** estudos por desfecho × tipo de intervenção × desenho.
2. **Para cada grupo**, reportar:
   - n de estudos e de estimativas; contextos (países/períodos);
   - direção dos resultados (contagem por sinal/significância como reportada — *vote
     counting* só descritivo, nunca como teste);
   - faixa de magnitudes **na mesma unidade** (se unidades diferem, listar separadamente);
   - qualidade/risco de viés (de `methodology-review`);
   - consistência e possíveis explicações para heterogeneidade [INFERÊNCIA];
   - força da evidência: `forte` · `moderada` · `limitada` · `insuficiente`, com critério explícito
     (desenho, consistência, precisão, aplicabilidade).
3. **Separar** em cada parágrafo [FONTE] / [AUTORES] / [INFERÊNCIA] e citar `E-…`.
4. **Lacunas**: perguntas sem evidência quantitativa → frase padrão:
   "Não foi encontrada evidência quantitativa que permita estimar este parâmetro."
5. **Aplicabilidade ao contexto do usuário** (ex.: Brasil) como [INFERÊNCIA], discutindo
   diferenças institucionais.

## Portão de viabilidade de meta-análise (obrigatório antes de qualquer pooling)

| Critério | Pergunta | Resultado |
|---|---|---|
| Outcome | Mesmo construto e mesma métrica? | sim/não/parcial |
| Unidade/escala | Mesma unidade (ou conversão válida e documentada)? | |
| Estimand | ATE/ATT/LATE/associação comparáveis? | |
| Desenho | Desenhos com vieses comparáveis? | |
| População/unidade de análise | Comparáveis? | |
| Intervenção/contraste | Mesma intervenção e comparador? | |
| Medida de precisão | EP/IC disponíveis para todos? | |
| Heterogeneidade | Heterogeneidade esperada é interpretável? | |
| Número de estudos | ≥ mínimo razoável e independentes (não mesma amostra)? | |

Resultado: `viável` · `viável para subconjunto` · `não viável`. **Na v0.1 o plugin não
calcula efeitos combinados.** Se viável, entregue a tabela de insumos (estimativa, EP,
unidade) e recomende software estatístico (ex.: `metafor` em R) com script documentado,
executado e revisado por humano. Nunca combinar coeficientes incompatíveis (ex.:
elasticidade + variação percentual; kWh/cliente + % do consumo; ITT + ATT).

## Output esperado

`research/synthesis/synthesis.md`: síntese por grupo, tabela de força da evidência,
lacunas, portão de meta-análise (se pedido), referências a `E-…`.

## Critérios de qualidade

- Toda afirmação sintética rastreável a `E-…`.
- Nenhuma média/agregação entre unidades diferentes.
- Divergências entre estudos expostas, não suavizadas.

## Situações de falha

- Evidência insuficiente → dizer claramente; não "preencher" com raciocínio teórico
  apresentado como evidência.
- Estudos dependentes (mesma base/amostra) → não contar como evidência independente.
