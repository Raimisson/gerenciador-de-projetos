# Exemplo 3 — Auditoria de artigo

Mostra como fornecer um manuscrito e pedir: auditoria das referências, verificação das
afirmações e inconsistências entre texto e evidência.

## Como pedir

```text
/scientific-research:citation-audit examples/03-manuscript-audit/manuscript.md
/scientific-research:bibliography-audit examples/03-manuscript-audit/references.json --estilo abnt
/scientific-research:manuscript-review examples/03-manuscript-audit/manuscript.md --profundidade completa
```

Ou em linguagem natural: *"Audite as referências e as afirmações deste manuscrito, verifique se as
fontes sustentam cada frase e aponte inconsistências entre texto e evidência."*

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `manuscript.md` | manuscrito com defeitos plantados (inclui referência falsa) |
| `references.json` | lista de referências no formato `sources.json`, com status de verificação |
| `scan-output.md` | saída real de `srtool.py scan --context Brasil` |
| `doi-check-fake-reference.json` | saída de `srtool.py doi-check` para o DOI falso (fixture de rede) |
| `citation-audit.json` / `citation-audit-report.md` | auditoria frase a frase (resultado esperado) |

## Defeitos plantados e como são detectados

| Defeito | Detectado por | Resultado |
|---|---|---|
| Referência inventada (Silva & Pereira, 2019; DOI 10.9999/…) | Scite (DOI e título: 0 resultados — verificação real) + `doi-check` | CONTRADICTED / NÃO SUPORTADA |
| Número não presente na fonte (20%) | leitura da fonte (abstract) | NÃO VERIFICÁVEL até página ser fornecida |
| Causalidade indevida ("causou", "reduziram") | `scan` (CAUSAL-VERIFICAR) + desenho da fonte | reescrita como associação/projeção |
| Projeção ex ante apresentada como efeito | leitura da fonte (CBA de esquema hipotético) | PARCIALMENTE SUPORTADA |
| Fonte secundária (16 estados) | leitura da fonte (citação de Berg et al., 2019) | PARCIALMENTE SUPORTADA |
| Número sem fonte (12%) | `scan` (NUMERO-SEM-FONTE) | NÃO SUPORTADA |
| Generalização para o Brasil sem evidência | `scan` (AFIRMACAO-SEM-FONTE) + auditoria | NÃO SUPORTADA |

## Reproduzir

```bash
S=../../scripts/srtool.py
python3 $S scan manuscript.md --context Brasil
python3 $S --fixture ../../tests/fixtures/network-fixtures.json doi-check 10.9999/jiee.2019.0457 --title "Revenue decoupling and utility energy efficiency spending: a global meta-analysis" --year 2019
python3 $S doi-check 10.9999/jiee.2019.0457     # ao vivo (requer rede)
python3 $S format references.json --style abnt --include-partial   # a referência CONTRADICTED não é formatada
python3 $S validate audit citation-audit.json
```
