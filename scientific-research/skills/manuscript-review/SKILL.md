---
name: manuscript-review
description: Auditoria final de manuscrito científico — coerência pergunta → método → resultado → conclusão, consistência dos números entre resumo, texto, tabelas e figuras, referências, afirmações causais, generalizações, limitações, transparência e reprodutibilidade — com relatório priorizado de problemas e localização. Use para "revisar o artigo inteiro", "auditoria do manuscrito", "revisão final antes de submeter", "manuscript review", "checar inconsistências entre texto e tabelas", "parecer do artigo".
argument-hint: "[arquivo do manuscrito] [--profundidade rapida|completa]"
---

# Manuscript Review

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

- Revisão final antes da submissão, ou parecer sobre manuscrito de terceiros.

## Quando NÃO usar

- Só a lista de referências → `bibliography-audit`.
- Só frase-a-frase das citações → `citation-audit` (é um dos módulos desta skill).

## Inputs esperados

Manuscrito completo (com tabelas/figuras), opcionalmente ledger, `sources.json`,
dados/códigos e normas do periódico.

## Workflow (módulos)

1. **Coerência central**: extrair pergunta, hipótese, método, principais resultados e
   conclusões; checar se a conclusão decorre do resultado e o resultado do método.
   Tabela: elemento | onde aparece | consistente? | problema.
2. **Números**: inventariar todos os números do resumo, texto, tabelas e figuras;
   cruzar (mesmo valor, mesma unidade, mesmo arredondamento, mesmo N). Recalcular
   percentuais/somas simples quando possível e registrar o cálculo como verificação.
   Automático: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" scan <manuscrito> [--ledger ...]`.
3. **Tabelas × texto** e **figuras × texto**: cada referência a tabela/figura corresponde
   ao conteúdo? Tabelas citadas existem? Notas explicam unidades, EP e significância?
4. **Referências**: executar `citation-audit` (amostral em revisão rápida; completa em
   revisão completa) e `bibliography-audit`.
5. **Causalidade**: listar frases causais; conferir contra o desenho (o próprio e o das
   fontes citadas).
6. **Generalização e validade externa**: conclusões extrapolam amostra/país/período?
7. **Limitações**: as ameaças relevantes (de `methodology-review`) estão reconhecidas?
8. **Transparência e reprodutibilidade**: executar `replication-check`.
9. **Integridade de IA**: sinais de conteúdo fabricado (referências sem DOI resolvível,
   números "redondos" sem fonte, citações genéricas).

## Classificação de problemas

`CRÍTICO` (invalida conclusão/integridade: número errado, referência inexistente, causalidade
sem identificação) · `MAIOR` (afeta interpretação) · `MENOR` (clareza/forma).

Relatório: `research/audit/manuscript-audit.md` (template
`${CLAUDE_PLUGIN_ROOT}/templates/manuscript-audit-report.md`).

Para manuscritos longos, pode-se paralelizar: `citation-auditor` (referências) e
`methodology-reviewer` (desenho) como verificações independentes; consolidar sem duplicar.

## Output esperado

Sumário executivo (3–5 linhas) + tabela de problemas (id, severidade, local, descrição,
evidência, recomendação) + checklists dos módulos + o que não foi possível verificar.

## Critérios de qualidade

- Todo problema com localização (seção/parágrafo/tabela) e evidência.
- Sugestões de reescrita não introduzem fatos novos.
- Cobertura declarada (o que foi e o que não foi auditado).

## Situações de falha

- Tabelas como imagem sem texto → declarar limitação na checagem numérica.
- Fontes inacessíveis → classificar como `NÃO VERIFICÁVEL`, não como erro do autor.
