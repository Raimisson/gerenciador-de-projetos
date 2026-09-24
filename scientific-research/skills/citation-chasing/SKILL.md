---
name: citation-chasing
description: "Expande a literatura a partir de artigos semente: referências (backward), citantes (forward) e similares. Use para \"quem citou\", \"snowballing\", \"citation chasing\", \"artigo seminal\"."
argument-hint: "[DOI ou título do artigo semente] [--rodadas N]"
---

# Citation Chasing

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

- O usuário tem um artigo seminal (ou poucos) e quer construir a literatura em volta.
- Complementar uma busca por palavras-chave (reduz viés de vocabulário).

## Quando NÃO usar

- Não há nenhum artigo semente verificado → primeiro `literature-search`.
- Busca de normas/relatórios → `regulatory-research` / `grey-literature`.

## Inputs esperados

DOI (preferível) ou título completo do(s) artigo(s) semente; número de rodadas
(padrão: 1; máximo recomendado: 2); critério de relevância (da pergunta de pesquisa).

## Ferramentas

| Direção | Preferência | Alternativas |
|---|---|---|
| Verificar semente | Crossref / DOI (`srtool.py doi-check`) | Scite (metadados), OpenAlex |
| Backward | OpenAlex `referenced_works` (`srtool.py chase backward <DOI>`) | Scite `citation_graph`, lista de referências do PDF |
| Forward | OpenAlex `cites:` (`srtool.py chase forward <DOI>`) | Scite `citation_graph`/smart citations, Semantic Scholar |
| Similar | OpenAlex `related_works` (`srtool.py chase similar <DOI>`) | Consensus/Elicit com a pergunta do artigo |

Sem ferramentas de rede: peça o PDF do artigo semente e extraia a lista de referências
dele (backward); forward/similar ficam registrados como **não executados**.

## Workflow

1. **Verificar a semente** (DOI resolve, título/autores/ano conferem). Semente
   não verificada não é usada.
2. **Backward**: listar referências; marcar cada uma com a seção do artigo semente em
   que é citada quando a ferramenta fornecer (Scite fornece `section`).
3. **Forward**: listar trabalhos citantes; quando houver contexto de citação
   (Scite smart citations), registrar se o citante **apoia, contrasta ou apenas menciona**
   — e o trecho literal.
4. **Similar**: listar trabalhos relacionados, indicando o critério da ferramenta.
5. **Triagem rápida** por título/abstract contra a pergunta; registrar decisão e motivo.
6. **Rodada seguinte** (opcional) só com os incluídos da rodada anterior; parar quando
   uma rodada não trouxer novos incluídos (saturação) ou ao atingir o limite de rodadas.
7. **Registrar** cada rodada no search log (`database: "OpenAlex (forward)"`, etc.) com
   data, semente, contagens e decisões.

## Output esperado

```markdown
## Semente: <citação verificada> — DOI — status
### Rodada 1
| Direção | Registro | Ano | DOI | Relação (apoia/contrasta/menciona/NR) | Decisão | Motivo |
### Saturação / critérios de parada
### Pistas não verificadas
```

## Critérios de qualidade

- Toda relação "apoia/contrasta" vem de trecho de citação recuperado, nunca de suposição.
- Contagens de citação reportadas com a fonte e a data (variam entre bases).
- Seminalidade não é inferida só por número de citações; justificar.

## Situações de falha

- Artigo semente sem DOI → usar título exato + ano; se não localizar, parar e informar.
- APIs bloqueadas/limitadas → registrar erro; nunca completar a lista de memória.
- Explosão de resultados → priorizar por relevância à pergunta, registrar o corte.
