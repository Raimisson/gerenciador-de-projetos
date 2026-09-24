"""Testes do módulo Publication Strategy (somente biblioteca padrão).

    python3 -m unittest discover -s tests -v
"""
import copy
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOD = ROOT / "modules" / "publication-strategy"
EX4 = ROOT / "examples" / "04-publication-strategy" / "research"
sys.path.insert(0, str(MOD / "scripts"))
import pubtool  # noqa: E402
import srtool  # noqa: E402  (importado por pubtool)

CLAUDE = shutil.which("claude")
EXPECTED = {"journal-search", "journal-fit-analysis", "journal-recent-content-analysis", "journal-due-diligence",
            "journal-requirements", "manuscript-compliance", "publication-strategy", "submission-preparation",
            "cover-letter", "peer-review-response", "resubmission-strategy", "pre-submission-audit"}
TODAY = pubtool.today()

MANUSCRIPT = """# A short synthetic title

## Abstract

This synthetic abstract has exactly twelve words for the compliance unit test.

**Keywords:** alpha; beta; gamma

## Highlights

- First synthetic highlight
- Second synthetic highlight

## 1. Introduction

Body text of the synthetic manuscript used only in tests.

Figure 1. A synthetic figure caption.

Table 1. A synthetic table caption.

Table 2. Another synthetic table caption.

## Data availability

Data are available in the supplementary material.

## Funding

[AUTHORS: fill in]

## References

Ref one words here.
"""


def rule(rid, check, value=None, **kw):
    d = {"rule_id": rid, "category": rid, "requirement": f"req {rid}", "status": "VERIFIED", "check": check,
         "excerpt": f"excerpt {rid}", "source_url": "https://example.org/guide", "accessed_on": TODAY}
    if value is not None:
        d["value"] = value
    d.update(kw)
    return d


def requirements(rules, **kw):
    d = {"journal": "Test Journal", "publisher": "Test", "sources": [{"url": "https://example.org/guide", "accessed_on": TODAY}],
         "accessed_on": TODAY, "access_status": "ok", "article_type": "research article", "rules": rules}
    d.update(kw)
    return d


def write(path: pathlib.Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) if not isinstance(data, str) else data, encoding="utf-8")
    return path


def run_pubtool(*args):
    return subprocess.run([sys.executable, str(MOD / "scripts" / "pubtool.py"), *args], capture_output=True, text=True)


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    return {k.strip(): v.strip().strip('"') for k, _, v in (l.partition(":") for l in m.group(1).splitlines()) if v}


