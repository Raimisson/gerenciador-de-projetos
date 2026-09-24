---
name: research-project
description: Workflow principal do plugin Scientific Research. Use quando o usuário quiser conduzir ou organizar um projeto de pesquisa/artigo científico de ponta a ponta ("iniciar projeto de pesquisa", "montar revisão de literatura para um artigo", "research project", "do zero até a publicação"), ou quando não souber qual etapa executar. Orienta pergunta → protocolo → busca → triagem → extração → Evidence Ledger → matriz → avaliação metodológica → redação → auditorias → escolha de periódico → Target Journal Mode → compliance → auditoria pré-submissão → submissão → resposta a pareceres → publicação/ressubmissão, sem obrigar a executar todas as etapas.
argument-hint: "[tema ou pergunta de pesquisa] [--dir caminho-do-projeto]"
---

# Research Project — workflow principal

Orquestra o ciclo completo de produção de um artigo científico. Não executa tudo de uma
vez: diagnostica em que ponto o usuário está e conduz à próxima etapa útil.

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

- Início de um artigo, dissertação, nota técnica ou revisão de literatura.
- O usuário quer um roteiro e não sabe qual skill acionar.
- Retomar um projeto existente (há uma pasta `research/`).

## Quando NÃO usar

- Pergunta pontual ("qual o DOI deste artigo?") → `bibliography-audit`.
- Só quer revisar um texto pronto → `manuscript-review` ou `citation-audit`.
- Só quer buscar literatura rapidamente → `literature-search`.

## Inputs esperados

- Tema ou pergunta (mesmo vaga).
- Opcional: pasta do projeto, prazo, tipo de produto (artigo, revisão sistemática, nota
  técnica, AIR/ARR), periódico-alvo, arquivos já disponíveis (PDFs, rascunho, `.bib`).

## Estrutura de projeto

