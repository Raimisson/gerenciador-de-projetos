---
name: evidence-ledger
description: "Registro de evidências (JSONL) e proveniência fonte → evidência → parágrafo. Use para \"registrar evidência\", \"de onde veio esta afirmação\", \"rastrear número\", \"evidence ledger\"."
argument-hint: "[add|validate|trace|status] [argumentos]"
---

# Evidence Ledger

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

## Conceito

Cadeia de proveniência do plugin:

```
sources.json (S-0001)  →  ledger/evidence.jsonl (E-0001)  →  manuscript.md  "... [E-0001]"
   fonte verificada          evidência extraída +                parágrafo que usa
                              interpretação rotulada               a evidência
```

- Um arquivo JSONL, **uma evidência por linha**, versionável em Git.
- Schema: `${CLAUDE_PLUGIN_ROOT}/schemas/ledger-entry.schema.json`.
- Exemplo real: `${CLAUDE_PLUGIN_ROOT}/examples/01-revenue-decoupling/research/ledger/evidence.jsonl`.

## Quando usar

- Toda vez que uma evidência for usada (ou candidata a uso) em síntese ou texto.
- Para auditar a origem de uma frase do manuscrito.

## Quando NÃO usar

- Para armazenar a ficha completa do estudo → isso é `extraction/<S-id>.json`.
  O ledger guarda **a evidência pontual** que sustenta uma afirmação.

## Campos

| Campo | Obrigatório | Descrição |
|---|---|---|
| `evidence_id` | sim | `E-0001`, sequencial, nunca reutilizado |
| `source_id` | sim | `S-0001` (existe em `sources.json`) |
| `citation` | sim | citação curta verificada (Autor, ano) |
| `doi` / `url` | sim | valor ou `NR — não reportado` |
| `page` / `table` / `figure` / `section` | sim (`page`, `section`) | localização; ou `página não identificável de forma confiável` |
| `excerpt` | sim | trecho literal (ou paráfrase fiel marcada `[paráfrase]` se o trecho for longo/tabela) |
| `claim_supported` | sim | a afirmação exata que esta evidência sustenta |
| `evidence_type` | sim | `source_evidence` · `author_interpretation` · `analytic_inference` |
| `derived_from` | se `analytic_inference` | lista de `E-…` usados na inferência |
| `method` | sim | método/desenho do estudo ou `NR` |
| `design_class` | sim | `causal` · `associational` · `descriptive` · `simulation` · `normative` · `review` · `NR — não reportado` |
| `context` | sim | `{country, population, period, sector}` |
| `quantitative_result` | sim | objeto `{estimate, unit, se, ci_low, ci_high, p_value, n}` ou `NR — não reportado` |
| `verification_status` | sim | `VERIFIED` · `PARTIALLY_VERIFIED` · `UNVERIFIED` · `CONTRADICTED` · `NOT_REPORTED` |
| `verified_by` / `verified_on` | sim | quem/quando (ex.: `claude+scite`, `2026-09-24`) |
| `used_in` | não | ids de parágrafo do manuscrito (ex.: `P-012`) |
| `notes` | não | observações, limitações de acesso |

## Workflow

### Adicionar
1. Confirme que a fonte está em `sources.json`.
2. Crie a linha JSON com todos os campos; `evidence_id` = próximo número livre.
3. Anexe ao arquivo (não reescreva linhas antigas; correções geram nova linha com
   `notes: "substitui E-0007"` e a antiga recebe `verification_status` atualizado apenas
   se foi demonstrado erro — registre o motivo).
4. Valide: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" validate ledger research/ledger/evidence.jsonl --sources research/sources/sources.json`.

### Rastrear ("de onde veio esta afirmação?")
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" trace E-0003 --ledger research/ledger/evidence.jsonl --sources research/sources/sources.json --manuscript research/manuscript/manuscript.md
```
Mostra: fonte completa → trecho e localização → tipo de evidência → parágrafos que a usam.
Sem Bash: leia os arquivos e apresente a mesma cadeia manualmente.

### Status
Resumo por `verification_status` e lista de evidências `UNVERIFIED`/`CONTRADICTED`
usadas no manuscrito (bloqueiam a entrega final).

## Critérios de qualidade

- Toda frase empírica do manuscrito aponta para ≥1 `E-…` com status `VERIFIED` ou
  `PARTIALLY_VERIFIED` (este último explicitado no texto ou em nota).
- `analytic_inference` nunca aparece no texto como resultado de estudo.
- Nenhum `E-…` órfão (sem fonte) nem fonte inexistente.

## Situações de falha

- Evidência sem trecho localizável → `verification_status: UNVERIFIED`; não usar no texto.
- Fonte `CONTRADICTED` → remover do texto ou reescrever a frase; registrar.
