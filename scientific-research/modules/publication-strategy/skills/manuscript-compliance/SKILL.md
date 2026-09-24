---
name: manuscript-compliance
description: "Publication Strategy: compara manuscrito × regras do periódico (COMPLIANT, ACTION REQUIRED, NOT APPLICABLE, UNABLE TO VERIFY) sem alterar a ciência. Use para \"está nas normas?\", \"compliance\"."
argument-hint: "[manuscrito.md] [requirements.json]"
---

# Manuscript Compliance

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

<!-- pubintegrity:start -->
## Regras de integridade editorial (módulo Publication Strategy)

1. **Nunca estimar probabilidade de aceitação** ("X% de chance de aceitação"): não há base publicada para calculá-la. *Journal fit* é avaliação de aderência com critérios e fontes explícitos — nunca probabilidade de publicação.
2. Informação de periódico é **mutável**: registrar URL oficial e data da consulta; reconsultar antes de submeter; sem fonte atual → `NOT VERIFIED`.
3. Não inferir aderência pelo nome do periódico: justificar com *aims & scope* e artigos publicados verificáveis.
4. Não declarar um periódico predatório só pela ausência de uma indexação específica: apresentar evidências e alertas objetivos.
5. Métricas (JIF, CiteScore, quartil) nunca substituem a aderência científica.
6. Regras editoriais **nunca** justificam alterar ou omitir resultados, fabricar análises ou referências, manipular evidência ou exagerar conclusões.
7. Não inventar informações de autores (afiliações, ORCID, financiamento, contribuições, conflitos de interesse).
8. Não afirmar que o trabalho é "o primeiro" ou "inédito" sem verificação documentada.

Referência completa: `${CLAUDE_PLUGIN_ROOT}/docs/publication-strategy.md`.
<!-- pubintegrity:end -->

## Quando usar

- Periódico-alvo escolhido e regras atuais registradas por `journal-requirements`.

## Quando NÃO usar

- Regras ainda não verificadas na fonte oficial → primeiro `journal-requirements`.

## Inputs esperados

`research/manuscript/manuscript.md` (ou texto do manuscrito) e
`research/publication/journals/<slug>/requirements.json`.

## Workflow

1. Rodar a comparação automática:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" check-compliance research/manuscript/manuscript.md research/publication/journals/<slug>/requirements.json --out research/publication/compliance/<slug>
   ```
   Gera `<slug>.json` e `<slug>.md`. Regras `manual` saem como `UNABLE_TO_VERIFY` e devem ser
   conferidas pelo modelo/usuário (ex.: estilo de referências, anonimização, formato de arquivo).
2. Para cada `ACTION_REQUIRED`, o relatório traz: (1) exigência; (2) estado atual; (3) diferença;
   (4) o que fazer; (5) fonte (URL + data + trecho).
3. **Revisar as ações sob a ótica da integridade**:
   - Cortes de palavras: reduzir redundância, mover detalhes para material suplementar — **nunca**
     remover resultados desfavoráveis, limitações ou robustez de forma seletiva.
   - Abstract/highlights: condensar sem exagerar conclusões nem trocar associação por causalidade.
   - Declarações (dados, financiamento, conflitos, CRediT, IA): preencher **somente** com
     informação fornecida pelos autores; campos desconhecidos ficam `[AUTORES: preencher]`.
4. Em **Target Journal Mode** (`research/publication/target-journal.json` ativo), usar as regras do
   periódico-alvo como referência prioritária de todas as recomendações editoriais.

## Output esperado

Relatório com resumo por status e tabela detalhada; lista priorizada de ações.

## Critérios de qualidade

- Nenhum item `COMPLIANT` sem medição ou evidência; incerteza → `UNABLE_TO_VERIFY`.
- Nenhuma alteração científica automática.

## Situações de falha

- Contagem de palavras depende do que o periódico inclui (referências, tabelas…): se a regra não
  define o escopo e as contagens com/sem referências divergem quanto ao limite → `UNABLE_TO_VERIFY`
  com os dois números.