Se não existir, proponha criar (com consentimento) a pasta do projeto:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" init <caminho-do-projeto>
```

Isso cria `research/` com: `protocol.md`, `search/`, `screening/`, `sources/sources.json`,
`extraction/`, `ledger/evidence.jsonl`, `matrix/`, `appraisal/`, `synthesis/`,
`manuscript/`, `audit/`, `data/raw/` (imutável), `data/derived/`, `analysis/`.
Sem Bash/Python disponível: crie os mesmos arquivos manualmente a partir de
`${CLAUDE_PLUGIN_ROOT}/templates/`.

## Workflow

Cada etapa é **opcional**; pergunte o que o usuário já tem e pule o que não agrega.

| # | Etapa | Skill | Saída principal |
|---|---|---|---|
| 1 | Pergunta | `research-question` | pergunta, constructos, hipóteses (rotuladas como hipóteses) |
| 2 | Protocolo | `systematic-review` (se revisão estruturada) | `protocol.md`, critérios de inclusão/exclusão |
| 3 | Busca | `literature-search`, `citation-chasing`, `grey-literature`, `regulatory-research` | `search/search-log.json` + `.md` |
| 4 | Triagem | `systematic-review` | `screening/screening.csv`, fluxo inspirado em PRISMA |
| 5 | Extração | `evidence-extraction`, `quantitative-evidence` | `extraction/<S-id>.json` |
| 6 | Evidence Ledger | `evidence-ledger` | `ledger/evidence.jsonl` |
| 7 | Matriz | `evidence-matrix` | `matrix/evidence-matrix.{md,csv,json}` |
| 8 | Avaliação metodológica | `methodology-review` | `appraisal/<S-id>.md` |
| 9 | Síntese | `evidence-synthesis` | `synthesis/synthesis.md` |
| 10 | Redação | `scientific-writing` | `manuscript/manuscript.md` com marcadores `[E-0001]` |
| 11 | Auditoria de citações | `citation-audit`, `bibliography-audit` | `audit/citation-audit.md`, `audit/bibliography-audit.md` |
| 12 | Auditoria final | `manuscript-review`, `replication-check` | `audit/manuscript-audit.md` |
| | **Módulo Publication Strategy** | (subagente `publication-strategist` coordena) | `research/publication/` |
| 13 | Journal Search | `journal-search` (+ `journal-recent-content-analysis`) | `publication/journals/candidates.json` |
| 14 | Journal Fit Analysis | `journal-fit-analysis`, `journal-due-diligence`, `journal-requirements` | `journals/<slug>/fit.json`, `fit-report.md`, `due-diligence.json`, `requirements.json` |
| 15 | Journal Selection | `publication-strategy` | `publication/strategy.md` (decisão do autor) |
| 16 | Target Journal Mode | `publication-strategy` → `pubtool.py target set` | `publication/target-journal.json` |
| 17 | Manuscript Compliance | `manuscript-compliance`, `submission-preparation`, `cover-letter` | `compliance/<slug>.{json,md}`, `submission/<slug>/` |
| 18 | Pre-Submission Audit | `pre-submission-audit` | READY TO SUBMIT ou ACTION REQUIRED |
| 19 | Submission | (feita pelos autores no sistema do periódico) | registro da data e versão submetida |
| 20 | Peer Review Response | `peer-review-response` | `peer-review/round-<n>/response-matrix.json`, carta de resposta |
| 21 | Publication / Resubmission | `resubmission-strategy` (se rejeitado) | `resubmission/plan-<data>.md` |

Fluxo resumido: Research Question → Protocol → Literature Search → Screening → Evidence Extraction →
Evidence Ledger → Evidence Matrix → Methodology Review → Scientific Writing → Citation Audit →
Manuscript Review → Journal Search → Journal Fit Analysis → Journal Selection → Target Journal Mode →
Manuscript Compliance → Pre-Submission Audit → Submission → Peer Review Response → Publication / Resubmission.

O módulo Publication Strategy reutiliza o manuscrito, o Evidence Ledger e as auditorias do mesmo
projeto; ele **não** reconstrói a evidência. Regras editoriais nunca justificam alterar resultados.
Detalhes: `${CLAUDE_PLUGIN_ROOT}/docs/publication-strategy.md`.

### Passo a passo

1. **Diagnóstico** (1 mensagem curta): objetivo, produto, o que já existe, ferramentas
   disponíveis (conectores). Liste quais conectores detectou na sessão e quais faltam.
2. **Plano mínimo**: proponha só as etapas necessárias. Ex.: "nota técnica rápida" pode
   pular protocolo formal e triagem dupla; "revisão sistemática" não pode.
3. **Execução etapa a etapa**, salvando artefatos na pasta `research/`. Ao final de cada
   etapa, mostre: o que foi produzido, o que ficou `UNVERIFIED`/`NR`, próxima etapa sugerida.
4. **Portões de qualidade** antes de avançar:
   - Antes da redação: toda evidência que sustentará o texto está no ledger com status ≠ `UNVERIFIED`?
   - Antes de entregar: `citation-audit` e `manuscript-review` executados?
   - Antes de submeter: `pre-submission-audit` com resultado READY TO SUBMIT?
5. **Validação automática** (se Bash disponível):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" validate project <caminho>/research
   ```

## Uso de subagentes

Use subagentes apenas quando houver ganho real (ver `${CLAUDE_PLUGIN_ROOT}/docs/architecture.md`):
- `literature-researcher` para buscas amplas em paralelo com a leitura do usuário;
- `methodology-reviewer` e `citation-auditor` como verificações **independentes**;
- `scientific-editor` só depois que o ledger estiver validado;
- `publication-strategist` para conduzir a etapa de publicação em contexto isolado.
Nunca dispare vários agentes para a mesma busca.

## Output esperado

- Mensagem com o estado do projeto (tabela das etapas: feito / pendente / não aplicável).
- Artefatos salvos na pasta `research/`.
- Lista explícita de lacunas e itens não verificados.

## Critérios de qualidade

- Cada etapa deixa artefato persistente e reproduzível.
- Nenhuma afirmação do manuscrito sem evidência no ledger.
- Etapas puladas são registradas com justificativa em `protocol.md`.

## Situações de falha

- **Nenhum conector acadêmico**: siga com WebSearch/WebFetch e APIs públicas via
  `srtool.py`; se nada estiver disponível, trabalhe com PDFs/listas fornecidos pelo usuário e
  declare a limitação de cobertura.
- **Sem Bash/Python** (ex.: alguns ambientes web): produza os artefatos em Markdown/JSON
  diretamente na conversa ou via ferramentas de arquivo disponíveis.
- **Usuário pede para "preencher" dados faltantes**: recuse a fabricação, explique a regra e
  ofereça alternativas (buscar fonte, marcar `NR`, declarar lacuna).
