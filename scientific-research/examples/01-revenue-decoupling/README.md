# Exemplo 1 — Economia/regulação: revenue decoupling e programas de eficiência energética

> **Pergunta:** "Quais estudos mensuraram quantitativamente os efeitos de mecanismos de revenue
> decoupling sobre programas de eficiência energética?"

Este exemplo foi produzido **com ferramentas reais** em 24/09/2026 (conector Scite; Elicit e
Consensus foram tentados e falharam — o que também é demonstrado). Ele **não** é uma revisão
completa: mostra o comportamento do plugin, inclusive quando o texto integral não está acessível.

## Como foi executado

```text
/scientific-research:research-project revenue decoupling e programas de eficiência energética
/scientific-research:literature-search <pergunta acima>
/scientific-research:citation-chasing 10.5547/01956574.37.4.jkah --rodadas 1
/scientific-research:systematic-review (triagem)
/scientific-research:evidence-extraction S-0001 / S-0002
/scientific-research:quantitative-evidence S-0002
/scientific-research:evidence-matrix --formato md
/scientific-research:evidence-synthesis
```

## Arquivos

| Etapa | Arquivo |
|---|---|
| Protocolo | `research/protocol.md` |
| Estratégia e log de busca (JSON + fluxo) | `research/search/search-log.json`, `research/search/prisma-flow.md` |
| Triagem (com motivos) | `research/screening/screening.csv` |
| Fontes e status de verificação | `research/sources/sources.json` |
| Fichas de extração | `research/extraction/S-000*.json` |
| Evidence Ledger | `research/ledger/evidence.jsonl` |
| Matriz (MD, CSV detalhado, JSON) | `research/matrix/` |
| Avaliação metodológica | `research/appraisal/S-0002.md` |
| Síntese | `research/synthesis/synthesis.md` |
| Rascunho com proveniência | `research/manuscript/manuscript.md` |
| Varredura automática | `research/audit/scan.md` |

## O que o exemplo demonstra

1. **Estratégia e log reproduzível**: queries exatas, base, data, contagens reportadas pela
   ferramenta (29.849 e 806 no Scite) e **buscas que falharam** registradas com `executed: false`.
2. **Citation chasing**: forward search a partir de Kahn-Lang (2016) encontrou Datta (2019) e
   von Loessl & Wetzel (2022), mais relevantes que a busca por palavras-chave.
3. **Triagem com aritmética checada**: 25 identificados → 3 duplicatas → 22 triados → 17
   excluídos → 4 sem texto completo + 1 avaliado → 0 incluídos formalmente.
4. **Regra NR**: "significant" no abstract de Kahn-Lang **não** virou número; estimativas `NR`.
5. **Extração quantitativa com localização**: Cappers et al. (2020), Table 2 / Results and
   Discussion, média 0.4 percent, mediana 0.2 percent, com trecho literal e aviso de paginação
   não confiável.
6. **Fonte secundária sinalizada**: o número "16 estados em 2017" é de Berg et al. (2019)
   citado por Cappers et al. — E-0004 fica `UNVERIFIED` até a fonte primária ser localizada.
7. **Honestidade sobre a lacuna**: "Não foi encontrada evidência quantitativa que permita estimar
   este parâmetro" nas fontes acessadas.

## Reproduzir as validações

```bash
S=../../scripts/srtool.py
python3 $S validate project research
python3 $S matrix research/extraction --sources research/sources/sources.json --format md
python3 $S prisma research/search/search-log.json
python3 $S scan research/manuscript/manuscript.md --ledger research/ledger/evidence.jsonl --sources research/sources/sources.json
python3 $S trace P-002 --ledger research/ledger/evidence.jsonl --sources research/sources/sources.json --manuscript research/manuscript/manuscript.md
python3 $S refs-check research/sources/sources.json   # requer rede (Crossref)
```

## Limitações deste exemplo

- Metadados conferidos só no índice Scite (Crossref/doi.org bloqueados no ambiente de geração):
  todas as fontes estão `PARTIALLY_VERIFIED`.
- Apenas os primeiros registros por relevância foram examinados; a ausência de outros estudos
  aqui **não** prova que não existam.
- Decisões de triagem são propostas do Claude (`claude-proposal`), sem revisão humana.
