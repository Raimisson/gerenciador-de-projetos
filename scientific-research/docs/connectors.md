# Conectores e integrações

O plugin **não embute nenhum servidor MCP ativo** (não há `.mcp.json` carregado por padrão).
Motivo: Consensus, Scite, Elicit e Google Drive são conectores do diretório do claude.ai;
quando o usuário já os conectou (situação comum no Claude.ai, no Cowork e no Claude Code
logado na mesma conta), um `.mcp.json` do plugin criaria **servidores duplicados** e novos
prompts de OAuth. As skills detectam as ferramentas disponíveis pelo nome e funcionam de
forma degradada quando elas faltam.

Verificação feita em 24/09/2026 (ver `ARCHITECTURE_PLAN.md`).

## Classificação

| Integração | Classificação | Evidência da verificação | Como ativar | Acesso |
|---|---|---|---|---|
| **Consensus** | **oficial** (diretório de conectores do claude.ai) · requer autenticação | Presente no registro de conectores do claude.ai; URL `https://mcp.consensus.app/mcp` usada no plugin oficial `bio-research` da Anthropic (`anthropics/knowledge-work-plugins`) | claude.ai → Configurações → Conectores → Consensus; ou `claude mcp add --transport http consensus https://mcp.consensus.app/mcp` | leitura (busca) |
| **Scite** | **oficial** (diretório claude.ai) · requer autenticação | Registro de conectores do claude.ai; URL `https://api.scite.ai/mcp` no repositório oficial `scitedotai/scite-mcp-skill` | Conector no claude.ai; ou `claude mcp add --transport http scite https://api.scite.ai/mcp` | leitura + escrita em coleções (o hook pede confirmação) |
| **Elicit** | **oficial** (diretório claude.ai) · requer autenticação e plano com acesso à API | Registro de conectores do claude.ai; URL `https://elicit.com/api/mcp` no repositório oficial `elicit/api-examples` | Conector no claude.ai; ou `claude mcp add --transport http elicit https://elicit.com/api/mcp` | leitura + escrita em biblioteca/revisões (o hook pede confirmação) |
| **Google Drive** | **oficial** · requer autenticação | Conector do claude.ai; URL `https://drivemcp.googleapis.com/mcp/v1` usada em plugin oficial da Anthropic | claude.ai → Conectores → Google Drive | leitura + escrita (o hook pede confirmação para criar/alterar/compartilhar) |
| **Exa** | **verificada** (plugin de terceiro no marketplace oficial `claude-plugins-official`) · opcional · requer chave/conta Exa | Entrada `exa` no marketplace oficial | `/plugin install exa@claude-plugins-official` | leitura web |
| **Firecrawl** | **verificada** (plugin de terceiro no marketplace oficial) · opcional · requer chave | Entrada `firecrawl` no marketplace oficial | `/plugin install firecrawl@claude-plugins-official` | leitura/raspagem web |
| **Tavily** | **verificada** (plugin de terceiro no marketplace oficial) · opcional · requer chave | Entrada `tavily` no marketplace oficial | `/plugin install tavily@claude-plugins-official` | leitura web |
| **OpenAlex** | **opcional** · sem conector oficial encontrado · **não requer credencial** | API REST pública | Automático via `scripts/srtool.py search-openalex` / `chase` (ou WebFetch) | leitura |
| **Crossref** | **opcional** · sem conector oficial encontrado · não requer credencial | API REST pública | Automático via `srtool.py doi-check` / `refs-check` | leitura |
| **Semantic Scholar** | **opcional** · sem conector oficial encontrado; não configurado | API REST pública (limites mais rígidos sem chave) | WebFetch `https://api.semanticscholar.org/graph/v1/...` quando necessário | leitura |
| **Zotero** | **comunitária** · **não configurável automaticamente** | Nenhum conector oficial; servidores comunitários (ex.: `kujenga/zotero-mcp`, somente leitura; `54yyyu/zotero-mcp`, leitura e escrita) | Ver seção Zotero | **leitura por padrão**; escrita só com pedido explícito (hook pede confirmação) |

