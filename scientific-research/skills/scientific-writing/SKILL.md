---
name: scientific-writing
description: "Redige seções de artigo usando só evidência validada do ledger, com marcadores [E-…] e linguagem causal calibrada. Use para \"escrever a introdução\", \"redigir seção\", \"melhorar o texto\"."
argument-hint: "[seção] [--estilo abnt|apa] [--idioma pt|en]"
---

# Scientific Writing

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

- Redigir ou reescrever seções de um manuscrito com base em evidência já registrada.
- Ajustar linguagem (causal vs. associativa), coesão, terminologia.

## Quando NÃO usar

- Não há ledger/evidência validada para as afirmações empíricas → primeiro
  `evidence-extraction` e `evidence-ledger`. Sem isso, escreva apenas estrutura e
  marque cada afirmação empírica como `[EVIDÊNCIA PENDENTE]`.
- Auditoria de um texto pronto → `citation-audit` / `manuscript-review`.

## Inputs esperados

Seção desejada; `research/ledger/evidence.jsonl`; `sources.json`; síntese; estilo de
citação; periódico-alvo (normas); rascunho existente (se houver).

## Regras específicas

1. **Somente evidência do ledger** com status `VERIFIED` ou `PARTIALLY_VERIFIED`
   (este último com a limitação explicitada). Cada frase empírica termina com
   marcador(es) `[E-0001]` que depois são convertidos em citação.
2. **Não adicionar referências** que não estejam em `sources.json` verificadas; não citar
   fonte que não sustente a frase específica.
3. **"Melhorar o texto" nunca adiciona fatos**, números, exemplos empíricos ou referências
   novas. Se o texto precisa de evidência que não existe no ledger, inserir
   `[EVIDÊNCIA PENDENTE: descrição]` e listar ao final.
4. **Linguagem causal** conforme `design_class` da evidência:
   | design_class | Verbos permitidos |
   |---|---|
   | `causal` | "reduziu", "aumentou", "o efeito estimado foi" (+ premissas) |
   | `associational` | "associado a", "correlacionado com" |
   | `descriptive` | "observou-se", "registrou-se" |
   | `simulation` | "projeta", "estima-se em cenário" |
   | `normative` | "estabelece", "determina" (norma vigente) / "propõe" (proposta) |
5. **Generalização**: evidência de outro país/período/setor recebe qualificação explícita
   ("em distribuidoras dos EUA entre 19xx e 20xx…").
6. **Inferências próprias** do autor/Claude aparecem como argumentação ("sugere-se",
   "é plausível que"), nunca atribuídas a um estudo.
7. **Consistência terminológica**: manter glossário do projeto
   (`research/manuscript/glossary.md`) e usar o mesmo termo para o mesmo conceito.
8. **Parágrafos com id** (`<!-- P-012 -->`) para proveniência; atualizar `used_in` no ledger.

## Workflow

1. Carregar ledger + síntese; listar evidências disponíveis para a seção.
2. Esboçar estrutura (tópicos por parágrafo) e mapear evidência → parágrafo.
3. Redigir; cada afirmação empírica com `[E-…]`.
4. Autochecagem:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" scan research/manuscript/manuscript.md --ledger research/ledger/evidence.jsonl --sources research/sources/sources.json
   ```
   (detecta números sem fonte, linguagem causal indevida, `E-…` inexistentes, generalização.)
5. Converter marcadores em citações no estilo pedido apenas na versão final
   (`bibliography-audit` gera as referências).

## Output esperado

Texto da seção com marcadores, lista de `[EVIDÊNCIA PENDENTE]`, resultado do scan,
glossário atualizado.

## Critérios de qualidade

- 0 números sem `[E-…]`; 0 `E-…` inexistentes; 0 verbos causais sobre evidência não causal.
- Seções coerentes com a pergunta e o método.

## Situações de falha

- Usuário pede para "citar algo que diga isso" sem fonte → buscar com `literature-search`;
  se não achar, manter `[EVIDÊNCIA PENDENTE]` — nunca citar uma fonte "provável".
