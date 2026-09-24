---
name: citation-audit
description: Auditoria frase por frase das afirmações e citações de um manuscrito — identifica a referência de cada afirmação verificável, confirma que a referência existe (DOI/metadados), verifica se a fonte efetivamente sustenta a frase (com página), detecta exageros, causalidade indevida, generalização e fonte secundária desnecessária, e classifica cada afirmação como SUPORTADA, PARCIALMENTE SUPORTADA, NÃO SUPORTADA ou NÃO VERIFICÁVEL. Use para "auditar citações", "checar referências do texto", "verificar se as fontes sustentam", "citation audit", "fact-check do artigo", "referência inventada".
argument-hint: "[arquivo do manuscrito] [--secoes introducao,discussao]"
---

# Citation Audit

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

- Antes de submeter um manuscrito; ao receber texto de terceiros/IA; ao herdar referências.

## Quando NÃO usar

- Só formatar/conferir metadados da lista de referências → `bibliography-audit`.
- Auditoria global (coerência, números, tabelas) → `manuscript-review` (que inclui esta).

## Inputs esperados

Manuscrito (MD, DOCX convertido, PDF, texto colado); lista de referências; opcional:
ledger, `sources.json`, PDFs das fontes.

## Regras específicas

1. **Conservadorismo**: na dúvida, `NÃO VERIFICÁVEL`, nunca `SUPORTADA`.
2. **Nunca corrigir uma referência inventando uma substituta.** Se sugerir outra fonte,
   ela precisa ter sido localizada e verificada, e a troca é **informada explicitamente**
   ("Sugestão de substituição — requer aprovação do autor").
3. Verificação de existência ≠ verificação de suporte. Uma referência pode existir e não
   sustentar a frase.
4. Página: indicar quando localizada; senão "página não localizada".

## Sinais de referência possivelmente inventada

DOI não resolve · título incompatível com o DOI · autores incompatíveis · periódico
incompatível · ano incompatível · volume/páginas inexistentes · referência não encontrada
em nenhum índice consultado. Checagem automática:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" doi-check 10.xxxx/yyyy --title "..." --year 2016 --authors "Sobrenome1; Sobrenome2"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" refs-check research/sources/sources.json
```

Sem rede/Bash: usar Scite (`search_literature` com `dois`), Crossref via WebFetch, ou
declarar `NÃO VERIFICÁVEL`.

## Workflow

1. **Segmentar** o texto em frases; marcar as **verificáveis** (empíricas, numéricas,
   atribuições a autores, afirmações sobre normas). Opiniões/transições não entram.
2. **Mapear** cada frase → referência(s) citada(s) (ou "sem citação").
3. **Existência**: conferir metadados (DOI, título, autores, ano, veículo) — status
   `VERIFIED`/`CONTRADICTED`/`UNVERIFIED`.
4. **Suporte**: localizar na fonte o trecho que sustenta a frase (texto integral quando
   possível; Scite smart citations e `read_fulltext` ajudam). Comparar alcance:
   população, período, direção, magnitude, força causal.
5. **Classificar** (SUPORTADA / PARCIALMENTE SUPORTADA / NÃO SUPORTADA / NÃO VERIFICÁVEL)
   com justificativa e trecho.
6. **Problemas específicos** (códigos): `EXAGERO`, `CAUSAL-INDEVIDA`, `GENERALIZACAO`,
   `FONTE-SECUNDARIA` (existe primária identificável), `NUMERO-SEM-FONTE`,
   `REF-INEXISTENTE`, `REF-INADEQUADA`, `PAGINA-AUSENTE`, `RETRATADO` (checar
   `editorialNotices` no Scite).
7. **Varredura automática complementar**: `srtool.py scan <manuscrito>`.
8. Relatório em `research/audit/citation-audit.md` (template
   `${CLAUDE_PLUGIN_ROOT}/templates/citation-audit-report.md`) e JSON opcional
   (`${CLAUDE_PLUGIN_ROOT}/schemas/citation-audit.schema.json`).

Para auditoria independente de manuscritos longos, delegar ao subagente `citation-auditor`
(por seção, sem sobreposição).

## Output esperado

Tabela: # | frase | referência | existência | suporte (classe) | problemas | página/trecho | ação recomendada.
Resumo: contagem por classe; lista de referências possivelmente inventadas; ações prioritárias.

## Critérios de qualidade

- Toda classificação `SUPORTADA` tem trecho e localização.
- Nenhuma referência nova introduzida sem aviso.
- Falhas de ferramenta viram `NÃO VERIFICÁVEL`, nunca `SUPORTADA`.

## Situações de falha

- Fonte com paywall → `NÃO VERIFICÁVEL (texto integral inacessível)`; o abstract pode
  indicar `PARCIALMENTE SUPORTADA` apenas se sustenta explicitamente a frase.
- Manuscrito muito longo → auditar por seções e registrar cobertura.
