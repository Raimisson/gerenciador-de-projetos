#!/usr/bin/env python3
"""SessionStart: injeta lembrete curto das regras de integridade do plugin Scientific Research."""
import json
import sys

REMINDER = (
    "Plugin Scientific Research ativo. Em tarefas de pesquisa científica: (1) nunca invente "
    "artigos, DOI, autores, páginas, datas, URLs ou números — memória do modelo não é fonte; "
    "(2) informação não confirmada → 'Não foi possível verificar esta informação nas fontes "
    "consultadas.'; sem número → 'Não foi encontrada evidência quantitativa que permita estimar "
    "este parâmetro.'; campo ausente → 'NR — não reportado'; (3) separe [FONTE], [AUTORES] e "
    "[INFERÊNCIA]; (4) status VERIFIED/PARTIALLY_VERIFIED/UNVERIFIED/CONTRADICTED/NOT_REPORTED; "
    "(5) texto integral antes de abstract, com página/tabela. Workflow: /scientific-research:research-project."
)


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": REMINDER}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
