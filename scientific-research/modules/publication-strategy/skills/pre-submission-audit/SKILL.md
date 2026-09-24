---
name: pre-submission-audit
description: "Publication Strategy: auditoria antes de submeter (regras, compliance, citações, referências, declarações, arquivos) → READY TO SUBMIT ou ACTION REQUIRED. Use para \"posso submeter?\", \"auditoria pré-submissão\"."
argument-hint: "[research/] [--journal slug]"
---

# Pre-Submission Audit

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

- Imediatamente antes de submeter (ou ressubmeter) ao periódico-alvo.

## Quando NÃO usar

- Periódico ainda não escolhido → `publication-strategy`.

## Inputs esperados

Projeto `research/` com: `publication/target-journal.json` (ou `--journal`), `requirements.json`
do alvo, manuscrito, ledger, `sources.json`, auditorias (`audit/citation-audit.json`), pasta de submissão.

## Workflow

```
Journal requirements → Manuscript compliance → Citation audit → Reference audit
→ Data/code availability → Ethical declarations → Files required → Submission checklist
→ READY TO SUBMIT | ACTION REQUIRED
```

1. **Journal requirements**: reconsultar a página oficial (regras mudam). Atualizar
   `requirements.json` e a data. Regras com mais de 30 dias sem reconsulta → pendência.
2. **Manuscript compliance**: `manuscript-compliance`.
3. **Citation audit**: `citation-audit` (nenhuma afirmação NÃO SUPORTADA pode permanecer).
4. **Reference audit**: `bibliography-audit` (nenhuma referência CONTRADICTED; UNVERIFIED listadas).
5. **Data/code availability**: declarações presentes e coerentes com `replication-check`.
6. **Ethical declarations**: financiamento, conflitos, CRediT, ética/consentimento, uso de IA — presentes
   e fornecidos pelos autores (placeholders `[AUTORES: preencher]` bloqueiam).
7. **Files required**: arquivos do checklist existem na pasta de submissão.
8. **Submission checklist** consolidado.

Automação:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" presubmit research --journal <slug> --out research/publication/pre-submission-audit-<slug>.md
```

O script consolida o que é verificável por arquivo (frescor das regras, compliance, auditorias,
referências, declarações, placeholders, arquivos, linguagem proibida) e devolve
**READY TO SUBMIT** apenas se não houver nenhuma pendência; caso contrário **ACTION REQUIRED** com
a lista completa. Itens que exigem julgamento (ex.: qualidade da anonimização) ficam listados para
revisão humana e impedem READY TO SUBMIT enquanto não confirmados.

## Output esperado

Relatório com status por etapa, pendências priorizadas e a conclusão final.

## Critérios de qualidade

- READY TO SUBMIT só com zero pendências e regras reconsultadas.
- Nenhuma pendência "resolvida" com alteração de resultado ou dado inventado.

## Situações de falha

- Regras oficiais inacessíveis → ACTION REQUIRED ("reconsultar guia oficial"), nunca READY.
