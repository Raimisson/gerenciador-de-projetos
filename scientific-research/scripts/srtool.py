#!/usr/bin/env python3
"""srtool — utilitário do plugin Scientific Research (somente biblioteca padrão).

Subcomandos:
  init <dir>                          cria a estrutura research/ de um projeto
  validate <kind> <path> [...]        valida sources | extraction | ledger | searchlog | audit | project
  matrix <dir|arquivos> ...           gera matriz de evidências (md | csv | json)
  doi-check <doi> [...]               confere DOI e metadados (Crossref / doi.org)
  refs-check <sources.json>           confere todas as referências de sources.json
  dedupe <sources.json|records.json>  aponta duplicatas por DOI e título+ano
  scan <manuscrito.md> [...]          números sem fonte, causalidade indevida, generalização...
  trace <E-0001|P-001> [...]          cadeia de proveniência fonte → evidência → parágrafo
  format <sources.json> --style ...   referências ABNT | APA | Chicago | BibTeX (só verificadas)
  prisma <search-log.json>            fluxo inspirado em PRISMA + checagem aritmética
  search-openalex "<query>"           busca na API pública do OpenAlex
  chase backward|forward|similar <doi> citation chasing via OpenAlex

Princípio: nenhuma função "completa" dado ausente. Falha de rede → UNVERIFIED.
Para testes offline: --fixture arquivo.json (mapa URL → resposta JSON ou {"__status__": 404}).
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import difflib
import io
import json
import os
import pathlib
import re
import shutil
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = PLUGIN_ROOT / "schemas"
TEMPLATE_DIR = PLUGIN_ROOT / "templates"

NR = "NR — não reportado"
NA = "NA — não se aplica"
NR_VALUES = {NR, NA}
PAGE_UNRELIABLE = "página não identificável de forma confiável"
STATUSES = ["VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED", "CONTRADICTED", "NOT_REPORTED"]
MSG_UNVERIFIABLE = "Não foi possível verificar esta informação nas fontes consultadas."

# --------------------------------------------------------------------------------------
# Utilidades gerais
# --------------------------------------------------------------------------------------


def today() -> str:
    return _dt.date.today().isoformat()


def load_json(path) -> object:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rows.append((lineno, json.loads(line)))
            except json.JSONDecodeError as exc:
                rows.append((lineno, exc))
    return rows


def is_nr(value) -> bool:
    return isinstance(value, str) and value.strip() in NR_VALUES


def is_numeric_like(value) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    return isinstance(value, str) and bool(re.search(r"\d", value)) and not is_nr(value)


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def norm_title(text: str) -> str:
    text = strip_accents(str(text)).lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def norm_doi(doi: str) -> str:
    doi = str(doi or "").strip().lower()
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi


def surname(name: str) -> str:
    name = str(name).strip()
    if "," in name:
        return name.split(",")[0].strip()
    parts = name.split()
    return parts[-1] if parts else name


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm_title(a), norm_title(b)).ratio()


class Report:
    """Acumula erros e avisos com localização."""

    def __init__(self, label: str):
        self.label = label
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str):
        self.warnings.append(f"{where}: {msg}")

    def merge(self, other: "Report"):
        self.errors += other.errors
        self.warnings += other.warnings

    def render(self) -> str:
        out = [f"== {self.label}"]
        out += [f"  ERRO  {e}" for e in self.errors]
        out += [f"  AVISO {w}" for w in self.warnings]
        out.append(f"  resultado: {'OK' if not self.errors else 'FALHOU'} "
                   f"({len(self.errors)} erro(s), {len(self.warnings)} aviso(s))")
        return "\n".join(out)

    @property
    def ok(self) -> bool:
        return not self.errors


# --------------------------------------------------------------------------------------
# Validador mínimo de JSON Schema (subconjunto usado pelos schemas do plugin)
# --------------------------------------------------------------------------------------

_SCHEMA_CACHE: dict[str, dict] = {}


def _load_schema(name: str) -> dict:
    if name not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[name] = load_json(SCHEMA_DIR / name)
    return _SCHEMA_CACHE[name]


def _resolve_ref(ref: str, current_file: str):
    file_part, _, pointer = ref.partition("#")
    file_name = file_part or current_file
    node = _load_schema(file_name)
    for part in [p for p in pointer.split("/") if p]:
        node = node[part]
    return node, file_name


_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def schema_validate(value, schema: dict, path: str, report: Report, current_file: str):
    if "$ref" in schema:
        target, file_name = _resolve_ref(schema["$ref"], current_file)
        schema_validate(value, target, path, report, file_name)
        return
    types = schema.get("type")
    if types is not None:
        types = types if isinstance(types, list) else [types]
        if not any(_TYPES[t](value) for t in types):
            shown = "vazio/null" if value is None else type(value).__name__
            report.error(path, f"tipo inválido ({shown}); esperado {'/'.join(types)}"
                         + ("; use 'NR — não reportado' para campo ausente" if value in (None, "") else ""))
            return
    if "enum" in schema:
        ok = any(value == e and type(value) is type(e) for e in schema["enum"])
        if not ok:
            report.error(path, f"valor {value!r} fora do domínio {schema['enum']}")
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            report.error(path, "string vazia; use 'NR — não reportado' se a informação não consta na fonte")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            report.error(path, f"{value!r} não segue o padrão {schema['pattern']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema:
        if value < schema["minimum"]:
            report.error(path, f"valor {value} menor que {schema['minimum']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            report.error(path, f"lista com menos de {schema['minItems']} item(ns)")
        if "items" in schema:
            for i, item in enumerate(value):
                schema_validate(item, schema["items"], f"{path}[{i}]", report, current_file)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                report.error(path, f"campo obrigatório ausente: '{key}' (use 'NR — não reportado' se não consta)")
        props = schema.get("properties", {})
        for key, sub in value.items():
            if key in props:
                schema_validate(sub, props[key], f"{path}.{key}", report, current_file)
            elif isinstance(schema.get("additionalProperties"), dict):
                schema_validate(sub, schema["additionalProperties"], f"{path}.{key}", report, current_file)


def validate_against(value, schema_file: str, label: str) -> Report:
    report = Report(label)
    schema_validate(value, _load_schema(schema_file), "$", report, schema_file)
    return report


# --------------------------------------------------------------------------------------
# Validações semânticas
# --------------------------------------------------------------------------------------

_QUANT_KEYS = ("estimate", "se", "ci_low", "ci_high", "p_value", "n")


def _number_in_text(value, text: str) -> bool:
    """Verifica se o número aparece no trecho (tolerante a vírgula decimal e sinal unicode)."""
    if not isinstance(text, str):
        return False
    t = text.replace("−", "-").replace("–", "-")
    raw = str(value).replace("−", "-")
    candidates = {raw, raw.replace(".", ","), raw.lstrip("+")}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        candidates |= {f"{value:g}", f"{value:g}".replace(".", ",")}
        if isinstance(value, float) and abs(value) < 1:
            s = f"{value:g}"
            candidates |= {s.replace("0.", "."), s.replace("0.", ",")}
    return any(c and c in t for c in candidates)


def validate_extraction(path) -> Report:
    data = load_json(path)
    report = validate_against(data, "extraction.schema.json", f"extraction {path}")
    if not isinstance(data, dict):
        return report
    access = data.get("access_level")
    pag_ok = data.get("pagination_reliable", True)
    for key, val in (data.get("fields") or {}).items():
        if isinstance(val, str) and val.strip().lower() in {"n/a", "na", "nr", "-", "?", "unknown", "desconhecido"}:
            report.error(f"$.fields.{key}", f"marcador informal {val!r}; use '{NR}' ou '{NA}'")
    for i, est in enumerate(data.get("estimates") or []):
        where = f"$.estimates[{i}]"
        if not isinstance(est, dict):
            continue
        for k in _QUANT_KEYS:
            v = est.get(k)
            if isinstance(v, str) and not is_nr(v) and not re.search(r"\d", v):
                report.error(f"{where}.{k}", f"descrição qualitativa {v!r} em campo numérico; "
                             f"use '{NR}' e registre a descrição em 'significance' ou 'notes'")
        has_number = any(is_numeric_like(est.get(k)) for k in _QUANT_KEYS)
        loc = est.get("location") or {}
        excerpt = est.get("excerpt")
        if has_number:
            if not isinstance(loc, dict) or (is_nr(loc.get("page", NR)) and all(
                    is_nr(loc.get(k, NR)) for k in ("table", "figure", "appendix"))):
                report.error(f"{where}.location", "número sem localização (página, tabela, figura ou apêndice)")
            if not isinstance(excerpt, str) or is_nr(excerpt):
                report.error(f"{where}.excerpt", "número sem trecho de suporte")
            elif is_numeric_like(est.get("estimate")) and not _number_in_text(est.get("estimate"), excerpt):
                report.warn(f"{where}.estimate", "valor não encontrado literalmente no trecho; confira transcrição/unidade")
            if access == "metadata_only":
                report.error(where, "estimativa numérica com access_level=metadata_only")
            if access == "abstract_only":
                report.warn(where, "extração só do abstract: confirme que o número consta no abstract")
        if isinstance(loc, dict) and not pag_ok and loc.get("page") not in (PAGE_UNRELIABLE, NR, NA):
            report.warn(f"{where}.location.page", f"pagination_reliable=false; use '{PAGE_UNRELIABLE}'")
    return report


def _load_sources_index(path):
    if not path:
        return None
    data = load_json(path)
    items = data.get("sources", []) if isinstance(data, dict) else data
    return {s.get("source_id"): s for s in items if isinstance(s, dict)}


def validate_sources(path) -> Report:
    data = load_json(path)
    report = validate_against(data, "sources.schema.json", f"sources {path}")
    seen = {}
    for i, src in enumerate(data.get("sources", []) if isinstance(data, dict) else []):
        sid = src.get("source_id")
        if sid in seen:
            report.error(f"$.sources[{i}]", f"source_id duplicado {sid}")
        seen[sid] = i
        if src.get("source_type") in {"working_paper", "preprint", "official_report", "technical_report",
                                      "program_evaluation", "international_org_report", "think_tank_report",
                                      "news", "blog", "regulator_document"} and src.get("peer_reviewed") is True:
            report.warn(f"$.sources[{i}]", "literatura cinzenta marcada como peer_reviewed=true; confirme")
        mv = src.get("metadata_verification") or {}
        if mv.get("status") == "VERIFIED" and not mv.get("checked_against"):
            report.error(f"$.sources[{i}].metadata_verification", "VERIFIED sem 'checked_against'")
    return report


def validate_ledger(path, sources_path=None) -> Report:
    report = Report(f"ledger {path}")
    sources = _load_sources_index(sources_path)
    rows = load_jsonl(path)
    ids = {}
    for lineno, row in rows:
        where = f"linha {lineno}"
        if isinstance(row, Exception):
            report.error(where, f"JSON inválido: {row}")
            continue
        sub = validate_against(row, "ledger-entry.schema.json", "")
        report.errors += [f"{where} {e}" for e in sub.errors]
        eid = row.get("evidence_id")
        if eid in ids:
            report.error(where, f"evidence_id duplicado {eid} (já na linha {ids[eid]})")
        ids[eid] = lineno
        if sources is not None and row.get("source_id") not in sources:
            report.error(where, f"source_id {row.get('source_id')} não existe em sources.json")
        if row.get("evidence_type") == "analytic_inference" and not row.get("derived_from"):
            report.error(where, "analytic_inference exige 'derived_from' com os E-… usados")
        qr = row.get("quantitative_result")
        if isinstance(qr, dict):
            est = qr.get("estimate")
            if is_numeric_like(est) and not _number_in_text(est, row.get("excerpt", "")):
                report.warn(where, "estimativa não aparece literalmente no trecho")
            for k, v in qr.items():
                if isinstance(v, str) and not is_nr(v) and not re.search(r"\d", v) and k != "unit":
                    report.error(where, f"quantitative_result.{k} com texto qualitativo {v!r}; use '{NR}'")
        if row.get("verification_status") == "VERIFIED" and row.get("page") in (NR, None) and row.get("section") in (NR, None):
            report.error(where, "VERIFIED sem localização (page/section)")
    for lineno, row in rows:
        if isinstance(row, dict):
            for ref in row.get("derived_from", []) or []:
                if ref not in ids:
                    report.error(f"linha {lineno}", f"derived_from referencia {ref} inexistente")
    return report


def prisma_check(log: dict) -> Report:
    report = Report("aritmética do fluxo de triagem")
    s = log.get("screening") or {}
    try:
        ident, dup, scr = s["records_identified"], s["duplicates_removed"], s["screened"]
        exc_ta, fta = s["excluded_title_abstract"], s["full_text_assessed"]
        not_ret = s.get("full_text_not_retrieved", 0)
        exc_ft = sum((s.get("excluded_full_text") or {}).values())
        inc = s["included"]
    except (KeyError, TypeError) as exc:
        report.error("screening", f"contagem ausente: {exc}")
        return report
    if ident - dup != scr:
        report.error("screening", f"identificados ({ident}) − duplicatas ({dup}) ≠ triados ({scr})")
    if scr - exc_ta != fta + not_ret:
        report.error("screening", f"triados ({scr}) − excluídos T/A ({exc_ta}) ≠ texto completo avaliado ({fta}) + não recuperados ({not_ret})")
    if fta - exc_ft != inc:
        report.error("screening", f"texto completo ({fta}) − excluídos TC ({exc_ft}) ≠ incluídos ({inc})")
    found = [x.get("results_found") for x in log.get("searches", []) if x.get("executed")]
    numeric = [x for x in found if isinstance(x, int)]
    if numeric and len(numeric) == len(found) and sum(numeric) > ident:
        report.warn("searches", f"soma dos resultados das buscas ({sum(numeric)}) > registros identificados ({ident}); "
                                "explique (ex.: nem todos os registros foram exportados)")
    return report


def validate_searchlog(path) -> Report:
    data = load_json(path)
    report = validate_against(data, "search-log.schema.json", f"searchlog {path}")
    if isinstance(data, dict):
        for i, srch in enumerate(data.get("searches", [])):
            if srch.get("executed") is False and isinstance(srch.get("results_found"), int):
                report.error(f"$.searches[{i}]", "busca não executada não pode ter contagem numérica")
        if "screening" in data:
            report.merge(prisma_check(data))
    return report


def validate_audit(path) -> Report:
    data = load_json(path)
    report = validate_against(data, "citation-audit.schema.json", f"citation-audit {path}")
    for i, c in enumerate(data.get("claims", []) if isinstance(data, dict) else []):
        if c.get("classification") == "SUPORTADA" and not c.get("support_excerpt"):
            report.error(f"$.claims[{i}]", "SUPORTADA exige 'support_excerpt'")
        if c.get("reference_existence") == "CONTRADICTED" and c.get("classification") == "SUPORTADA":
            report.error(f"$.claims[{i}]", "referência CONTRADICTED não pode sustentar afirmação SUPORTADA")
    return report


def validate_project(research_dir) -> Report:
    root = pathlib.Path(research_dir)
    total = Report(f"projeto {root}")
    sources = root / "sources" / "sources.json"
    if sources.exists():
        total.merge(validate_sources(sources))
    for ext in sorted((root / "extraction").glob("*.json")):
        total.merge(validate_extraction(ext))
    ledger = root / "ledger" / "evidence.jsonl"
    if ledger.exists():
        total.merge(validate_ledger(ledger, sources if sources.exists() else None))
    log = root / "search" / "search-log.json"
    if log.exists():
        total.merge(validate_searchlog(log))
    audit = root / "audit" / "citation-audit.json"
    if audit.exists():
        total.merge(validate_audit(audit))
    return total


# --------------------------------------------------------------------------------------
# Matriz de evidências
# --------------------------------------------------------------------------------------

COMPACT_COLS = ["Study", "Country", "Period", "Unit", "N", "Method", "Treatment", "Outcome",
                "Estimate", "SE/CI", "Identification", "Page", "DOI"]
DETAILED_EXTRA = ["Peer reviewed", "Access", "Data source", "Comparison", "Specification", "p-value",
                  "Significance", "Robustness", "Limitations", "Excerpt", "Metadata status"]


def short_citation(src: dict | None, fallback: str) -> str:
    if not src:
        return fallback
    authors = src.get("authors")
    if isinstance(authors, str):
        first = authors
        many = False
    else:
        first = surname(authors[0]) if authors else fallback
        many = len(authors) > 2
        if authors and len(authors) == 2:
            first = f"{surname(authors[0])} & {surname(authors[1])}"
    return f"{first}{' et al.' if many else ''} ({src.get('year', NR)})"


def _fmt(v) -> str:
    if v is None:
        return NR
    return str(v)


def _se_ci(est: dict) -> str:
    parts = []
    if not is_nr(est.get("se", NR)):
        parts.append(f"SE {est['se']}")
    lo, hi = est.get("ci_low", NR), est.get("ci_high", NR)
    if not is_nr(lo) and not is_nr(hi):
        lvl = est.get("ci_level")
        parts.append(f"CI{'' if lvl is None else ' ' + str(lvl)} [{lo}; {hi}]")
    return "; ".join(parts) if parts else NR


def _location(est: dict) -> str:
    loc = est.get("location") or {}
    parts = []
    for key, label in (("page", "p."), ("table", "Tab."), ("figure", "Fig."), ("appendix", "Ap."), ("section", "§")):
        val = loc.get(key)
        if val and not is_nr(val):
            parts.append(f"{label} {val}")
    return "; ".join(parts) if parts else NR


def build_matrix(extractions: list[dict], sources: dict | None, detailed: bool):
    rows = []
    for ex in extractions:
        f = ex.get("fields", {})
        src = (sources or {}).get(ex.get("source_id"))
        study = short_citation(src, f.get("reference", ex.get("source_id", NR)))
        ests = ex.get("estimates") or [{}]
        for est in ests:
            estimate = _fmt(est.get("estimate", NR))
            unit = est.get("unit")
            if unit and not is_nr(unit) and not is_nr(estimate):
                estimate = f"{estimate} {unit}"
            row = {
                "Study": study,
                "Country": _fmt(f.get("country_jurisdiction")),
                "Period": _fmt(est.get("period") or f.get("period")),
                "Unit": _fmt(f.get("unit_of_analysis")),
                "N": _fmt(est.get("n") if est.get("n") not in (None,) else f.get("sample_size")),
                "Method": _fmt(f.get("method")),
                "Treatment": _fmt(est.get("treatment_group") or f.get("intervention")),
                "Outcome": _fmt(est.get("dependent_variable") or f.get("outcome")),
                "Estimate": estimate if est else NR,
                "SE/CI": _se_ci(est) if est else NR,
                "Identification": _fmt(est.get("identification") or f.get("causal_identification")),
                "Page": _location(est) if est else NR,
                "DOI": _fmt(f.get("doi")),
            }
            if detailed:
                row.update({
                    "Peer reviewed": _fmt(src.get("peer_reviewed") if src else NR),
                    "Access": _fmt(ex.get("access_level")),
                    "Data source": _fmt(f.get("data_source")),
                    "Comparison": _fmt(est.get("control_group") or f.get("comparison")),
                    "Specification": _fmt(est.get("specification", NR)),
                    "p-value": _fmt(est.get("p_value", NR)),
                    "Significance": _fmt(est.get("significance", NR)),
                    "Robustness": _fmt(f.get("robustness")),
                    "Limitations": _fmt(f.get("limitations")),
                    "Excerpt": _fmt(est.get("excerpt", NR)),
                    "Metadata status": _fmt((src or {}).get("metadata_verification", {}).get("status", NR)),
                })
            rows.append(row)
    return rows


def render_rows(rows: list[dict], cols: list[str], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue()
    def cell(v):
        return str(v).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(cell(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------
# Rede (Crossref, doi.org, OpenAlex) com suporte a fixtures
# --------------------------------------------------------------------------------------

_FIXTURES: dict | None = None


class NotFound(Exception):
    pass


class NetworkError(Exception):
    pass


def http_get_json(url: str, timeout: int = 20):
    if _FIXTURES is not None:
        if url not in _FIXTURES:
            raise NetworkError(f"fixture sem resposta para {url}")
        resp = _FIXTURES[url]
        if isinstance(resp, dict) and resp.get("__status__") == 404:
            raise NotFound(url)
        if isinstance(resp, dict) and resp.get("__status__") == "error":
            raise NetworkError(resp.get("message", "erro simulado"))
        return resp
    contact = os.environ.get("SR_CONTACT_EMAIL", "").strip()
    agent = "scientific-research-plugin/0.1 (+https://github.com/Raimisson/gerenciador-de-projetos)"
    if contact:
        agent += f" mailto:{contact}"
    req = urllib.request.Request(url, headers={"User-Agent": agent, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise NotFound(url) from exc
        raise NetworkError(f"HTTP {exc.code} em {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise NetworkError(f"{type(exc).__name__}: {exc}") from exc


def crossref_url(doi: str) -> str:
    return "https://api.crossref.org/works/" + urllib.parse.quote(norm_doi(doi), safe="/")


def handle_url(doi: str) -> str:
    return "https://doi.org/api/handles/" + urllib.parse.quote(norm_doi(doi), safe="/")


def doi_check(doi: str, title=None, authors=None, year=None, journal=None) -> dict:
    """Confere um DOI. Retorna dict com status (taxonomia do plugin) e flags."""
    result = {"doi": norm_doi(doi), "checked_on": today(), "checked_against": [], "flags": [],
              "comparisons": {}, "registry_metadata": None}
    if not re.match(r"^10\.\d{4,9}/\S+$", result["doi"]):
        result.update(status="CONTRADICTED", verdict="DOI com sintaxe inválida")
        result["flags"].append("DOI_SINTAXE_INVALIDA")
        return result
    try:
        msg = http_get_json(crossref_url(doi))
        result["checked_against"].append("Crossref")
        work = msg.get("message", msg) if isinstance(msg, dict) else {}
    except NotFound:
        result["checked_against"].append("Crossref (404)")
        try:
            handle = http_get_json(handle_url(doi))
            result["checked_against"].append("doi.org handle API")
            if isinstance(handle, dict) and handle.get("responseCode") == 1:
                result.update(status="UNVERIFIED",
                              verdict="DOI registrado fora do Crossref (ex.: DataCite); metadados não conferidos")
                result["flags"].append("DOI_OUTRA_AGENCIA")
                return result
        except NotFound:
            result["checked_against"].append("doi.org handle API (404)")
        except NetworkError as exc:
            result.update(status="UNVERIFIED", verdict=f"{MSG_UNVERIFIABLE} ({exc})")
            result["flags"].append("FALHA_DE_REDE")
            return result
        result.update(status="CONTRADICTED", verdict="DOI não registrado — referência possivelmente inventada ou DOI incorreto")
        result["flags"] += ["DOI_NAO_RESOLVE", "POSSIVELMENTE_INVENTADA"]
        return result
    except NetworkError as exc:
        result.update(status="UNVERIFIED", verdict=f"{MSG_UNVERIFIABLE} ({exc})")
        result["flags"].append("FALHA_DE_REDE")
        return result

    reg_title = " ".join(work.get("title") or []) or ""
    reg_authors = [a.get("family") or a.get("name") or "" for a in work.get("author") or []]
    parts = ((work.get("issued") or {}).get("date-parts") or [[None]])[0]
    reg_year = parts[0] if parts else None
    reg_journal = " ".join(work.get("container-title") or []) or ""
    result["registry_metadata"] = {"title": reg_title, "authors": reg_authors, "year": reg_year,
                                   "container": reg_journal, "type": work.get("type"),
                                   "volume": work.get("volume"), "issue": work.get("issue"),
                                   "page": work.get("page"), "publisher": work.get("publisher")}
    mismatches, partial, compared = [], [], 0
    if title:
        compared += 1
        sim = similarity(title, reg_title)
        result["comparisons"]["title"] = {"given": title, "registry": reg_title, "similarity": round(sim, 3)}
        if sim < 0.6:
            mismatches.append("TITULO_INCOMPATIVEL")
        elif sim < 0.9:
            partial.append("TITULO_PARCIAL")
    if authors:
        compared += 1
        given = [surname(a) for a in (authors if isinstance(authors, list) else re.split(r";", authors)) if a.strip()]
        reg_norm = {norm_title(a) for a in reg_authors}
        hits = [g for g in given if norm_title(g) in reg_norm]
        result["comparisons"]["authors"] = {"given": given, "registry": reg_authors, "matched": hits}
        if not hits:
            mismatches.append("AUTORES_INCOMPATIVEIS")
        elif len(hits) < len(given):
            partial.append("AUTORES_PARCIAIS")
    if year:
        compared += 1
        result["comparisons"]["year"] = {"given": year, "registry": reg_year}
        try:
            diff = abs(int(str(year)[:4]) - int(reg_year))
        except (TypeError, ValueError):
            diff = None
        if diff is None:
            partial.append("ANO_NAO_COMPARAVEL")
        elif diff > 1:
            mismatches.append("ANO_INCOMPATIVEL")
        elif diff == 1:
            partial.append("ANO_DIFERE_1 (online-first vs. impresso?)")
    if journal:
        compared += 1
        sim = similarity(journal, reg_journal)
        result["comparisons"]["journal"] = {"given": journal, "registry": reg_journal, "similarity": round(sim, 3)}
        if sim < 0.5:
            mismatches.append("PERIODICO_INCOMPATIVEL")
        elif sim < 0.85:
            partial.append("PERIODICO_PARCIAL")
    result["flags"] += mismatches + partial
    if mismatches:
        result["flags"].append("POSSIVELMENTE_INVENTADA_OU_INCORRETA")
        result.update(status="CONTRADICTED", verdict="DOI resolve, mas aponta para trabalho com metadados incompatíveis")
    elif partial or compared == 0:
        result.update(status="PARTIALLY_VERIFIED",
                      verdict="DOI resolve; " + ("nenhum metadado fornecido para comparação" if compared == 0
                                                 else "metadados parcialmente compatíveis"))
    else:
        result.update(status="VERIFIED", verdict="DOI resolve e metadados compatíveis")
    return result


def refs_check(sources_path) -> list[dict]:
    data = load_json(sources_path)
    out = []
    for src in data.get("sources", []):
        doi = src.get("doi")
        if not doi or is_nr(doi):
            out.append({"source_id": src.get("source_id"), "doi": NR, "status": "UNVERIFIED",
                        "verdict": "sem DOI — conferir por título/emissor", "flags": ["SEM_DOI"]})
            continue
        authors = src.get("authors")
        res = doi_check(doi, title=src.get("title"),
                        authors=authors if isinstance(authors, list) else None,
                        year=src.get("year"),
                        journal=src.get("container") if src.get("source_type") == "peer_reviewed_article" else None)
        res["source_id"] = src.get("source_id")
        out.append(res)
    return out


def find_duplicates(items: list[dict]) -> list[tuple[str, list[str]]]:
    by_doi, by_title = {}, {}
    for it in items:
        rid = it.get("source_id") or it.get("record_id") or it.get("id") or "?"
        d = norm_doi(it.get("doi", ""))
        if d and not is_nr(it.get("doi", "")):
            by_doi.setdefault(d, []).append(rid)
        key = (norm_title(it.get("title", "")), str(it.get("year", "")))
        if key[0]:
            by_title.setdefault(key, []).append(rid)
    dups = [(f"DOI {k}", v) for k, v in by_doi.items() if len(v) > 1]
    dups += [(f"título+ano '{k[0][:60]}' {k[1]}", v) for k, v in by_title.items() if len(v) > 1]
    return dups


# --------------------------------------------------------------------------------------
# Varredura do manuscrito
# --------------------------------------------------------------------------------------

E_MARK = re.compile(r"\[(E-\d{4,}(?:\s*[,;]\s*E-\d{4,})*)\]")
P_MARK = re.compile(r"<!--\s*(P-\d{3,})\s*-->")
CITATION = re.compile(
    r"\((?:[^()]*?[A-ZÀ-Ý][\w'’\-]+(?: et al\.)?(?:,| e | & | and )[^()]*?\b(?:1[89]|20)\d{2}[a-z]?)\)"
    r"|[A-ZÀ-Ý][\w'’\-]+(?: et al\.)? \((?:1[89]|20)\d{2}[a-z]?\)"
    r"|\[\d+(?:[,–-]\d+)*\]")
NUMBER = re.compile(r"(?<![\w\-])[-−+]?\d+(?:[.,]\d+)*\s?%?")
IGNORE_NUMBER_CONTEXT = re.compile(
    r"(tabela|table|figura|figure|fig\.|eq\.|equa[cç][aã]o|se[cç][aã]o|section|cap[ií]tulo|chapter|"
    r"ap[eê]ndice|appendix|hip[oó]tese|h|art\.|§|inciso|p\.|pp\.|E-|P-|S-|nota|note)\s*\(?$", re.I)
CAUSAL = re.compile(
    r"\b(caus(?:a|ou|aram|am|ado|ada)|provoc(?:a|ou|aram)|levou a|levaram a|result(?:a|ou|aram) em|"
    r"reduz(?:iu|iram)|aument(?:ou|aram)|diminu(?:iu|íram|iram)|elev(?:ou|aram)|impacto (?:de|do|da)|"
    r"efeito (?:de|do|da|causal)|gra[cç]as a|em raz[aã]o d[eoa]|"
    r"caused|causes|led to|leads to|resulted in|results in|reduced|increased|decreased|"
    r"effect of|impact of|drove|drives|due to)\b", re.I)
UNIVERSAL = re.compile(r"\b(sempre|todos os|todas as|universalmente|em qualquer|always|universally|in all)\b", re.I)
COUNTRY_TERMS = {
    "brasil": ["brasil", "brazil", "brasileir"],
    "estados unidos": ["estados unidos", "eua", "united states", "u.s.", "us ", "americano", "norte-americano"],
    "união europeia": ["união europeia", "european union", "ue ", "eu "],
    "reino unido": ["reino unido", "united kingdom", "uk ", "great britain", "grã-bretanha"],
    "frança": ["frança", "france"], "itália": ["itália", "italy"], "alemanha": ["alemanha", "germany"],
    "china": ["china"], "índia": ["índia", "india"], "méxico": ["méxico", "mexico"], "chile": ["chile"],
    "argentina": ["argentina"], "colômbia": ["colômbia", "colombia"], "portugal": ["portugal"],
    "espanha": ["espanha", "spain"], "canadá": ["canadá", "canada"], "austrália": ["austrália", "australia"],
    "dinamarca": ["dinamarca", "denmark"], "suécia": ["suécia", "sweden"], "letônia": ["letônia", "latvia"],
}
SECONDARY_TYPES = {"news", "blog", "other"}


def _countries_in(text: str) -> set[str]:
    t = " " + strip_accents(text.lower()) + " "
    found = set()
    for canon, terms in COUNTRY_TERMS.items():
        for term in terms:
            if " " + strip_accents(term) in t:
                found.add(canon)
                break
    return found


def split_sentences(paragraph: str) -> list[str]:
    protected = re.sub(r"\b(et al|p|pp|Fig|Eq|Tab|art|n|vol|ed|e\.g|i\.e|cf)\.", lambda m: m.group(0).replace(".", "<DOT>"), paragraph)
    protected = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", protected)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\"“(\[])", protected)
    return [p.replace("<DOT>", ".").strip() for p in parts if p.strip()]


def manuscript_paragraphs(text: str):
    """Gera (paragraph_id, linha_inicial, texto) ignorando títulos, código, comentários e tabelas."""
    in_code = False
    para, start, pid, current_pid = [], 0, 0, None
    lines = text.splitlines()
    for i, line in enumerate(lines + [""], 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        m = P_MARK.search(stripped)
        if m:
            current_pid = m.group(1)
            stripped = P_MARK.sub("", stripped).strip()
            if not stripped:
                continue
        if in_code or stripped.startswith("#") or stripped.startswith("|") or stripped.startswith("<!--"):
            if para:
                pid += 1
                yield (current_pid or f"¶{pid}", start, " ".join(para))
                para, current_pid = [], None
            continue
        if not stripped:
            if para:
                pid += 1
                yield (current_pid or f"¶{pid}", start, " ".join(para))
                para, current_pid = [], None
            continue
        if not para:
            start = i
        para.append(stripped)


def _numbers_needing_source(sentence: str) -> list[str]:
    clean = E_MARK.sub(" ", sentence)
    clean = CITATION.sub(" ", clean)
    hits = []
    for m in NUMBER.finditer(clean):
        token = m.group(0).strip()
        prefix = clean[max(0, m.start() - 14):m.start()]
        if IGNORE_NUMBER_CONTEXT.search(prefix):
            continue
        digits = re.sub(r"[^\d]", "", token)
        if re.fullmatch(r"(1[89]|20)\d{2}", digits) and "%" not in token and "," not in token and "." not in token:
            continue  # ano isolado
        if len(digits) == 1 and "%" not in token and re.match(r"^\s*\d\s*[.)]", sentence):
            continue  # numeração de lista
        hits.append(token)
    return hits


def scan_manuscript(text: str, ledger: dict | None = None, sources: dict | None = None,
                    target_context: str | None = None) -> list[dict]:
    findings = []
    target = _countries_in(target_context) if target_context else set()
    for pid, line, para in manuscript_paragraphs(text):
        for sent in split_sentences(para):
            ids = []
            for grp in E_MARK.findall(sent):
                ids += [x.strip() for x in re.split(r"[,;]", grp)]
            has_cite = bool(CITATION.search(sent))
            short = sent if len(sent) <= 180 else sent[:177] + "..."

            def add(code, severity, msg):
                findings.append({"paragraph": pid, "line": line, "code": code, "severity": severity,
                                 "sentence": short, "message": msg})

            nums = _numbers_needing_source(sent)
            if nums and not ids and not has_cite:
                add("NUMERO-SEM-FONTE", "CRÍTICO", f"número(s) {', '.join(nums[:5])} sem marcador [E-…] nem citação")
            entries = []
            for eid in ids:
                entry = (ledger or {}).get(eid)
                if ledger is not None and entry is None:
                    add("EVIDENCIA-INEXISTENTE", "CRÍTICO", f"{eid} não existe no ledger")
                elif entry is not None:
                    entries.append(entry)
                    st = entry.get("verification_status")
                    if st in ("UNVERIFIED", "CONTRADICTED", "NOT_REPORTED"):
                        add("EVIDENCIA-NAO-VERIFICADA", "CRÍTICO", f"{eid} tem status {st}")
                    if entry.get("evidence_type") == "analytic_inference" and has_cite:
                        add("INFERENCIA-ATRIBUIDA", "MAIOR", f"{eid} é inferência analítica, mas a frase cita estudo")
            if CAUSAL.search(sent):
                classes = {e.get("design_class") for e in entries}
                if entries and classes - {"causal", "normative"}:
                    add("CAUSAL-INDEVIDA", "MAIOR",
                        f"linguagem causal ('{CAUSAL.search(sent).group(0)}') apoiada em evidência {sorted(c for c in classes if c)}")
                elif not entries and (has_cite or nums):
                    add("CAUSAL-VERIFICAR", "AVISO",
                        f"linguagem causal ('{CAUSAL.search(sent).group(0)}'); confirme que o desenho citado identifica causalidade")
            mentioned = _countries_in(sent) | target
            if entries and mentioned:
                ev_countries = set()
                for e in entries:
                    ev_countries |= _countries_in((e.get("context") or {}).get("country", ""))
                if ev_countries and not (mentioned & ev_countries):
                    add("GENERALIZACAO", "MAIOR",
                        f"frase/contexto {sorted(mentioned)} apoiada em evidência de {sorted(ev_countries)}")
            if entries and UNIVERSAL.search(sent):
                add("GENERALIZACAO", "AVISO", f"quantificador universal ('{UNIVERSAL.search(sent).group(0)}') sobre evidência específica")
            if sources is not None:
                for e in entries:
                    src = sources.get(e.get("source_id"), {})
                    if src.get("source_type") in SECONDARY_TYPES:
                        add("FONTE-SECUNDARIA", "MAIOR",
                            f"{e.get('evidence_id')} vem de fonte '{src.get('source_type')}'; procure a fonte primária")
    return findings


def render_findings(findings: list[dict], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(findings, ensure_ascii=False, indent=2) + "\n"
    if not findings:
        return "Nenhum problema detectado pela varredura automática (isso não substitui a auditoria frase a frase).\n"
    counts = {}
    for f in findings:
        counts[f["code"]] = counts.get(f["code"], 0) + 1
    out = ["## Varredura automática do manuscrito", "",
           "Resumo: " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())), "",
           "| # | Parágrafo (linha) | Código | Severidade | Mensagem | Frase |", "|---|---|---|---|---|---|"]
    for i, f in enumerate(findings, 1):
        sent = f["sentence"].replace("|", "\\|")
        out.append(f"| {i} | {f['paragraph']} ({f['line']}) | {f['code']} | {f['severity']} | {f['message']} | {sent} |")
    out += ["", "_Heurísticas: confirme cada item manualmente; ausência de alerta não prova correção._"]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------
# Proveniência
# --------------------------------------------------------------------------------------


def load_ledger_index(path) -> dict:
    idx = {}
    for _, row in load_jsonl(path):
        if isinstance(row, dict) and row.get("evidence_id"):
            idx[row["evidence_id"]] = row
    return idx


def trace(target: str, ledger: dict, sources: dict | None, manuscript: str | None) -> str:
    out = []
    ids = []
    paragraphs = list(manuscript_paragraphs(manuscript)) if manuscript else []
    if target.startswith("P-") or target.startswith("¶"):
        para = next((p for p in paragraphs if p[0] == target), None)
        if not para:
            return f"Parágrafo {target} não encontrado no manuscrito.\n"
        out += [f"# Parágrafo {target} (linha {para[1]})", "", f"> {para[2]}", ""]
        for grp in E_MARK.findall(para[2]):
            ids += [x.strip() for x in re.split(r"[,;]", grp)]
        if not ids:
            out.append("Nenhum marcador [E-…] neste parágrafo: as afirmações empíricas dele não são rastreáveis.")
    else:
        ids = [target]
    for eid in ids:
        e = ledger.get(eid)
        out.append(f"## {eid}")
        if not e:
            out.append(f"- **Não encontrado no ledger.** {MSG_UNVERIFIABLE}")
            continue
        src = (sources or {}).get(e.get("source_id"), {})
        authors = src.get("authors")
        authors = "; ".join(authors) if isinstance(authors, list) else (authors or NR)
        out += [
            "**1. Fonte**",
            f"- {e.get('source_id')}: {authors} ({src.get('year', NR)}). {src.get('title', NR)}. {src.get('container', NR)}.",
            f"- DOI: {e.get('doi')} · URL: {e.get('url')}",
            f"- Metadados: {src.get('metadata_verification', {}).get('status', NR)} · tipo: {src.get('source_type', NR)} · revisado por pares: {src.get('peer_reviewed', NR)} · acesso: {src.get('access_level', NR)}",
            "**2. Evidência extraída**",
            f"- Local: página {e.get('page')}; seção {e.get('section')}"
            + (f"; tabela {e['table']}" if e.get("table") else "") + (f"; figura {e['figure']}" if e.get("figure") else ""),
            f"- Trecho: \"{e.get('excerpt')}\"",
            f"- Resultado quantitativo: {json.dumps(e.get('quantitative_result'), ensure_ascii=False)}",
            f"- Método: {e.get('method')} · classe de desenho: {e.get('design_class')}",
            f"- Contexto: {json.dumps(e.get('context'), ensure_ascii=False)}",
            "**3. Interpretação**",
            f"- Tipo: {e.get('evidence_type')}" + (f" (derivada de {', '.join(e.get('derived_from', []))})" if e.get("derived_from") else ""),
            f"- Afirmação sustentada: {e.get('claim_supported')}",
            f"- Status: {e.get('verification_status')} (por {e.get('verified_by')} em {e.get('verified_on')})",
        ]
        if e.get("notes"):
            out.append(f"- Notas: {e['notes']}")
        out.append("**4. Uso no manuscrito**")
        used = [p for p in paragraphs if eid in p[2]]
        if used:
            out += [f"- {p[0]} (linha {p[1]}): {p[2][:200]}{'...' if len(p[2]) > 200 else ''}" for p in used]
        else:
            declared = e.get("used_in") or []
            out.append(f"- Declarado em used_in: {', '.join(declared)}" if declared else "- Não usado no manuscrito fornecido.")
        out.append("")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------
# Formatação de referências (apenas metadados verificados)
# --------------------------------------------------------------------------------------


def _split_name(name: str):
    name = name.strip()
    if "," in name:
        last, first = [x.strip() for x in name.split(",", 1)]
    else:
        parts = name.split()
        last, first = (parts[-1], " ".join(parts[:-1])) if len(parts) > 1 else (name, "")
    return last, first


def _initials(first: str, sep=". ") -> str:
    parts = [p for p in re.split(r"[\s\-]+", first) if p]
    return sep.join(p[0].upper() for p in parts) + ("." if parts else "")


def format_reference(src: dict, style: str) -> str:
    authors = src.get("authors") or []
    if isinstance(authors, str):
        authors = [authors]
    institutional = len(authors) == 1 and "," not in authors[0] and len(authors[0].split()) > 3
    year = src.get("year", "s.d.")
    title = src.get("title", "")
    cont = src.get("container", "")
    vol, iss, pages = src.get("volume"), src.get("issue"), src.get("pages")
    doi = norm_doi(src.get("doi", "")) if src.get("doi") and not is_nr(src.get("doi")) else ""
    url = src.get("url") if src.get("url") and not is_nr(src.get("url")) else ""
    article = src.get("source_type") == "peer_reviewed_article"
    if style == "abnt":
        if institutional:
            auth = authors[0].upper()
        else:
            names = []
            for a in authors[:3]:
                last, first = _split_name(a)
                names.append(f"{last.upper()}, {first}".strip().rstrip(","))
            auth = "; ".join(names) + ("; et al" if len(authors) > 3 else "")
        s = f"{auth}. {title}. "
        if article:
            s += f"**{cont}**"
            if vol:
                s += f", v. {vol}"
            if iss:
                s += f", n. {iss}"
            if pages:
                s += f", p. {pages}"
            s += f", {year}."
        else:
            s += f"{cont}, {year}."
        if doi:
            s += f" DOI: https://doi.org/{doi}."
        elif url:
            s += f" Disponível em: {url}." + (f" Acesso em: {src['accessed']}." if src.get("accessed") else "")
        return s
    if style == "apa":
        if institutional:
            auth = authors[0]
        else:
            names = []
            for a in authors[:20]:
                last, first = _split_name(a)
                names.append(f"{last}, {_initials(first, '. ')}".strip().rstrip(","))
            auth = names[0] if len(names) == 1 else ", ".join(names[:-1]) + ", & " + names[-1]
        s = f"{auth} ({year}). {title}. "
        if article:
            s += f"*{cont}*"
            if vol:
                s += f", *{vol}*"
            if iss:
                s += f"({iss})"
            if pages:
                s += f", {pages}"
            s += "."
        else:
            s += f"{cont}."
        if doi:
            s += f" https://doi.org/{doi}"
        elif url:
            s += f" {url}"
        return s
    if style == "chicago":
        names = []
        for i, a in enumerate(authors):
            last, first = _split_name(a)
            names.append(a if institutional else (f"{last}, {first}" if i == 0 else f"{first} {last}").strip().rstrip(","))
        auth = names[0] if len(names) == 1 else ", ".join(names[:-1]) + ", and " + names[-1]
        s = f"{auth}. {year}. “{title}.” "
        if article:
            s += f"*{cont}*"
            if vol:
                s += f" {vol}"
            if iss:
                s += f" ({iss})"
            if pages:
                s += f": {pages}"
            s += "."
        else:
            s += f"{cont}."
        if doi:
            s += f" https://doi.org/{doi}."
        elif url:
            s += f" {url}."
        return s
    if style == "bibtex":
        first_last = _split_name(authors[0])[0] if authors else "anon"
        key = re.sub(r"[^A-Za-z0-9]", "", strip_accents(first_last)) + str(year)
        etype = "article" if article else ("techreport" if src.get("source_type") in {
            "technical_report", "official_report", "working_paper", "program_evaluation",
            "international_org_report", "think_tank_report"} else "misc")
        fields = {"author": " and ".join(("{" + a + "}") if institutional else a for a in authors), "title": "{" + title + "}", "year": str(year)}
        if article:
            fields["journal"] = cont
        elif etype == "techreport":
            fields["institution"] = cont
        else:
            fields["howpublished"] = cont
        for k, v in (("volume", vol), ("number", iss), ("pages", pages), ("doi", doi), ("url", url)):
            if v:
                fields[k] = str(v).replace("-", "--") if k == "pages" else str(v)
        body = ",\n".join(f"  {k} = {{{v}}}" if not v.startswith("{") else f"  {k} = {v}" for k, v in fields.items())
        return f"@{etype}{{{key},\n{body}\n}}"
    raise ValueError(f"estilo desconhecido: {style}")


# --------------------------------------------------------------------------------------
# PRISMA e OpenAlex
# --------------------------------------------------------------------------------------


def render_prisma(log: dict) -> str:
    s = log.get("screening", {})
    exc = s.get("excluded_full_text") or {}
    lines = ["## Fluxo de seleção (inspirado em PRISMA 2020)", "",
             "_Não constitui declaração de conformidade PRISMA; ver checklist na skill systematic-review._", "",
             "```",
             f"Registros identificados nas buscas ........... n = {s.get('records_identified', NR)}",
             f"  └─ duplicatas removidas ..................... n = {s.get('duplicates_removed', NR)}",
             f"Registros triados (título/resumo) ............ n = {s.get('screened', NR)}",
             f"  └─ excluídos na triagem ..................... n = {s.get('excluded_title_abstract', NR)}",
             f"Textos completos não recuperados ............. n = {s.get('full_text_not_retrieved', 0)}",
             f"Textos completos avaliados ................... n = {s.get('full_text_assessed', NR)}"]
    for reason, n in exc.items():
        lines.append(f"  └─ excluídos: {reason:<32} n = {n}")
    lines += [f"Estudos incluídos .............................. n = {s.get('included', NR)}", "```", "",
              "### Buscas", "", "| Base | Data | Executada | Resultados | Query |", "|---|---|---|---|---|"]
    for x in log.get("searches", []):
        q = str(x.get("query", "")).replace("|", "\\|")
        lines.append(f"| {x.get('database')} | {x.get('date')} | {'sim' if x.get('executed') else 'não'} | {x.get('results_found')} | `{q}` |")
    return "\n".join(lines) + "\n"


def openalex_work_summary(w: dict) -> dict:
    authors = [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])]
    loc = (w.get("primary_location") or {}).get("source") or {}
    return {"openalex_id": w.get("id"), "doi": norm_doi(w.get("doi") or "") or NR,
            "title": w.get("display_name") or w.get("title") or NR,
            "year": w.get("publication_year") or NR, "authors": authors or [NR],
            "venue": loc.get("display_name") or NR, "type": w.get("type") or NR,
            "cited_by_count": w.get("cited_by_count", NR)}


OPENALEX = "https://api.openalex.org"


def openalex_search(query: str, per_page=25, from_year=None, to_year=None) -> dict:
    params = {"search": query, "per-page": str(per_page)}
    filters = []
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{to_year}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    url = f"{OPENALEX}/works?" + urllib.parse.urlencode(params)
    data = http_get_json(url)
    return {"url": url, "date": today(), "count": (data.get("meta") or {}).get("count", NR),
            "results": [openalex_work_summary(w) for w in data.get("results", [])]}


def openalex_chase(direction: str, doi: str, limit=25) -> dict:
    seed = http_get_json(f"{OPENALEX}/works/doi:{norm_doi(doi)}")
    seed_id = seed.get("id", "").rsplit("/", 1)[-1]
    if direction == "forward":
        url = f"{OPENALEX}/works?" + urllib.parse.urlencode({"filter": f"cites:{seed_id}", "per-page": str(limit)})
        data = http_get_json(url)
        return {"seed": openalex_work_summary(seed), "direction": direction, "url": url, "date": today(),
                "count": (data.get("meta") or {}).get("count", NR),
                "results": [openalex_work_summary(w) for w in data.get("results", [])]}
    key = "referenced_works" if direction == "backward" else "related_works"
    ids = [x.rsplit("/", 1)[-1] for x in seed.get(key, [])]
    results = []
    for i in range(0, min(len(ids), limit), 50):
        chunk = ids[i:min(i + 50, limit)]
        url = f"{OPENALEX}/works?" + urllib.parse.urlencode({"filter": "openalex_id:" + "|".join(chunk), "per-page": "50"})
        results += [openalex_work_summary(w) for w in http_get_json(url).get("results", [])]
    return {"seed": openalex_work_summary(seed), "direction": direction, "date": today(),
            "count": len(ids), "results": results}


def render_works(payload: dict, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    out = []
    if "seed" in payload:
        s = payload["seed"]
        out.append(f"Semente: {s['title']} ({s['year']}) DOI {s['doi']} — direção: {payload['direction']}")
    out.append(f"Fonte: OpenAlex · data: {payload['date']} · total reportado: {payload['count']}")
    out += ["", "| # | Ano | Título | Autores | Veículo | DOI | Citações (OpenAlex) |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(payload["results"], 1):
        auth = r["authors"][0] + (" et al." if len(r["authors"]) > 1 else "")
        out.append(f"| {i} | {r['year']} | {str(r['title']).replace('|', '/')} | {auth} | {r['venue']} | {r['doi']} | {r['cited_by_count']} |")
    out.append("\n_Registros retornados pela API; metadados ainda UNVERIFIED até conferência de DOI._")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------------------

PROJECT_DIRS = ["search", "screening", "sources", "extraction", "ledger", "matrix", "appraisal", "synthesis",
                "manuscript", "audit", "data/raw", "data/derived", "analysis"]


def init_project(target: str) -> list[str]:
    root = pathlib.Path(target) / "research"
    created = []
    for d in PROJECT_DIRS:
        p = root / d
        if not p.exists():
            p.mkdir(parents=True)
            created.append(str(p))
    copies = {
        "research-protocol.md": root / "protocol.md",
        "search-log.json": root / "search" / "search-log.json",
        "search-log.md": root / "search" / "search-log.md",
        "inclusion-exclusion-criteria.md": root / "protocol-criteria.md",
        "screening.csv": root / "screening" / "screening.csv",
        "sources.json": root / "sources" / "sources.json",
        "analysis-run-log.md": root / "analysis" / "analysis-run-log.md",
    }
    for tpl, dest in copies.items():
        if not dest.exists() and (TEMPLATE_DIR / tpl).exists():
            shutil.copy(TEMPLATE_DIR / tpl, dest)
            created.append(str(dest))
    ledger = root / "ledger" / "evidence.jsonl"
    if not ledger.exists():
        ledger.touch()
        created.append(str(ledger))
    readme = root / "data" / "raw" / "README.md"
    if not readme.exists():
        readme.write_text("# Dados brutos (imutáveis)\n\nNão edite arquivos desta pasta. Transformações vão para "
                          "`../derived/` por meio de scripts versionados em `../../analysis/`.\n", encoding="utf-8")
        created.append(str(readme))
    return created


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _write(text: str, out: str | None):
    if out:
        pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(out).write_text(text, encoding="utf-8")
        print(f"salvo em {out}")
    else:
        sys.stdout.write(text)


def main(argv=None) -> int:
    global _FIXTURES
    p = argparse.ArgumentParser(prog="srtool", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fixture", help="JSON com respostas simuladas de rede (testes offline)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init"); s.add_argument("dir")
    s = sub.add_parser("validate"); s.add_argument("kind", choices=["sources", "extraction", "ledger", "searchlog", "audit", "project"])
    s.add_argument("paths", nargs="+"); s.add_argument("--sources")
    s = sub.add_parser("matrix"); s.add_argument("inputs", nargs="+"); s.add_argument("--sources")
    s.add_argument("--format", choices=["md", "csv", "json"], default="md"); s.add_argument("--detailed", action="store_true"); s.add_argument("--out")
    s = sub.add_parser("doi-check"); s.add_argument("doi"); s.add_argument("--title"); s.add_argument("--authors", help="sobrenomes separados por ';'")
    s.add_argument("--year"); s.add_argument("--journal"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("refs-check"); s.add_argument("sources"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("dedupe"); s.add_argument("file")
    s = sub.add_parser("scan"); s.add_argument("manuscript"); s.add_argument("--ledger"); s.add_argument("--sources")
    s.add_argument("--context", help="contexto-alvo do manuscrito, ex.: 'Brasil'"); s.add_argument("--format", choices=["md", "json"], default="md"); s.add_argument("--out")
    s = sub.add_parser("trace"); s.add_argument("target"); s.add_argument("--ledger", required=True); s.add_argument("--sources"); s.add_argument("--manuscript")
    s = sub.add_parser("format"); s.add_argument("sources"); s.add_argument("--style", choices=["abnt", "apa", "chicago", "bibtex"], required=True)
    s.add_argument("--include-partial", action="store_true", help="inclui PARTIALLY_VERIFIED (campos ausentes ficam de fora)"); s.add_argument("--out")
    s = sub.add_parser("prisma"); s.add_argument("searchlog"); s.add_argument("--out")
    s = sub.add_parser("search-openalex"); s.add_argument("query"); s.add_argument("--per-page", type=int, default=25)
    s.add_argument("--from-year"); s.add_argument("--to-year"); s.add_argument("--format", choices=["md", "json"], default="md")
    s = sub.add_parser("chase"); s.add_argument("direction", choices=["backward", "forward", "similar"]); s.add_argument("doi")
    s.add_argument("--limit", type=int, default=25); s.add_argument("--format", choices=["md", "json"], default="md")

    a = p.parse_args(argv)
    if a.fixture:
        _FIXTURES = load_json(a.fixture)

    if a.cmd == "init":
        created = init_project(a.dir)
        print("\n".join(created) if created else "estrutura já existia; nada criado")
        return 0
    if a.cmd == "validate":
        ok = True
        for path in a.paths:
            if a.kind == "extraction" and pathlib.Path(path).is_dir():
                files = sorted(pathlib.Path(path).glob("*.json"))
            else:
                files = [path]
            for f in files:
                rep = {"sources": validate_sources, "extraction": validate_extraction, "searchlog": validate_searchlog,
                       "audit": validate_audit, "project": validate_project}.get(a.kind)
                r = validate_ledger(f, a.sources) if a.kind == "ledger" else rep(f)
                print(r.render())
                ok &= r.ok
        return 0 if ok else 1
    if a.cmd == "matrix":
        files = []
        for inp in a.inputs:
            pth = pathlib.Path(inp)
            files += sorted(pth.glob("*.json")) if pth.is_dir() else [pth]
        exts = [load_json(f) for f in files]
        rows = build_matrix(exts, _load_sources_index(a.sources), a.detailed)
        cols = COMPACT_COLS + (DETAILED_EXTRA if a.detailed else [])
        _write(render_rows(rows, cols, a.format), a.out)
        return 0
    if a.cmd == "doi-check":
        authors = [x.strip() for x in a.authors.split(";")] if a.authors else None
        res = doi_check(a.doi, a.title, authors, a.year, a.journal)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"DOI {res['doi']}: {res['status']} — {res['verdict']}")
            if res["flags"]:
                print("  sinais: " + ", ".join(res["flags"]))
            for k, v in res["comparisons"].items():
                print(f"  {k}: {v}")
            print(f"  conferido em: {', '.join(res['checked_against'])} ({res['checked_on']})")
        return 0 if res["status"] in ("VERIFIED", "PARTIALLY_VERIFIED") else 2
    if a.cmd == "refs-check":
        res = refs_check(a.sources)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print("| source_id | DOI | status | veredito | sinais |\n|---|---|---|---|---|")
            for r in res:
                print(f"| {r.get('source_id')} | {r.get('doi')} | {r['status']} | {r['verdict']} | {', '.join(r.get('flags', []))} |")
        return 0 if all(r["status"] in ("VERIFIED", "PARTIALLY_VERIFIED") for r in res) else 2
    if a.cmd == "dedupe":
        data = load_json(a.file)
        items = data.get("sources", data.get("records", [])) if isinstance(data, dict) else data
        dups = find_duplicates(items)
        if not dups:
            print("Nenhuma duplicata por DOI ou título+ano.")
        for key, ids in dups:
            print(f"DUPLICATA {key}: {', '.join(ids)}")
        return 0
    if a.cmd == "scan":
        text = pathlib.Path(a.manuscript).read_text(encoding="utf-8")
        ledger = load_ledger_index(a.ledger) if a.ledger else None
        sources = _load_sources_index(a.sources)
        findings = scan_manuscript(text, ledger, sources, a.context)
        _write(render_findings(findings, a.format), a.out)
        return 1 if any(f["severity"] == "CRÍTICO" for f in findings) else 0
    if a.cmd == "trace":
        text = pathlib.Path(a.manuscript).read_text(encoding="utf-8") if a.manuscript else None
        sys.stdout.write(trace(a.target, load_ledger_index(a.ledger), _load_sources_index(a.sources), text))
        return 0
    if a.cmd == "format":
        data = load_json(a.sources)
        allowed = {"VERIFIED"} | ({"PARTIALLY_VERIFIED"} if a.include_partial else set())
        out, skipped = [], []
        for src in data.get("sources", []):
            st = (src.get("metadata_verification") or {}).get("status")
            if st in allowed:
                out.append(format_reference(src, a.style))
            else:
                skipped.append(f"{src.get('source_id')} ({st})")
        text = ("\n\n" if a.style == "bibtex" else "\n\n").join(sorted(out)) + "\n"
        if skipped:
            text += ("\n% " if a.style == "bibtex" else "\n<!-- ") + "não formatadas por falta de verificação: " + \
                    ", ".join(skipped) + ("" if a.style == "bibtex" else " -->") + "\n"
        _write(text, a.out)
        return 0
    if a.cmd == "prisma":
        log = load_json(a.searchlog)
        rep = prisma_check(log)
        text = render_prisma(log) + "\n" + rep.render().replace("== ", "### ") + "\n"
        _write(text, a.out)
        return 0 if rep.ok else 1
    try:
        if a.cmd == "search-openalex":
            sys.stdout.write(render_works(openalex_search(a.query, a.per_page, a.from_year, a.to_year), a.format))
            return 0
        if a.cmd == "chase":
            sys.stdout.write(render_works(openalex_chase(a.direction, a.doi, a.limit), a.format))
            return 0
    except (NetworkError, NotFound) as exc:
        print(f"{MSG_UNVERIFIABLE} Busca não executada: {exc}", file=sys.stderr)
        return 3
    return 1


if __name__ == "__main__":
    sys.exit(main())
