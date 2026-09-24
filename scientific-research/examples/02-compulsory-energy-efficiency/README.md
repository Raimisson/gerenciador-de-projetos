# Exemplo 2 — Avaliação de política pública: programas compulsórios de eficiência energética

> **Pergunta:** "Qual é a evidência empírica sobre os efeitos de programas compulsórios de
> eficiência energética?"

Produzido com o conector Scite em 24/09/2026 (Consensus indisponível por cota — registrado).
Demonstração, não revisão completa.

## Como foi executado

```text
/scientific-research:research-question Qual é a evidência empírica sobre os efeitos de programas compulsórios de eficiência energética?
/scientific-research:literature-search --periodo sem-restricao
/scientific-research:systematic-review (triagem)
/scientific-research:quantitative-evidence S-0001 S-0002 S-0003
/scientific-research:methodology-review (classificação ex ante × ex post)
/scientific-research:evidence-synthesis --meta-feasibility
/scientific-research:scientific-writing revisão de literatura
```

## O que o exemplo demonstra

1. **Classificação por desenho antes da síntese**: ex post descritivo (Letônia), contabilidade
   custo-benefício (GB/IT/FR), CBA ex ante (Suécia), contexto institucional (UE). Só desenhos com
   contrafactual sustentariam "efeito"; nenhum foi encontrado nesta busca — e isso é dito
   explicitamente.
2. **Projeção ≠ efeito observado**: BCR 1.56–2.17 de Xylia et al. é marcado `design_class: simulation`.
3. **Unidade ausente não é inventada**: o abstract recuperado de Giraudet et al. traz
   "0. 009/kWh" sem símbolo monetário → `unit: NR`; o validador ainda alerta que "0.009" não
   aparece literalmente no trecho (o texto tem um espaço espúrio) — sinal para conferir no PDF.
4. **Fonte primária por trás do artigo**: os 329,2 GWh da Letônia vêm de um relatório
   governamental citado pelo artigo (ref. [25]); a extração registra isso.
5. **Generalização**: `srtool.py scan --context Brasil` sinaliza a frase de P-002, que usa
   evidência europeia sem qualificar o contexto quando o manuscrito é sobre o Brasil; P-001, que
   nomeia explicitamente UE e Letônia, não é sinalizado.
6. **Meta-análise recusada com justificativa** (métricas incompatíveis, sem erros-padrão).

## Arquivos

`research/search/search-log.json` · `research/search/prisma-flow.md` · `research/screening/screening.csv` ·
`research/sources/sources.json` · `research/extraction/*.json` · `research/ledger/evidence.jsonl` ·
`research/matrix/*` · `research/synthesis/synthesis.md` · `research/manuscript/manuscript.md` ·
`research/audit/scan.md`

## Reproduzir

```bash
S=../../scripts/srtool.py
python3 $S validate project research
python3 $S scan research/manuscript/manuscript.md --ledger research/ledger/evidence.jsonl --sources research/sources/sources.json --context Brasil
python3 $S trace E-0001 --ledger research/ledger/evidence.jsonl --sources research/sources/sources.json --manuscript research/manuscript/manuscript.md
```

## Limitações

Metadados apenas no índice Scite (`PARTIALLY_VERIFIED`); textos integrais não lidos por completo;
8 primeiros registros de 898. A literatura norte-americana sobre EERS e a regulação brasileira não
foram cobertas nesta demonstração.
