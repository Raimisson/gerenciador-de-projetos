# Módulo Publication Strategy

Etapa entre o **manuscrito concluído** e a **publicação**. O módulo é funcionalmente separado
(`modules/publication-strategy/`: skills, schemas, templates e `pubtool.py`), mas faz parte do mesmo
plugin: compartilha o projeto `research/`, o manuscrito, o **Evidence Ledger** e as auditorias.

## 1. Princípio fundamental

**Nunca inventar probabilidade de aceitação.** Frases como "este artigo tem 80% de chance de
aceitação" são proibidas: não há evidência publicada que permita calculá-las para um manuscrito
específico. O módulo produz **indicadores de aderência (journal fit)** com:

- critérios transparentes (sete dimensões, notas e pesos declarados);
- fontes mostradas (URL/DOI + data de verificação para cada evidência);
- apresentação como **avaliação de aderência** — nunca como probabilidade de publicação.

O objetivo é melhorar a decisão e reduzir riscos evitáveis de desk rejection — não prometer publicação.
O validador (`pubtool.py validate`) rejeita campos como `probability`/`acceptance_chance`, e o `lint`
bloqueia textos com probabilidade ou garantia de aceitação.

## 2. Regras de integridade editorial

As regras estão em `docs/partials/publication-integrity-block.md` e são sincronizadas em todas as skills
do módulo e no agente `publication-strategist` (`scripts/sync_integrity.py`). Resumo:

1. sem probabilidade de aceitação; 2. informação de periódico é mutável — URL oficial + data, senão
`NOT VERIFIED`; 3. aderência não se infere pelo nome; 4. "predatório" nunca por ausência de uma
indexação isolada; 5. métricas não substituem aderência; 6. regras editoriais nunca justificam
alterar/omitir resultados, fabricar análises/referências, manipular evidência ou exagerar conclusões;
7. dados de autores nunca inventados; 8. "primeiro/inédito" só com verificação documentada.

## 3. Skills e fluxo

```
manuscrito concluído (manuscript-review, citation-audit)
        │
        ▼
journal-search ──► journal-recent-content-analysis ──► journal-fit-analysis
        │                                                    │
        │                               journal-due-diligence│  journal-requirements
        ▼                                                    ▼
                      publication-strategy (comparação, escolha do autor)
                                   │
                          TARGET JOURNAL MODE  (pubtool target set)
                                   │
                 manuscript-compliance ──► submission-preparation ──► cover-letter
                                   │
                          pre-submission-audit ──► READY TO SUBMIT | ACTION REQUIRED
                                   │
                         submissão (autores) ──► decisão editorial
                                   │
                 peer-review-response   |   resubmission-strategy (rejeição)
```

| Skill | Função |
|---|---|
| `journal-search` | candidatos a partir de várias fontes (veículos da literatura citada, artigos comparáveis recentes, citantes, diretórios, editoras diversas) |
| `journal-recent-content-analysis` | artigos comparáveis dos últimos 3–5 anos, com DOI e relação com o manuscrito |
| `journal-fit-analysis` | sete dimensões de aderência + índice transparente (não probabilidade) |
| `journal-due-diligence` | legitimidade e transparência (ISSN, peer review, indexações, COPE, DOAJ, APC, licenças, ética) |
| `journal-requirements` | regras atuais do guia oficial, com URL, data e versão |
| `manuscript-compliance` | COMPLIANT / ACTION REQUIRED / NOT APPLICABLE / UNABLE TO VERIFY |
| `publication-strategy` | lista curta comparada, ordem sugerida, riscos, Target Journal Mode |
| `submission-preparation` | checklist e arquivos de submissão (sem inventar dados de autores) |
| `cover-letter` | carta específica ao periódico, sem elogios genéricos nem "primeiro" sem verificação |
| `peer-review-response` | matriz Comment → Interpretation → Action → Change → Location → Response |
| `resubmission-strategy` | diagnóstico da rejeição, reuso da pesquisa de periódicos, regras reconsultadas |
| `pre-submission-audit` | workflow de auditoria final antes de submeter |

Subagente: `publication-strategist` (coordena o módulo; reutiliza o ledger).

## 4. Journal fit

Dimensões: **Topic**, **Method**, **Contribution**, **Empirical**, **Audience**, **Recent Publication**,
**Article-Type**. Cada uma: `STRONG` · `MODERATE` · `WEAK` · `INSUFFICIENT_EVIDENCE`, com justificativa
e lista de evidências (fonte, URL/DOI, trecho, data). Classificações sem evidência são rejeitadas.

