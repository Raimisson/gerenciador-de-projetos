# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões seguem
[SemVer](https://semver.org/lang/pt-BR/).

## [0.2.1] - 2026-09-24

### Alterado
- Descrições das 30 skills e dos 7 agentes encurtadas (máx. ~215 caracteres), mantendo os gatilhos
  principais, para reduzir o custo fixo de contexto por sessão (antes ≈ 7,3 mil tokens).
- Descrições do frontmatter entre aspas (YAML válido em parsers estritos).
- Manual do usuário: `MANUAL.md`.

## [0.2.0] - 2026-09-24

### Adicionado — módulo Publication Strategy
- Módulo funcionalmente separado em `modules/publication-strategy/` (skills, schemas, templates,
  `pubtool.py`), carregado pelo mesmo manifesto (`"skills": ["./skills", "./modules/publication-strategy/skills"]`)
  e compartilhando projeto, manuscrito e Evidence Ledger.
- 12 skills: `journal-search`, `journal-fit-analysis`, `journal-recent-content-analysis`,
  `journal-due-diligence`, `journal-requirements`, `manuscript-compliance`, `publication-strategy`,
  `submission-preparation`, `cover-letter`, `peer-review-response`, `resubmission-strategy`,
  `pre-submission-audit` (workflow).
- Subagente `publication-strategist`.
- Regras de integridade editorial (sem probabilidade de aceitação; dados de periódicos com URL e data;
  "predatório" nunca por ausência de uma indexação; regras editoriais nunca justificam alterar resultados)
  sincronizadas por `scripts/sync_integrity.py`.
- Journal Fit Report padronizado e índice de aderência transparente (fórmula, pesos, cobertura) — não é probabilidade.
- Target Journal Mode (`research/publication/target-journal.json`) com limites de integridade.
- `pubtool.py`: perfil do manuscrito, venues, validação por schema, fit report, comparação, compliance
  automático (COMPLIANT / ACTION REQUIRED / NOT APPLICABLE / UNABLE TO VERIFY), checklist, frescor das
  regras, lint de linguagem (probabilidade/garantia de aceitação, "primeiro a", elogios genéricos), carta de
  resposta a revisores e auditoria pré-submissão (READY TO SUBMIT / ACTION REQUIRED).
- 9 JSON Schemas e 12 templates do módulo; `docs/publication-strategy.md`.
- Exemplo 4 (estratégia de publicação completa com dados reais do Scite; requisitos oficiais inacessíveis
  marcados NOT VERIFIED; requisitos sintéticos rotulados para demonstrar o compliance; pareceres fictícios rotulados).
- Testes do módulo (`tests/test_publication.py`) e novos casos de eval.

### Alterado
- Workflow principal (`research-project`) estendido até Submission, Peer Review Response e Publication/Resubmission.
- `srtool.py`: suporte a diretórios de schema de módulos.

## [0.1.0] - 2026-09-24

### Adicionado
- Manifesto `.claude-plugin/plugin.json` e marketplace local na raiz do repositório.
- 18 skills: `research-project` (workflow principal), `research-question`, `literature-search`,
  `citation-chasing`, `grey-literature`, `systematic-review`, `evidence-extraction`,
  `evidence-ledger`, `evidence-matrix`, `methodology-review`, `quantitative-evidence`,
  `evidence-synthesis`, `regulatory-research`, `scientific-writing`, `citation-audit`,
  `bibliography-audit`, `replication-check`, `manuscript-review`.
- 6 subagentes: `literature-researcher`, `methodology-reviewer`, `citation-auditor`,
  `scientific-editor`, `quantitative-analyst`, `regulatory-researcher`.
- Evidence Ledger (JSONL) com proveniência fonte → evidência → interpretação → parágrafo.
- `scripts/srtool.py` (stdlib): validação por schema, matriz MD/CSV/JSON, `doi-check`,
  `refs-check`, `dedupe`, `scan` do manuscrito, `trace`, formatação ABNT/APA/Chicago/BibTeX
  (só metadados verificados), fluxo inspirado em PRISMA, busca e citation chasing via OpenAlex.
- Hooks: lembrete de integridade (SessionStart); confirmação antes de alterar `data/raw/` e de
  escrever em Zotero/bibliotecas de conectores de pesquisa (PreToolUse).
- JSON Schemas, 16 templates, configuração opcional de conectores com URLs verificadas.
- Três exemplos completos gerados com ferramentas reais (Scite) e documentação de limitações.
- Testes `unittest` (fixtures com referência propositalmente falsa), smoke test do CLI e casos de eval.

### Fora do escopo desta versão
- Cálculo automático de meta-análise (apenas portão de viabilidade).
- Servidor MCP próprio ou `.mcp.json` ativo por padrão.
