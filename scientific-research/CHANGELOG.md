# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões seguem
[SemVer](https://semver.org/lang/pt-BR/).

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
