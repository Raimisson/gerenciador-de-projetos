#!/usr/bin/env python3
"""Sincroniza o bloco canônico de integridade em skills e agentes.

Fonte única: docs/partials/integrity-block.md
Alvo: trecho entre <!-- integrity:start --> e <!-- integrity:end --> em
skills/*/SKILL.md e agents/*.md.

Uso:
    python3 scripts/sync_integrity.py          # reescreve os blocos
    python3 scripts/sync_integrity.py --check  # só verifica (exit 1 se divergente)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCK = (ROOT / "docs" / "partials" / "integrity-block.md").read_text(encoding="utf-8").strip()
PATTERN = re.compile(r"<!-- integrity:start -->.*?<!-- integrity:end -->", re.S)
REPLACEMENT = f"<!-- integrity:start -->\n{BLOCK}\n<!-- integrity:end -->"


def targets():
    yield from sorted((ROOT / "skills").glob("*/SKILL.md"))
    yield from sorted((ROOT / "agents").glob("*.md"))


def main(argv):
    check = "--check" in argv
    problems = []
    for path in targets():
        text = path.read_text(encoding="utf-8")
        if not PATTERN.search(text):
            problems.append(f"{path.relative_to(ROOT)}: marcadores integrity:start/end ausentes")
            continue
        new = PATTERN.sub(lambda _m: REPLACEMENT, text)
        if new != text:
            if check:
                problems.append(f"{path.relative_to(ROOT)}: bloco de integridade desatualizado")
            else:
                path.write_text(new, encoding="utf-8")
                print(f"atualizado: {path.relative_to(ROOT)}")
    for p in problems:
        print(p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
