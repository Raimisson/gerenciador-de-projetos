# Relatório de auditoria de citações — manuscrito de teste

- **Manuscrito:** `manuscript.md` (propositalmente defeituoso)
- **Data:** 2026-09-24
- **Cobertura:** completa (7 frases verificáveis, P-001 a P-004)
- **Ferramentas:** Scite MCP (metadados, abstracts, texto integral quando aberto) — real;
  `srtool.py scan` — real; `srtool.py doi-check` — com fixture de rede (Crossref bloqueado no
  ambiente de geração; repetir ao vivo).
- **JSON estruturado:** `citation-audit.json` (valida contra `schemas/citation-audit.schema.json`)

## Resumo

| Classe | n |
|---|---|
| SUPORTADA | 1 |
| PARCIALMENTE SUPORTADA | 2 |
| NÃO SUPORTADA | 3 |
| NÃO VERIFICÁVEL | 1 |

**Referência possivelmente inventada:** SILVA, J.; PEREIRA, M. (2019), *Journal of Imaginary
Energy Economics*, DOI 10.9999/jiee.2019.0457 — não encontrada no Scite por DOI nem por título
exato; `doi-check` → `CONTRADICTED` (`DOI_NAO_RESOLVE`, `POSSIVELMENTE_INVENTADA`).

## Detalhamento

| # | Local | Afirmação (resumida) | Ref. | Existência | Classe | Problemas | Suporte localizado | Ação |
|---|---|---|---|---|---|---|---|---|
| C1 | P-001 | decoupling **causou** redução de **20%** no consumo (EUA) | Kahn-Lang 2016 | PARTIALLY_VERIFIED | **NÃO VERIFICÁVEL** | CAUSAL-INDEVIDA, EXAGERO, PAGINA-AUSENTE | Abstract: "historically **associated** with significant residential electricity consumption reductions" — sem magnitude | Pedir página do texto integral; reescrever como associação |
| C2 | P-001 | ajustes médios de 0,4% (2005–2017) | Cappers et al. 2020 | PARTIALLY_VERIFIED | **SUPORTADA** | PAGINA-AUSENTE | Results and Discussion / Table 2: "rate adjustments of 0.4 percent of all-in average retail rates" | Acrescentar amostra e página |
| C3 | P-002 | meta-análise global: +35% no gasto em EE | Silva & Pereira 2019 | **CONTRADICTED** | **NÃO SUPORTADA** | REF-INEXISTENTE, POSSIVELMENTE-INVENTADA | — | Remover; não substituir sem fonte verificada |
| C4 | P-002 | 16 estados com decoupling em 2017 | Cappers et al. 2020 | PARTIALLY_VERIFIED | **PARCIALMENTE SUPORTADA** | FONTE-SECUNDARIA | Introduction: "...16 states... (Berg et al., 2019)" | Citar e verificar a fonte primária |
| C5 | P-003 | obrigações **reduziram** consumo na Suécia; B/C até 2,17 | Xylia et al. 2016 | PARTIALLY_VERIFIED | **PARCIALMENTE SUPORTADA** | CAUSAL-INDEVIDA, EXAGERO | Abstract: BCR "ranges from 1.56 to 2.17" em CBA **ex ante** de esquema **hipotético** | Reescrever como projeção |
| C6 | P-003 | potencial de 12% no Brasil | — | NO_CITATION | **NÃO SUPORTADA** | NUMERO-SEM-FONTE | — | Fonte ou remoção |
| C7 | P-004 | decoupling **elevaria** investimentos no Brasil | — | NO_CITATION | **NÃO SUPORTADA** | GENERALIZACAO, CAUSAL-INDEVIDA | — | Reformular como hipótese e discutir validade externa |

## Sugestões de substituição

Nenhuma. Não foi localizada fonte verificada que sustente as afirmações C3, C6 e C7 — e o
plugin não substitui referências sem verificação e aprovação do autor.

## Varredura automática

Ver `scan-output.md`: 1 NUMERO-SEM-FONTE (C6), 1 AFIRMACAO-SEM-FONTE (C7) e 2 CAUSAL-VERIFICAR
(C1, C5). A varredura não detecta sozinha C3 (número citado, mas referência inexistente) nem C4
(fonte secundária) — por isso a auditoria frase a frase é necessária.

## Versão corrigida sugerida (sem fatos novos)

> Kahn-Lang (2016) relata, no resumo, que o decoupling esteve historicamente associado a reduções
> no consumo residencial de eletricidade nos Estados Unidos [magnitude: EVIDÊNCIA PENDENTE —
> página do texto integral]. Entre 2005 e 2017, em 21 utilidades de 11 estados norte-americanos e do
> District of Columbia, os ajustes tarifários do decoupling foram em média de 0,4% da tarifa média de
> varejo (Cappers et al., 2020). Para um esquema sueco hipotético de obrigação de eficiência
> energética, uma análise custo-benefício ex ante projeta razão benefício-custo entre 1,56 e 2,17
> (Xylia et al., 2016). Sugere-se investigar se, no contexto regulatório brasileiro, o decoupling
> alteraria os incentivos das distribuidoras a investir em eficiência energética.
