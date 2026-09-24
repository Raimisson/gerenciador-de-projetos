# ARCHITECTURE_PLAN — Scientific Research (v0.1.0)

Plano de decisões tomado **antes** da implementação (Fase 2). Registra o que foi
verificado na Fase 1 (Discovery) e as escolhas que derivam disso.

## 1. O que foi verificado na Discovery (24/09/2026)

| Item | Fonte verificada | Conclusão |
|---|---|---|
| Manifesto | `claude plugin init --with skills agents hooks mcp` (Claude Code 2.1.282) e repositório `anthropics/claude-plugins-official` | Manifesto em `.claude-plugin/plugin.json`; único campo obrigatório é `name` (kebab-case). `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords` são opcionais e reconhecidos. |
| Skills | `plugins/example-plugin` oficial | Formato preferido: `skills/<nome>/SKILL.md` com frontmatter `name` + `description`. `commands/` é formato legado. Skills de plugin viram `/scientific-research:<nome>`. |
| Subagentes | scaffold oficial | `agents/<nome>.md` com frontmatter `name`, `description`, `tools`, `model`. |
| Hooks | scaffold oficial | `hooks/hooks.json` com `${CLAUDE_PLUGIN_ROOT}`. |
| MCP | scaffold oficial e `knowledge-work-plugins` | `.mcp.json` com `mcpServers`; servidores remotos usam `"type": "http"`. |
| Validador | `claude plugin validate <path> [--strict]` | Existe e será usado na Fase 11. |
| Marketplace | `.claude-plugin/marketplace.json` dos dois repositórios oficiais | Entrada com `"source": "./subdir"`. |
| Conectores | Registro de conectores do claude.ai + `.mcp.json` oficiais da Anthropic + busca web | Ver §4. |

## 2. Decisões principais

1. **Um plugin, um marketplace local.** O plugin fica em `scientific-research/`. Na raiz
   do repositório há `.claude-plugin/marketplace.json` apontando para `./scientific-research`,
   permitindo `/plugin marketplace add <repo>` + `/plugin install scientific-research@...`.
2. **Skills como unidade principal** (não `commands/`). 18 skills focadas, cada uma com
   seções fixas: quando usar, quando NÃO usar, inputs, workflow, output, critérios de
   qualidade, situações de falha.
3. **Regras de integridade replicadas de forma curta em cada skill** + documento canônico
   `docs/scientific-method.md`. Motivo: skills podem ser carregadas isoladamente; a regra
   anti-fabricação não pode depender de outra skill estar carregada.
4. **Evidence Ledger em JSONL** (`research/ledger/evidence.jsonl`), uma evidência por linha,
   com JSON Schema em `schemas/`. JSONL é diff-friendly no Git, anexável e legível.
   Proveniência por marcadores `[E-0001]` no manuscrito → ledger → `sources.json`.
5. **Scripts pequenos, somente biblioteca padrão Python 3** (`scripts/srtool.py`):
   validação de schemas, exportação de matriz (MD/CSV/JSON), checagem de DOI
   (online, com modo fixture para testes), varredura de manuscrito (números sem fonte,
   linguagem causal, generalização), rastreio de proveniência. Sem servidor, sem banco.
6. **Sem `.mcp.json` ativo por padrão.** Consensus, Scite, Elicit e Google Drive são
   conectores do diretório do claude.ai; se o usuário já os conectou (caso comum), um
   `.mcp.json` do plugin criaria servidores duplicados e prompts de OAuth extras. O plugin
   detecta as ferramentas pelo nome e degrada graciosamente. `connectors/` traz a
   configuração opcional e os comandos `claude mcp add` com URLs verificadas.
7. **Hooks de proteção, não de automação invasiva**:
   - `PreToolUse` em `Write|Edit|MultiEdit|NotebookEdit`: pede confirmação antes de
     alterar dados brutos (`data/raw/`, `*.raw.*`) — "nunca modificar o dataset original
     silenciosamente".
   - `PreToolUse` em `mcp__.*`: pede confirmação para operações de escrita em Zotero e em
     bibliotecas/coleções de conectores de pesquisa (Zotero somente leitura por padrão).
   - `SessionStart`: injeta um lembrete curto (≈120 palavras) das regras de integridade.
