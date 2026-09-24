# Síntese — revenue decoupling × programas de eficiência energética (demonstração)

**Pergunta:** Quais estudos mensuraram quantitativamente os efeitos de mecanismos de revenue
decoupling sobre programas de eficiência energética?

## Estado da evidência nesta busca

| Estudo | Status de acesso | O que se pode afirmar | Ledger |
|---|---|---|---|
| Kahn-Lang (2016), *The Energy Journal* | só abstract | [AUTORES] associação empírica entre decoupling e maior gasto/eficácia de DSM; magnitudes NR | E-0001 |
| Datta (2019), *Energy Policy* | só metadados | título indica evidência empírica sobre decoupling e DSM; conteúdo não verificado | — |
| von Loessl & Wetzel (2022), *Utilities Policy* | só metadados | título indica evidência empírica sobre decoupling, demanda e EE; conteúdo não verificado | — |
| Arimura, Li & Newell (2012), *The Energy Journal* | abstract truncado | Não foi possível verificar esta informação nas fontes consultadas (se decoupling é regressor) | — |
| Cappers et al. (2020), *The Electricity Journal* | texto integral (parcial) | [FONTE] contexto: ajuste tarifário médio 0,4% (mediana 0,2%) da tarifa de varejo, 21 utilidades, 2005–2017; **não** mede efeitos sobre EE | E-0002, E-0003 |

## Resposta à pergunta

- Registros que **declaram** ter mensurado empiricamente a relação: Kahn-Lang (2016)
  (pelo abstract). Datta (2019) e von Loessl & Wetzel (2022) são candidatos fortes pelo título,
  identificados por forward citation chasing.
- **Magnitudes:** Não foi encontrada evidência quantitativa que permita estimar este parâmetro
  nas fontes acessadas (textos integrais indisponíveis via conector).
- [INFERÊNCIA] A literatura pertinente parece concentrada em utilidades dos EUA; qualquer
  transposição para o Brasil exigiria discutir diferenças de regime tarifário (ex.: revisão
  tarifária periódica, obrigações legais de investimento em eficiência energética) — ponto a
  desenvolver com `regulatory-research`.

## Portão de meta-análise

`não viável`: nenhuma estimativa de efeito com erro-padrão foi extraída.

## Próximos passos

1. Obter os PDFs de S-0001, S-0003, S-0004 e S-0005 (DOIs no `sources.json`) e rodar
   `evidence-extraction` / `quantitative-evidence`.
2. Rodar `srtool.py refs-check research/sources/sources.json` em ambiente com rede para
   promover metadados a VERIFIED.
3. Repetir B3 (Elicit) e B4 (Consensus) quando houver acesso; buscar em RePEc/SSRN.
4. Localizar a fonte primária do número "16 estados em 2017" (Berg et al., 2019) — E-0004 está `UNVERIFIED`.