> "oficial" = disponível no diretório de conectores do claude.ai e/ou usado em plugin oficial
> da Anthropic; "verificada" = listada no marketplace oficial `claude-plugins-official`, mas
> mantida pelo fornecedor; "comunitária" = mantida por terceiros sem vínculo com o serviço.

Os nomes das ferramentas mudam conforme a forma de conexão: conector do claude.ai
(ex.: `mcp__Scite__search_literature`), servidor adicionado com `claude mcp add`
(ex.: `mcp__scite__search_literature`) ou servidor de plugin
(`mcp__plugin_<plugin>_<servidor>__<ferramenta>`). As skills procuram pelo nome do serviço,
não por um identificador fixo.

## Hierarquia padrão de descoberta (não rígida)

```
Pesquisa acadêmica:   Consensus / Elicit → Semantic Scholar / OpenAlex (e Scite) → Crossref → web
Validação de citação: Scite → artigo original → Crossref / DOI → outras fontes
Biblioteca pessoal:   Zotero (somente leitura)
Literatura cinzenta:  Exa / Firecrawl / Tavily / WebSearch → site do emissor (fonte primária)
Normas/regulação:     portais oficiais (diários oficiais, sites de agências) → literatura
```

Use outra ordem quando for claramente mais apropriado (ex.: RePEc/SSRN para economia;
SciELO para América Latina; portal da agência para normas).

## Modo degradado (sem conectores)

| Disponível | Comportamento |
|---|---|
| Só WebSearch/WebFetch | Busca web + APIs públicas via WebFetch; cobertura declarada como limitada |
| Só Bash + rede | `srtool.py search-openalex`, `chase`, `doi-check`, `refs-check` |
| Nada de rede | O plugin entrega estratégia, strings, templates e validações locais; buscas ficam `executed: false` no log e nenhuma referência é "lembrada" |
| Sem Bash/Python | Skills funcionam como instruções; validações feitas manualmente pelo modelo seguindo os schemas |

Toda falha de ferramenta é registrada e leva a `UNVERIFIED`, nunca a "preenchimento".

## Zotero (comunitário, somente leitura por padrão)

1. Zotero 7+ → Configurações → Avançado → marque *Allow other applications on this
   computer to communicate with Zotero*.
2. Instale `uv` e adicione o servidor somente leitura:
   ```bash
   claude mcp add zotero --env ZOTERO_LOCAL=true -- uvx zotero-mcp@latest
   ```
   (exemplo equivalente em `connectors/zotero-readonly.example.json`).
3. **Riscos**: código de terceiros executado localmente com acesso à sua biblioteca;
   revise o repositório antes (`https://github.com/kujenga/zotero-mcp`). Servidores com
   escrita (ex.: `54yyyu/zotero-mcp`) podem alterar a biblioteca — o hook
   `guard_library_writes.py` pede confirmação para qualquer ferramenta de escrita de um
   servidor cujo nome contenha "zotero".
4. Se usar Web API em vez do modo local, crie uma chave **somente leitura** e guarde-a em
   variável de ambiente (ver `connectors/.env.example`), nunca no repositório.

## Claude Code × Claude.ai/Cowork

| Componente | Claude Code (CLI/Desktop/Web) | Claude.ai / Cowork |
|---|---|---|
| Skills | sim | sim (formato `skills/<nome>/SKILL.md`) |
| Subagentes | sim | depende do ambiente; as skills funcionam sem eles |
| Hooks (`python3`) | sim, se `python3` estiver no PATH | podem não ser executados; regras também estão nas skills |
| `srtool.py` | sim, com Bash | só onde houver execução de código |
| Conectores | conectores do claude.ai (conta logada) ou `claude mcp add` | conectores do claude.ai |

A documentação oficial consultada (code.claude.com) não traz matriz de compatibilidade entre
Claude Code e Cowork; o desenho acima maximiza compatibilidade mantendo as regras críticas
dentro das próprias skills.
