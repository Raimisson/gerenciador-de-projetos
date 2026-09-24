---
name: replication-check
description: "Checklist de reprodutibilidade: dados, código, amostra, filtros, especificações, software e seeds. Use para \"dá para replicar?\", \"reprodutibilidade\", \"pacote de replicação\"."
argument-hint: "[estudo/manuscrito] [--com-codigo caminho]"
---

# Replication Check

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

- Avaliar se um estudo publicado pode ser reproduzido.
- Preparar o próprio manuscrito/pacote de replicação antes da submissão.

## Quando NÃO usar

- Avaliar validade do desenho → `methodology-review`.
- Rodar de fato a replicação completa — esta skill verifica **informação suficiente**;
  execução de código só com pedido explícito e em cópia dos dados.

## Inputs esperados

Texto integral + apêndices; links de dados/código (repositórios, Dataverse, Zenodo,
OSF, GitHub); para o manuscrito do usuário: pasta `research/analysis/` e `research/data/`.

## Checklist

| Item | Pergunta | Status (`sim`·`parcial`·`não`·`NA`·`não verificável`) | Localização |
|---|---|---|---|
| Dados | Fonte identificada, acesso descrito (público/restrito), versão/data de extração? | | |
| Código | Disponível? Linguagem? Executa do início ao fim? | | |
| Amostra | Construção, filtros, exclusões e contagens por etapa? | | |
| Transformações | Deflatores, logs, winsorização, imputação descritos? | | |
| Variáveis | Definições operacionais e fontes? | | |
| Especificações | Equações, controles, efeitos fixos, cluster? | | |
| Parâmetros | Hiperparâmetros, bandwidths, janelas, tolerâncias? | | |
| Software | Programas e versões? pacotes? | | |
| Aleatoriedade | Seeds para bootstrap/simulação/ML? | | |
| Resultados | Tabelas/figuras mapeadas a scripts? | | |
| Links | Links de dados/código resolvem? (verificar, não supor) | | |

## Workflow

1. Ler métodos, apêndices e declarações de disponibilidade de dados/código.
2. Preencher o checklist com localização (página/seção) e evidência.
3. Se houver links, verificar se resolvem (WebFetch); registrar data.
4. Para o manuscrito do usuário: conferir `analysis-run-log.md`, scripts e dados
   derivados; confirmar que `data/raw/` não foi alterado (hash, se registrado).
5. Classificar: `reproduzível` · `potencialmente reproduzível` · `não reproduzível com a informação disponível`.

## Output esperado

Checklist preenchido + lacunas priorizadas + recomendações concretas (o que falta documentar).

## Critérios de qualidade

- Cada "sim" com localização; links verificados de fato.
- Não presumir que "dados disponíveis mediante solicitação" = disponíveis.

## Situações de falha

- Apêndice online inacessível → `não verificável` e registrar tentativa.
