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
