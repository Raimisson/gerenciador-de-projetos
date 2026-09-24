#!/usr/bin/env bash
# Smoke test com o Claude Code real: valida, instala via marketplace local e verifica que
# skills e agentes do plugin são carregados numa sessão `claude -p`.
# Consome algumas chamadas de modelo. Uso: bash tests/cli_smoke_test.sh
set -euo pipefail
PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$(cd "$PLUGIN_DIR/.." && pwd)"
command -v claude >/dev/null || { echo "claude CLI não encontrado"; exit 1; }

echo "== 1. validação oficial (--strict)"
claude plugin validate "$PLUGIN_DIR" --strict
claude plugin validate "$PLUGIN_DIR/skills" --strict
claude plugin validate "$PLUGIN_DIR/agents" --strict
claude plugin validate "$PLUGIN_DIR/modules/publication-strategy/skills" --strict
claude plugin validate "$REPO_DIR" --strict

echo "== 2. instalação via marketplace local"
claude plugin marketplace add "$REPO_DIR" >/dev/null
claude plugin install scientific-research@raimisson-research
claude plugin list | grep -q "scientific-research" && echo "instalado: OK"
claude plugin details scientific-research@raimisson-research | head -40

echo "== 3. carga numa sessão (--plugin-dir) — lista de skills/agentes vista pelo modelo"
OUT="$(cd "$(mktemp -d)" && claude -p --plugin-dir "$PLUGIN_DIR" \
  "Liste, um por linha e sem comentários, os nomes de todas as skills e subagentes disponíveis cujo nome começa com 'scientific-research:'.")"
echo "$OUT"
for s in research-project evidence-extraction citation-audit regulatory-research manuscript-review journal-search journal-fit-analysis pre-submission-audit peer-review-response; do
  echo "$OUT" | grep -q "scientific-research:$s" || { echo "FALHA: skill $s não visível"; exit 1; }
done
for a in literature-researcher citation-auditor scientific-editor publication-strategist; do
  echo "$OUT" | grep -q "scientific-research:$a" || { echo "FALHA: agente $a não visível"; exit 1; }
done
echo "skills e agentes visíveis: OK"

echo "== 4. desinstalação (limpeza)"
claude plugin uninstall scientific-research@raimisson-research >/dev/null || true
claude plugin marketplace remove raimisson-research >/dev/null || true
echo "smoke test concluído"
