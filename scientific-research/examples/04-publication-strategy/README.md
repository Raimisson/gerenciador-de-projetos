# Exemplo 4 — Publication Strategy: do manuscrito concluído à submissão

Continua o Exemplo 1: o manuscrito "Revenue decoupling and utility energy efficiency programs: a
structured rapid review of the quantitative evidence" (`research/manuscript/manuscript.md`) foi
escrito **apenas** com evidência do Evidence Ledger do Exemplo 1 (copiado para `research/`), acrescido
do registro da própria busca como fonte `S-0006`.

Gerado em 24/09/2026 com o conector Scite (dados reais de conteúdo recente dos periódicos). Os sites
das editoras (ScienceDirect, portal ISSN, DOAJ etc.) estavam **bloqueados** no ambiente de geração:
por isso aims & scope, requisitos, APC, indexação e prazos aparecem como `NOT VERIFIED`, e a
auditoria pré-submissão termina, corretamente, em **ACTION REQUIRED**.

## Como foi executado

```text
/scientific-research:journal-search research/manuscript/manuscript.md
/scientific-research:journal-recent-content-analysis "Utilities Policy" --anos 5
/scientific-research:journal-recent-content-analysis "Energy Policy" --anos 5
/scientific-research:journal-fit-analysis research/publication/journals/candidates.json
/scientific-research:journal-due-diligence "Utilities Policy"
/scientific-research:journal-requirements "Utilities Policy"
/scientific-research:publication-strategy research/
/scientific-research:manuscript-compliance research/manuscript/manuscript.md research/publication/journals/utilities-policy/requirements.json
/scientific-research:submission-preparation utilities-policy
/scientific-research:cover-letter utilities-policy
/scientific-research:pre-submission-audit research/ --journal utilities-policy
/scientific-research:peer-review-response research/publication/peer-review/round-1/reviewer-comments-FICTITIOUS.md
/scientific-research:resubmission-strategy (decisão fictícia)
```

## Arquivos (em `research/publication/`)

| Etapa | Arquivo | Destaque |
|---|---|---|
| Perfil do manuscrito | `manuscript-profile.json` | contagens medidas + campos completados a partir do ledger |
| Candidatos | `journals/venues.md`, `journals/candidates.json` | origem de cada candidato documentada (DOI) |
| Conteúdo recente | `journals/utilities-policy/recent-content.json`, `journals/energy-policy/recent-content.json` | dados reais (Scite, 2021–2026); 2 resultados de outros periódicos descartados |
| Journal fit | `journals/*/fit.json`, `journals/*/fit-report.md`, `comparison.md` | Utilities Policy 67 (cobertura 3/7) · Energy Policy 50 (2/7) — **não são probabilidades** |
| Due diligence | `journals/utilities-policy/due-diligence.json` | só publisher confirmado; demais `NOT_VERIFIED`, **sem** conclusão negativa |
| Requisitos | `journals/utilities-policy/requirements.json` | `access_status: blocked`, regras `NOT_VERIFIED` |
| Requisitos sintéticos | `journals/demo-synthetic-journal/requirements.json` | **SINTÉTICOS**, só para demonstrar a comparação automática |
| Estratégia | `strategy.md` | ordem preliminar, riscos de desk rejection com evidência |
| Target Journal Mode | `target-journal.json` | ativo para `utilities-policy` (decisão simulada para a demo), com limites de integridade |
| Compliance | `compliance/utilities-policy.{json,md}` | 17 × UNABLE TO VERIFY (regras não verificadas) |
| Compliance (sintético) | `compliance/demo-synthetic-journal.{json,md}` | 6 COMPLIANT · 3 ACTION REQUIRED (título, declarações de dados e de conflitos) · 1 NOT APPLICABLE · 1 UNABLE TO VERIFY |
| Submissão | `submission/utilities-policy/` | cover letter com `[NOT VERIFIED]` e placeholders dos autores, highlights, title page, checklist |
| Auditoria pré-submissão | `pre-submission-audit-utilities-policy.md` | **ACTION REQUIRED** com todas as pendências |
| Peer review | `peer-review/round-1/` | pareceres **fictícios**; matriz com ACCEPTED / PARTIALLY / NOT ACCEPTED; carta de resposta |
| Ressubmissão | `resubmission/plan-DEMO.md` | decisão **fictícia**; reuso da pesquisa de periódicos |

## O que o exemplo demonstra

1. **Candidatos derivados de evidência**, não de nomes de periódicos: onde a literatura do ledger foi
   publicada + periódicos dos trabalhos que citaram o estudo-semente.
2. **Recent content com filtro exato**: o filtro de periódico do Scite trouxe 2 artigos de outros
   periódicos na busca de Energy Policy — descartados e registrados.
3. **Journal fit transparente**: sete dimensões, evidência por dimensão, índice com fórmula e
   **cobertura**; dimensões sem evidência não entram no cálculo.
4. **Nenhuma probabilidade de aceitação** em lugar nenhum (`pubtool.py lint` e validadores).
5. **Due diligence sem julgamento indevido**: não verificado ≠ problema.
6. **Compliance automático** (palavras, abstract, keywords, título, highlights, declarações, seções,
   figuras) com as 5 informações exigidas por ACTION REQUIRED e notas de integridade.
7. **Target Journal Mode** com limites de integridade explícitos.
8. **Peer review**: pedido para afirmar causalidade não sustentada é **NOT ACCEPTED** com justificativa
   científica; pedido de nova leitura é aceito **sem antecipar resultados**.

## Reproduzir

```bash
P=../../modules/publication-strategy/scripts/pubtool.py
J=research/publication/journals
python3 $P validate fit $J/utilities-policy/fit.json
python3 $P fit-report $J/utilities-policy/fit.json
python3 $P compare $J/utilities-policy/fit.json $J/energy-policy/fit.json
python3 $P check-compliance research/manuscript/manuscript.md $J/demo-synthetic-journal/requirements.json
python3 $P target show research/publication
python3 $P presubmit research --journal utilities-policy
python3 $P response-letter research/publication/peer-review/round-1/response-matrix.json
```

## Limitações

- Periódicos reais: quase tudo `NOT VERIFIED` por bloqueio de rede — repetir `journal-requirements`,
  `journal-due-diligence` e `journal-fit-analysis` com acesso aos sites oficiais.
- Busca de conteúdo recente limitada a 5–6 registros por periódico.
- Pareceres e decisão de rejeição são fictícios; nenhum periódico avaliou este manuscrito.
