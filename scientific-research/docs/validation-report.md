# Relatório de validação — v0.2.0 (24/09/2026)

Ambiente: Claude Code 2.1.282 (Linux), Python 3.11. Rede do ambiente de construção **bloqueava**
`api.crossref.org`, `api.openalex.org`, `api.semanticscholar.org` e `doi.org` (proxy 403).

| Verificação | Comando | Resultado |
|---|---|---|
| Manifesto (validador oficial, estrito) | `claude plugin validate scientific-research --strict` | ✔ passou |
| Skills (validador oficial, estrito) | `claude plugin validate scientific-research/skills --strict` | ✔ passou |
| Agentes (validador oficial, estrito) | `claude plugin validate scientific-research/agents --strict` | ✔ passou |
| Marketplace (validador oficial, estrito) | `claude plugin validate . --strict` (raiz do repo) | ✔ passou |
| Instalação real | `claude plugin marketplace add <repo>` + `claude plugin install scientific-research@raimisson-research` | ✔ instalado (escopo user); `plugin details`: 18 skills, 6 agentes, 2 eventos de hook, 0 MCP; custo fixo projetado ≈ 4,6 mil tokens/sessão |
| Carga numa sessão | `claude -p --plugin-dir …` (tests/cli_smoke_test.sh) | ✔ 18 skills e 6 agentes visíveis como `scientific-research:*` |
| Substituição de variáveis em skills | skill de teste com `${CLAUDE_PLUGIN_ROOT}` e `${CLAUDE_SKILL_DIR}` | ✔ ambas substituídas por caminhos absolutos |
| Hook PreToolUse (dados brutos) | `claude -p` tentando sobrescrever `research/data/raw/base.csv` com `acceptEdits` | ✔ escrita bloqueada com o motivo do plugin; arquivo intacto |
| Hook SessionStart | mesma sessão | ✔ lembrete de integridade presente no contexto |
| Testes unitários | `python3 -m unittest discover -s tests` | ✔ 45/45 |
| Evals de comportamento | `claude plugin eval . --runs 1 --ablation none` | ✔ 4/4 casos aprovados (juízes 3/3 em cada); custo ≈ US$ 0,55 |
| Exemplos | `srtool.py validate project examples/0*/research` | ✔ 0 erros (avisos documentados) |


## v0.2.0 — módulo Publication Strategy

| Verificação | Comando | Resultado |
|---|---|---|
| Manifesto com dois diretórios de skills | `claude plugin validate scientific-research --strict` | ✔ passou |
| Skills do módulo | `claude plugin validate scientific-research/modules/publication-strategy/skills --strict` | ✔ passou |
| Instalação real | marketplace local + `plugin install` + `plugin details` | ✔ 0.2.0 · 30 skills · 7 agentes · 2 hooks · 0 MCP; custo fixo projetado ≈ 7,3 mil tokens/sessão |
| Carga numa sessão | `tests/cli_smoke_test.sh` | ✔ 30 skills e 7 agentes visíveis como `scientific-research:*` |
| Testes unitários | `python3 -m unittest discover -s tests` | ✔ 68/68 (45 núcleo + 23 módulo) |
| Evals | `claude plugin eval . --runs 1 --ablation none` | ✔ 6/6 (incl. `no-acceptance-probability` e `editorial-integrity`), juízes 3/3; custo ≈ US$ 0,91 |
| Exemplo 4 | `pubtool.py validate …` e `presubmit` | ✔ todos os artefatos válidos; auditoria pré-submissão = ACTION REQUIRED (esperado) |

Pendências do módulo: sites de editoras (ScienceDirect, portal ISSN, DOAJ, SAGE, Springer, SCImago,
OpenAlex) bloqueados no ambiente de construção — requisitos, aims & scope, APC, indexação e due
diligence de periódicos reais não puderam ser verificados; o exemplo os marca `NOT VERIFIED`.

## Não verificado / pendente (v0.1.0)

- **Checagem de DOI ao vivo** (Crossref/doi.org) e **citation chasing via OpenAlex**: bloqueados pela
  rede do ambiente; testados com fixtures sintéticas. Rodar `srtool.py doi-check 10.1016/j.tej.2020.106858`
  e `srtool.py chase forward 10.5547/01956574.37.4.jkah` em máquina com rede.
- **Claude.ai / Cowork**: não testado (sem acesso a esse ambiente a partir desta sessão).
- **Hook de escrita em Zotero/bibliotecas**: testado por unidade com nomes de ferramenta; não
  testado com um servidor Zotero real.
- **Evals com ablação** (com × sem plugin): não executados para limitar custo; rodar
  `claude plugin eval . --runs 3` para medir o ganho atribuível ao plugin.
- Conectores Elicit e Consensus da conta usada na construção falharam (plano sem API / cota) —
  comportamento de falha registrado nos exemplos.
