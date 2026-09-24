---
name: evidence-extraction
description: "Ficha estruturada de evidências por documento (método, amostra, resultados, página, trecho), com campos ausentes como NR. Use para \"extrair evidências\", \"ficha de extração\", \"data extraction\"."
argument-hint: "[PDF/DOI/arquivo] [--source-id S-0001]"
---

# Evidence Extraction

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

- Há um documento (idealmente texto integral) e é preciso registrar o que ele efetivamente reporta.
- Antes de montar matriz, síntese ou redação.

## Quando NÃO usar

- Foco exclusivo em equações/tabelas de regressão de um estudo quantitativo complexo →
  `quantitative-evidence` (que produz o mesmo formato, com mais detalhe).
- Avaliar qualidade do desenho → `methodology-review` (depois da extração).

## Inputs esperados

- Documento: PDF, texto, DOI com acesso ao texto integral (ex.: Scite `read_fulltext`,
  Elicit `get_library_source_full_text`), ou arquivo do usuário.
- `source_id` (se já existir em `sources.json`) e a pergunta de pesquisa.

## Regras específicas

1. **Nível de acesso primeiro.** Registre `access_level`: `full_text` · `abstract_only` ·
   `metadata_only`. Se a ferramenta retornou só o abstract (ex.: Scite `source: "abstract"`),
   é `abstract_only`, e os campos que o abstract não contém ficam `NR — não reportado`.
2. **Valores permitidos em qualquer campo**: o valor como reportado, `NR — não reportado`
   ou `NA — não se aplica`. Campo vazio/`null` é inválido.
3. **Não inferir.** Se o autor não diz o tamanho da amostra, é `NR`, mesmo que "dê para
   calcular". Um cálculo próprio vai em `notes` rotulado [INFERÊNCIA] com a fórmula.
4. **Qualitativo não vira número.** "significant reduction" → `estimate: "NR — não reportado"`,
   `significance: "descrito como significativo (sem valor reportado)"`.
5. **Localização obrigatória** para todo número: página, tabela, figura, apêndice ou
   seção. Se o texto não tiver paginação confiável: `page: "página não identificável de forma confiável"` e informar a seção.
6. **Trecho literal** (`excerpt`) curto que sustenta cada estimativa e o resultado principal.
7. **Escopo da conclusão**: registrar se o resultado vale para a amostra toda ou só para
   uma especificação/subgrupo/seção.

## Workflow

1. Confirmar/registrar a fonte em `research/sources/sources.json` (metadados verificados
   ou `UNVERIFIED`).
2. Ler o documento na ordem: abstract → dados/métodos → resultados/tabelas →
   robustez → limitações → apêndices. Não parar no abstract se o texto integral existir.
3. Preencher a ficha (template humano: `${CLAUDE_PLUGIN_ROOT}/templates/extraction-form.md`;
   formato de máquina: `${CLAUDE_PLUGIN_ROOT}/schemas/extraction.schema.json`).
4. Uma entrada em `estimates[]` por resultado quantitativo relevante (por outcome ×
   especificação principal). Resultados de robustez relevantes também.
5. Salvar em `research/extraction/<source_id>.json` e validar:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" validate extraction research/extraction/S-0001.json
   ```
   O validador rejeita campos vazios, números sem localização e estimativas numéricas
   sem trecho; alerta quando o número não aparece no trecho.
6. Registrar no Evidence Ledger as evidências que serão usadas (`evidence-ledger`).

## Campos da ficha

`reference`, `research_question`, `country_jurisdiction`, `population`,
`unit_of_analysis`, `period`, `data_source`, `sample_size`, `intervention`,
`comparison`, `outcome`, `method`, `empirical_strategy`, `causal_identification`,
`model_equation`, `variables`, `main_result`, `robustness`, `limitations`, `doi`, `url`
+ `field_locations` (onde cada campo foi encontrado)
+ `estimates[]`: `estimate`, `unit`, `denominator`, `se`, `ci_low`, `ci_high`,
`p_value`, `significance`, `n`, `period`, `model`, `specification`,
`dependent_variable`, `explanatory_variable`, `treatment_group`, `control_group`,
`identification`, `location{page,table,figure,section}`, `excerpt`.

## Output esperado

1. Tabela Markdown da ficha (campo | valor | localização).
2. Tabela de estimativas.
3. JSON salvo e resultado da validação.
4. Seção "Não verificado / lacunas" listando os `NR` relevantes para a pergunta.

## Critérios de qualidade

- 100% dos números com localização e trecho.
- Nenhum campo vazio; `NR` usado sempre que a informação não está no documento.
- Distinção visível entre [FONTE] e [AUTORES] no resultado principal.

## Situações de falha

- Só abstract disponível → extração marcada `abstract_only`; recomendar obter o texto integral; resultados quantitativos permanecem `NR` salvo se no abstract.
- PDF escaneado/ilegível → informar; não "adivinhar" números de tabelas ilegíveis.
- Documento contraditório (texto ≠ tabela) → registrar ambos, com localizações, em `notes`.
