---
name: peer-review-response
description: Módulo Publication Strategy — organiza pareceres de revisores em matriz Reviewer Comment → Interpretation → Action → Manuscript Change → Location → Response, classificando cada item como ACCEPTED, PARTIALLY ACCEPTED ou NOT ACCEPTED, redigindo justificativas científicas respeitosas quando não aceito, e nunca alterando resultado científico para satisfazer revisor. Use para "responder revisores", "response to reviewers", "carta de resposta", "revisão major/minor", "pareceres".
argument-hint: "[arquivo com pareceres] [--rodada 1]"
---

# Peer Review Response

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

- Decisão editorial com pareceres (major/minor revision, reject and resubmit).

## Quando NÃO usar

- Rejeição definitiva e troca de periódico → `resubmission-strategy`.

## Inputs esperados

Carta do editor e pareceres (texto integral); manuscrito submetido; ledger; regras do periódico
para revisão (formato da resposta, marcação de alterações, prazo).

## Workflow

1. **Segmentar** cada parecer em comentários atômicos (`R1.1`, `R1.2`, `R2.1`…; editor = `E.1`).
2. **Interpretar** cada comentário (o que o revisor pede de fato; é pedido de análise, esclarecimento,
   literatura, redação?).
3. **Decidir**: `ACCEPTED` · `PARTIALLY_ACCEPTED` · `NOT_ACCEPTED`.
   - Pedido de nova análise → executar de verdade (scripts registrados, `quantitative-evidence`)
     e reportar o resultado **qualquer que seja**; nunca simular resultado.
   - Pedido de literatura → só referências verificadas (`literature-search`, `bibliography-audit`).
   - Pedido para reforçar conclusões além do que os dados sustentam → `NOT_ACCEPTED` ou
     `PARTIALLY_ACCEPTED` com justificativa.
4. **Registrar** na matriz `research/publication/peer-review/round-<n>/response-matrix.json`
   (schema `response-matrix.schema.json`): comment · interpretation · decision · action ·
   manuscript_change · location · response · (justification se NOT/PARTIALLY) ·
   `results_changed` (true só para correção de erro, com explicação).
5. **Gerar** a matriz legível e a carta de resposta:
   `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" response-letter research/publication/peer-review/round-1/response-matrix.json --out …/response-letter.md`.
6. Conferir que toda alteração citada existe no manuscrito revisado (local indicado).

## Tom das respostas

Agradecer de forma específica (não genérica), responder ao ponto, citar a mudança e o local
(seção/página/linha), e quando discordar: argumento técnico + evidência (ledger, literatura
verificada, limites do desenho) + alternativa oferecida (ex.: nova limitação explicitada).

## Output esperado

Matriz (Markdown/JSON) + carta de resposta + manuscrito revisado com alterações marcadas.

## Critérios de qualidade

- 100% dos comentários com decisão e resposta; NOT_ACCEPTED sempre justificado.
- Nenhum resultado alterado para agradar revisor; mudanças de resultado só por correção de erro, declaradas.

## Situações de falha

- Pedido inexequível (dados indisponíveis) → explicar a limitação honestamente e propor alternativa.
