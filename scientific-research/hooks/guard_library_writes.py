#!/usr/bin/env python3
"""PreToolUse (mcp__.*): pede confirmação antes de operações de escrita em bibliotecas de pesquisa.

- Zotero (qualquer servidor cujo nome contenha 'zotero'): toda operação que não seja de leitura.
- Scite / Elicit / Consensus / Google Drive / outros servidores de pesquisa: operações que criam,
  alteram, importam, compartilham ou apagam coleções, bibliotecas, notas ou arquivos.
Leituras e buscas passam sem interferência. Nunca nega: devolve "ask" com o motivo.
"""
import json
import re
import sys

WRITE_VERBS = re.compile(
    r"(^|_|-)(create|add|update|delete|remove|trash|import|save|upload|stage|write|edit|modify|move|"
    r"share|copy|rename|set|put|post|patch|attach|tag|untag|merge)(_|-|$)", re.I)
RESEARCH_SERVERS = re.compile(r"zotero|scite|elicit|consensus|drive|semantic|openalex|crossref|scholar", re.I)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    name = event.get("tool_name") or ""
    if not name.startswith("mcp__"):
        return 0
    parts = name.split("__")
    server = parts[1] if len(parts) > 2 else ""
    tool = parts[-1]
    if not RESEARCH_SERVERS.search(server):
        return 0
    if not WRITE_VERBS.search(tool):
        return 0
    kind = "Zotero é usado em modo somente leitura por padrão" if "zotero" in server.lower() else \
        "operações de escrita em bibliotecas/coleções de pesquisa exigem intenção explícita"
    out = {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": (
            f"Scientific Research: '{name}' altera dados em um serviço externo ({kind}). "
            "Confirme somente se você pediu explicitamente esta alteração."),
    }}
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
