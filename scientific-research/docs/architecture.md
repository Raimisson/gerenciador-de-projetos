# Arquitetura do plugin Scientific Research

## 1. Visão geral

```
                    ┌────────────────────────────────────────────┐
  usuário ─────────►│ skills (18)  — instruções de workflow      │
  /scientific-      │   research-project (orquestra)             │
  research:<skill>  │   research-question · literature-search ·  │
  ou linguagem      │   citation-chasing · grey-literature ·     │
  natural           │   regulatory-research · systematic-review ·│
                    │   evidence-extraction · quantitative-      │
                    │   evidence · evidence-ledger · evidence-   │
                    │   matrix · methodology-review · evidence-  │
                    │   synthesis · scientific-writing ·         │
                    │   citation-audit · bibliography-audit ·    │
                    │   replication-check · manuscript-review    │
                    └──────┬──────────────┬───────────────┬──────┘
                           │              │               │
             subagentes (6, opcionais)    │         scripts/srtool.py
             contexto isolado / paralelo  │         (stdlib Python)
                           │              │               │
                    ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼───────────┐
                    │ conectores  │ │ arquivos do│ │ schemas/*.json   │
                    │ (Consensus, │ │ projeto    │ │ templates/*      │
                    │ Scite,      │ │ research/  │ └──────────────────┘
                    │ Elicit, ... │ └────────────┘
                    │ web, APIs)  │
                    └─────────────┘
  hooks: SessionStart (lembrete) · PreToolUse (dados brutos, escrita em bibliotecas)

                    ┌────────────────────────────────────────────┐
  manuscrito ──────►│ módulo Publication Strategy                │
  concluído         │  modules/publication-strategy/             │
                    │  12 skills · pubtool.py · schemas · tmpl.  │
                    │  subagente publication-strategist          │
                    │  lê: manuscrito, Evidence Ledger, auditorias│
                    │  escreve: research/publication/            │
                    └────────────────────────────────────────────┘
```

Princípios de desenho: **arquivos simples** (Markdown, JSON, JSONL, CSV), **nenhum servidor**,
**nenhuma dependência externa** (Python 3 padrão), **regras críticas dentro de cada skill**.

## 2. Componentes

| Componente | Local | Papel |
|---|---|---|
| Manifesto | `.claude-plugin/plugin.json` | nome, versão, metadados |
| Marketplace | `../.claude-plugin/marketplace.json` (raiz do repositório) | distribuição via `/plugin marketplace add` |
| Skills (núcleo) | `skills/<nome>/SKILL.md` | workflows científicos; viram `/scientific-research:<nome>` |
| Módulo Publication Strategy | `modules/publication-strategy/` (`skills/`, `schemas/`, `templates/`, `scripts/pubtool.py`) | etapa entre manuscrito concluído e publicação; skills carregadas pelo manifesto (`"skills": ["./skills", "./modules/publication-strategy/skills"]`) |
| Subagentes | `agents/*.md` | especialistas com contexto isolado e ferramentas restritas |
| Hooks | `hooks/hooks.json` + `hooks/*.py` | lembrete de integridade; confirmação para dados brutos e escrita em bibliotecas |
| Ferramenta | `scripts/srtool.py` | validação, matriz, DOI, varredura, proveniência, PRISMA, OpenAlex |
| Sincronização | `scripts/sync_integrity.py` | mantém o bloco de integridade idêntico em skills e agentes |
| Schemas | `schemas/*.schema.json` | contratos de dados (fonte, extração, ledger, search log, auditoria) |
| Templates | `templates/` | protocolo, search log, critérios, ficha, matriz, avaliação, relatórios |
| Conectores | `connectors/` + `docs/connectors.md` | configuração opcional e classificação das integrações |
| Testes | `tests/` | `unittest` + fixtures + smoke test do CLI |
| Evals | `evals/` | casos para `claude plugin eval` (comportamento do modelo) |

## 3. Interação entre skills

```
research-question ──► systematic-review (protocolo, critérios)
        │                     │
        ▼                     ▼
literature-search ◄──► citation-chasing        grey-literature / regulatory-research
        │                     │                         │
        └──────────► triagem (systematic-review) ◄──────┘
                              │
                              ▼
          evidence-extraction ◄──► quantitative-evidence
                              │
                              ▼
                       evidence-ledger ──► evidence-matrix
                              │                  │
                              ▼                  ▼
                   methodology-review ──► evidence-synthesis
                                                 │
                                                 ▼
                                        scientific-writing
                                                 │
                                                 ▼
                     citation-audit · bibliography-audit · replication-check
                                                 │
                                                 ▼
                                        manuscript-review
                                                 │
                    ═══════════ módulo Publication Strategy ═══════════
                                                 ▼
        journal-search → journal-recent-content-analysis → journal-fit-analysis
                 → journal-due-diligence → journal-requirements → publication-strategy
                 → [escolha do autor] TARGET JOURNAL MODE → manuscript-compliance
                 → submission-preparation / cover-letter → pre-submission-audit
                 → submissão (autores) → peer-review-response | resubmission-strategy
```

`research-project` percorre esse grafo **sob demanda**: diagnostica o que existe e propõe só as
etapas necessárias (etapas puladas são registradas no protocolo).

## 4. Subagentes — quando usar

