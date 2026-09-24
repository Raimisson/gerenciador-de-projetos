---
name: journal-requirements
description: "Publication Strategy: regras atuais de submissão tiradas do guia oficial, com URL e data. Use para \"regras da revista\", \"guide for authors\", \"normas de submissão\"."
argument-hint: "[periódico] [--url guia-oficial] [--tipo research-article]"
---

# Journal Requirements

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

- Após escolher candidatos (para `publication-strategy`) e, obrigatoriamente, antes da submissão
  (`pre-submission-audit`).

## Quando NÃO usar

- Comparar com o manuscrito → `manuscript-compliance` (usa o JSON gerado aqui).

## Inputs esperados

Periódico; tipo de artigo pretendido; URL oficial do guia (ou texto/PDF oficial fornecido pelo
usuário — nesse caso registrar a origem como "fornecido pelo usuário" + URL/data informadas).

## Regras específicas

1. **Fonte oficial e atual**: site do periódico/editora. Agregadores, blogs e fóruns não servem.
2. **Nunca confiar só em regras salvas**: se houver acesso à página atual, reconsultar; regra
   salva sem reconsulta recebe `status: NOT_VERIFIED` na auditoria pré-submissão.
3. Cada regra registra: categoria, valor, **trecho literal**, URL, data de consulta, e para quais
   tipos de artigo vale. Regra não encontrada no guia → `NOT_FOUND` (não presumir padrão da editora).
4. Regras "gerais da editora" e "específicas do periódico" são registradas separadamente; em
   conflito, prevalece a do periódico e o conflito é anotado.

## Categorias a extrair (conforme aplicável)

tipos de artigo · escopo · limite de palavras (e o que conta) · estrutura/seções · limite do abstract ·
keywords (mín./máx.) · título (limite) · nº de figuras · nº de tabelas · material suplementar ·
estilo de referências · blind review (simples/duplo) · formato de arquivos · templates · highlights ·
graphical abstract · data availability statement · code availability · funding · conflict of
interest · author contributions/CRediT · acknowledgments · ethics approval · consent · uso de IA
generativa · preprints · copyright/licença · open access · APC · cover letter · ORCID ·
suggested/excluded reviewers · reporting guidelines · checklist de submissão.

Regras verificáveis automaticamente usam `check` (ver schema): `max_words`, `max_abstract_words`,
`keywords_range`, `max_title_words`, `max_title_chars`, `max_figures`, `max_tables`,
`required_section`, `required_statement`, `highlights`; as demais usam `manual`.

## Workflow

1. Acessar o guia oficial (WebFetch/Firecrawl/navegação); anotar URL e data; procurar data/versão do guia.
2. Preencher `research/publication/journals/<slug>/requirements.json` (schema
   `journal-requirements.schema.json`; template em `templates/`).
3. Validar: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" validate requirements …`; frescor: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" freshness … --max-age-days 30`.

## Output esperado

JSON de regras + tabela legível (categoria | exigência | trecho | URL | data).

## Critérios de qualidade

- 100% das regras com trecho e URL; data de consulta em todas.
- Nada preenchido de memória ("a Elsevier costuma pedir…") — isso seria `NOT_VERIFIED`.

## Situações de falha

- Página inacessível → arquivo com `access_status: "blocked"` e regras `NOT_VERIFIED`; pedir ao
  usuário o texto/PDF oficial. A auditoria pré-submissão ficará `ACTION REQUIRED` até isso.
