#!/usr/bin/env python3
"""Sincroniza blocos canônicos de integridade em skills e agentes.

Fontes únicas (docs/partials/):
  integrity-block.md             → <!-- integrity:start --> ... <!-- integrity:end -->
                                   em todas as skills (núcleo e módulos) e agentes
  publication-integrity-block.md → <!-- pubintegrity:start --> ... <!-- pubintegrity:end -->
                                   nas skills do módulo Publication Strategy e no agente
                                   publication-strategist

Uso:
    python3 scripts/sync_integrity.py          # reescreve os blocos
    python3 scripts/sync_integrity.py --check  # só verifica (exit 1 se divergente/ausente)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTIALS = ROOT / "docs" / "partials"
PUB_AGENTS = {"publication-strategist.md"}


def block(marker: str, filename: str):
    text = (PARTIALS / filename).read_text(encoding="utf-8").strip()
    pattern = re.compile(rf"<!-- {marker}:start -->.*?<!-- {marker}:end -->", re.S)
    return marker, pattern, f"<!-- {marker}:start -->\n{text}\n<!-- {marker}:end -->"


CORE = block("integrity", "integrity-block.md")
PUB = block("pubintegrity", "publication-integrity-block.md")


def targets():
    """Gera (caminho, blocos exigidos)."""
    for p in sorted((ROOT / "skills").glob("*/SKILL.md")):
        yield p, [CORE]
    for p in sorted((ROOT / "modules").glob("*/skills/*/SKILL.md")):
        yield p, [CORE, PUB]
    for p in sorted((ROOT / "agents").glob("*.md")):
        yield p, [CORE, PUB] if p.name in PUB_AGENTS else [CORE]


def main(argv):
    check = "--check" in argv
    problems = []
    for path, blocks in targets():
        text = path.read_text(encoding="utf-8")
        new = text
        for marker, pattern, replacement in blocks:
            if not pattern.search(new):
                problems.append(f"{path.relative_to(ROOT)}: marcadores {marker}:start/end ausentes")
                continue
            new = pattern.sub(lambda _m, r=replacement: r, new)
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
