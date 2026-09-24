#!/usr/bin/env python3
"""pubtool — ferramenta do módulo Publication Strategy (somente biblioteca padrão).

Reutiliza o núcleo do plugin (scripts/srtool.py): validador de schemas, varredura de manuscrito,
Evidence Ledger. Nenhuma função calcula probabilidade de aceitação.

Subcomandos:
  init <research_dir>                         cria research/publication/
  profile <manuscript.md>                     perfil mensurável do manuscrito (JSON)
  venues <sources.json>...                    periódicos onde a literatura citada foi publicada
  validate <kind> <file>                      profile|candidates|recent|due-diligence|requirements|fit|compliance|response|target
  fit-report <fit.json>                       Journal Fit Report + índice de aderência (não é probabilidade)
  compare <fit.json>...                       tabela comparativa de candidatos
  check-compliance <manuscript.md> <requirements.json>   COMPLIANT / ACTION REQUIRED / NOT APPLICABLE / UNABLE TO VERIFY
  checklist <requirements.json>               checklist operacional de submissão
  freshness <requirements.json|due-diligence.json>       idade da consulta às fontes oficiais
  target set|show|clear <publication_dir>     Target Journal Mode
  lint <arquivos>...                          probabilidades de aceitação, "primeiro a...", elogios genéricos
  response-letter <response-matrix.json>      matriz legível + carta de resposta aos revisores
  presubmit <research_dir> --journal <slug>   READY TO SUBMIT | ACTION REQUIRED
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import re
import sys

MODULE_ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN_ROOT = MODULE_ROOT.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
import srtool  # noqa: E402

srtool.SCHEMA_DIRS.append(MODULE_ROOT / "schemas")
TEMPLATES = MODULE_ROOT / "templates"
NR = srtool.NR
NOT_VERIFIED = "NOT VERIFIED"
PLACEHOLDER = re.compile(r"\[(AUTORES|AUTHORS?)\s*:[^\]]*\]|\bPREENCHER\b|\bTODO\b|XXX", re.I)
DIMENSIONS = [
    ("topic_fit", "TOPIC FIT"), ("method_fit", "METHOD FIT"), ("contribution_fit", "CONTRIBUTION FIT"),
    ("empirical_fit", "EMPIRICAL FIT"), ("audience_fit", "AUDIENCE FIT"),
    ("recent_publication_fit", "RECENT ARTICLE FIT"), ("article_type_fit", "ARTICLE TYPE FIT"),
]
RATING_SCORE = {"STRONG": 2, "MODERATE": 1, "WEAK": 0}
INTEGRITY_LIMITS = [
    "Regras editoriais não justificam alteração ou omissão seletiva de resultados.",
    "Regras editoriais não justificam fabricação de análise.",
    "Regras editoriais não justificam fabricação de referência.",
    "Regras editoriais não justificam manipulação de evidência.",
    "Regras editoriais não justificam exagero de conclusão.",
]
FIT_DISCLAIMER = ("Índice de aderência (journal fit) calculado a partir de critérios explícitos — "
                  "NÃO é probabilidade de aceitação nem de publicação.")

STATEMENT_PATTERNS = {
    "data_availability": r"data availability|availability of data|disponibilidade d[eo]s? dados",
    "code_availability": r"code availability|disponibilidade d[eo] c[oó]digo",
    "funding": r"\bfunding\b|financiamento|fomento",
    "competing_interests": r"competing interest|conflicts? of interest|declaration of interest|conflitos? de interesses?",
    "credit": r"credit author|author contributions?|contribui[cç][aãõo]+e?s? d[oe]s? autor",
    "ethics": r"\bethic|\b[ée]tica\b",
    "consent": r"\bconsent|consentimento",
    "ai_use": r"generative ai|artificial intelligence|intelig[eê]ncia artificial|\buso de ia\b|ai-assisted",
    "acknowledgments": r"acknowledg|agradecimentos?",
}


def today() -> str:
    return _dt.date.today().isoformat()


def words(text: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ'’\-]+", text))


# --------------------------------------------------------------------------------------
# Leitura do manuscrito (Markdown)
# --------------------------------------------------------------------------------------


class Manuscript:
    """Estrutura mínima de um manuscrito em Markdown."""

    def __init__(self, text: str):
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        self.raw = text
        self.lines = text.splitlines()
        self.title = ""
        self.headings: list[str] = []
        self.sections: dict[str, list[str]] = {}
        current = "_preamble"
        self.sections[current] = []
        in_code = False
        for line in self.lines:
            s = line.strip()
            if s.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            m = re.match(r"^(#{1,6})\s+(.*)$", s)
            if m:
                if len(m.group(1)) == 1 and not self.title:
                    self.title = m.group(2).strip()
                    continue
                current = m.group(2).strip()
                self.headings.append(current)
                self.sections.setdefault(current, [])
                continue
            self.sections.setdefault(current, []).append(line)

    def _find(self, pattern: str):
        for h in self.headings:
            if re.search(pattern, h, re.I):
                return h
        return None

    @property
    def abstract(self) -> str:
        h = self._find(r"^(abstract|resumo)\b")
        if not h:
            return ""
        kw = re.compile(r"^\s*\**\s*(keywords|key words|palavras-chave)\s*\**\s*:", re.I)
        return "\n".join(l for l in self.sections.get(h, []) if not kw.match(l)).strip()

    @property
    def keywords(self) -> list[str]:
        for line in self.lines:
            m = re.match(r"^\s*\**\s*(keywords|key words|palavras-chave)\s*\**\s*:\s*\**\s*(.+)$", line, re.I)
            if m:
                return [k.strip(" .*") for k in re.split(r"[;,]", m.group(2)) if k.strip(" .*")]
        return []

    @property
    def highlights(self) -> list[str]:
        h = self._find(r"^highlights?$|^destaques$")
        if not h:
            return []
        return [re.sub(r"^\s*[-*•]\s*", "", l).strip() for l in self.sections[h] if re.match(r"^\s*[-*•]\s+", l)]

    def _body_sections(self, include_refs: bool):
        skip = re.compile(r"^(abstract|resumo|highlights?|destaques|keywords|palavras-chave)\b", re.I)
        refs = re.compile(r"^(refer[eê]ncias|references|bibliografia|bibliography)\b", re.I)
        for h, lines in self.sections.items():
            if h == "_preamble" or skip.search(h):
                continue
            if refs.search(h) and not include_refs:
                continue
            yield h, lines

    def word_count(self, include_refs: bool) -> int:
        total = 0
        for _, lines in self._body_sections(include_refs):
            for l in lines:
                if re.match(r"^\s*\**\s*(keywords|palavras-chave)", l, re.I) or l.strip().startswith("|"):
                    continue
                total += words(l)
        return total

    def _numbered(self, pattern: str) -> int:
        nums = set()
        for l in self.lines:
            m = re.match(rf"^\s*[*_]*\s*(?:{pattern})\s*(\d+)", l, re.I)
            if m:
                nums.add(int(m.group(1)))
        return len(nums)

    @property
    def figures(self) -> int:
        return self._numbered(r"figure|figura|fig\.")

    @property
    def tables(self) -> int:
        return self._numbered(r"table|tabela")

    def statement(self, kind: str):
        """Retorna (encontrado, texto) para uma declaração (por título de seção ou linha em negrito)."""
        pat = re.compile(STATEMENT_PATTERNS[kind], re.I)
        for h in self.headings:
            if pat.search(h):
                return True, "\n".join(self.sections.get(h, [])).strip()
        for l in self.lines:
            m = re.match(r"^\s*\*\*([^*]+)\*\*\s*[:.]?\s*(.*)$", l)
            if m and pat.search(m.group(1)):
                return True, m.group(2).strip()
        return False, ""

    def statements_found(self) -> list[str]:
        return [k for k in STATEMENT_PATTERNS if self.statement(k)[0]]


def load_manuscript(path) -> Manuscript:
    return Manuscript(pathlib.Path(path).read_text(encoding="utf-8"))


def build_profile(ms: Manuscript) -> dict:
    return {
        "title": ms.title or NR,
        "abstract": ms.abstract or NR,
        "keywords": ms.keywords or NR,
        "research_question": NR,
        "methodology": NR,
        "main_results": NR,
        "contribution": NR,
        "key_references": NR,
        "article_type": NR,
        "counts": {
            "words_main_text": ms.word_count(False),
            "words_with_references": ms.word_count(True),
            "abstract_words": words(ms.abstract),
            "keywords": len(ms.keywords),
            "title_words": words(ms.title),
            "title_chars": len(ms.title),
            "figures": ms.figures,
            "tables": ms.tables,
            "highlights": len(ms.highlights),
        },
        "sections_found": ms.headings,
        "statements_found": ms.statements_found(),
        "generated_on": today(),
    }


# --------------------------------------------------------------------------------------
# Validação
# --------------------------------------------------------------------------------------

FORBIDDEN_KEY = re.compile(r"prob|chance|likelihood|acceptance_(rate|odds)", re.I)
PROBABILITY_TEXT = re.compile(
    r"\d+(?:[.,]\d+)?\s*%\s*(?:de\s+)?(?:chances?|probabilidade)"
    r"|(?:chances?|probabilidade|likelihood|probability|odds)\s+(?:de|of)\s+(?:ser\s+|being\s+)?(?:aceit|accept|publica|publish)"
    r"|acceptance\s+(?:chance|probability|likelihood|odds)"
    r"|\d+(?:[.,]\d+)?\s*%\s+(?:chance|likelihood|probability)", re.I)
GUARANTEE_TEXT = re.compile(r"garant\w*\s+(?:a\s+|de\s+)?(?:aceita|publica)|guarantee\w*\s+(?:of\s+)?(?:acceptance|publication)", re.I)
FIRST_CLAIM = re.compile(r"\b(o primeiro|a primeira|pela primeira vez|pioneir\w*|in[eé]dit\w*|the first (?:study|paper|article|analysis|to)|for the first time)\b", re.I)
GENERIC_PRAISE = re.compile(r"\b(prestigious|renowned|esteemed|world[- ]class|leading journal|top journal|prestigios[ao]|renomad[ao]|conceituad[ao])\b", re.I)


NEGATION = re.compile(r"\b(n[aã]o|nunca|nenhum[a]?|sem|jamais|never|not|no|without|nor)\b[^.;:]{0,40}$", re.I)


def claims(pattern: re.Pattern, text: str):
    """Ocorrências afirmativas do padrão (ignora as precedidas de negação, ex.: 'nunca estimar probabilidade…')."""
    for m in pattern.finditer(text):
        if not NEGATION.search(text[max(0, m.start() - 60):m.start()]):
            yield m


def _walk(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}.{k}", k, v
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")


def _no_probability(data, report):
    for where, key, value in _walk(data):
        if FORBIDDEN_KEY.search(key):
            report.error(where, "campo de probabilidade/chance de aceitação não é permitido (journal fit ≠ probabilidade)")
        if isinstance(value, str) and (any(claims(PROBABILITY_TEXT, value)) or any(claims(GUARANTEE_TEXT, value))):
            report.error(where, "texto contém probabilidade/garantia de aceitação")


def _date_age(date_str):
    try:
        return (_dt.date.today() - _dt.date.fromisoformat(date_str)).days
    except (TypeError, ValueError):
        return None


def validate(kind: str, path) -> srtool.Report:
    data = srtool.load_json(path)
    schema = {
        "profile": "manuscript-profile.schema.json", "candidates": "journal-candidates.schema.json",
        "recent": "recent-content.schema.json", "due-diligence": "due-diligence.schema.json",
        "requirements": "journal-requirements.schema.json", "fit": "journal-fit.schema.json",
        "compliance": "compliance.schema.json", "response": "response-matrix.schema.json",
        "target": "target-journal.schema.json",
    }[kind]
    r = srtool.validate_against(data, schema, f"{kind} {path}")
    if not isinstance(data, dict):
        return r
    _no_probability(data, r)
    if kind == "candidates":
        for i, c in enumerate(data.get("candidates", [])):
            a = c.get("aims_scope", {})
            if a.get("status") == "VERIFIED" and not all(a.get(k) for k in ("url", "excerpt", "checked_on")):
                r.error(f"$.candidates[{i}].aims_scope", "VERIFIED exige url, excerpt e checked_on")
    if kind == "fit":
        a = data.get("aims_scope", {})
        if a.get("status") == "VERIFIED" and not all(a.get(k) for k in ("url", "excerpt", "checked_on")):
            r.error("$.aims_scope", "VERIFIED exige url, excerpt e checked_on")
        for key, _ in DIMENSIONS:
            dim = (data.get("dimensions") or {}).get(key) or {}
            if dim.get("rating") in RATING_SCORE and not dim.get("evidence"):
                r.error(f"$.dimensions.{key}", f"classificação {dim.get('rating')} sem evidência; use INSUFFICIENT_EVIDENCE")
        if a.get("status") != "VERIFIED" and ((data.get("dimensions") or {}).get("topic_fit") or {}).get("rating") == "STRONG":
            r.warn("$.dimensions.topic_fit", "Topic Fit STRONG sem aims & scope verificado")
    if kind == "due-diligence":
        for name, item in (data.get("items") or {}).items():
            if item.get("status") == "CONFIRMED" and not item.get("evidence_url"):
                r.error(f"$.items.{name}", "CONFIRMED exige evidence_url")
        text = json.dumps(data, ensure_ascii=False).lower()
        if "predat" in text and len([a for a in data.get("alerts", []) if a.get("evidence")]) < 3:
            r.error("$", "rótulo 'predatório' exige ao menos 3 alertas com evidência (nunca por ausência de uma indexação)")
        if data.get("conclusion") == "SERIOUS_ALERTS" and not any(a.get("severity") == "high" for a in data.get("alerts", [])):
            r.error("$.conclusion", "SERIOUS_ALERTS exige ao menos um alerta de severidade high com evidência")
    if kind == "requirements":
        if data.get("synthetic"):
            r.warn("$", "requisitos SINTÉTICOS (demonstração/teste) — não usar para submissão real")
        for i, rule in enumerate(data.get("rules", [])):
            if rule.get("status") == "VERIFIED":
                for k in ("excerpt", "source_url", "accessed_on"):
                    if not rule.get(k):
                        r.error(f"$.rules[{i}]", f"regra VERIFIED sem '{k}'")
                if data.get("access_status") == "blocked":
                    r.error(f"$.rules[{i}]", "access_status=blocked: nenhuma regra pode estar VERIFIED")
            if rule.get("check") not in ("manual", "required_section", "required_statement") and rule.get("value") is None and rule.get("status") == "VERIFIED":
                r.error(f"$.rules[{i}]", f"check '{rule.get('check')}' exige 'value'")
    if kind == "response":
        for i, c in enumerate(data.get("comments", [])):
            if c.get("decision") in ("NOT_ACCEPTED", "PARTIALLY_ACCEPTED") and not c.get("justification"):
                r.error(f"$.comments[{i}]", f"{c.get('decision')} exige justificativa científica")
            if c.get("results_changed") and not re.search(r"corre[cç]|error|erro", c.get("results_change_reason", ""), re.I):
                r.error(f"$.comments[{i}]", "resultado alterado só é admissível para correção de erro, declarada em results_change_reason")
    if kind == "recent":
        w = data.get("window", {})
        for i, a in enumerate(data.get("articles", [])):
            y = a.get("year")
            if isinstance(y, int) and not (w.get("from_year", 0) <= y <= w.get("to_year", 9999)):
                r.error(f"$.articles[{i}]", f"ano {y} fora da janela {w}")
            if srtool.is_nr(a.get("doi", "")) and srtool.is_nr(a.get("url", "")):
                r.error(f"$.articles[{i}]", "artigo sem DOI nem URL não é rastreável")
    return r


# --------------------------------------------------------------------------------------
# Journal fit
# --------------------------------------------------------------------------------------


def fit_index(fit: dict) -> dict:
    num = den = 0.0
    assessed = 0
    for key, _ in DIMENSIONS:
        dim = (fit.get("dimensions") or {}).get(key) or {}
        rating = dim.get("rating")
        if rating in RATING_SCORE:
            w = float(dim.get("weight", 1))
            num += w * RATING_SCORE[rating]
            den += w * 2
            assessed += 1
    value = round(100 * num / den) if den else None
    return {"index": value, "assessed": assessed, "total": len(DIMENSIONS),
            "formula": "100 × Σ(peso × nota) / Σ(peso × 2), nota: STRONG=2, MODERATE=1, WEAK=0; "
                       "dimensões INSUFFICIENT_EVIDENCE excluídas e reportadas como cobertura"}


def _nv(value, short: bool = False) -> str:
    if value in (None, "", []):
        return NOT_VERIFIED
    if isinstance(value, dict):
        if value.get("status") in ("NOT_VERIFIED", NOT_VERIFIED):
            return NOT_VERIFIED + (f" — {value['note']}" if value.get("note") and not short else "")
        parts = [str(value.get("value", ""))]
        if value.get("source"):
            parts.append(f"(fonte: {value['source']}")
            parts.append(f"{value.get('checked_on', 'data NR')})")
        return " ".join(p for p in parts if p).strip() or NOT_VERIFIED
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value)


def render_fit_report(fit: dict) -> str:
    idx = fit_index(fit)
    a = fit.get("aims_scope", {})
    aims = (f"\"{a.get('excerpt')}\" — {a.get('url')} (consultado em {a.get('checked_on')})"
            if a.get("status") == "VERIFIED" else NOT_VERIFIED)
    L = [f"# Journal Fit Report — {fit.get('journal')}", "",
         f"> {FIT_DISCLAIMER}", "",
         "| Campo | Conteúdo |", "|---|---|",
         f"| JOURNAL | {fit.get('journal')} |",
         f"| PUBLISHER | {_nv(fit.get('publisher'))} |",
         f"| AIMS & SCOPE | {aims} |"]
    for key, label in DIMENSIONS:
        d = (fit.get("dimensions") or {}).get(key) or {}
        L.append(f"| {label} | **{d.get('rating', 'INSUFFICIENT_EVIDENCE')}** — {d.get('justification', '')} |")
    L += [f"| OPEN ACCESS | {_nv(fit.get('open_access'))} |",
          f"| APC | {_nv(fit.get('apc'))} |",
          f"| INDEXING | {_nv(fit.get('indexing'))} |",
          f"| REVIEW TIME IF PUBLISHED | {_nv(fit.get('review_time'))} |",
          f"| PUBLICATION TIME IF PUBLISHED | {_nv(fit.get('publication_time'))} |",
          f"| KEY REQUIREMENTS | {_nv(fit.get('key_requirements'))} |",
          f"| SIMILAR ARTICLES | {_nv(fit.get('similar_articles'))} |",
          f"| RISKS | {_nv(fit.get('risks'))} |",
          f"| DUE DILIGENCE | {_nv(fit.get('due_diligence_conclusion'))} |",
          f"| DATE VERIFIED | {fit.get('date_verified')} |", "",
          "## Índice de aderência", "",
          f"- Journal Fit Index: **{idx['index'] if idx['index'] is not None else NOT_VERIFIED}** / 100 "
          f"(cobertura: {idx['assessed']}/{idx['total']} dimensões com evidência)",
          f"- Fórmula: {idx['formula']}",
          f"- {FIT_DISCLAIMER}", "", "## EVIDENCE", ""]
    for key, label in DIMENSIONS:
        d = (fit.get("dimensions") or {}).get(key) or {}
        for ev in d.get("evidence", []):
            ref = ev.get("doi") or ev.get("url") or ""
            exc = f" — \"{ev['excerpt']}\"" if ev.get("excerpt") else ""
            L.append(f"- [{label}] {ev.get('source')} {ref}{exc} (verificado em {ev.get('checked_on')})")
        if not d.get("evidence"):
            L.append(f"- [{label}] sem evidência registrada → INSUFFICIENT_EVIDENCE")
    return "\n".join(L) + "\n"


def render_compare(fits: list[dict]) -> str:
    L = ["## Comparação de periódicos candidatos", "", f"> {FIT_DISCLAIMER} Métricas bibliométricas não substituem a aderência.", "",
         "| Periódico | Índice (cobertura) | Topic | Method | Contribution | Empirical | Audience | Recent | Article type | OA | APC | Indexação | Prazos publicados | Due diligence | Verificado em |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for f in fits:
        idx = fit_index(f)
        dims = [((f.get("dimensions") or {}).get(k) or {}).get("rating", "INSUFFICIENT_EVIDENCE") for k, _ in DIMENSIONS]
        dims = [d.replace("INSUFFICIENT_EVIDENCE", "INSUF.") for d in dims]
        times = f"{_nv(f.get('review_time'), True)} / {_nv(f.get('publication_time'), True)}"
        rows.append((idx["index"] if idx["index"] is not None else -1,
                     f"| {f.get('journal')} | {idx['index'] if idx['index'] is not None else NOT_VERIFIED} ({idx['assessed']}/7) | "
                     + " | ".join(dims) + f" | {_nv(f.get('open_access'), True)} | {_nv(f.get('apc'), True)} | {_nv(f.get('indexing'), True)} | {times} | "
                     f"{_nv(f.get('due_diligence_conclusion'))} | {f.get('date_verified')} |"))
    L += [r for _, r in sorted(rows, key=lambda x: -x[0])]
    L += ["", "_Ordenado pelo índice de aderência; a decisão final considera também restrições do autor (APC, OA, indexação exigida, prazo)._"]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------------------
# Compliance
# --------------------------------------------------------------------------------------


def _source(rule: dict, req: dict) -> str:
    url = rule.get("source_url") or (req.get("sources") or [{}])[0].get("url", NR)
    acc = rule.get("accessed_on") or req.get("accessed_on", NR)
    exc = f' — "{rule["excerpt"]}"' if rule.get("excerpt") else ""
    syn = " [REQUISITO SINTÉTICO]" if req.get("synthetic") else ""
    return f"{url} (consultado em {acc}){exc}{syn}"


def check_compliance(ms: Manuscript, req: dict, manual: dict | None = None) -> list[dict]:
    manual = manual or {}
    items = []
    for rule in req.get("rules", []):
        rid, check, val = rule["rule_id"], rule.get("check"), rule.get("value")
        item = {"rule_id": rid, "category": rule.get("category", ""), "requirement": rule.get("requirement", ""),
                "source": _source(rule, req), "status": "UNABLE_TO_VERIFY", "current_state": NR, "gap": "", "action": ""}

        def set_(status, current, gap="", action="", note=""):
            item.update(status=status, current_state=current, gap=gap, action=action)
            if note:
                item["integrity_note"] = note

        if rule.get("applicable") is False:
            set_("NOT_APPLICABLE", "regra não se aplica a este tipo de manuscrito", "", "")
        elif rule.get("status") != "VERIFIED":
            set_("UNABLE_TO_VERIFY", f"regra com status {rule.get('status')} — não confirmada na fonte oficial atual",
                 "", "Consultar o guia oficial do periódico e registrar trecho, URL e data (journal-requirements).")
        elif check == "max_words":
            a, b = ms.word_count(False), ms.word_count(True)
            scope = rule.get("count_scope", "unspecified")
            count = a if scope == "main_text_excluding_references" else b if scope == "all_text" else None
            note = "Reduzir sem remover resultados, limitações ou análises de robustez de forma seletiva; mover detalhes para material suplementar."
            if count is not None:
                if count <= val:
                    set_("COMPLIANT", f"{count} palavras ({scope})")
                else:
                    set_("ACTION_REQUIRED", f"{count} palavras ({scope})", f"excede em {count - val} palavras",
                         f"Reduzir para ≤ {val} palavras.", note)
            elif a <= val and b <= val:
                set_("COMPLIANT", f"{a} palavras sem referências; {b} com referências")
            elif a > val and b > val:
                set_("ACTION_REQUIRED", f"{a} palavras sem referências; {b} com referências", f"excede em ≥ {a - val} palavras",
                     f"Reduzir para ≤ {val} palavras.", note)
            else:
                set_("UNABLE_TO_VERIFY", f"{a} palavras sem referências; {b} com referências",
                     "o guia não define se referências contam e o resultado depende disso",
                     "Confirmar no guia/editorial office o que entra na contagem.")
        elif check == "max_abstract_words":
            n = words(ms.abstract)
            if not ms.abstract:
                set_("ACTION_REQUIRED", "seção Abstract/Resumo não encontrada", "abstract ausente", "Incluir abstract.")
            elif n <= val:
                set_("COMPLIANT", f"{n} palavras")
            else:
                set_("ACTION_REQUIRED", f"{n} palavras", f"excede em {n - val}", f"Condensar para ≤ {val} palavras.",
                     "Não exagerar conclusões nem trocar associação por causalidade ao condensar.")
        elif check == "keywords_range":
            lo, hi = val
            n = len(ms.keywords)
            if lo <= n <= hi:
                set_("COMPLIANT", f"{n} keywords")
            else:
                set_("ACTION_REQUIRED", f"{n} keywords", f"exigido entre {lo} e {hi}", f"Ajustar para {lo}–{hi} keywords.")
        elif check in ("max_title_words", "max_title_chars"):
            n = words(ms.title) if check == "max_title_words" else len(ms.title)
            unit = "palavras" if check == "max_title_words" else "caracteres"
            if not ms.title:
                set_("ACTION_REQUIRED", "título não encontrado (use '# Título')", "título ausente", "Incluir título.")
            elif n <= val:
                set_("COMPLIANT", f"{n} {unit}")
            else:
                set_("ACTION_REQUIRED", f"{n} {unit}", f"excede em {n - val}", f"Encurtar título para ≤ {val} {unit}.")
        elif check in ("max_figures", "max_tables"):
            n = ms.figures if check == "max_figures" else ms.tables
            kind = "figuras" if check == "max_figures" else "tabelas"
            if n <= val:
                set_("COMPLIANT", f"{n} {kind}")
            else:
                set_("ACTION_REQUIRED", f"{n} {kind}", f"excede em {n - val}", f"Reduzir para ≤ {val} {kind} (ex.: mover para suplementar).",
                     "Não omitir seletivamente resultados desfavoráveis; o material movido continua acessível.")
        elif check == "required_section":
            pat = rule.get("section_pattern") or re.escape(rule.get("requirement", ""))
            found = [h for h in ms.headings if re.search(pat, h, re.I)]
            if found:
                set_("COMPLIANT", f"seção encontrada: {found[0]}")
            else:
                set_("ACTION_REQUIRED", "seção não encontrada", f"falta seção que corresponda a /{pat}/", "Incluir a seção exigida.")
        elif check == "required_statement":
            kind = rule.get("statement_kind")
            ok, content = ms.statement(kind) if kind in STATEMENT_PATTERNS else (False, "")
            if not ok:
                set_("ACTION_REQUIRED", f"declaração '{kind}' não encontrada", "declaração ausente",
                     "Incluir a declaração com informação fornecida pelos autores.", "Não inventar informações dos autores.")
            elif not content or PLACEHOLDER.search(content):
                set_("ACTION_REQUIRED", f"declaração '{kind}' presente mas incompleta/placeholder", "conteúdo pendente",
                     "Autores devem preencher.", "Não inventar informações dos autores.")
            else:
                set_("COMPLIANT", f"declaração '{kind}' presente")
        elif check == "highlights":
            hl = ms.highlights
            spec = val or {}
            problems = []
            if spec.get("required") and not hl:
                problems.append("highlights ausentes")
            if hl and spec.get("min_items") and len(hl) < spec["min_items"]:
                problems.append(f"{len(hl)} itens (< {spec['min_items']})")
            if hl and spec.get("max_items") and len(hl) > spec["max_items"]:
                problems.append(f"{len(hl)} itens (> {spec['max_items']})")
            if spec.get("max_chars_each"):
                longs = [i + 1 for i, h in enumerate(hl) if len(h) > spec["max_chars_each"]]
                if longs:
                    problems.append(f"itens {longs} com mais de {spec['max_chars_each']} caracteres")
            if problems:
                set_("ACTION_REQUIRED", f"{len(hl)} highlights", "; ".join(problems), "Ajustar highlights sem introduzir números ou afirmações ausentes do texto.",
                     "Highlights não podem exagerar resultados.")
            elif not hl and not spec.get("required"):
                set_("NOT_APPLICABLE", "highlights não exigidos e ausentes")
            else:
                set_("COMPLIANT", f"{len(hl)} highlights")
        else:  # manual
            set_("UNABLE_TO_VERIFY", "requer verificação manual", "", "Conferir manualmente e registrar confirmação.")
        if rid in manual and item["status"] == "UNABLE_TO_VERIFY":
            m = manual[rid]
            item["status"] = m.get("status", "UNABLE_TO_VERIFY")
            item["current_state"] = f"confirmação manual por {m.get('confirmed_by', NR)} em {m.get('confirmed_on', NR)}: {m.get('note', '')}"
        items.append(item)
    return items


def render_compliance(items: list[dict], journal: str, target_mode: bool) -> str:
    counts = {}
    for it in items:
        counts[it["status"]] = counts.get(it["status"], 0) + 1
    L = [f"# Compliance — manuscrito × {journal}", "",
         f"Gerado em {today()}." + (" **Target Journal Mode ativo.**" if target_mode else ""), "",
         "| Status | n |", "|---|---|"]
    for s in ("COMPLIANT", "ACTION_REQUIRED", "NOT_APPLICABLE", "UNABLE_TO_VERIFY"):
        L.append(f"| {s.replace('_', ' ')} | {counts.get(s, 0)} |")
    L += ["", "## Itens", "", "| Regra | Categoria | Status | Estado atual | Fonte |", "|---|---|---|---|---|"]
    for it in items:
        L.append(f"| {it['rule_id']} | {it['category']} | {it['status'].replace('_', ' ')} | {it['current_state']} | {it['source']} |")
    acts = [it for it in items if it["status"] == "ACTION_REQUIRED"]
    if acts:
        L += ["", "## ACTION REQUIRED — detalhamento", ""]
        for it in acts:
            L += [f"### {it['rule_id']} — {it['category']}",
                  f"1. **Exigência:** {it['requirement']}",
                  f"2. **Estado atual:** {it['current_state']}",
                  f"3. **Diferença:** {it['gap']}",
                  f"4. **O que fazer:** {it['action']}",
                  f"5. **Fonte:** {it['source']}"]
            if it.get("integrity_note"):
                L.append(f"   - _Integridade:_ {it['integrity_note']}")
            L.append("")
    L.append("_Nenhuma alteração científica é feita automaticamente para satisfazer preferência editorial._")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------------------
# Lint de linguagem
# --------------------------------------------------------------------------------------


def lint_text(text: str) -> list[dict]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for code, pat, sev, msg in (
            ("PROBABILIDADE-DE-ACEITACAO", PROBABILITY_TEXT, "ERRO", "probabilidade/chance de aceitação sem base publicada"),
            ("GARANTIA-DE-PUBLICACAO", GUARANTEE_TEXT, "ERRO", "promessa/garantia de aceitação ou publicação"),
            ("PRIMEIRO-A-SEM-VERIFICACAO", FIRST_CLAIM, "AVISO", "'primeiro/inédito' exige busca documentada que sustente"),
            ("ELOGIO-GENERICO", GENERIC_PRAISE, "AVISO", "elogio genérico ao periódico; prefira aderência concreta ao aims & scope"),
        ):
            m = next(claims(pat, line), None)
            if m:
                out.append({"line": i, "code": code, "severity": sev, "match": m.group(0), "message": msg})
    return out


# --------------------------------------------------------------------------------------
# Checklist, resposta a revisores, Target Journal Mode
# --------------------------------------------------------------------------------------


def render_checklist(req: dict) -> str:
    L = [f"# Checklist de submissão — {req.get('journal')}", "",
         f"Regras consultadas em {req.get('accessed_on')} ({', '.join(s['url'] for s in req.get('sources', []))})."
         + (" **REQUISITOS SINTÉTICOS — só para demonstração.**" if req.get("synthetic") else ""),
         "Reconsulte o guia oficial antes de submeter.", "",
         "| # | Item | Exigência | Arquivo | Status da regra | Feito? |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(req.get("rules", []), 1):
        if r.get("applicable") is False:
            continue
        L.append(f"| {i} | {r.get('category')} | {r.get('requirement')} | {r.get('file_required', '—')} | {r.get('status')} | ☐ |")
    L += ["", "Itens sempre verificados: título/autores idênticos em todos os arquivos · ORCID dos autores (fornecido por eles) · "
          "declarações preenchidas pelos autores · figuras/tabelas citadas no texto · referências auditadas (`bibliography-audit`)."]
    return "\n".join(L) + "\n"


def render_response(matrix: dict) -> str:
    L = [f"# Resposta aos revisores — {matrix.get('journal')} — manuscrito {matrix.get('manuscript_id')} (rodada {matrix.get('round')})", "",
         "## Matriz", "",
         "| ID | Revisor | Comentário | Interpretação | Decisão | Ação | Alteração no manuscrito | Local |", "|---|---|---|---|---|---|---|---|"]
    counts = {}
    for c in matrix.get("comments", []):
        counts[c["decision"]] = counts.get(c["decision"], 0) + 1
        esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")  # noqa: E731
        L.append(f"| {c['id']} | {c['reviewer']} | {esc(c['comment'])} | {esc(c['interpretation'])} | {c['decision'].replace('_', ' ')} | "
                 f"{esc(c['action'])} | {esc(c['manuscript_change'])} | {esc(c['location'])} |")
    L += ["", "Resumo: " + ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in sorted(counts.items())), "",
          "## Carta de resposta", "", "Dear Editor,", "",
          "We thank the editor and the reviewers for their careful reading of the manuscript. Below we respond point by point; "
          "changes are indicated with their location in the revised manuscript.", ""]
    for c in matrix.get("comments", []):
        L += [f"**{c['id']} ({c['reviewer']}).** _{c['comment']}_", "", f"**Response.** {c['response']}"]
        if c.get("justification"):
            L.append(f"_Justification._ {c['justification']}")
        L += [f"_Change:_ {c['manuscript_change']} — _Location:_ {c['location']}", ""]
    if any(c.get("results_changed") for c in matrix.get("comments", [])):
        L.append("> Nota: resultados foram alterados apenas para correção de erro, conforme declarado nos itens correspondentes.")
    return "\n".join(L) + "\n"


def target_set(pub_dir: pathlib.Path, slug: str, article_type: str | None) -> dict:
    req_file = pub_dir / "journals" / slug / "requirements.json"
    if not req_file.exists():
        raise SystemExit(f"requirements.json não encontrado para '{slug}' ({req_file}); rode journal-requirements antes.")
    req = srtool.load_json(req_file)
    data = {"active": True, "journal": req.get("journal", slug), "slug": slug, "activated_on": today(),
            "requirements_file": str(req_file.relative_to(pub_dir)), "article_type": article_type or req.get("article_type", NR),
            "integrity_limits": INTEGRITY_LIMITS}
    (pub_dir / "target-journal.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def read_target(pub_dir: pathlib.Path) -> dict | None:
    f = pub_dir / "target-journal.json"
    if not f.exists():
        return None
    d = srtool.load_json(f)
    return d if d.get("active") else None


# --------------------------------------------------------------------------------------
# Auditoria pré-submissão
# --------------------------------------------------------------------------------------


def presubmit(research: pathlib.Path, slug: str | None, max_age: int) -> tuple[str, str]:
    pub = research / "publication"
    tgt = read_target(pub)
    slug = slug or (tgt or {}).get("slug")
    steps: list[tuple[str, list[str], list[str]]] = []  # (etapa, pendências, observações)
    if not slug:
        return "ACTION REQUIRED", "# Auditoria pré-submissão\n\nNenhum periódico-alvo definido (use `pubtool target set` ou `--journal`).\n"
    jdir = pub / "journals" / slug
    manuscript = research / "manuscript" / "manuscript.md"
    sub_dir = pub / "submission" / slug

    # 1. Journal requirements
    pend, obs = [], []
    req_file = jdir / "requirements.json"
    req = None
    if not req_file.exists():
        pend.append(f"requirements.json ausente para '{slug}' — executar journal-requirements na fonte oficial.")
    else:
        req = srtool.load_json(req_file)
        rv = validate("requirements", req_file)
        pend += [f"requirements.json inválido: {e}" for e in rv.errors]
        if req.get("synthetic"):
            pend.append("requisitos SINTÉTICOS (demonstração) — substituir pelas regras oficiais do periódico.")
        if req.get("access_status") != "ok":
            pend.append(f"acesso ao guia oficial: {req.get('access_status')} — reconsultar a fonte oficial.")
        age = _date_age(req.get("accessed_on"))
        if age is None or age > max_age:
            pend.append(f"regras consultadas há {age} dias (> {max_age}) — reconsultar o guia oficial antes de submeter.")
        nv = [r["rule_id"] for r in req.get("rules", []) if r.get("status") != "VERIFIED" and r.get("applicable") is not False]
        if nv:
            pend.append(f"regras não verificadas na fonte oficial: {', '.join(nv)}.")
        obs.append(f"fonte: {', '.join(s['url'] for s in req.get('sources', []))} (consulta: {req.get('accessed_on')})")
    steps.append(("1. Journal requirements", pend, obs))

    # 2. Manuscript compliance
    pend, obs = [], []
    if not manuscript.exists():
        pend.append("manuscrito research/manuscript/manuscript.md não encontrado.")
        ms = None
    else:
        ms = load_manuscript(manuscript)
        if req:
            manual_file = pub / "compliance" / f"{slug}-manual.json"
            manual = srtool.load_json(manual_file) if manual_file.exists() else {}
            items = check_compliance(ms, req, manual)
            for it in items:
                if it["status"] == "ACTION_REQUIRED":
                    pend.append(f"{it['rule_id']} ({it['category']}): {it['gap'] or it['current_state']} → {it['action']}")
                elif it["status"] == "UNABLE_TO_VERIFY":
                    pend.append(f"{it['rule_id']} ({it['category']}): não verificável automaticamente — confirmar e registrar em compliance/{slug}-manual.json.")
            obs.append(f"{sum(1 for i in items if i['status'] == 'COMPLIANT')} regra(s) COMPLIANT de {len(items)}")
    steps.append(("2. Manuscript compliance", pend, obs))

    # 3. Citation audit
    pend, obs = [], []
    ca = research / "audit" / "citation-audit.json"
    if not ca.exists():
        pend.append("auditoria de citações ausente (audit/citation-audit.json) — executar citation-audit.")
    else:
        audit = srtool.load_json(ca)
        r = srtool.validate_audit(ca)
        pend += [f"citation-audit inválido: {e}" for e in r.errors]
        for c in audit.get("claims", []):
            if c.get("classification") in ("NÃO SUPORTADA", "NÃO VERIFICÁVEL"):
                pend.append(f"{c['claim_id']} ({c.get('location')}): {c['classification']} — resolver antes de submeter.")
        obs.append(f"{len(audit.get('claims', []))} afirmação(ões) auditada(s) em {audit.get('audited_on')}")
    if ms is not None:
        ledger_file = research / "ledger" / "evidence.jsonl"
        ledger = srtool.load_ledger_index(ledger_file) if ledger_file.exists() else None
        sources = srtool._load_sources_index(research / "sources" / "sources.json") if (research / "sources" / "sources.json").exists() else None
        for f in srtool.scan_manuscript(manuscript.read_text(encoding="utf-8"), ledger, sources):
            if f["severity"] in ("CRÍTICO", "MAIOR"):
                pend.append(f"scan {f['code']} em {f['paragraph']}: {f['message']}")
    steps.append(("3. Citation audit", pend, obs))

    # 4. Reference audit
    pend, obs = [], []
    src = research / "sources" / "sources.json"
    if not src.exists():
        pend.append("sources.json ausente — executar bibliography-audit.")
    else:
        data = srtool.load_json(src)
        for s in data.get("sources", []):
            st = (s.get("metadata_verification") or {}).get("status")
            if st == "CONTRADICTED":
                pend.append(f"{s['source_id']}: metadados CONTRADICTED (referência possivelmente inventada/errada).")
            elif st in ("UNVERIFIED", "NOT_REPORTED", "PARTIALLY_VERIFIED"):
                pend.append(f"{s['source_id']}: metadados {st} — conferir DOI/metadados em fonte autoritativa (bibliography-audit / srtool refs-check).")
        obs.append(f"{len(data.get('sources', []))} fonte(s) no registro")
    steps.append(("4. Reference audit", pend, obs))

    # 5-6. Declarações
    required_kinds = {"funding", "competing_interests", "data_availability"}
    if req:
        required_kinds |= {r.get("statement_kind") for r in req.get("rules", [])
                           if r.get("check") == "required_statement" and r.get("applicable") is not False and r.get("statement_kind")}
    for title, kinds in (("5. Data/code availability", {"data_availability", "code_availability"}),
                         ("6. Ethical declarations", {"funding", "competing_interests", "credit", "ethics", "consent", "ai_use"})):
        pend, obs = [], []
        for k in sorted(kinds & required_kinds):
            if ms is None:
                continue
            ok, content = ms.statement(k)
            if not ok:
                pend.append(f"declaração '{k}' ausente no manuscrito.")
            elif not content or PLACEHOLDER.search(content):
                pend.append(f"declaração '{k}' com placeholder — autores devem preencher (não inventar).")
            else:
                obs.append(f"'{k}' presente")
        steps.append((title, pend, obs))

    # 7. Files required
    pend, obs = [], []
    files = [r["file_required"] for r in (req or {}).get("rules", []) if r.get("file_required") and r.get("applicable") is not False]
    for f in files:
        if not (sub_dir / f).exists():
            pend.append(f"arquivo exigido ausente: submission/{slug}/{f}")
        else:
            obs.append(f"{f} presente")
    steps.append(("7. Files required", pend, obs))

    # 8. Submission checklist (linguagem, placeholders)
    pend, obs = [], []
    texts = list(sub_dir.glob("*.md")) if sub_dir.exists() else []
    for f in texts + ([pub / "strategy.md"] if (pub / "strategy.md").exists() else []):
        body = f.read_text(encoding="utf-8")
        for fnd in lint_text(body):
            if fnd["severity"] == "ERRO":
                pend.append(f"{f.name}:{fnd['line']} {fnd['code']} ('{fnd['match']}')")
            else:
                pend.append(f"{f.name}:{fnd['line']} {fnd['code']} ('{fnd['match']}') — confirmar ou remover")
        if f.parent == sub_dir and PLACEHOLDER.search(body):
            pend.append(f"{f.name}: contém placeholders a preencher pelos autores")
    if not texts:
        pend.append(f"pasta de submissão vazia ou ausente (submission/{slug}/) — executar submission-preparation.")
    steps.append(("8. Submission checklist", pend, obs))

    total = sum(len(p) for _, p, _ in steps)
    verdict = "READY TO SUBMIT" if total == 0 else "ACTION REQUIRED"
    L = [f"# Auditoria pré-submissão — {(req or {}).get('journal', slug)}", "",
         f"Data: {today()} · Target Journal Mode: {'ativo' if tgt and tgt.get('slug') == slug else 'inativo'}", "",
         f"## Resultado: **{verdict}**" + (f" ({total} pendência(s))" if total else ""), "",
         "| Etapa | Pendências |", "|---|---|"]
    L += [f"| {name} | {len(p)} |" for name, p, _ in steps]
    for name, p, o in steps:
        L += ["", f"## {name}", ""]
        L += [f"- [ ] {x}" for x in p] or ["- ✔ sem pendências"]
        L += [f"- _obs._ {x}" for x in o]
    L += ["", "_READY TO SUBMIT exige zero pendências e regras reconsultadas na fonte oficial. "
          "Nenhuma pendência pode ser resolvida alterando resultados ou inventando dados dos autores._"]
    return verdict, "\n".join(L) + "\n"


# --------------------------------------------------------------------------------------
# init / venues
# --------------------------------------------------------------------------------------


def init(research: pathlib.Path) -> list[str]:
    pub = research / "publication"
    created = []
    for d in ("journals", "compliance", "submission", "peer-review", "resubmission"):
        p = pub / d
        if not p.exists():
            p.mkdir(parents=True)
            created.append(str(p))
    return created


def venues(paths) -> list[dict]:
    agg = {}
    for p in paths:
        for s in srtool.load_json(p).get("sources", []):
            if s.get("source_type") != "peer_reviewed_article":
                continue
            name = s.get("container", NR)
            key = srtool.norm_title(name)
            e = agg.setdefault(key, {"venue": name, "count": 0, "source_ids": [], "years": [],
                                     "statuses": set()})
            e["count"] += 1
            e["source_ids"].append(s.get("source_id"))
            e["years"].append(s.get("year"))
            e["statuses"].add((s.get("metadata_verification") or {}).get("status", NR))
    out = sorted(agg.values(), key=lambda x: -x["count"])
    for e in out:
        e["statuses"] = sorted(e["statuses"])
    return out


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _emit(text: str, out: str | None):
    if out:
        pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(out).write_text(text, encoding="utf-8")
        print(f"salvo em {out}")
    else:
        sys.stdout.write(text)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="pubtool", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("research")
    s = sub.add_parser("profile"); s.add_argument("manuscript"); s.add_argument("--out")
    s = sub.add_parser("venues"); s.add_argument("sources", nargs="+")
    s = sub.add_parser("validate"); s.add_argument("kind", choices=["profile", "candidates", "recent", "due-diligence", "requirements", "fit", "compliance", "response", "target"]); s.add_argument("file")
    s = sub.add_parser("fit-report"); s.add_argument("fit"); s.add_argument("--out")
    s = sub.add_parser("compare"); s.add_argument("fits", nargs="+"); s.add_argument("--out")
    s = sub.add_parser("check-compliance"); s.add_argument("manuscript"); s.add_argument("requirements"); s.add_argument("--manual"); s.add_argument("--out", help="prefixo de saída (gera .json e .md)")
    s = sub.add_parser("checklist"); s.add_argument("requirements"); s.add_argument("--out")
    s = sub.add_parser("freshness"); s.add_argument("file"); s.add_argument("--max-age-days", type=int, default=30)
    s = sub.add_parser("target"); s.add_argument("action", choices=["set", "show", "clear"]); s.add_argument("publication_dir")
    s.add_argument("--journal"); s.add_argument("--article-type")
    s = sub.add_parser("lint"); s.add_argument("files", nargs="+")
    s = sub.add_parser("response-letter"); s.add_argument("matrix"); s.add_argument("--out")
    s = sub.add_parser("presubmit"); s.add_argument("research"); s.add_argument("--journal"); s.add_argument("--max-age-days", type=int, default=30); s.add_argument("--out")
    a = p.parse_args(argv)

    if a.cmd == "init":
        print("\n".join(init(pathlib.Path(a.research))) or "estrutura já existia")
        return 0
    if a.cmd == "profile":
        _emit(json.dumps(build_profile(load_manuscript(a.manuscript)), ensure_ascii=False, indent=2) + "\n", a.out)
        return 0
    if a.cmd == "venues":
        rows = venues(a.sources)
        print("| Periódico | nº de fontes | source_ids | anos | status dos metadados |\n|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['venue']} | {r['count']} | {', '.join(r['source_ids'])} | {', '.join(str(y) for y in r['years'])} | {', '.join(r['statuses'])} |")
        print("\n_Indica onde a literatura usada foi publicada — ponto de partida, não prova de aderência._")
        return 0
    if a.cmd == "validate":
        r = validate(a.kind, a.file)
        print(r.render())
        return 0 if r.ok else 1
    if a.cmd == "fit-report":
        _emit(render_fit_report(srtool.load_json(a.fit)), a.out)
        return 0
    if a.cmd == "compare":
        _emit(render_compare([srtool.load_json(f) for f in a.fits]), a.out)
        return 0
    if a.cmd == "check-compliance":
        req = srtool.load_json(a.requirements)
        manual = srtool.load_json(a.manual) if a.manual else None
        items = check_compliance(load_manuscript(a.manuscript), req, manual)
        pub_dir = pathlib.Path(a.requirements).resolve().parent.parent.parent
        tgt = read_target(pub_dir) if (pub_dir / "target-journal.json").exists() else None
        if tgt and tgt.get("slug") != pathlib.Path(a.requirements).resolve().parent.name:
            tgt = None  # modo ativo para outro periódico
        report = {"journal": req.get("journal"), "manuscript": a.manuscript, "requirements_file": a.requirements,
                  "generated_on": today(), "target_journal_mode": bool(tgt), "items": items}
        md = render_compliance(items, req.get("journal", ""), bool(tgt))
        if a.out:
            _emit(json.dumps(report, ensure_ascii=False, indent=2) + "\n", a.out + ".json")
            _emit(md, a.out + ".md")
        else:
            sys.stdout.write(md)
        return 1 if any(i["status"] == "ACTION_REQUIRED" for i in items) else 0
    if a.cmd == "checklist":
        _emit(render_checklist(srtool.load_json(a.requirements)), a.out)
        return 0
    if a.cmd == "freshness":
        d = srtool.load_json(a.file)
        date = d.get("accessed_on") or d.get("checked_on")
        age = _date_age(date)
        ok = age is not None and age <= a.max_age_days
        print(f"{a.file}: consultado em {date} ({age} dias) — {'OK' if ok else 'DESATUALIZADO: reconsultar a fonte oficial'}")
        return 0 if ok else 1
    if a.cmd == "target":
        pub = pathlib.Path(a.publication_dir)
        if a.action == "set":
            if not a.journal:
                raise SystemExit("--journal <slug> é obrigatório")
            d = target_set(pub, a.journal, a.article_type)
            print(f"Target Journal Mode ATIVO: {d['journal']} ({d['slug']}). Limites de integridade:")
            print("\n".join(f"  - {x}" for x in d["integrity_limits"]))
        elif a.action == "show":
            d = read_target(pub)
            print(json.dumps(d, ensure_ascii=False, indent=2) if d else "Target Journal Mode inativo.")
        else:
            f = pub / "target-journal.json"
            if f.exists():
                d = srtool.load_json(f)
                d["active"] = False
                f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("Target Journal Mode desativado.")
        return 0
    if a.cmd == "lint":
        bad = False
        for f in a.files:
            for fnd in lint_text(pathlib.Path(f).read_text(encoding="utf-8")):
                print(f"{f}:{fnd['line']}: {fnd['severity']} {fnd['code']} — '{fnd['match']}': {fnd['message']}")
                bad |= fnd["severity"] == "ERRO"
        return 1 if bad else 0
    if a.cmd == "response-letter":
        r = validate("response", a.matrix)
        if not r.ok:
            print(r.render())
            return 1
        _emit(render_response(srtool.load_json(a.matrix)), a.out)
        return 0
    if a.cmd == "presubmit":
        verdict, text = presubmit(pathlib.Path(a.research), a.journal, a.max_age_days)
        _emit(text, a.out)
        print(f"Resultado: {verdict}")
        return 0 if verdict == "READY TO SUBMIT" else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
