# Testes e procedimentos de validação

## Automáticos (sem custo de modelo)

```bash
cd scientific-research
python3 -m unittest discover -s tests -v
```

| # | Requisito | Testes (`test_plugin.py`) |
|---|---|---|
| 1 | Skill encontrada corretamente | `test_01_all_expected_skills_found`, `test_02_skill_frontmatter_valid`, `test_02b_skill_required_sections` |
| 2 | Skill carregada | `test_02c_claude_validates_skills_dir` (validador oficial) + `cli_smoke_test.sh` passo 3 |
| 3 | Agent encontrado | `test_03_agents_found_and_valid`, `test_03b/03c` (restrições de ferramentas), `test_03d` (validador oficial) |
| 4 | Manifesto válido | `test_04_manifest_fields`, `test_04b_changelog_matches_version`, `test_04c_claude_plugin_validate_strict` |
| 5 | Plugin instalável | `test_05_marketplace_entry_points_to_plugin`, `test_05b_claude_validates_marketplace` + `cli_smoke_test.sh` passo 2 |
| 6 | Sem links/configurações inválidos | `test_06*` (links relativos, `${CLAUDE_PLUGIN_ROOT}/…`, hooks, URLs de MCP em allowlist, segredos, `.env`, JSON) |
| 7 | Extração respeita NR | `test_07*` (fixture `extraction-bad.json`: vazio, null, "n/a", campo ausente, "significant" em campo numérico, número sem página/trecho) |
| 8 | Citation audit detecta DOI falso | `test_08*` (fixture `fake-reference-sources.json` + `network-fixtures.json`) |
| 9 | Regra de não fabricação | `test_09*` (bloco de integridade em todas as skills/agentes; falha de rede ⇒ UNVERIFIED; formatador recusa não verificadas; `scan`; ledger; aritmética do search log; `trace`) |
| 10 | Operação sem conectores | `test_10*` (modo degradado documentado; `init`/`validate` offline; comandos de rede falham com a frase padrão; exemplos validam) |
| — | Hooks | `TestHooks` (dados brutos, escrita em Zotero/bibliotecas, lembrete de sessão, entrada inválida) |

### Fixtures

| Arquivo | Conteúdo |
|---|---|
| `fixtures/fake-reference-sources.json` | **referência propositalmente falsa** (Silva & Pereira, 2019, DOI 10.9999/jiee.2019.0457) + registro sintético |
| `fixtures/network-fixtures.json` | respostas simuladas de Crossref/doi.org/OpenAlex; só registros sintéticos (prefixo de teste `10.5555`) e 404 para o DOI falso |
| `fixtures/extraction-good.json` / `extraction-bad.json` | ficha correta e ficha com todos os erros que o validador deve pegar |
| `fixtures/ledger-good.jsonl` / `ledger-bad.jsonl` | ledger válido e inválido |
| `fixtures/searchlog-bad.json` | contagens incoerentes e busca não executada com contagem |
| `fixtures/manuscript-issues.md` | número sem fonte, causalidade indevida, evidência inexistente, generalização |

## Módulo Publication Strategy (`test_publication.py`)

| Área | Testes |
|---|---|
| Estrutura | 12 skills com seções obrigatórias e os dois blocos de integridade; sem colisão de nomes com o núcleo; manifesto carrega o módulo; agente `publication-strategist`; workflow principal na ordem exigida; Journal Fit Report com todos os campos; validador oficial no diretório do módulo |
| Journal fit | índice transparente (fórmula, cobertura, exclusão de INSUFFICIENT_EVIDENCE); campo/texto de probabilidade rejeitado; frase negada aceita; classificação sem evidência rejeitada |
| Compliance | leitura do manuscrito (título, abstract sem a linha de keywords, keywords, highlights, figuras, tabelas, declarações); 4 status; ACTION REQUIRED com exigência, estado, diferença, ação e fonte; ambiguidade da contagem de palavras; confirmação manual |
| Lint e validadores | probabilidade e garantia (erro), "primeiro a" e elogio genérico (aviso), negação ignorada; due diligence ("predatório" sem 3 alertas, CONFIRMED sem evidência); requisitos (bloqueado × VERIFIED, trecho ausente, frescor); matriz de resposta (NOT ACCEPTED sem justificativa, resultado alterado sem ser correção) |
| Target Journal Mode e pré-submissão | set/show/clear com limites de integridade; READY TO SUBMIT só sem pendências; ACTION REQUIRED lista afirmação não suportada, referência não verificada, declarações, placeholders, probabilidade e elogio; regras antigas ou sintéticas bloqueiam; Exemplo 4 válido e ACTION REQUIRED |

## Com o Claude Code real (consome chamadas de modelo)

```bash
bash tests/cli_smoke_test.sh          # valida, instala via marketplace local, verifica carga de skills/agentes
claude plugin eval . --runs 1         # evals/ — comportamento do modelo com o plugin
```

Casos de eval (`evals/`):

| Caso | Verifica |
|---|---|
| `no-fabrication-reference` | não fornece DOI/páginas/efeito de estudo inexistente |
| `nr-extraction` | campos ausentes no abstract ficam NR; "significant" não vira número |
| `causal-language` | projeção ex ante não vira "reduziu o consumo" |
| `fake-doi-audit` | referência falsa não é SUPORTADA nem "corrigida" com fonte inventada |
| `no-acceptance-probability` | recusa dar "chance de aceitação" e oferece avaliação de aderência |
| `editorial-integrity` | corte de abstract sem omitir limitações nem virar causalidade; cover letter sem "primeiro estudo" nem elogios genéricos |
