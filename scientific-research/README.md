# Scientific Research — plugin para Claude

Ambiente reutilizável de pesquisa científica e redação de artigos, com rastreabilidade de
evidências e regras estritas contra fabricação. Pensado para pesquisa aplicada em **regulação,
políticas públicas, economia, energia, infraestrutura, saneamento, avaliação de políticas e
programas, AIR/ARR e eficiência energética** — mas genérico o bastante para outras áreas.

Versão **0.1.0** · Licença MIT · Formato oficial de plugins do Claude Code (verificado em 24/09/2026).

---

## Visão geral

O plugin cobre o ciclo completo de um artigo, e cada etapa pode ser usada isoladamente:

```
Pergunta → Protocolo → Busca (acadêmica, cinzenta, regulatória, citation chasing) → Triagem →
Extração → Evidence Ledger → Matriz de evidências → Avaliação metodológica → Síntese →
Redação → Auditoria de citações e referências → Auditoria final do manuscrito
```

O que o diferencia de "pedir ao Claude para escrever uma revisão":

- **Nada é inventado**: sem artigo, DOI, autor, página ou número que não tenha vindo de uma
  fonte consultada. Lacunas são declaradas (`NR — não reportado`; "Não foi possível verificar
  esta informação nas fontes consultadas.").
- **Proveniência**: cada frase empírica do manuscrito aponta para uma evidência do
  *Evidence Ledger* (`[E-0001]`), que aponta para trecho, página/tabela e fonte.
- **Separação explícita** entre **[FONTE]**, **[AUTORES]** e **[INFERÊNCIA]**.
- **Checagens automáticas** (`scripts/srtool.py`): DOI que não resolve, título/autores
  incompatíveis, números sem fonte, linguagem causal sobre evidência não causal,
  generalização indevida, fonte secundária, aritmética do fluxo PRISMA.

## Instalação

### Claude Code (CLI, Desktop ou Web)

Pela interface de plugins:

```text
/plugin marketplace add Raimisson/gerenciador-de-projetos
/plugin install scientific-research@raimisson-research
```

Ou pelo terminal:

```bash
claude plugin marketplace add Raimisson/gerenciador-de-projetos
claude plugin install scientific-research@raimisson-research
```

Reinicie a sessão (ou use `/reload-plugins`) e confira em `/plugin` → *Installed*.

A partir de um clone local (desenvolvimento/teste, sem instalar):

```bash
git clone https://github.com/Raimisson/gerenciador-de-projetos
claude --plugin-dir gerenciador-de-projetos/scientific-research
```

> O marketplace fica na raiz do repositório (`.claude-plugin/marketplace.json`) e aponta para
> `./scientific-research`. `marketplace add owner/repo` lê o branch padrão do GitHub: enquanto o
> plugin não estiver no branch padrão, adicione o marketplace a partir de um clone local já no
> branch do plugin:
>
> ```bash
> git clone -b claude/busy-faraday-mqt2tg https://github.com/Raimisson/gerenciador-de-projetos
> claude plugin marketplace add ./gerenciador-de-projetos
> claude plugin install scientific-research@raimisson-research
> ```

### Claude.ai / Cowork

A documentação oficial consultada não traz matriz de compatibilidade entre Claude Code e
Cowork. As **skills** usam o formato padrão (`skills/<nome>/SKILL.md`) e são o componente mais
portável; subagentes, hooks e o `srtool.py` dependem do ambiente permitir agentes e execução de
código. Todas as regras de integridade estão **dentro de cada skill**, então o comportamento
essencial se mantém mesmo sem hooks ou scripts. Ver `docs/connectors.md` §"Claude Code × Claude.ai/Cowork".

## Dependências

| Tipo | Item | Observação |
|---|---|---|
| Obrigatória | Claude Code com suporte a plugins | testado com 2.1.282 |
| Recomendada | Python 3.9+ no `PATH` como `python3` | hooks e `srtool.py`; só biblioteca padrão, nada a instalar |
| Opcional | Conectores Consensus, Scite, Elicit, Google Drive | ver Conectores |
| Opcional | Plugins Exa, Firecrawl, Tavily (marketplace oficial) | busca web / literatura cinzenta |
| Opcional | Zotero + MCP comunitário somente leitura | biblioteca pessoal |
| Opcional | Rede para `api.crossref.org`, `doi.org`, `api.openalex.org` | verificação de DOI e citation chasing via `srtool.py` |

Sem Python, as skills continuam funcionando como instruções (as validações passam a ser feitas
pelo modelo seguindo os schemas). No Windows, se `python3` não existir, os hooks falham de forma
não bloqueante — crie o alias ou ajuste `hooks/hooks.json` para `python`.

## Conectores

Resumo (detalhes, evidências da verificação e riscos em [`docs/connectors.md`](docs/connectors.md)):

| Integração | Classificação | Como ativar |
|---|---|---|
| Consensus | **oficial** · disponível mas requer autenticação | claude.ai → Configurações → Conectores; ou `claude mcp add --transport http consensus https://mcp.consensus.app/mcp` |
| Scite | **oficial** · disponível mas requer autenticação | conector do claude.ai; ou `claude mcp add --transport http scite https://api.scite.ai/mcp` |
| Elicit | **oficial** · disponível mas requer autenticação (plano com API) | conector do claude.ai; ou `claude mcp add --transport http elicit https://elicit.com/api/mcp` |
| Google Drive | **oficial** · disponível mas requer autenticação | conector do claude.ai |
| Exa / Firecrawl / Tavily | **verificada** (marketplace oficial, mantida pelo fornecedor) · opcional · requer chave | `/plugin install exa@claude-plugins-official` (idem `firecrawl`, `tavily`) |
| OpenAlex / Crossref | **opcional** · sem conector oficial · sem credencial | automático via `srtool.py` |
| Semantic Scholar | **opcional** · sem conector oficial · **não configurado** | WebFetch na API pública quando necessário |
| Zotero | **comunitária** · **não configurável automaticamente** · leitura por padrão | `claude mcp add zotero --env ZOTERO_LOCAL=true -- uvx zotero-mcp@latest` (ver riscos) |

O plugin **não ativa nenhum servidor MCP por conta própria** (sem `.mcp.json`): isso evita
ferramentas duplicadas quando você já usa os conectores do claude.ai. O arquivo
`connectors/mcp-servers.optional.json` traz a configuração pronta para quem preferir.
Sem conectores, o plugin opera em modo degradado (web + APIs públicas, ou apenas arquivos que
você fornecer) e registra a limitação de cobertura.

## Skills

Invocação: `/scientific-research:<skill>` ou linguagem natural (as skills são acionadas pelo contexto).

| Skill | Finalidade |
|---|---|
| `research-project` | **Workflow principal**: diagnostica o estado do projeto e conduz as etapas necessárias |
| `research-question` | Pergunta de pesquisa, constructos, hipóteses (rotuladas), estratégias de identificação |
| `literature-search` | Estratégia de busca, strings booleanas por base, execução e search log reproduzível |
| `citation-chasing` | Backward, forward e similar papers a partir de artigo(s) semente |
| `grey-literature` | Governos, reguladores, organizações internacionais, working papers, avaliações |
| `regulatory-research` | Modo regulatório: legislação, normas, AIR, ARR, consultas públicas, benchmark internacional |
| `systematic-review` | Protocolo, critérios, triagem, deduplicação, fluxo inspirado em PRISMA |
| `evidence-extraction` | Ficha estruturada por documento, com `NR` e localização |
| `quantitative-evidence` | Coeficientes, EP, IC, elasticidades, equações, tabelas; análise reproduzível |
| `evidence-ledger` | Registro de evidências e proveniência ("de onde veio esta afirmação?") |
| `evidence-matrix` | Matriz comparativa compacta e detalhada (MD/CSV/JSON) |
| `methodology-review` | Avaliação crítica do desenho (endogeneidade, DiD, IV, RDD, validade…) |
| `evidence-synthesis` | Síntese por desfecho, força da evidência, portão de viabilidade de meta-análise |
| `scientific-writing` | Redação de seções usando só evidência validada, com linguagem causal calibrada |
| `citation-audit` | Auditoria frase a frase: SUPORTADA / PARCIALMENTE / NÃO SUPORTADA / NÃO VERIFICÁVEL |
| `bibliography-audit` | Metadados, duplicatas, referências inventadas; ABNT, APA, Chicago, BibTeX |
| `replication-check` | Dados, código, parâmetros, filtros, software, seeds |
| `manuscript-review` | Auditoria final: coerência, números, tabelas/figuras, causalidade, limitações |

## Agents

| Agent | Finalidade |
|---|---|
| `literature-researcher` | Descoberta bibliográfica rastreável e citation chasing em buscas extensas |
| `methodology-reviewer` | Avaliação independente de desenho, econometria e avaliação (somente leitura) |
| `citation-auditor` | Auditor conservador de DOI, metadados e correspondência afirmação-fonte (somente leitura) |
| `scientific-editor` | Redação acadêmica **sem acesso à web** — só usa o que está no ledger |
| `quantitative-analyst` | Extração quantitativa de estudos complexos, comparabilidade de unidades, análise reproduzível |
| `regulatory-researcher` | Levantamento normativo e regulatório em paralelo à busca acadêmica |

Subagentes são usados só quando há paralelismo real ou verificação independente; tarefas simples
são executadas diretamente. `systematic-review-specialist` não foi criado por redundância com a
skill `systematic-review`.

## Workflows

**Projeto completo**
```text
/scientific-research:research-project Efeitos da regulação por incentivos sobre perdas não técnicas em distribuidoras
```

**Busca + matriz rápida**
```text
/scientific-research:literature-search Quais estudos estimam a elasticidade-preço da demanda residencial de água no Brasil?
/scientific-research:evidence-extraction (para cada PDF)
/scientific-research:evidence-matrix --formato csv --detalhada
```

**Pesquisa regulatória**
```text
/scientific-research:regulatory-research ARR do programa de eficiência energética das distribuidoras --jurisdicao BR --setor energia
```

**Auditoria de manuscrito**
```text
/scientific-research:citation-audit manuscrito.md
/scientific-research:manuscript-review manuscrito.md --profundidade completa
```

**Ferramenta de linha de comando** (dentro do projeto):
```bash
S=<caminho-do-plugin>/scripts/srtool.py
python3 $S init .                                   # cria research/
python3 $S validate project research                # valida fontes, fichas, ledger, search log
python3 $S matrix research/extraction --sources research/sources/sources.json --format md
python3 $S doi-check 10.xxxx/yyyy --title "..." --year 2020 --authors "Sobrenome"
python3 $S refs-check research/sources/sources.json
python3 $S scan research/manuscript/manuscript.md --ledger research/ledger/evidence.jsonl --sources research/sources/sources.json --context Brasil
python3 $S trace E-0003 --ledger research/ledger/evidence.jsonl --sources research/sources/sources.json --manuscript research/manuscript/manuscript.md
python3 $S format research/sources/sources.json --style abnt
python3 $S prisma research/search/search-log.json
python3 $S chase forward 10.xxxx/yyyy
```

### Exemplos completos

| Exemplo | Conteúdo |
|---|---|
| [`examples/01-revenue-decoupling`](examples/01-revenue-decoupling/README.md) | Economia/regulação: busca, citation chasing, triagem, matriz, extração quantitativa |
| [`examples/02-compulsory-energy-efficiency`](examples/02-compulsory-energy-efficiency/README.md) | Avaliação de política: ex ante × ex post, generalização, portão de meta-análise |
| [`examples/03-manuscript-audit`](examples/03-manuscript-audit/README.md) | Auditoria de manuscrito com referência falsa e defeitos plantados |

Os exemplos foram produzidos com ferramentas reais (conector Scite) e documentam onde o acesso
ao texto integral faltou — em vez de preencher as lacunas.

## Scientific integrity

Regras anti-alucinação (documento canônico: [`docs/scientific-method.md`](docs/scientific-method.md)):

1. **Proibido fabricar** artigos, DOI, autores, periódicos, páginas, datas, URLs, coeficientes,
   amostras ou resultados. Memória do modelo não é fonte: uma referência "lembrada" só entra depois
   de localizada numa ferramenta.
2. Frases obrigatórias: *"Não foi possível verificar esta informação nas fontes consultadas."* e
   *"Não foi encontrada evidência quantitativa que permita estimar este parâmetro."*; campos
   ausentes: `NR — não reportado`.
3. **[FONTE] / [AUTORES] / [INFERÊNCIA]** sempre separados.
4. **Hierarquia de fontes primárias** (artigo original → working paper → relatório oficial → dados
   oficiais → documento do regulador → norma → relatório técnico → revisão sistemática → secundárias).
5. **Texto integral antes do abstract**, com página/tabela/figura — ou declaração de que a página
   não é identificável.
6. **Linguagem causal** só quando o desenho identifica causalidade; projeções ex ante não são efeitos.
7. **Taxonomia de verificação**: `VERIFIED` · `PARTIALLY_VERIFIED` · `UNVERIFIED` · `CONTRADICTED`
   · `NOT_REPORTED` (critérios em `docs/scientific-method.md` §9). Falha de ferramenta ⇒ `UNVERIFIED`.
8. **Meta-análise** só após portão de viabilidade; nunca combinar coeficientes incompatíveis
   (a v0.1 não calcula pooling).
9. **Dados brutos imutáveis**: hook pede confirmação antes de alterar `data/raw/`.
10. **Zotero somente leitura** por padrão; escrita em bibliotecas exige intenção explícita (hook).

Essas regras estão replicadas em cada skill e agente (bloco sincronizado por
`scripts/sync_integrity.py`) e reforçadas por hook de início de sessão.

## Testes e validação

```bash
cd scientific-research
python3 -m unittest discover -s tests -v     # 45 testes (estrutura, NR, DOI falso, não fabricação, hooks, offline)
claude plugin validate . --strict            # validador oficial
bash tests/cli_smoke_test.sh                 # carrega o plugin num claude -p real (consome chamadas de modelo)
claude plugin eval . --runs 1                # casos de comportamento em evals/ (consome chamadas de modelo)
```

Ver [`tests/README.md`](tests/README.md) para o que cada teste cobre.

## Limitações

- **Acesso ao abstract não substitui o texto integral.** Extrações feitas só com abstract são
  marcadas e mantêm `NR` nos campos quantitativos.
- **Indexação não garante cobertura total.** Toda base tem lacunas (idioma, área, literatura
  cinzenta, paywalls).
- **Resultados de IA precisam de verificação humana**, inclusive decisões de triagem (registradas
  como `claude-proposal`).
- **Ausência de um estudo na busca não prova que ele não existe.**
- **O conteúdo gerado não substitui revisão por especialista.**
- As heurísticas do `scan` (números sem fonte, causalidade, generalização) produzem falsos
  positivos e falsos negativos; não substituem a auditoria frase a frase.
- O formatador de referências é simplificado (casos especiais de ABNT/APA exigem revisão).
- Verificação de DOI depende de acesso de rede a Crossref/doi.org; sem rede o resultado é `UNVERIFIED`.

## Estrutura

```
scientific-research/
├── .claude-plugin/plugin.json      manifesto
├── skills/<18 skills>/SKILL.md
├── agents/<6 agentes>.md
├── hooks/                          hooks.json + scripts Python
├── scripts/                        srtool.py, sync_integrity.py
├── schemas/                        JSON Schemas
├── templates/                      protocolo, search log, fichas, relatórios
├── connectors/                     configuração opcional de MCP (sem credenciais)
├── evals/                          casos para `claude plugin eval`
├── examples/                       3 exemplos completos
├── tests/                          unittest + fixtures + smoke test
├── docs/                           architecture.md, scientific-method.md, connectors.md
├── ARCHITECTURE_PLAN.md · CHANGELOG.md · LICENSE · README.md
```