**Journal Fit Index** = 100 × Σ(peso × nota) / Σ(peso × 2), com STRONG=2, MODERATE=1, WEAK=0;
dimensões `INSUFFICIENT_EVIDENCE` ficam fora do cálculo e aparecem como **cobertura** (ex.: 4/7).
O relatório sempre imprime a fórmula e o aviso de que o índice não é probabilidade.

O **Journal Fit Report** padronizado (template `modules/publication-strategy/templates/journal-fit-report.md`)
contém: JOURNAL · PUBLISHER · AIMS & SCOPE · TOPIC FIT · METHOD FIT · AUDIENCE FIT · RECENT ARTICLE FIT ·
ARTICLE TYPE FIT · OPEN ACCESS · APC · INDEXING · REVIEW TIME IF PUBLISHED · PUBLICATION TIME IF
PUBLISHED · KEY REQUIREMENTS · SIMILAR ARTICLES · RISKS · EVIDENCE · DATE VERIFIED (e, adicionalmente,
CONTRIBUTION FIT, EMPIRICAL FIT e DUE DILIGENCE). Dados ausentes: `NOT VERIFIED`.

## 5. Target Journal Mode

Ativado depois que o **autor** escolhe o periódico:

```bash
python3 modules/publication-strategy/scripts/pubtool.py target set research/publication --journal <slug>
```

Cria `research/publication/target-journal.json` (schema `target-journal.schema.json`) com o periódico,
o arquivo de requisitos e os **limites de integridade**. Enquanto ativo, todas as recomendações
editoriais consideram prioritariamente as regras desse periódico (compliance, preparação da submissão,
cover letter, auditoria). As regras editoriais **nunca** justificam: alteração ou omissão seletiva de
resultados; fabricação de análise; fabricação de referência; manipulação de evidência; exagero de
conclusão. `target show` exibe o estado; `target clear` desativa.

## 6. Dados temporais

Regras de periódicos, APC, prazos, indexações e métricas mudam. Por isso:

- toda regra/evidência registra **URL** e **data da consulta** (e versão do guia, se houver);
- fontes oficiais têm prioridade (site do periódico/editora, ISSN Portal, DOAJ, COPE, listas oficiais de indexadores);
- `pubtool.py freshness` mede a idade da consulta; a auditoria pré-submissão exige reconsulta com
  no máximo 30 dias (configurável) — regras antigas nunca são assumidas válidas;
- após rejeição, `resubmission-strategy` reconsulta as regras do novo periódico.

## 7. Auditoria pré-submissão

`/scientific-research:pre-submission-audit` (ou `pubtool.py presubmit research --journal <slug>`):

```
Journal requirements → Manuscript compliance → Citation audit → Reference audit
→ Data/code availability → Ethical declarations → Files required → Submission checklist
```

Resultado **READY TO SUBMIT** somente com zero pendências; caso contrário **ACTION REQUIRED** com a
lista completa (regras não reconsultadas, itens de compliance, afirmações não suportadas, referências
não verificadas, declarações ausentes ou com placeholder, arquivos faltantes, linguagem proibida).
Itens não verificáveis automaticamente podem ser confirmados manualmente em
`research/publication/compliance/<slug>-manual.json` (quem confirmou, quando, nota).

## 8. Estrutura de arquivos

```
research/publication/
├── manuscript-profile.json            pubtool profile (+ campos completados a partir do ledger)
├── journals/
│   ├── candidates.json
│   └── <slug>/
│       ├── recent-content.json
│       ├── fit.json  →  fit-report.md
│       ├── due-diligence.json
│       └── requirements.json
├── strategy.md
├── target-journal.json                Target Journal Mode
├── compliance/<slug>.{json,md} (+ <slug>-manual.json)
├── submission/<slug>/                 checklist, manuscript(-blinded), title page, cover letter, highlights, statements
├── pre-submission-audit-<slug>.md
├── peer-review/round-<n>/             response-matrix.json, response-letter.md
└── resubmission/plan-<data>.md
```

## 9. Limitações

- O módulo não acessa sistemas de submissão (Editorial Manager, ScholarOne etc.) e não submete nada.
- A checagem automática cobre regras mensuráveis em Markdown (palavras, abstract, keywords, título,
  figuras, tabelas, seções, declarações, highlights); o resto é `UNABLE TO VERIFY` até confirmação manual.
- Sites de editoras podem bloquear acesso automatizado; nesse caso as regras ficam `NOT VERIFIED` e o
  usuário deve colar o texto oficial (registrado como `provided_by_user`, com URL e data).
- Nenhuma avaliação de aderência garante aceitação.
