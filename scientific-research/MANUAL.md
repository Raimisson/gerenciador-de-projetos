# Manual do usuário — Plugin **Scientific Research** (v0.2.2)

> Manual didático e completo. Leia as seções 1 a 6 antes de começar (cerca de 20 minutos) e use o
> restante como consulta. Os termos em `código` são nomes de comandos, arquivos ou status.

---

## Sumário

1. [O que é, em 1 minuto](#1-o-que-é-em-1-minuto)
2. [Para quem é e quando vale a pena](#2-para-quem-é-e-quando-vale-a-pena)
3. [Conceitos que você precisa conhecer](#3-conceitos-que-você-precisa-conhecer)
4. [Instalação passo a passo](#4-instalação-passo-a-passo)
5. [Preparando o ambiente: conectores, Python e Zotero](#5-preparando-o-ambiente-conectores-python-e-zotero)
6. [Seus primeiros 20 minutos (tutorial guiado)](#6-seus-primeiros-20-minutos-tutorial-guiado)
7. [Como conversar com o plugin](#7-como-conversar-com-o-plugin)
8. [A pasta do projeto: o que fica onde](#8-a-pasta-do-projeto-o-que-fica-onde)
9. [Guia etapa por etapa — Parte A: da pergunta ao manuscrito](#9-guia-etapa-por-etapa--parte-a-da-pergunta-ao-manuscrito)
10. [Guia etapa por etapa — Parte B: do manuscrito à publicação](#10-guia-etapa-por-etapa--parte-b-do-manuscrito-à-publicação)
11. [Receitas prontas para situações comuns](#11-receitas-prontas-para-situações-comuns)
12. [Como ler os resultados](#12-como-ler-os-resultados)
13. [Os subagentes: quando o plugin trabalha "em equipe"](#13-os-subagentes-quando-o-plugin-trabalha-em-equipe)
14. [Ferramentas de linha de comando (opcional)](#14-ferramentas-de-linha-de-comando-opcional)
15. [O que o plugin NÃO faz](#15-o-que-o-plugin-não-faz)
16. [Limitações e cuidados](#16-limitações-e-cuidados)
17. [Boas práticas para usar com efetividade](#17-boas-práticas-para-usar-com-efetividade)
18. [Solução de problemas (FAQ)](#18-solução-de-problemas-faq)
19. [Cola de referência rápida](#19-cola-de-referência-rápida)
20. [Onde saber mais](#20-onde-saber-mais)

---

## 1. O que é, em 1 minuto

O **Scientific Research** é um plugin para o Claude (Claude Code) que transforma o Claude num
**assistente de pesquisa científica disciplinado**. Ele acompanha todo o ciclo de um artigo:

```
Pergunta → Protocolo → Busca → Triagem → Extração de evidências → Evidence Ledger → Matriz
→ Avaliação metodológica → Síntese → Redação → Auditoria de citações → Revisão do manuscrito
→ Escolha do periódico → Adequação às normas → Auditoria pré-submissão → Submissão
→ Resposta aos revisores → Publicação ou ressubmissão
```

O que o torna diferente de simplesmente "pedir ao Claude um artigo":

| Sem o plugin | Com o plugin |
|---|---|
| O modelo pode "lembrar" referências que não existem | **Nada é inventado.** Referência só entra se foi encontrada numa ferramenta e verificada |
| Números aparecem sem origem clara | Cada número do texto aponta para uma **evidência registrada**, com trecho e página |
| Fatos, interpretações dos autores e opiniões se misturam | Tudo é rotulado: **[FONTE]**, **[AUTORES]**, **[INFERÊNCIA]** |
| "O estudo mostra que X causou Y" (mesmo quando não mostra) | Linguagem causal só quando o desenho do estudo permite |
| "Essa revista tem 80% de chance de aceitar" | **Nunca** há probabilidade de aceitação; há avaliação de aderência com fontes |
| Lacunas preenchidas "no chute" | Lacunas declaradas: `NR — não reportado`, "Não foi possível verificar…" |

Foi pensado para pesquisa aplicada em **regulação, políticas públicas, economia, energia,
infraestrutura, saneamento, avaliação de políticas, AIR/ARR e eficiência energética**, mas funciona
em qualquer área.

---

## 2. Para quem é e quando vale a pena

**Vale muito a pena quando você:**
- vai escrever um artigo, dissertação, tese, nota técnica, AIR/ARR ou relatório com revisão de literatura;
- precisa **provar de onde veio** cada afirmação (bancas, pareceristas, órgãos de controle);
- quer extrair números de estudos (coeficientes, elasticidades, custos) com rastreabilidade;
- recebeu um texto (seu, de colegas ou gerado por IA) e precisa **auditar** as citações;
- vai escolher um periódico e quer reduzir o risco de *desk rejection*;
- recebeu pareceres e precisa organizar a resposta.

**Vale menos a pena quando:**
- você só quer uma explicação rápida de um conceito (pergunte direto ao Claude);
- o texto é opinativo, sem pretensão de rastreabilidade;
- você não pretende verificar nada do que for produzido (o plugin reduz erros, mas não substitui você).

---

## 3. Conceitos que você precisa conhecer

### 3.1 Skill (habilidade)
Um roteiro de trabalho especializado. O plugin tem **30 skills** (18 de pesquisa + 12 de publicação).
Você pode chamá-las pelo nome (`/scientific-research:citation-audit`) ou simplesmente descrever o que
quer — o Claude escolhe a skill adequada.

### 3.2 Subagente
Um "especialista" que o Claude pode acionar para trabalhar em paralelo ou de forma independente
(ex.: um auditor de citações que confere o trabalho do redator). São 7. Ver seção 13.

### 3.3 Conector (MCP)
Uma ligação do Claude com um serviço externo: Consensus, Scite, Elicit (bases acadêmicas), Google
Drive, Zotero… O plugin **usa os conectores que você tiver** e funciona de forma reduzida sem eles.

### 3.4 Projeto de pesquisa (`research/`)
Uma pasta com tudo o que o plugin produz: log de busca, fichas de extração, Evidence Ledger, matriz,
manuscrito, auditorias, estratégia de publicação. É o "caderno de laboratório" do seu artigo. Ver seção 8.

### 3.5 Evidence Ledger (livro-razão de evidências)
O coração do plugin. É um arquivo (`research/ledger/evidence.jsonl`) com **uma linha por evidência**:
qual fonte, qual trecho literal, qual página/tabela, qual afirmação ela sustenta, que tipo de estudo é,
se foi verificada. No manuscrito, cada frase empírica termina com um marcador como `[E-0003]`, que
aponta para essa linha. Assim, qualquer pessoa pode perguntar **"de onde veio esta frase?"** e
obter a resposta completa.

```
fonte (S-0002) → evidência (E-0003: trecho, página, tabela) → parágrafo do artigo (... [E-0003])
```

### 3.6 NR — não reportado
Quando um estudo não informa algo (tamanho da amostra, erro-padrão, período…), o campo fica
`NR — não reportado`. **O plugin nunca preenche por dedução.** `NA — não se aplica` é usado quando o
campo não faz sentido para aquele estudo.

### 3.7 As três etiquetas
| Etiqueta | Significa | Exemplo |
|---|---|---|
| **[FONTE]** | o que o documento mostra | "Tabela 2: média de 0,4%" |
| **[AUTORES]** | o que os autores concluem | "os autores interpretam como efeito do mecanismo" |
| **[INFERÊNCIA]** | raciocínio do Claude | "isso sugere que o resultado pode não valer para o Brasil" |

### 3.8 Status de verificação
| Status | Quer dizer |
|---|---|
| `VERIFIED` | conferido em fonte autoritativa e com trecho localizado |
| `PARTIALLY_VERIFIED` | parte conferida (ex.: só o abstract; ou metadados só num índice) |
| `UNVERIFIED` | ainda não conferido **ou a ferramenta falhou** — não significa falso |
| `CONTRADICTED` | a fonte contradiz (ex.: DOI de outro artigo) |
| `NOT_REPORTED` | a fonte foi lida e a informação não está lá |

### 3.9 Journal fit (aderência ao periódico)
Avaliação, em 7 dimensões, de quanto o seu manuscrito combina com um periódico (tema, método,
contribuição, dados, público, publicações recentes, tipo de artigo). Gera um **índice de 0 a 100 com
cobertura** (ex.: "67, cobertura 3/7"). **Não é probabilidade de aceitação.**

### 3.10 Target Journal Mode (modo periódico-alvo)
Depois que **você** escolhe o periódico, esse modo faz todas as recomendações editoriais seguirem as
regras daquele periódico. Mesmo nesse modo, nenhuma regra editorial justifica alterar resultados,
omitir achados, inventar análises ou referências, ou exagerar conclusões.

---

## 4. Instalação passo a passo

### 4.1 O que você precisa
- **Claude Code** (terminal, app Desktop ou versão web em claude.ai/code), com login na sua conta.
- **Recomendado:** Python 3.9 ou superior disponível como `python3` (para os scripts e proteções automáticas).
  Não é preciso instalar bibliotecas.

### 4.2 Instalar (Claude Code, qualquer versão)

**Opção A — pelo próprio Claude (mais simples).** Numa conversa do Claude Code, digite:

```text
/plugin marketplace add Raimisson/gerenciador-de-projetos
/plugin install scientific-research@raimisson-research
```

**Opção B — pelo terminal:**

```bash
claude plugin marketplace add Raimisson/gerenciador-de-projetos
claude plugin install scientific-research@raimisson-research
```

> **Importante:** `marketplace add Raimisson/gerenciador-de-projetos` lê o **branch padrão** do
> repositório no GitHub. Enquanto o plugin não tiver sido mesclado nesse branch, instale a partir de
> uma cópia local do branch do plugin:
>
> ```bash
> git clone -b claude/busy-faraday-mqt2tg https://github.com/Raimisson/gerenciador-de-projetos
> claude plugin marketplace add ./gerenciador-de-projetos
> claude plugin install scientific-research@raimisson-research
> ```

### 4.2b Instalação local no Windows (pasta `C:\Users\raimi\Documents\claude`)

Use esta opção para manter o plugin numa pasta do seu computador, sem depender do GitHub.

1. Baixe o pacote `scientific-research-windows.zip` (ou gere-o a partir do repositório: conteúdo de
   `install/` + pastas `.claude-plugin/` e `scientific-research/` da raiz do repositório).
2. Extraia **todo** o conteúdo em `C:\Users\raimi\Documents\claude`. Devem existir:
   - `C:\Users\raimi\Documents\claude\.claude-plugin\marketplace.json` (pasta que começa com ponto)
   - `C:\Users\raimi\Documents\claude\scientific-research\` (o plugin)
   - `C:\Users\raimi\Documents\claude\instalar-plugin.ps1`
3. Abra o **PowerShell** e execute:
   ```powershell
   cd C:\Users\raimi\Documents\claude
   powershell -ExecutionPolicy Bypass -File .\instalar-plugin.ps1
   ```
   O script confere o Claude Code e o Python, registra a pasta como *marketplace* local e instala
   `scientific-research@raimisson-research`.
4. Sem o script, o equivalente é:
   ```powershell
   claude plugin marketplace add "C:\Users\raimi\Documents\claude"
   claude plugin install scientific-research@raimisson-research
   ```
5. Feche e abra o Claude Code. **Não apague nem mova a pasta** depois de instalar; para atualizar,
   substitua a pasta `scientific-research` pela versão nova e rode o script de novo.

**Python no Windows:** instale o Python 3 em python.org marcando *"Add python.exe to PATH"*. As
proteções automáticas (hooks) tentam `python3`, `python` e `py`, nessa ordem. Nos comandos das
seções 14.1 e 14.2, troque `python3` por `python` se necessário.

### 4.3 Conferir se deu certo

```bash
claude plugin list
```

Deve aparecer `scientific-research@raimisson-research — Version: 0.2.1 — Status: enabled`.
Para ver o inventário (30 skills, 7 agentes, 2 hooks):

```bash
claude plugin details scientific-research@raimisson-research
```

Depois **reinicie a sessão** do Claude Code (ou use `/reload-plugins`). Na conversa, digite `/` e
comece a escrever `scientific-research` — as skills aparecem na lista.

### 4.4 Atualizar, desativar, remover

```bash
claude plugin marketplace update raimisson-research        # busca a versão nova
claude plugin update scientific-research@raimisson-research
claude plugin disable scientific-research@raimisson-research   # desliga sem remover
claude plugin enable scientific-research@raimisson-research
claude plugin uninstall scientific-research@raimisson-research
```

### 4.5 Testar sem instalar
```bash
claude --plugin-dir caminho/para/gerenciador-de-projetos/scientific-research
```

### 4.6 Usar no Claude Cowork (app Desktop) e no Claude.ai

Plugins estão disponíveis nos planos pagos (Pro, Max, Team, Enterprise). Fonte: artigo oficial
"Use plugins in Claude" (support.claude.com), consultado em 25/09/2026.

**Instalar no Cowork — opção 1: enviar o arquivo do plugin**
1. Obtenha `scientific-research-cowork.zip` (o `.claude-plugin/plugin.json` fica na raiz do zip).
   Para gerar a partir do repositório: compacte o **conteúdo** da pasta `scientific-research/`
   (não a pasta em si); `tests/`, `evals/` e `install/` podem ficar de fora.
2. No app Claude Desktop, abra a aba **Cowork**.
3. Clique em **Customize** → aba **Plugins**.
4. Use a opção de **enviar (upload) um plugin personalizado** e selecione o `.zip`.
5. Confirme que "Scientific Research" aparece como instalado e ativo.

**Instalar no Cowork — opção 2: sincronizar a partir do GitHub**
Em **Customize → Plugins**, adicione um marketplace sincronizado com o repositório
`Raimisson/gerenciador-de-projetos` (o arquivo `.claude-plugin/marketplace.json` está na raiz) e instale
`scientific-research`. Só funciona depois que o plugin estiver no branch padrão do repositório.

**No Claude.ai (chat web):** menu **Customize** (barra lateral) → **Plugins**. No chat, **apenas as
skills** funcionam; subagentes e hooks aparecem desabilitados (funcionam no Cowork e no Claude Code).

**O que funciona onde**

| Componente | Claude Code | Cowork | Chat (claude.ai) |
|---|---|---|---|
| 30 skills (`/scientific-research:…`) | ✔ | ✔ | ✔ |
| 7 subagentes | ✔ | ✔ | — |
| Hooks (lembrete, proteção de `data/raw/`, Zotero) | ✔ | ✔ (exigem Python no ambiente) | — |
| Scripts `srtool.py` / `pubtool.py` | ✔ | quando o ambiente executa código | — |
| Conectores do claude.ai (Scite, Consensus, Elicit, Drive…) | ✔ | ✔ | ✔ |

**Como trabalhar no Cowork**
1. Ative os conectores de pesquisa em **Customize → Connectors** (Scite, Consensus, Elicit, Google Drive).
2. Dê ao Cowork acesso a uma **pasta de trabalho** do seu computador — por exemplo
   `C:\Users\raimi\Documents\claude\projetos\<nome-do-artigo>`. É nela que o plugin cria `research/`
   (log de busca, fichas, Evidence Ledger, manuscrito, auditorias, estratégia de publicação).
3. Coloque os PDFs dos artigos nessa pasta (ou numa subpasta `pdfs/`) e peça, por exemplo:
   *"Use /scientific-research:research-project para iniciar um projeto sobre … nesta pasta."*
4. Dê as tarefas em linguagem natural; o Cowork trabalha por etapas e entrega arquivos prontos.
   Exemplos: *"extraia as evidências de todos os PDFs da pasta pdfs/ para fichas e para o ledger"*,
   *"gere a matriz de evidências em CSV"*, *"audite as citações de manuscrito.docx"*,
   *"faça a auditoria pré-submissão para a revista X"*.

**Limites e cuidados no Cowork**
- A compatibilidade específica deste plugin com o Cowork **não foi testada**; ele segue o formato
  oficial de plugins, que o Cowork usa.
- Se os scripts não puderem ser executados no ambiente, as skills seguem funcionando como
  instruções, e as validações são feitas pelo próprio Claude seguindo os schemas.
- Não instale o mesmo plugin pelo Cowork e pelo Claude Code com versões diferentes; atualize os dois
  juntos para evitar comportamentos distintos.

### 4.7 Custo de contexto
O plugin adiciona cerca de **3,1 mil tokens** a cada sessão (as descrições das skills que o Claude
precisa conhecer). O conteúdo completo de uma skill só é carregado quando ela é usada. Se você
não estiver fazendo pesquisa por um tempo, pode desativar o plugin (seção 4.4).

---

## 5. Preparando o ambiente: conectores, Python e Zotero

### 5.1 Conectores recomendados

Quanto mais conectores, melhor a busca. Nenhum é obrigatório.

| Conector | Para quê | Como ativar |
|---|---|---|
| **Scite** | busca acadêmica, texto integral de artigos abertos, "quem citou", checagem de retratações | claude.ai → Configurações → Conectores → Scite (ou `claude mcp add --transport http scite https://api.scite.ai/mcp`) |
| **Consensus** | busca acadêmica semântica | claude.ai → Conectores → Consensus (ou `claude mcp add --transport http consensus https://mcp.consensus.app/mcp`) |
| **Elicit** | busca e revisões sistemáticas (exige plano com acesso à API) | claude.ai → Conectores → Elicit (ou `claude mcp add --transport http elicit https://elicit.com/api/mcp`) |
| **Google Drive** | ler seus PDFs e rascunhos | claude.ai → Conectores → Google Drive |
| **Exa / Tavily / Firecrawl** | web e literatura cinzenta | `/plugin install exa@claude-plugins-official` (idem `tavily`, `firecrawl`); exigem chave do fornecedor |
| **Zotero** | sua biblioteca pessoal, **somente leitura** | ver 5.3 |

Se você usa o Claude Code logado na mesma conta do claude.ai, os conectores ativados lá costumam
aparecer automaticamente. **Não ative o mesmo serviço duas vezes** (pelo claude.ai e pelo
`claude mcp add`): as ferramentas ficam duplicadas.

> Dica: planos gratuitos têm limites (ex.: número de buscas por mês). Quando uma busca falha por
> limite, o plugin **registra a falha** no log em vez de inventar resultados.

### 5.2 Python
Com `python3` disponível, o plugin:
- valida automaticamente fichas, ledger e logs;
- gera matrizes em Markdown/CSV/JSON;
- verifica DOIs no Crossref;
- varre o manuscrito atrás de números sem fonte e causalidade indevida;
- faz a auditoria pré-submissão;
- **protege seus dados brutos** e sua biblioteca Zotero (pede confirmação antes de alterações).

No Windows, se só existir `python` (sem o "3"), crie um alias `python3` ou peça ao Claude para ajustar.

### 5.3 Zotero (opcional, somente leitura)
1. No Zotero 7+: Configurações → Avançado → marque **"Allow other applications on this computer to communicate with Zotero"**.
2. Instale o `uv` (gerenciador Python) e rode:
   ```bash
   claude mcp add zotero --env ZOTERO_LOCAL=true -- uvx zotero-mcp@latest
   ```
Esse servidor é **comunitário** (mantido por terceiros) e só lê a biblioteca. Se você usar outro
servidor que também escreve, o plugin pedirá confirmação antes de qualquer alteração.

---

## 6. Seus primeiros 20 minutos (tutorial guiado)

Vamos fazer um mini-projeto real. Abra o Claude Code numa pasta vazia (ex.: `meu-artigo/`).

**Passo 1 — Comece pelo workflow principal**
```text
/scientific-research:research-project Quero estudar os efeitos do revenue decoupling sobre programas de eficiência energética de distribuidoras
```
O Claude vai: perguntar o que você já tem; listar os conectores disponíveis; propor as etapas
necessárias; oferecer criar a pasta `research/`. Aceite.

**Passo 2 — Afine a pergunta**
```text
/scientific-research:research-question
```
Você recebe versões da pergunta (ambiciosa, factível, mínima), elementos (população, intervenção,
comparação, desfechos), hipóteses rotuladas como `[HIPÓTESE]` e estratégias de identificação.
Escolha uma versão.

**Passo 3 — Busque a literatura**
```text
/scientific-research:literature-search
```
O plugin monta blocos de conceitos e strings booleanas, executa nos conectores e salva o log
(`research/search/search-log.json`). Repare: as contagens são **exatamente** as informadas pela
ferramenta, e buscas que falharam aparecem como "não executada".

**Passo 4 — Expanda a partir de um artigo-chave**
```text
/scientific-research:citation-chasing 10.5547/01956574.37.4.jkah
```
(troque pelo DOI de um artigo importante para você). Você recebe quem o artigo cita e quem o citou.

**Passo 5 — Extraia a evidência de um estudo**
Envie o PDF (arraste para a conversa ou indique o caminho) e peça:
```text
/scientific-research:evidence-extraction artigo.pdf
```
Você recebe uma ficha com cada campo, **onde** estava no texto e o trecho literal. O que o artigo não
informa fica `NR — não reportado`.

**Passo 6 — Pergunte "de onde veio?"**
```text
De onde veio a evidência E-0001?
```
O plugin mostra a cadeia completa: fonte → trecho e página → tipo de evidência → onde é usada.

Pronto: você já usou o núcleo do plugin. Os exemplos completos em `examples/` mostram o mesmo
fluxo até a matriz, a síntese, a auditoria e a estratégia de publicação.

---

## 7. Como conversar com o plugin

### 7.1 Duas formas de acionar
1. **Comando direto:** `/scientific-research:<skill> [argumentos]`. Útil quando você sabe o que quer.
2. **Linguagem natural:** "audite as citações deste texto", "onde devo publicar este artigo?".
   O Claude reconhece e usa a skill certa.

### 7.2 O que fornecer para ter bons resultados
| Situação | Forneça |
|---|---|
| Extração, avaliação, auditoria | o **PDF ou texto integral** (não só o resumo) |
| Busca | a pergunta, o período, os idiomas e as bases que você considera essenciais |
| Pesquisa regulatória | jurisdição, setor, período e se é para AIR, ARR ou artigo |
| Redação | a seção desejada, o estilo de citação e o periódico-alvo (se já houver) |
| Publicação | o manuscrito, suas restrições (orçamento de APC, open access, indexação exigida, prazo) |
| Resposta a revisores | a carta do editor e os pareceres **na íntegra** |

### 7.3 Frases que ajudam
- "Use apenas evidências do ledger."
- "Se não conseguir verificar, diga que não verificou."
- "Mostre as páginas e os trechos."
- "Separe o que é do estudo, o que é dos autores e o que é inferência sua."
- "Trabalhe no projeto em `research/`."

### 7.4 O que esperar de volta
O plugin costuma responder com: o que foi feito, os arquivos salvos, **o que ficou sem verificação**
e a próxima etapa sugerida. Leia sempre a parte "não verificado / lacunas".

---

## 8. A pasta do projeto: o que fica onde

Criada na primeira vez (o Claude oferece; ou `python3 <plugin>/scripts/srtool.py init .`):

```
research/
├── protocol.md                 pergunta, critérios, decisões e etapas puladas
├── search/                     search-log.json (máquina) + search-log.md (leitura) + prisma-flow.md
├── screening/screening.csv     decisão de triagem de cada registro, com motivo
├── sources/sources.json        todas as fontes, com status de verificação dos metadados
├── extraction/S-0001.json …    fichas de extração (uma por estudo)
├── ledger/evidence.jsonl       Evidence Ledger (uma evidência por linha)
├── matrix/                     matriz de evidências (.md, .csv, .json)
├── appraisal/S-0001.md …       avaliações metodológicas
├── synthesis/synthesis.md      síntese da literatura
├── manuscript/manuscript.md    seu texto, com marcadores [E-…] e ids de parágrafo
├── audit/                      auditorias (citações, referências, manuscrito, varredura)
├── data/raw/                   dados brutos — NUNCA são alterados sem sua confirmação
├── data/derived/               dados transformados por scripts
├── analysis/                   scripts e registro de execução das análises
└── publication/                estratégia de publicação (criada na Parte B)
```

**Dicas:**
- Guarde essa pasta num repositório Git: você terá histórico de todas as decisões.
- Tudo é texto (Markdown, JSON, CSV): você pode abrir e editar no editor que preferir.
- Os identificadores são estáveis: `S-0001` (fonte), `E-0001` (evidência), `P-001` (parágrafo).

---

## 9. Guia etapa por etapa — Parte A: da pergunta ao manuscrito

Cada etapa é **opcional**. Use só o que o seu trabalho exige.

### 9.1 Pergunta de pesquisa — `research-question`
- **Para quê:** transformar um tema amplo numa pergunta respondível.
- **Você recebe:** tipo de pergunta (descritiva, associativa, causal…), elementos, hipóteses
  `[HIPÓTESE]`, estratégias de identificação com premissas e ameaças, dados necessários.
- **Atenção:** hipóteses nunca são apresentadas como fatos.

### 9.2 Protocolo e critérios — `systematic-review`
- **Para quê:** definir antes de buscar o que entra e o que sai (evita viés de seleção).
- **Você recebe:** `protocol.md` e critérios com códigos (ex.: `EX-OUTCOME`).
- **Quando pular:** notas técnicas rápidas (registre no protocolo que pulou).

### 9.3 Busca — `literature-search`, `citation-chasing`, `grey-literature`, `regulatory-research`
- **Acadêmica:** `literature-search` (strings por base, execução, log reproduzível).
- **A partir de um artigo-chave:** `citation-chasing` (referências, citantes, similares).
- **Relatórios, working papers, avaliações:** `grey-literature` (marcados como **não** revisados por pares).
- **Normas e regulação:** `regulatory-research` (ver 9.3.1).
- **Resultado:** registros com a ferramenta de origem; nada "de memória" — o que o Claude lembra
  vira "pista não verificada" até ser encontrado numa ferramenta.

#### 9.3.1 Modo regulatório — `regulatory-research`
Classifica cada fonte (LEG lei, REG norma, PROP proposta, AIR, ARR, CP consulta pública, NT nota
técnica, DEC decisão, GUIDE, EVAL, GOV, DATA, ACAD, GREY, INTL) e cada afirmação como
**[NORMA VIGENTE]**, **[PROPOSTA]**, **[INTERPRETAÇÃO]** ou **[EVIDÊNCIA EMPÍRICA]**. Exige link oficial,
dispositivo exato (art., §, inciso) e data de consulta. Lembra que AIR é projeção *ex ante* e ARR é
avaliação *ex post*.

### 9.4 Triagem — `systematic-review`
- Decisões em `screening.csv` com motivo codificado.
- O Claude **propõe** decisões (`claude-proposal`); em revisão sistemática, recomenda-se revisão humana.
- O fluxo inspirado em PRISMA confere a aritmética (identificados − duplicatas = triados, etc.).
- O plugin só diz "conforme PRISMA" se todos os itens do checklist estiverem cumpridos.

### 9.5 Extração — `evidence-extraction` e `quantitative-evidence`
- **Ficha completa** por estudo: jurisdição, população, amostra, período, método, identificação,
  resultado, robustez, limitações, DOI — cada item com localização.
- **Números:** estimativa, unidade, denominador, erro-padrão, IC, p-valor, N, especificação,
  variáveis, grupos, desenho — com página/tabela e trecho.
- **Regras de ouro:** "significativo" nunca vira número; conversões são rotuladas `[INFERÊNCIA]`
  com a fórmula; se só havia o resumo, a ficha diz `abstract_only`.

### 9.6 Evidence Ledger — `evidence-ledger`
- Registra as evidências que você vai usar no texto (com `claim_supported`, tipo e status).
- Pergunte a qualquer momento: "de onde veio E-0004?" ou "de onde vêm as afirmações do parágrafo P-002?".

### 9.7 Matriz — `evidence-matrix`
- Tabela comparativa compacta (Study, Country, Period, Unit, N, Method, Treatment, Outcome,
  Estimate, SE/CI, Identification, Page, DOI) e detalhada; exporta Markdown, CSV (Excel) e JSON.
- Gerada **a partir das fichas**: para corrigir um valor, corrija a ficha e gere de novo.

### 9.8 Avaliação metodológica — `methodology-review`
- Checklist por desenho (DiD, IV, RDD, matching, controle sintético, RCT, simulação…).
- Toda crítica tem mecanismo e localização; o que os autores já trataram não é apontado como falha.
- Com só o resumo, a avaliação é marcada **PRELIMINAR**.

### 9.9 Síntese — `evidence-synthesis`
- Por desfecho: direção, magnitude **na mesma unidade**, qualidade, consistência, força da evidência.
- **Meta-análise:** o plugin só verifica se é viável (mesmo desfecho, unidade, desenho…). Ele **não**
  calcula efeito combinado nesta versão.

### 9.10 Redação — `scientific-writing` (ou o agente `scientific-editor`)
- Escreve usando **só** evidências do ledger, com `[E-…]` ao fim das frases empíricas.
- "Melhorar o texto" nunca adiciona fatos ou referências; o que faltar vira `[EVIDÊNCIA PENDENTE]`.
- Verbos calibrados: "reduziu" só com desenho causal; "associado a" para correlação; "projeta" para simulação.

### 9.11 Auditoria de citações — `citation-audit` e `bibliography-audit`
- **citation-audit:** frase por frase — a referência existe? sustenta a frase inteira? Classifica
  SUPORTADA, PARCIALMENTE SUPORTADA, NÃO SUPORTADA, NÃO VERIFICÁVEL e aponta exagero, causalidade
  indevida, generalização, fonte secundária, número sem fonte, referência inventada.
- **bibliography-audit:** confere DOI, autores, título, periódico, volume, páginas; acha duplicatas;
  formata em ABNT, APA, Chicago ou BibTeX **apenas** o que foi verificado.
- Nunca troca uma referência por outra "parecida" sem avisar você.

### 9.12 Revisão final — `manuscript-review` e `replication-check`
- Coerência pergunta → método → resultado → conclusão; números do resumo × texto × tabelas × figuras;
  causalidade; generalização; limitações; reprodutibilidade (dados, código, parâmetros, seeds).
- Problemas classificados como CRÍTICO, MAIOR ou MENOR, sempre com local e evidência.

---

## 10. Guia etapa por etapa — Parte B: do manuscrito à publicação

Esta parte é o **módulo Publication Strategy**. Ele usa o mesmo projeto, o mesmo manuscrito e o mesmo
ledger. Os arquivos ficam em `research/publication/`.

> **Regra de ouro do módulo:** o plugin **nunca** dirá que o seu artigo tem "X% de chance" de ser
> aceito. Ele avalia **aderência** com critérios e fontes que você pode conferir.

### 10.1 Encontrar periódicos — `journal-search`
- Usa várias fontes: onde a literatura que você citou foi publicada; onde saíram artigos parecidos
  nos últimos anos; periódicos que citam seus artigos-chave; diretórios (DOAJ, SciELO…); várias editoras.
- Cada candidato vem com a **origem** (por que entrou na lista) e o aims & scope com URL e data — ou `NOT VERIFIED`.
- **Informe suas restrições:** orçamento para APC, open access obrigatório, indexação exigida pelo
  programa/instituição, prazo, idioma.

### 10.2 Ver o que o periódico publicou — `journal-recent-content-analysis`
- Lista artigos comparáveis dos últimos 3–5 anos (título, autores, ano, DOI, método, relação com o seu).
- Descarta resultados de outros periódicos com nome parecido (acontece nas ferramentas de busca).

### 10.3 Avaliar a aderência — `journal-fit-analysis`
Sete dimensões, cada uma STRONG, MODERATE, WEAK ou INSUFFICIENT_EVIDENCE, com evidência:
Topic · Method · Contribution · Empirical · Audience · Recent Publication · Article Type.
Resultado: **Journal Fit Report** + índice (ex.: "67 / 100, cobertura 3/7"). Ver 12.4 para interpretar.

### 10.4 Checar a legitimidade — `journal-due-diligence`
ISSN, peer review, conselho editorial, Crossref, DOAJ, COPE, SciELO, Scopus, Web of Science,
Redalyc, Latindex, arquivamento, APC, licença, políticas de ética — com data e fonte. Usa o roteiro
Think. Check. Submit. **Não** rotula um periódico como predatório só por não estar numa base.

### 10.5 Levantar as regras atuais — `journal-requirements`
Tira do guia oficial do periódico: tipos de artigo, limites de palavras e do resumo, keywords,
highlights, estilo de referências, anonimização, declarações (dados, código, financiamento, conflitos,
CRediT, ética, uso de IA), cover letter, ORCID, revisores sugeridos… sempre com URL, **data** e trecho.
Se o site bloquear o acesso, **cole o texto oficial** na conversa (o plugin registra "fornecido pelo usuário").

### 10.6 Escolher o periódico — `publication-strategy`
Tabela comparativa da lista curta, ordem sugerida com justificativa, riscos de *desk rejection* e o que
ficou `NOT VERIFIED`. Métricas (fator de impacto, CiteScore, quartil) só entram como critério secundário.
**A decisão é sua.**

### 10.7 Ativar o Target Journal Mode
Depois de escolher, diga: "ative o Target Journal Mode para <periódico>". A partir daí, as
recomendações editoriais seguem as regras desse periódico — respeitando os limites de integridade.

### 10.8 Adequar o manuscrito — `manuscript-compliance`
Compara automaticamente o manuscrito com as regras e devolve, regra por regra:
`COMPLIANT`, `ACTION REQUIRED`, `NOT APPLICABLE` ou `UNABLE TO VERIFY`. Cada ação vem com
**exigência, estado atual, diferença, o que fazer e fonte**. Nada científico é mudado automaticamente.

### 10.9 Preparar a submissão — `submission-preparation` e `cover-letter`
- Checklist operacional e arquivos: manuscrito, versão anonimizada, title page, highlights,
  declarações, material suplementar, revisores sugeridos (se permitido).
- **Dados dos autores** (afiliação, ORCID, financiamento, conflitos, contribuições) **só vêm de você** —
  o plugin deixa `[AUTHORS: fill in]` onde faltar.
- A cover letter explica problema, contribuição, resultados, relevância e aderência ao escopo, sem
  elogios genéricos e sem "somos o primeiro estudo" sem verificação.

### 10.10 Auditoria pré-submissão — `pre-submission-audit`
```text
/scientific-research:pre-submission-audit research/ --journal <periódico>
```
Encadeia: regras atuais → compliance → citações → referências → dados/código → declarações éticas →
arquivos → checklist. Resultado: **READY TO SUBMIT** (zero pendências) ou **ACTION REQUIRED** (com a
lista completa). Regras consultadas há mais de 30 dias precisam ser reconsultadas.

### 10.11 Submeter
A submissão no sistema do periódico é feita **por você**. Registre a data e a versão enviada.

### 10.12 Responder aos revisores — `peer-review-response`
Cole a carta do editor e os pareceres. Você recebe uma matriz:
Comentário → Interpretação → Decisão (ACCEPTED / PARTIALLY ACCEPTED / NOT ACCEPTED) → Ação →
Alteração → Local → Resposta — e a carta de resposta. Se o revisor pedir algo que a evidência não
sustenta, o plugin redige uma recusa respeitosa e técnica. Nova análise pedida? Ela é **executada de
verdade** e o resultado é reportado, seja qual for.

### 10.13 Se for rejeitado — `resubmission-strategy`
Analisa o motivo **escrito** na decisão, separa melhorias científicas de preferências do periódico,
reaproveita a pesquisa de periódicos, reavalia a aderência e **reconsulta as regras** do novo alvo.

---

## 11. Receitas prontas para situações comuns

### Receita 1 — Nota técnica rápida (1–2 dias)
```text
/scientific-research:research-project Nota técnica sobre <tema>. Prazo curto: sem revisão sistemática formal.
/scientific-research:literature-search <pergunta> --periodo 2015-2026
/scientific-research:evidence-extraction (para os 5–10 estudos principais, com PDF)
/scientific-research:evidence-matrix --formato md
/scientific-research:evidence-synthesis
/scientific-research:scientific-writing síntese executiva
/scientific-research:citation-audit
```

### Receita 2 — Revisão sistemática para artigo
```text
/scientific-research:research-question
/scientific-research:systematic-review <pergunta> --tipo sistematica
/scientific-research:literature-search + citation-chasing + grey-literature
/scientific-research:systematic-review (triagem e fluxo)
/scientific-research:evidence-extraction / quantitative-evidence (cada estudo incluído)
/scientific-research:methodology-review (cada estudo)
/scientific-research:evidence-matrix --detalhada ; evidence-synthesis --meta-feasibility
/scientific-research:scientific-writing ; citation-audit ; manuscript-review
```

### Receita 3 — Subsídio para AIR ou ARR
```text
/scientific-research:regulatory-research <tema> --jurisdicao BR --setor <setor>
/scientific-research:grey-literature <tema> --organizacoes <reguladores, organismos internacionais>
/scientific-research:literature-search <pergunta empírica>
/scientific-research:evidence-extraction ; evidence-synthesis
```
Peça explicitamente o quadro "norma vigente × proposta × interpretação × evidência empírica".

### Receita 4 — Auditar um texto (seu, de colega ou gerado por IA)
```text
/scientific-research:citation-audit texto.md
/scientific-research:bibliography-audit referencias.bib --estilo abnt
/scientific-research:manuscript-review texto.md --profundidade completa
```
Veja `examples/03-manuscript-audit` (com uma referência falsa plantada, que o plugin detecta).

### Receita 5 — Extrair números de um estudo complexo
```text
/scientific-research:quantitative-evidence estudo.pdf --parametro elasticidade-preço
```

### Receita 6 — Escolher periódico e submeter
```text
/scientific-research:journal-search research/manuscript/manuscript.md
/scientific-research:journal-fit-analysis research/publication/journals/candidates.json
/scientific-research:journal-due-diligence <periódico>
/scientific-research:journal-requirements <periódico>
/scientific-research:publication-strategy research/
(escolha + "ative o Target Journal Mode para <periódico>")
/scientific-research:manuscript-compliance ; submission-preparation ; cover-letter
/scientific-research:pre-submission-audit research/ --journal <periódico>
```
Veja `examples/04-publication-strategy`.

### Receita 7 — Revisores pediram mudanças
```text
/scientific-research:peer-review-response pareceres.md --rodada 1
```

### Receita 8 — Artigo rejeitado
```text
/scientific-research:resubmission-strategy carta-de-decisao.md
```

---

## 12. Como ler os resultados

### 12.1 Classificação de afirmações (auditoria de citações)
| Classe | Significa | O que fazer |
|---|---|---|
| SUPORTADA | a fonte, no local indicado, sustenta a frase inteira | manter (e incluir a página) |
| PARCIALMENTE SUPORTADA | sustenta parte, ou a frase exagera/generaliza/é mais causal que o estudo | reescrever com o alcance correto |
| NÃO SUPORTADA | a fonte não diz isso, diz o contrário, ou a referência não existe | remover ou buscar fonte real |
| NÃO VERIFICÁVEL | não foi possível acessar a fonte | obter o texto e reauditar |

### 12.2 Alertas da varredura automática do manuscrito
| Código | Significa |
|---|---|
| NUMERO-SEM-FONTE | número sem citação nem marcador `[E-…]` |
| EVIDENCIA-INEXISTENTE | marcador aponta para evidência que não existe no ledger |
| EVIDENCIA-NAO-VERIFICADA | evidência usada está UNVERIFIED/CONTRADICTED |
| CAUSAL-INDEVIDA | verbo causal sobre evidência associativa, descritiva ou simulação |
| CAUSAL-VERIFICAR | verbo causal com citação: confira o desenho do estudo citado |
| AFIRMACAO-SEM-FONTE | afirmação causal/preditiva sem fonte (se for sua inferência, rotule) |
| GENERALIZACAO | frase sobre um contexto (ex.: Brasil) apoiada em evidência de outro |
| FONTE-SECUNDARIA | evidência vinda de notícia/blog quando deveria haver fonte primária |

São **heurísticas**: podem errar para mais ou para menos. Nunca substituem a auditoria frase a frase.

### 12.3 Verificação de DOI
| Resultado | Leitura |
|---|---|
| VERIFIED | DOI existe e título/autores/ano batem |
| PARTIALLY_VERIFIED | DOI existe, mas algo diverge levemente ou faltou informar dados para comparar |
| CONTRADICTED + POSSIVELMENTE_INVENTADA | DOI não existe, ou aponta para outro trabalho |
| UNVERIFIED | falha de rede/ferramenta — **não** quer dizer que a referência é falsa |

### 12.4 Índice de aderência (journal fit)
- Fórmula: 100 × soma(peso × nota) ÷ soma(peso × 2), com STRONG=2, MODERATE=1, WEAK=0.
- Dimensões sem evidência **não entram** e aparecem na **cobertura**.
- Leia sempre os dois números juntos: "80 com cobertura 2/7" é muito menos informativo que
  "70 com cobertura 6/7".
- **Não é probabilidade de aceitação.** Serve para comparar candidatos com critérios explícitos.

### 12.5 Compliance e pré-submissão
| Status | Leitura |
|---|---|
| COMPLIANT | medido e dentro da regra |
| ACTION REQUIRED | há algo a fazer (com exigência, estado, diferença, ação e fonte) |
| NOT APPLICABLE | a regra não vale para o seu tipo de manuscrito |
| UNABLE TO VERIFY | precisa de conferência humana (ou a regra não foi confirmada na fonte oficial) |
| READY TO SUBMIT | zero pendências, regras reconsultadas |
| ACTION REQUIRED (auditoria) | lista completa do que falta |

Confirmou manualmente um item (ex.: estilo de referências)? Peça ao Claude para registrar a
confirmação; ela passa a contar na auditoria.

---

## 13. Os subagentes: quando o plugin trabalha "em equipe"

| Agente | Especialidade | Peça quando |
|---|---|---|
| `literature-researcher` | buscas extensas e citation chasing | "faça uma busca ampla em paralelo enquanto eu leio" |
| `methodology-reviewer` | avaliação metodológica independente (só lê) | "quero uma segunda avaliação independente do desenho" |
| `citation-auditor` | auditoria conservadora de citações (só lê) | "audite o manuscrito longo por seções" |
| `scientific-editor` | redação **sem acesso à web** — só usa o ledger | "redija a discussão só com o que está validado" |
| `quantitative-analyst` | números de estudos complexos e análises reproduzíveis | "extraia todas as especificações das tabelas 2 a 5" |
| `regulatory-researcher` | levantamento normativo | "levante as normas enquanto você busca os artigos" |
| `publication-strategist` | coordena toda a etapa de publicação | "cuide da escolha de periódico e da submissão" |

Você pode pedir pelo nome ("use o citation-auditor para…"). Para tarefas simples, o Claude trabalha
sem subagentes — é mais rápido e barato.

---

## 14. Ferramentas de linha de comando (opcional)

Normalmente **o Claude roda essas ferramentas para você**. Se quiser usá-las no terminal, localize o
plugin instalado:

```bash
find ~/.claude/plugins/cache -path "*scientific-research*" -name srtool.py
```

### 14.1 `srtool.py` (núcleo)
| Comando | Faz |
|---|---|
| `init <pasta>` | cria a estrutura `research/` |
| `validate project research` | valida fontes, fichas, ledger, log e auditoria |
| `matrix research/extraction --sources research/sources/sources.json --format md\|csv\|json [--detailed]` | gera a matriz |
| `doi-check <DOI> --title "…" --year AAAA --authors "Sobrenome"` | confere um DOI no Crossref |
| `refs-check research/sources/sources.json` | confere todas as referências |
| `dedupe <arquivo>` | aponta duplicatas |
| `scan <manuscrito.md> --ledger … --sources … [--context Brasil]` | varredura do manuscrito |
| `trace E-0001` ou `trace P-002 --ledger … --sources … --manuscript …` | "de onde veio?" |
| `format research/sources/sources.json --style abnt\|apa\|chicago\|bibtex` | referências formatadas (só verificadas) |
| `prisma research/search/search-log.json` | fluxo de seleção + checagem das contagens |
| `search-openalex "consulta"` / `chase forward\|backward\|similar <DOI>` | busca e citation chasing no OpenAlex |

### 14.2 `pubtool.py` (módulo de publicação, em `modules/publication-strategy/scripts/`)
| Comando | Faz |
|---|---|
| `init research` | cria `research/publication/` |
| `profile <manuscrito.md>` | mede o manuscrito (palavras, resumo, keywords, figuras, declarações) |
| `venues research/sources/sources.json` | onde a literatura citada foi publicada |
| `fit-report <fit.json>` / `compare <fit.json…>` | relatório e comparação de aderência |
| `check-compliance <manuscrito.md> <requirements.json>` | compliance automático |
| `target set\|show\|clear research/publication --journal <slug>` | Target Journal Mode |
| `freshness <requirements.json>` | idade da consulta às regras |
| `lint <arquivos>` | acusa probabilidades de aceitação, "primeiro a…", elogios genéricos |
| `response-letter <response-matrix.json>` | carta de resposta aos revisores |
| `presubmit research --journal <slug>` | auditoria pré-submissão |

---

## 15. O que o plugin NÃO faz

- **Não inventa** artigos, DOIs, autores, páginas, números, datas ou URLs — e não "completa" lacunas.
- **Não trata o resumo como se fosse o artigo** — e avisa quando só teve acesso ao resumo.
- **Não garante cobertura total** da literatura; ausência de um estudo na busca não prova que ele não exista.
- **Não acessa conteúdo pago** que você não tenha como acessar; paywall vira "não verificável".
- **Não calcula meta-análise** (só avalia se ela seria viável).
- **Não calcula probabilidade de aceitação** nem promete publicação.
- **Não afirma** que um periódico é predatório sem um conjunto de evidências.
- **Não altera resultados** para caber em regras editoriais ou agradar revisores.
- **Não inventa dados dos autores** (afiliações, ORCID, financiamento, conflitos, contribuições).
- **Não submete** o artigo nem acessa sistemas de submissão (Editorial Manager, ScholarOne etc.).
- **Não escreve na sua biblioteca Zotero** nem altera seus **dados brutos** sem sua confirmação.
- **Não substitui** o julgamento do pesquisador, do orientador ou de especialistas.

---

## 16. Limitações e cuidados

- **Resultados de IA precisam de verificação humana**, inclusive decisões de triagem (marcadas `claude-proposal`).
- **Bases e conectores têm limites**: cobertura por idioma e área, cotas de uso, paywalls, sites que
  bloqueiam acesso automatizado. Quando algo falha, o plugin registra — confira o log.
- **Heurísticas automáticas erram**: a varredura do manuscrito e o compliance automático cobrem o que
  é mensurável; o resto fica para conferência humana.
- **O formatador de referências é simplificado**: casos especiais de ABNT/APA (autoria institucional,
  normas, capítulos) precisam de revisão.
- **Regras de periódicos mudam**: reconsulte antes de submeter (a auditoria cobra isso).
- **Claude.ai/Cowork**: compatibilidade não testada; no chat só as skills funcionam (seção 4.6).
- **Custo**: buscas em conectores e leituras de texto integral consomem cotas dos serviços e tokens.

---

## 17. Boas práticas para usar com efetividade

1. **Comece por `research-project`** quando estiver em dúvida — ele diz o próximo passo.
2. **Dê o texto integral** sempre que puder (PDF ou arquivo). É a maior diferença de qualidade.
3. **Conecte pelo menos um conector acadêmico** (Scite é o mais completo para verificação).
4. **Trabalhe sempre na mesma pasta `research/`** e versione com Git.
5. **Leia a seção "não verificado" de cada resposta** antes de seguir em frente.
6. **Registre no ledger tudo o que vai para o texto** — e escreva só a partir dele.
7. **Use a auditoria de citações antes de mostrar o texto** a orientador, banca ou periódico.
8. **Peça segunda opinião independente** (`methodology-reviewer`, `citation-auditor`) em pontos críticos.
9. **Na publicação, informe suas restrições logo no início** (APC, open access, indexação, prazo).
10. **Cole o guia oficial do periódico** se o site bloquear o acesso; não confie em regras antigas.
11. **Não peça "preencha com um valor plausível"**: o plugin vai recusar — e está certo.
12. **Guarde as decisões**: etapas puladas, critérios alterados e confirmações manuais ficam registradas.

---

## 18. Solução de problemas (FAQ)

**As skills não aparecem quando digito `/`.**
Confira `claude plugin list` (deve estar `enabled`), reinicie a sessão ou use `/reload-plugins`.

**"marketplace add" não encontra o plugin.**
O plugin ainda não está no branch padrão do GitHub: use o clone local (seção 4.2).

**O Claude disse que não conseguiu verificar uma referência que eu sei que existe.**
Provavelmente a ferramenta falhou ou o conector não está ativo (status `UNVERIFIED`, não "falso").
Ative um conector (Scite) ou forneça o PDF/DOI e peça para verificar de novo.

**Pedi um número e recebi "Não foi encontrada evidência quantitativa…".**
É o comportamento correto quando nenhuma fonte acessada reporta o número. Forneça o texto
integral ou amplie a busca.

**Ele não quis dizer qual revista tem mais chance de aceitar.**
Por desenho. Peça a avaliação de aderência (`journal-fit-analysis`) e compare os candidatos.

**Tudo aparece como `NOT VERIFIED` na parte de periódicos.**
O site da editora não pôde ser acessado. Cole o *guide for authors* ou o *aims & scope* na conversa
e peça para registrar como fornecido por você (com a URL e a data).

**Apareceu um pedido de confirmação ao salvar um arquivo em `data/raw/`.**
É a proteção de dados brutos. Confirme só se a alteração for intencional; o recomendado é salvar em `data/derived/`.

**Apareceu um pedido de confirmação ao usar o Zotero/Scite/Elicit.**
A operação escreveria na sua biblioteca ou coleção. Confirme apenas se você pediu isso.

**Os scripts não rodam (erro com `python3`).**
Instale o Python 3 ou crie o alias `python3`. Sem Python, as skills funcionam, mas sem as validações automáticas.

**A auditoria pré-submissão continua em ACTION REQUIRED.**
Leia a lista: cada item diz o que fazer. Os mais comuns: regras não reconsultadas, declarações com
`[AUTHORS: fill in]`, referências só parcialmente verificadas, afirmações NÃO SUPORTADAS.

---

## 19. Cola de referência rápida

**Frases que o plugin usa (e o que significam)**
- "Não foi possível verificar esta informação nas fontes consultadas." → não confirmado; não é "falso".
- "Não foi encontrada evidência quantitativa que permita estimar este parâmetro." → não há número nas fontes acessadas.
- `NR — não reportado` → o estudo não informa. `NA — não se aplica` → não faz sentido para aquele estudo.
- `NOT VERIFIED` (periódicos) → sem fonte oficial atual.

**As 30 skills** (`/scientific-research:<nome>`)

| Pesquisa | Publicação |
|---|---|
| `research-project` (comece aqui) | `journal-search` |
| `research-question` | `journal-recent-content-analysis` |
| `literature-search` | `journal-fit-analysis` |
| `citation-chasing` | `journal-due-diligence` |
| `grey-literature` | `journal-requirements` |
| `regulatory-research` | `publication-strategy` |
| `systematic-review` | `manuscript-compliance` |
| `evidence-extraction` | `submission-preparation` |
| `quantitative-evidence` | `cover-letter` |
| `evidence-ledger` | `pre-submission-audit` |
| `evidence-matrix` | `peer-review-response` |
| `methodology-review` | `resubmission-strategy` |
| `evidence-synthesis` | |
| `scientific-writing` | |
| `citation-audit` | |
| `bibliography-audit` | |
| `replication-check` | |
| `manuscript-review` | |

**Fluxo completo**
```
Pergunta → Protocolo → Busca → Triagem → Extração → Ledger → Matriz → Metodologia → Síntese
→ Redação → Auditoria de citações → Revisão do manuscrito → Busca de periódicos → Aderência
→ Escolha → Target Journal Mode → Compliance → Pré-submissão → Submissão → Revisores
→ Publicação | Ressubmissão
```

---

## 20. Onde saber mais

| Documento | Conteúdo |
|---|---|
| [`README.md`](README.md) | visão geral técnica, instalação, conectores |
| [`docs/scientific-method.md`](docs/scientific-method.md) | princípios científicos em detalhe |
| [`docs/publication-strategy.md`](docs/publication-strategy.md) | módulo de publicação em detalhe |
| [`docs/connectors.md`](docs/connectors.md) | conectores, classificação, riscos, modo sem conectores |
| [`docs/architecture.md`](docs/architecture.md) | como o plugin é organizado |
| [`examples/`](examples/) | 4 exemplos completos (busca e matriz; avaliação de política; auditoria; publicação) |
| [`templates/`](templates/) | modelos de protocolo, ficha, matriz, relatórios |
| [`CHANGELOG.md`](CHANGELOG.md) | histórico de versões |