8. **Subagentes**: 6 (literature-researcher, methodology-reviewer, citation-auditor,
   scientific-editor, quantitative-analyst, regulatory-researcher). `systematic-review-specialist`
   **não** foi criado: duplicaria a skill `systematic-review` e o `literature-researcher`.
9. **Meta-análise**: não há skill que calcule efeitos combinados na v0.1. Existe
   `evidence-synthesis` com *portão de viabilidade* (comparabilidade de outcome, unidade,
   desenho, população, intervenção, heterogeneidade). Pooling automático fica fora do
   escopo até haver salvaguardas testadas.
10. **Idioma**: conteúdo em português (público-alvo), com gatilhos bilíngues nas
    `description` e rótulos de status em inglês (VERIFIED, NR…) para interoperabilidade.

## 3. Estrutura

```
scientific-research/
├── .claude-plugin/plugin.json
├── skills/<18 skills>/SKILL.md
├── agents/<6 agentes>.md
├── hooks/hooks.json + hooks/*.py
├── scripts/srtool.py (+ módulos)
├── schemas/*.schema.json
├── templates/*.md|json|csv
├── connectors/ (config opcional de MCP, sem credenciais)
├── examples/ (3 exemplos completos)
├── tests/ (unittest + fixtures, inclui referência falsa)
├── docs/architecture.md, docs/scientific-method.md, docs/connectors.md
├── README.md, CHANGELOG.md, LICENSE
```

## 4. Conectores — classificação preliminar

| Integração | Situação encontrada |
|---|---|
| Consensus | Conector oficial do diretório claude.ai; URL `https://mcp.consensus.app/mcp` usada no plugin oficial `bio-research` da Anthropic. |
| Scite | Conector oficial do diretório claude.ai; URL `https://api.scite.ai/mcp` publicada pelo fornecedor. |
| Elicit | Conector oficial do diretório claude.ai; URL `https://elicit.com/api/mcp` reportada publicamente (confirmar). |
| Google Drive | Conector oficial; URL `https://drivemcp.googleapis.com/mcp/v1` usada em plugin oficial da Anthropic. |
| Exa / Firecrawl / Tavily | Plugins de terceiros listados no marketplace oficial `claude-plugins-official`; exigem conta/chave do fornecedor. |
| Semantic Scholar / OpenAlex / Crossref | Nenhum conector oficial encontrado; APIs REST públicas usadas via `srtool.py` ou WebFetch. |
| Zotero | Somente servidores MCP comunitários; não configurado automaticamente; leitura por padrão. |

## 5. Riscos conhecidos

- A rede do ambiente de construção bloqueia Crossref/OpenAlex/Semantic Scholar/doi.org:
  a checagem online de DOI é testada com fixtures; teste online fica documentado como pendente.
- Compatibilidade Cowork/claude.ai: skills e agentes são portáveis; hooks e scripts dependem
  de execução local de `python3` e podem não estar disponíveis em todos os ambientes.
  As skills funcionam sem eles (os scripts são aceleradores, não requisitos).

## 6. Adendo v0.2.0 — módulo Publication Strategy

| Decisão | Motivo |
|---|---|
| Módulo em `modules/publication-strategy/` dentro do mesmo plugin | separação funcional sem perder contexto compartilhado (projeto `research/`, manuscrito, Evidence Ledger) — não é um plugin independente |
| Skills do módulo carregadas por `"skills": ["./skills", "./modules/publication-strategy/skills"]` | testado com `claude plugin validate --strict`, instalação real e `plugin details` |
| Agente `publication-strategist` em `agents/` | o campo `agents` substitui o diretório padrão; manter um único diretório evita ambiguidade |
| `pubtool.py` separado, importando `srtool.py` | reutiliza validador e varredura do núcleo; nenhuma dependência externa |
| Índice de aderência com cobertura, sem probabilidade | exigência do princípio fundamental; validadores e lint bloqueiam probabilidades |
| Target Journal Mode como arquivo de estado | simples, auditável e legível por skills, scripts e humanos |
| Exemplo com requisitos reais `NOT VERIFIED` + requisitos sintéticos rotulados | sites de editoras bloqueados no ambiente de construção; nada foi preenchido de memória |
