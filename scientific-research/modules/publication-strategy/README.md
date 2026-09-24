# Módulo Publication Strategy (parte do plugin Scientific Research)

Etapa entre o manuscrito concluído e a publicação: escolha de periódicos por **aderência verificável**,
due diligence, regras atuais do periódico, compliance, preparação da submissão, cover letter,
auditoria pré-submissão, resposta a pareceres e ressubmissão.

- Documentação completa: [`../../docs/publication-strategy.md`](../../docs/publication-strategy.md)
- Skills: [`skills/`](skills/) (carregadas pelo manifesto do plugin: `"skills": ["./skills", "./modules/publication-strategy/skills"]`)
- Subagente: [`../../agents/publication-strategist.md`](../../agents/publication-strategist.md)
- Schemas: [`schemas/`](schemas/) · Templates: [`templates/`](templates/) · Ferramenta: [`scripts/pubtool.py`](scripts/pubtool.py)
- Exemplo completo: [`../../examples/04-publication-strategy/`](../../examples/04-publication-strategy/README.md)

**Princípio:** nunca estimar probabilidade de aceitação. O índice de aderência é transparente
(critérios, pesos, fontes, cobertura) e não é probabilidade de publicação.

```bash
P=scripts/pubtool.py
python3 $P init research
python3 $P profile research/manuscript/manuscript.md --out research/publication/manuscript-profile.json
python3 $P venues research/sources/sources.json
python3 $P fit-report research/publication/journals/<slug>/fit.json --out research/publication/journals/<slug>/fit-report.md
python3 $P compare research/publication/journals/*/fit.json
python3 $P target set research/publication --journal <slug>
python3 $P check-compliance research/manuscript/manuscript.md research/publication/journals/<slug>/requirements.json --out research/publication/compliance/<slug>
python3 $P presubmit research --journal <slug>
python3 $P lint research/publication/submission/<slug>/cover-letter.md
python3 $P response-letter research/publication/peer-review/round-1/response-matrix.json
```
