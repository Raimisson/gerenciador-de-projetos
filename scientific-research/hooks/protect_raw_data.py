#!/usr/bin/env python3
"""PreToolUse (Write/Edit/MultiEdit/NotebookEdit): pede confirmação antes de alterar dados brutos.

Considera "dados brutos": caminhos contendo /data/raw/ ou /raw-data/, ou arquivos *.raw.*
Nunca bloqueia silenciosamente: devolve permissionDecision "ask" com o motivo.
"""
import json
import re
import sys

RAW = re.compile(r"(^|[\\/])(data[\\/]raw|raw[-_]data)([\\/]|$)|\.raw\.[A-Za-z0-9]+$", re.I)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or tool_input.get("path") or ""
    if path and RAW.search(path) and not path.lower().endswith("readme.md"):
        out = {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"Scientific Research: '{path}' parece ser um dataset bruto (data/raw). Dados originais não "
                "devem ser modificados silenciosamente. Prefira gerar um arquivo em data/derived/ por script. "
                "Confirme apenas se a alteração for intencional."),
        }}
        print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