class TestModuleStructure(unittest.TestCase):
    def test_skills_found_and_valid(self):
        found = {p.parent.name for p in (MOD / "skills").glob("*/SKILL.md")}
        self.assertEqual(found, EXPECTED)
        for name in found:
            path = MOD / "skills" / name / "SKILL.md"
            fm = frontmatter(path)
            self.assertEqual(fm["name"], name)
            text = path.read_text(encoding="utf-8")
            for sec in ("## Quando usar", "## Quando NÃO usar", "## Inputs esperados", "## Workflow",
                        "## Output esperado", "## Critérios de qualidade", "## Situações de falha"):
                self.assertIn(sec, text, f"{name}: {sec}")
            self.assertIn("Nunca estimar probabilidade de aceitação", text, f"{name}: bloco editorial ausente")
            self.assertIn("NR — não reportado", text, f"{name}: bloco científico ausente")

    def test_no_name_collision_with_core(self):
        core = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertFalse(core & EXPECTED)

    def test_manifest_loads_module(self):
        m = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn("./modules/publication-strategy/skills", m["skills"])
        self.assertIn("./skills", m["skills"])

    def test_agent_publication_strategist(self):
        path = ROOT / "agents" / "publication-strategist.md"
        text = path.read_text(encoding="utf-8")
        self.assertEqual(frontmatter(path)["name"], "publication-strategist")
        self.assertIn("Evidence Ledger", text)
        self.assertIn("Nunca estimar probabilidade de aceitação", text)

    def test_main_workflow_updated_in_order(self):
        text = (ROOT / "skills" / "research-project" / "SKILL.md").read_text(encoding="utf-8")
        stages = ["Research Question", "Protocol", "Literature Search", "Screening", "Evidence Extraction",
                  "Evidence Ledger", "Evidence Matrix", "Methodology Review", "Scientific Writing", "Citation Audit",
                  "Manuscript Review", "Journal Search", "Journal Fit Analysis", "Journal Selection", "Target Journal Mode",
                  "Manuscript Compliance", "Pre-Submission Audit", "Submission", "Peer Review Response", "Publication / Resubmission"]
        line = next(l for l in text.splitlines() if l.startswith("Research Question →") or "Research Question → Protocol" in l)
        flow = " ".join(text[text.index(line):].split("\n\n")[0].split())
        positions = [flow.index(s) for s in stages]
        self.assertEqual(positions, sorted(positions))

    def test_docs_and_templates_exist(self):
        for f in ("docs/publication-strategy.md", "modules/publication-strategy/README.md",
                  "modules/publication-strategy/templates/journal-fit-report.md"):
            self.assertTrue((ROOT / f).exists(), f)
        tpl = (MOD / "templates" / "journal-fit-report.md").read_text(encoding="utf-8")
        for field in ("JOURNAL", "PUBLISHER", "AIMS & SCOPE", "TOPIC FIT", "METHOD FIT", "AUDIENCE FIT", "RECENT ARTICLE FIT",
                      "ARTICLE TYPE FIT", "OPEN ACCESS", "APC", "INDEXING", "REVIEW TIME IF PUBLISHED",
                      "PUBLICATION TIME IF PUBLISHED", "KEY REQUIREMENTS", "SIMILAR ARTICLES", "RISKS", "EVIDENCE", "DATE VERIFIED"):
            self.assertIn(field, tpl)

    @unittest.skipUnless(CLAUDE, "Claude Code CLI não instalado")
    def test_claude_validates_module_skills(self):
        r = subprocess.run([CLAUDE, "plugin", "validate", str(MOD / "skills"), "--strict"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestJournalFit(unittest.TestCase):
    def setUp(self):
        self.fit = json.loads((EX4 / "publication" / "journals" / "utilities-policy" / "fit.json").read_text(encoding="utf-8"))

    def test_index_is_transparent_and_excludes_insufficient(self):
        idx = pubtool.fit_index(self.fit)
        self.assertEqual((idx["index"], idx["assessed"], idx["total"]), (67, 3, 7))  # (1+1+2)/(3*2)
        report = pubtool.render_fit_report(self.fit)
        self.assertIn("NÃO é probabilidade de aceitação", report)
        self.assertIn("cobertura: 3/7", report)
        for field in ("REVIEW TIME IF PUBLISHED", "DATE VERIFIED", "SIMILAR ARTICLES", "NOT VERIFIED"):
            self.assertIn(field, report)

    def test_probability_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            bad = copy.deepcopy(self.fit)
            bad["acceptance_probability"] = 0.8
            r = pubtool.validate("fit", write(pathlib.Path(d) / "f.json", bad))
            self.assertFalse(r.ok)
            bad = copy.deepcopy(self.fit)
            bad["notes"] = "Este artigo tem 80% de chance de aceitação."
            self.assertFalse(pubtool.validate("fit", write(pathlib.Path(d) / "g.json", bad)).ok)
            ok = copy.deepcopy(self.fit)
            ok["notes"] = "Nunca estimar probabilidade de aceitação."
            self.assertTrue(pubtool.validate("fit", write(pathlib.Path(d) / "h.json", ok)).ok)

    def test_rating_without_evidence_rejected(self):
        bad = copy.deepcopy(self.fit)
        bad["dimensions"]["audience_fit"] = {"rating": "STRONG", "justification": "nome do periódico sugere", "evidence": []}
        with tempfile.TemporaryDirectory() as d:
            r = pubtool.validate("fit", write(pathlib.Path(d) / "f.json", bad))
        self.assertFalse(r.ok)
        self.assertIn("sem evidência", "\n".join(r.errors))


class TestCompliance(unittest.TestCase):
    def setUp(self):
        self.ms = pubtool.Manuscript(MANUSCRIPT)

    def test_manuscript_parsing(self):
        self.assertEqual(self.ms.title, "A short synthetic title")
        self.assertEqual(pubtool.words(self.ms.abstract), 12)
        self.assertEqual(self.ms.keywords, ["alpha", "beta", "gamma"])
        self.assertEqual(len(self.ms.highlights), 2)
        self.assertEqual((self.ms.figures, self.ms.tables), (1, 2))
        self.assertEqual(set(self.ms.statements_found()), {"data_availability", "funding"})

    def test_statuses_and_action_fields(self):
        req = requirements([
            rule("ABS", "max_abstract_words", 10),
            rule("KW", "keywords_range", [3, 6]),
            rule("TAB", "max_tables", 1),
            rule("DATA", "required_statement", statement_kind="data_availability"),
            rule("FUND", "required_statement", statement_kind="funding"),
            rule("COI", "required_statement", statement_kind="competing_interests"),
            rule("LIM", "required_section", section_pattern="limitation"),
            rule("STYLE", "manual"),
            rule("SC", "manual", applicable=False),
            dict(rule("OLD", "max_figures", 5), status="NOT_VERIFIED"),
            rule("HL", "highlights", {"required": True, "min_items": 3, "max_items": 5, "max_chars_each": 85}),
        ])
        items = {i["rule_id"]: i for i in pubtool.check_compliance(self.ms, req)}
        expect = {"ABS": "ACTION_REQUIRED", "KW": "COMPLIANT", "TAB": "ACTION_REQUIRED", "DATA": "COMPLIANT",
                  "FUND": "ACTION_REQUIRED", "COI": "ACTION_REQUIRED", "LIM": "ACTION_REQUIRED", "STYLE": "UNABLE_TO_VERIFY",
                  "SC": "NOT_APPLICABLE", "OLD": "UNABLE_TO_VERIFY", "HL": "ACTION_REQUIRED"}
        self.assertEqual({k: v["status"] for k, v in items.items()}, expect)
        for it in items.values():
            if it["status"] == "ACTION_REQUIRED":
                for key in ("requirement", "current_state", "gap", "action", "source"):
                    self.assertTrue(it[key], f"{it['rule_id']} sem {key}")
                self.assertIn("https://example.org/guide", it["source"])
        self.assertIn("placeholder", items["FUND"]["current_state"])
        self.assertIn("Não exagerar", items["ABS"]["integrity_note"])

    def test_word_count_scope_ambiguity(self):
        a, b = self.ms.word_count(False), self.ms.word_count(True)
        self.assertLess(a, b)
        items = pubtool.check_compliance(self.ms, requirements([rule("W", "max_words", a, count_scope="unspecified")]))
        self.assertEqual(items[0]["status"], "UNABLE_TO_VERIFY")
        items = pubtool.check_compliance(self.ms, requirements([rule("W", "max_words", a, count_scope="main_text_excluding_references")]))
        self.assertEqual(items[0]["status"], "COMPLIANT")

    def test_manual_confirmation_applies_only_to_unverifiable(self):
        req = requirements([rule("STYLE", "manual")])
        items = pubtool.check_compliance(self.ms, req, {"STYLE": {"status": "COMPLIANT", "confirmed_by": "autor", "confirmed_on": TODAY}})
        self.assertEqual(items[0]["status"], "COMPLIANT")
        self.assertIn("confirmação manual", items[0]["current_state"])


class TestLintAndValidators(unittest.TestCase):
    def test_lint(self):
        text = ("Este artigo tem 80% de chance de aceitação.\nWe guarantee acceptance.\n"
                "Nunca estimar probabilidade de aceitação.\nThis is the first study to do so.\nYour prestigious journal.\n")
        codes = [(f["line"], f["code"], f["severity"]) for f in pubtool.lint_text(text)]
        self.assertIn((1, "PROBABILIDADE-DE-ACEITACAO", "ERRO"), codes)
        self.assertIn((2, "GARANTIA-DE-PUBLICACAO", "ERRO"), codes)
        self.assertFalse([c for c in codes if c[0] == 3], "frase negada não deve ser sinalizada")
        self.assertIn((4, "PRIMEIRO-A-SEM-VERIFICACAO", "AVISO"), codes)
        self.assertIn((5, "ELOGIO-GENERICO", "AVISO"), codes)

    def test_due_diligence_rules(self):
        dd = json.loads((EX4 / "publication" / "journals" / "utilities-policy" / "due-diligence.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(pubtool.validate("due-diligence", write(pathlib.Path(d) / "a.json", dd)).ok)
            bad = copy.deepcopy(dd)
            bad["conclusion_note"] = "Periódico predatório porque não está no Scopus."
            r = pubtool.validate("due-diligence", write(pathlib.Path(d) / "b.json", bad))
            self.assertFalse(r.ok)
            self.assertIn("3 alertas", "\n".join(r.errors))
            bad = copy.deepcopy(dd)
            bad["items"]["issn"] = {"status": "CONFIRMED"}
            self.assertFalse(pubtool.validate("due-diligence", write(pathlib.Path(d) / "c.json", bad)).ok)

    def test_requirements_rules(self):
        with tempfile.TemporaryDirectory() as d:
            bad = requirements([rule("A", "max_abstract_words", 200)], access_status="blocked")
            self.assertFalse(pubtool.validate("requirements", write(pathlib.Path(d) / "r.json", bad)).ok)
            bad = requirements([dict(rule("A", "max_abstract_words", 200), excerpt="")])
            self.assertFalse(pubtool.validate("requirements", write(pathlib.Path(d) / "s.json", bad)).ok)
            old = requirements([rule("A", "max_abstract_words", 200)], accessed_on="2020-01-01")
            r = run_pubtool("freshness", str(write(pathlib.Path(d) / "t.json", old)))
            self.assertEqual(r.returncode, 1)
            self.assertIn("DESATUALIZADO", r.stdout)

    def test_response_matrix_rules(self):
        base = json.loads((EX4 / "publication" / "peer-review" / "round-1" / "response-matrix.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(pubtool.validate("response", write(pathlib.Path(d) / "a.json", base)).ok)
            bad = copy.deepcopy(base)
            del bad["comments"][0]["justification"]
            self.assertFalse(pubtool.validate("response", write(pathlib.Path(d) / "b.json", bad)).ok)
            bad = copy.deepcopy(base)
            bad["comments"][1]["results_changed"] = True
            bad["comments"][1]["results_change_reason"] = "o revisor preferiu um efeito maior"
            self.assertFalse(pubtool.validate("response", write(pathlib.Path(d) / "c.json", bad)).ok)
            letter = pubtool.render_response(base)
            self.assertIn("NOT ACCEPTED", letter)
            self.assertIn("Justification", letter)


class TestTargetModeAndPresubmit(unittest.TestCase):
    def _project(self, d: pathlib.Path, complete: bool):
        r = d / "research"
        ms = MANUSCRIPT.replace("[AUTHORS: fill in]", "This work received no specific funding.") if complete else MANUSCRIPT
        if complete:
            ms = ms.replace("## References", "## Declaration of competing interest\n\nThe authors declare no competing interests.\n\n## References")
        write(r / "manuscript" / "manuscript.md", ms)
        write(r / "sources" / "sources.json", {"sources": [{"source_id": "S-0001", "source_type": "peer_reviewed_article", "authors": ["A, B"], "year": 2020,
               "title": "t", "container": "c", "doi": "10.5555/x", "url": "https://doi.org/10.5555/x", "peer_reviewed": True, "access_level": "full_text",
               "metadata_verification": {"status": "VERIFIED" if complete else "UNVERIFIED", "checked_against": ["Crossref"], "checked_on": TODAY}}]})
        write(r / "audit" / "citation-audit.json", {"manuscript": "m", "audited_on": TODAY, "claims": [
            {"claim_id": "C1", "sentence": "s", "location": "p", "cited_refs": ["S-0001"], "reference_existence": "VERIFIED",
             "classification": "SUPORTADA" if complete else "NÃO SUPORTADA", "issues": [], "justification": "j", "support_excerpt": "e"}]})
        rules = [rule("KW", "keywords_range", [3, 6]), rule("DATA", "required_statement", statement_kind="data_availability"),
                 rule("COVER", "keywords_range", [1, 9], file_required="cover-letter.md")]
        write(r / "publication" / "journals" / "tj" / "requirements.json", requirements(rules))
        sub = r / "publication" / "submission" / "tj"
        write(sub / "cover-letter.md", "Dear Editor,\n\nWe submit our manuscript.\n" if complete
              else "Dear Editor,\n\nOur paper has a 90% chance of acceptance in your prestigious journal.\n[AUTHORS: name]\n")
        return r

    def test_target_mode_set_show_clear(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._project(pathlib.Path(d), True)
            pub = r / "publication"
            self.assertNotEqual(run_pubtool("target", "set", str(pub), "--journal", "nao-existe").returncode, 0)
            out = run_pubtool("target", "set", str(pub), "--journal", "tj")
            self.assertEqual(out.returncode, 0, out.stderr)
            data = json.loads((pub / "target-journal.json").read_text(encoding="utf-8"))
            self.assertTrue(data["active"])
            self.assertEqual(len(data["integrity_limits"]), 5)
            self.assertTrue(pubtool.validate("target", pub / "target-journal.json").ok)
            self.assertIn('"slug": "tj"', run_pubtool("target", "show", str(pub)).stdout)
            run_pubtool("target", "clear", str(pub))
            self.assertIn("inativo", run_pubtool("target", "show", str(pub)).stdout)

    def test_presubmit_ready_only_without_pending(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._project(pathlib.Path(d), True)
            verdict, text = pubtool.presubmit(r, "tj", 30)
            self.assertEqual(verdict, "READY TO SUBMIT", text)

    def test_presubmit_action_required_lists_everything(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._project(pathlib.Path(d), False)
            verdict, text = pubtool.presubmit(r, "tj", 30)
            self.assertEqual(verdict, "ACTION REQUIRED")
            for expected in ("NÃO SUPORTADA", "UNVERIFIED", "competing_interests", "PROBABILIDADE-DE-ACEITACAO",
                             "ELOGIO-GENERICO", "placeholders", "'funding' com placeholder"):
                self.assertIn(expected, text)

    def test_presubmit_blocks_stale_or_synthetic_rules(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._project(pathlib.Path(d), True)
            f = r / "publication" / "journals" / "tj" / "requirements.json"
            req = json.loads(f.read_text(encoding="utf-8"))
            req["accessed_on"] = "2020-01-01"
            req["synthetic"] = True
            write(f, req)
            verdict, text = pubtool.presubmit(r, "tj", 30)
            self.assertEqual(verdict, "ACTION REQUIRED")
            self.assertIn("reconsultar o guia oficial", text)
            self.assertIn("SINTÉTICOS", text)

    def test_example_04_is_action_required_and_valid(self):
        pub = EX4 / "publication"
        checks = [("profile", "manuscript-profile.json"), ("candidates", "journals/candidates.json"),
                  ("recent", "journals/utilities-policy/recent-content.json"), ("recent", "journals/energy-policy/recent-content.json"),
                  ("fit", "journals/utilities-policy/fit.json"), ("fit", "journals/energy-policy/fit.json"),
                  ("due-diligence", "journals/utilities-policy/due-diligence.json"), ("requirements", "journals/utilities-policy/requirements.json"),
                  ("requirements", "journals/demo-synthetic-journal/requirements.json"), ("compliance", "compliance/utilities-policy.json"),
                  ("compliance", "compliance/demo-synthetic-journal.json"), ("response", "peer-review/round-1/response-matrix.json"),
                  ("target", "target-journal.json")]
        for kind, rel in checks:
            r = pubtool.validate(kind, pub / rel)
            self.assertTrue(r.ok, r.render())
        verdict, _ = pubtool.presubmit(EX4, "utilities-policy", 100000)
        self.assertEqual(verdict, "ACTION REQUIRED")
        for f in (pub / "strategy.md", pub / "submission" / "utilities-policy" / "cover-letter.md",
                  pub / "peer-review" / "round-1" / "response-letter.md", pub / "resubmission" / "plan-DEMO.md"):
            self.assertFalse([x for x in pubtool.lint_text(f.read_text(encoding="utf-8")) if x["severity"] == "ERRO"], f)


if __name__ == "__main__":
    unittest.main()
