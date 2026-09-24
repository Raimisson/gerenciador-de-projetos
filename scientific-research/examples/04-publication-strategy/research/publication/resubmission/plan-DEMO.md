# Plano de ressubmissão — DEMONSTRAÇÃO (decisão fictícia)

> Cenário fictício para demonstrar a skill `resubmission-strategy`. Nenhum periódico real tomou esta decisão.

## Decisão recebida (fictícia)
Periódico: Utilities Policy · tipo: desk rejection · trecho da carta (fictício):
"The manuscript does not report new empirical findings and falls outside the types of contribution the journal currently prioritises."

## Motivos (trechos literais)
| # | Trecho | Categoria |
|---|---|---|
| 1 | "does not report new empirical findings" | contribuição |
| 2 | "types of contribution the journal currently prioritises" | escopo / tipo de artigo |

## Melhorias científicas a incorporar (independem do periódico)
- Ler e extrair von Loessl & Wetzel (2022) e Datta (2019) — lacuna científica real do manuscrito.
- Estender a busca (ver R2.1 da rodada fictícia).

## Preferências do periódico anterior (não necessariamente transferíveis)
- Preferência por achados empíricos originais.

## Próximo periódico
- Reutilizar `journals/candidates.json`. Rejeição por **tipo de contribuição** ⇒ priorizar candidatos cujo
  aims & scope aceite revisões/policy analyses (Contribution e Article-Type Fit passam a ter peso maior).
- Todos os candidatos estão com aims & scope `NOT VERIFIED`: executar `journal-requirements` e
  `journal-fit-analysis` antes de escolher. Nenhuma probabilidade de aceitação é estimada.
- Após escolher: `pubtool.py target set research/publication --journal <novo-slug>`, depois
  `manuscript-compliance` e `pre-submission-audit` com regras reconsultadas.