| Agente | Usar quando | Não usar quando |
|---|---|---|
| `literature-researcher` | busca extensa em várias bases, citation chasing multi-rodada | busca de um único artigo |
| `methodology-reviewer` | segunda avaliação independente; muitos estudos em paralelo | um estudo simples já avaliado |
| `citation-auditor` | auditoria independente de manuscrito longo (por seções, sem sobreposição) | checar um DOI isolado |
| `scientific-editor` | redação/revisão após o ledger validado (sem web por desenho) | ainda não há evidência validada |
| `quantitative-analyst` | estudos com muitas tabelas/especificações; análise reproduzível | um número isolado de um abstract |
| `regulatory-researcher` | levantamento normativo em paralelo à busca acadêmica | pergunta sem componente normativo |
| `publication-strategist` | conduzir a etapa de publicação (vários periódicos, compliance, pareceres) em contexto isolado | checar uma única regra de um periódico já escolhido |

`systematic-review-specialist` **não** foi criado: duplicaria a skill `systematic-review` e o
`literature-researcher`. Regra geral: um agente por tarefa independente; nunca vários agentes
repetindo a mesma busca.

## 5. Conectores

Nenhum MCP é ativado pelo plugin. As skills detectam ferramentas por nome
(Consensus/Elicit/Scite/Zotero/Drive/Exa/Tavily/Firecrawl, WebSearch/WebFetch) e aplicam a
hierarquia de `docs/connectors.md`. APIs públicas (Crossref, OpenAlex) são acessadas por
`srtool.py` sem credenciais. Falhas viram `UNVERIFIED` e ficam registradas no search log.

## 6. Proveniência

```
research/sources/sources.json        S-0001  metadados + metadata_verification{status, checked_against}
          │
research/extraction/S-0001.json      ficha completa; estimates[] com location + excerpt
          │
research/ledger/evidence.jsonl       E-0001  excerpt, page/table, claim_supported,
          │                                   evidence_type (fonte/autores/inferência),
          │                                   design_class, context, verification_status, used_in
          ▼
research/manuscript/manuscript.md    <!-- P-001 --> ... frase [E-0001]
```

- `srtool.py trace E-0001` ou `trace P-001` responde "de onde veio esta afirmação?".
- `srtool.py scan` usa o ledger para detectar números sem fonte, evidência inexistente/não
  verificada, linguagem causal sobre evidência não causal e generalização de contexto.
- Inferências analíticas são entradas do ledger com `evidence_type: analytic_inference` e
  `derived_from`, para nunca se confundirem com resultados de estudos.

Por que JSONL: uma evidência por linha, anexável, diff legível no Git, sem banco de dados.

## 7. Estrutura de um projeto de pesquisa

Criada por `srtool.py init <dir>`:

```
research/
├── protocol.md
├── search/        search-log.json, search-log.md, prisma-flow.md
├── screening/     screening.csv
├── sources/       sources.json
├── extraction/    S-0001.json ...
├── ledger/        evidence.jsonl
├── matrix/        evidence-matrix.{md,csv,json}
├── appraisal/     S-0001.md ...
├── synthesis/     synthesis.md
├── manuscript/    manuscript.md, glossary.md
├── audit/         citation-audit.{md,json}, bibliography-audit.md, manuscript-audit.md, scan.md
├── data/raw/      imutável (hook pede confirmação antes de qualquer escrita)
├── data/derived/  gerado por scripts
├── analysis/      scripts + analysis-run-log.md
└── publication/   (módulo Publication Strategy — criado por pubtool.py init)
    ├── manuscript-profile.json · strategy.md · target-journal.json
    ├── journals/candidates.json · journals/<slug>/{recent-content,fit,due-diligence,requirements}.json
    ├── compliance/ · submission/<slug>/ · pre-submission-audit-<slug>.md
    └── peer-review/round-<n>/ · resubmission/
```

## 7b. Proveniência na etapa de publicação

O módulo não reconstrói evidência: cover letter, highlights e abstract usam os números do manuscrito
(rastreáveis ao ledger), e a auditoria pré-submissão roda `srtool.py scan` com o ledger. Informação de
periódico tem sua própria proveniência (URL oficial + data + trecho) em `requirements.json`,
`fit.json` e `due-diligence.json`; o que não tem fonte atual é `NOT VERIFIED`.

## 8. Compatibilidade

| Ambiente | Skills | Agentes | Hooks | srtool | Conectores |
|---|---|---|---|---|---|
| Claude Code CLI / Desktop / Web | ✔ | ✔ | ✔ (requer `python3`) | ✔ | claude.ai ou `claude mcp add` |
| Claude.ai / Cowork | ✔ | depende do ambiente | pode não executar | só com execução de código | conectores do claude.ai |

As regras de integridade estão replicadas em cada skill e agente justamente para não depender de
hooks ou scripts.

## 9. Manutenção

- Editar regras de integridade só em `docs/partials/integrity-block.md` (científicas) e
  `docs/partials/publication-integrity-block.md` (editoriais) e rodar
  `python3 scripts/sync_integrity.py`.
- Rodar `python3 -m unittest discover -s tests` e `claude plugin validate . --strict` antes de publicar.
- Atualizar `version` em `plugin.json`, na entrada do marketplace e no `CHANGELOG.md`.
