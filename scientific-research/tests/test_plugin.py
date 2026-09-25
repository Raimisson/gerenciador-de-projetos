"""Testes do plugin Scientific Research (somente biblioteca padrão).

Executar a partir da raiz do plugin:
    python3 -m unittest discover -s tests -v

Testes que dependem do Claude Code CLI (`claude plugin validate`) são pulados se o CLI
não estiver instalado. O teste de carga real (skills/agentes num `claude -p`) está em
tests/cli_smoke_test.sh, por consumir chamadas de modelo.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
FIX = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(ROOT / "scripts"))
import srtool  # noqa: E402

NR = srtool.NR
SKILLS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
AGENTS = sorted(p.stem for p in (ROOT / "agents").glob("*.md"))
EXPECTED_SKILLS = {
    "research-project", "research-question", "literature-search", "citation-chasing", "grey-literature",
    "systematic-review", "evidence-extraction", "evidence-ledger", "evidence-matrix", "methodology-review",
    "quantitative-evidence", "evidence-synthesis", "regulatory-research", "scientific-writing",
    "citation-audit", "bibliography-audit", "replication-check", "manuscript-review",
}
EXPECTED_AGENTS = {"literature-researcher", "methodology-reviewer", "citation-auditor", "scientific-editor",
                   "quantitative-analyst", "regulatory-researcher", "publication-strategist"}
KNOWN_TOOLS = {"Read", "Write", "Edit", "MultiEdit", "NotebookEdit", "Grep", "Glob", "Bash", "WebSearch", "WebFetch",
               "Agent", "Skill", "TodoWrite"}
INTEGRITY_PHRASES = [
    "Não foi possível verificar esta informação nas fontes consultadas.",
    "Não foi encontrada evidência quantitativa que permita estimar este parâmetro.",
    "NR — não reportado",
]
CLAUDE = shutil.which("claude")


def frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise AssertionError(f"{path}: frontmatter ausente")
    data = {}
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z][\w-]*:", line):
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip().strip('"')
    return data


def run(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def srtool_cli(*args, fixture=True):
    base = [sys.executable, str(ROOT / "scripts" / "srtool.py")]
    if fixture:
        base += ["--fixture", str(FIX / "network-fixtures.json")]
    return run(base + list(args))


# ---------------------------------------------------------------------------------------
# 1–2. Skills encontradas e carregáveis
# ---------------------------------------------------------------------------------------
class TestSkills(unittest.TestCase):
    def test_01_all_expected_skills_found(self):
        self.assertEqual(set(SKILLS), EXPECTED_SKILLS)

    def test_02_skill_frontmatter_valid(self):
        for name in SKILLS:
            fm = frontmatter(ROOT / "skills" / name / "SKILL.md")
            self.assertEqual(fm.get("name"), name, f"{name}: 'name' deve igualar o diretório")
            self.assertGreater(len(fm.get("description", "")), 80, f"{name}: description curta demais para acionamento")
            self.assertLessEqual(len(fm.get("description", "")), 1024, f"{name}: description longa demais")

    def test_02b_skill_required_sections(self):
        required = ["## Quando usar", "## Quando NÃO usar", "## Inputs esperados", "## Workflow",
                    "## Output esperado", "## Critérios de qualidade", "## Situações de falha"]
        for name in SKILLS:
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            for sec in required:
                if name == "evidence-ledger" and sec in ("## Inputs esperados", "## Output esperado"):
                    continue  # ledger documenta campos e operações em seções próprias
                self.assertIn(sec, text, f"{name}: seção ausente {sec}")

    @unittest.skipUnless(CLAUDE, "Claude Code CLI não instalado")
    def test_02c_claude_validates_skills_dir(self):
        r = run([CLAUDE, "plugin", "validate", str(ROOT / "skills"), "--strict"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


# ---------------------------------------------------------------------------------------
# 3. Agentes
# ---------------------------------------------------------------------------------------
class TestAgents(unittest.TestCase):
    def test_03_agents_found_and_valid(self):
        self.assertEqual(set(AGENTS), EXPECTED_AGENTS)
        for name in AGENTS:
            fm = frontmatter(ROOT / "agents" / f"{name}.md")
            self.assertEqual(fm.get("name"), name)
            self.assertTrue(fm.get("description"))
            for key in ("tools", "disallowedTools"):
                if key in fm:
                    tools = {t.strip() for t in fm[key].split(",") if t.strip()}
                    self.assertTrue(tools <= KNOWN_TOOLS, f"{name}.{key}: ferramentas desconhecidas {tools - KNOWN_TOOLS}")

    def test_03b_scientific_editor_has_no_web_access(self):
        fm = frontmatter(ROOT / "agents" / "scientific-editor.md")
        tools = {t.strip() for t in fm["tools"].split(",")}
        self.assertFalse(tools & {"WebSearch", "WebFetch"}, "scientific-editor não pode buscar fatos novos")

    def test_03c_auditors_are_read_only(self):
        for name in ("citation-auditor", "methodology-reviewer"):
            fm = frontmatter(ROOT / "agents" / f"{name}.md")
            self.assertIn("Write", fm.get("disallowedTools", ""))

    @unittest.skipUnless(CLAUDE, "Claude Code CLI não instalado")
    def test_03d_claude_validates_agents_dir(self):
        r = run([CLAUDE, "plugin", "validate", str(ROOT / "agents"), "--strict"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


# ---------------------------------------------------------------------------------------
# 4–5. Manifesto e instalabilidade
# ---------------------------------------------------------------------------------------
class TestManifest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

    def test_04_manifest_fields(self):
        self.assertRegex(self.manifest["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertEqual(self.manifest["name"], "scientific-research")
        self.assertRegex(self.manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(self.manifest["version"], "0.2.2")

    def test_04b_changelog_matches_version(self):
        self.assertIn(f"[{self.manifest['version']}]", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    @unittest.skipUnless(CLAUDE, "Claude Code CLI não instalado")
    def test_04c_claude_plugin_validate_strict(self):
        r = run([CLAUDE, "plugin", "validate", str(ROOT), "--strict"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_05_marketplace_entry_points_to_plugin(self):
        mp_path = REPO / ".claude-plugin" / "marketplace.json"
        self.assertTrue(mp_path.exists(), "marketplace.json ausente na raiz do repositório")
        mp = json.loads(mp_path.read_text(encoding="utf-8"))
        entry = next(p for p in mp["plugins"] if p["name"] == self.manifest["name"])
        self.assertTrue(entry["source"].startswith("./"))
        self.assertEqual((REPO / entry["source"]).resolve(), ROOT)
        self.assertEqual(entry.get("version", self.manifest["version"]), self.manifest["version"])

    @unittest.skipUnless(CLAUDE, "Claude Code CLI não instalado")
    def test_05b_claude_validates_marketplace(self):
        r = run([CLAUDE, "plugin", "validate", str(REPO), "--strict"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


# ---------------------------------------------------------------------------------------
# 6. Links, configurações e segurança
# ---------------------------------------------------------------------------------------
class TestLinksAndConfig(unittest.TestCase):
    def _md_files(self):
        return [p for p in ROOT.rglob("*.md") if "results" not in p.parts]

    def test_06_relative_markdown_links_resolve(self):
        bad = []
        for md in self._md_files():
            for target in re.findall(r"\]\((?!https?://|mailto:|#)([^)\s]+)\)", md.read_text(encoding="utf-8")):
                path = (md.parent / target.split("#")[0]).resolve()
                if not path.exists():
                    bad.append(f"{md.relative_to(ROOT)} → {target}")
        self.assertFalse(bad, "links quebrados:\n" + "\n".join(bad))

    def test_06b_plugin_root_references_exist(self):
        bad = []
        for f in list((ROOT / "skills").rglob("*.md")) + list((ROOT / "modules").rglob("SKILL.md")) + list((ROOT / "agents").glob("*.md")):
            for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", f.read_text(encoding="utf-8")):
                if not (ROOT / ref.rstrip(".")).exists():
                    bad.append(f"{f.relative_to(ROOT)} → {ref}")
        self.assertFalse(bad, "referências inexistentes:\n" + "\n".join(bad))

    def test_06c_hooks_reference_existing_scripts(self):
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        for event, groups in hooks["hooks"].items():
            for g in groups:
                for h in g["hooks"]:
                    for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", h["command"]):
                        self.assertTrue((ROOT / ref).exists(), f"{event}: {ref} não existe")

    def test_06d_no_active_mcp_config_and_urls_allowlisted(self):
        self.assertFalse((ROOT / ".mcp.json").exists(), "o plugin não deve ativar MCPs por padrão (ver docs/connectors.md)")
        allowed = {"https://mcp.consensus.app/mcp", "https://api.scite.ai/mcp", "https://elicit.com/api/mcp",
                   "https://drivemcp.googleapis.com/mcp/v1"}
        cfg = json.loads((ROOT / "connectors" / "mcp-servers.optional.json").read_text(encoding="utf-8"))
        urls = {v["url"] for v in cfg["mcpServers"].values()}
        self.assertEqual(urls, allowed)

    def test_06e_no_secrets_committed(self):
        patterns = [r"sk-[A-Za-z0-9]{20,}", r"ghp_[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"xox[bp]-[A-Za-z0-9-]{10,}",
                    r"(?i)(api[_-]?key|token|secret|password)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,}"]
        offenders = []
        for f in ROOT.rglob("*"):
            if f.is_file() and f.suffix in {".md", ".json", ".jsonl", ".py", ".sh", ".example", ".csv", ".txt", ""}:
                text = f.read_text(encoding="utf-8", errors="ignore")
                for pat in patterns:
                    if re.search(pat, text):
                        offenders.append(f"{f.relative_to(ROOT)} ~ {pat}")
        self.assertFalse(offenders, "\n".join(offenders))
        self.assertFalse([p for p in ROOT.rglob(".env") if p.is_file()], ".env não pode estar no repositório")

    def test_06f_no_personal_tracking_urls_in_examples(self):
        for f in (ROOT / "examples").rglob("*"):
            if f.is_file():
                self.assertNotIn("email=", f.read_text(encoding="utf-8", errors="ignore"), f"{f}: URL com e-mail")

    def test_06g_json_files_parse(self):
        for f in ROOT.rglob("*.json"):
            json.loads(f.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------
# 7. Extração respeita NR
# ---------------------------------------------------------------------------------------
class TestExtractionNR(unittest.TestCase):
    def test_07_good_extraction_passes(self):
        r = srtool.validate_extraction(FIX / "extraction-good.json")
        self.assertTrue(r.ok, r.render())

    def test_07b_bad_extraction_rejected_with_specific_errors(self):
        r = srtool.validate_extraction(FIX / "extraction-bad.json")
        text = "\n".join(r.errors)
        self.assertFalse(r.ok)
        self.assertIn("sample_size", text)                  # string vazia
        self.assertIn("population", text)                   # null
        self.assertIn("marcador informal", text)            # "n/a"
        self.assertIn("limitations", text)                  # campo ausente
        self.assertIn("descrição qualitativa", text)        # "significant improvement" em campo numérico
        self.assertIn("número sem localização", text)
        self.assertIn("número sem trecho", text)

    def test_07c_matrix_preserves_nr(self):
        ex = json.loads((FIX / "extraction-good.json").read_text(encoding="utf-8"))
        rows = srtool.build_matrix([ex], None, detailed=True)
        qual = rows[1]
        self.assertEqual(qual["Estimate"], NR)
        self.assertEqual(qual["SE/CI"], NR)
        self.assertIn("sem valor reportado", qual["Significance"])
        self.assertEqual(rows[0]["Estimate"], "-0.021 log kWh")

    def test_07d_matrix_exports(self):
        with tempfile.TemporaryDirectory() as d:
            for fmt in ("md", "csv", "json"):
                out = pathlib.Path(d) / f"m.{fmt}"
                r = srtool_cli("matrix", str(FIX / "extraction-good.json"), "--format", fmt, "--out", str(out), fixture=False)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn("-0.021", out.read_text(encoding="utf-8"))
            json.loads((pathlib.Path(d) / "m.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------
# 8. Auditoria de citação detecta DOI falso
# ---------------------------------------------------------------------------------------
class TestFakeReference(unittest.TestCase):
    def setUp(self):
        srtool._FIXTURES = json.loads((FIX / "network-fixtures.json").read_text(encoding="utf-8"))

    def tearDown(self):
        srtool._FIXTURES = None

    def test_08_fake_doi_rejected(self):
        res = srtool.doi_check("10.9999/jiee.2019.0457", title="Revenue decoupling and utility energy efficiency spending: a global meta-analysis", year=2019)
        self.assertEqual(res["status"], "CONTRADICTED")
        self.assertIn("POSSIVELMENTE_INVENTADA", res["flags"])

    def test_08b_doi_pointing_to_other_work_rejected(self):
        res = srtool.doi_check("10.5555/sr-test.0001", title="Revenue decoupling and utility energy efficiency spending", authors=["Silva"], year=2019)
        self.assertEqual(res["status"], "CONTRADICTED")
        self.assertIn("TITULO_INCOMPATIVEL", res["flags"])
        self.assertIn("AUTORES_INCOMPATIVEIS", res["flags"])

    def test_08c_matching_doi_verified(self):
        res = srtool.doi_check("10.5555/sr-test.0001", title="Synthetic test record for the Scientific Research plugin",
                               authors=["Tester", "Fixture"], year=2020, journal="Journal of Test Fixtures")
        self.assertEqual(res["status"], "VERIFIED")

    def test_08d_refs_check_flags_fake_in_list(self):
        res = {r["source_id"]: r for r in srtool.refs_check(FIX / "fake-reference-sources.json")}
        self.assertEqual(res["S-0001"]["status"], "CONTRADICTED")
        self.assertEqual(res["S-0002"]["status"], "VERIFIED")

    def test_08e_invalid_doi_syntax(self):
        self.assertEqual(srtool.doi_check("not-a-doi")["status"], "CONTRADICTED")

    def test_08f_cli_exit_code(self):
        r = srtool_cli("doi-check", "10.9999/jiee.2019.0457")
        self.assertEqual(r.returncode, 2)
        self.assertIn("POSSIVELMENTE_INVENTADA", r.stdout)


# ---------------------------------------------------------------------------------------
# 9. Regra de não fabricação
# ---------------------------------------------------------------------------------------
class TestNoFabrication(unittest.TestCase):
    def test_09_integrity_block_synced_everywhere(self):
        r = run([sys.executable, str(ROOT / "scripts" / "sync_integrity.py"), "--check"])
        self.assertEqual(r.returncode, 0, r.stderr)
        for f in list((ROOT / "skills").glob("*/SKILL.md")) + list((ROOT / "modules").glob("*/skills/*/SKILL.md")) + list((ROOT / "agents").glob("*.md")):
            text = f.read_text(encoding="utf-8")
            for phrase in INTEGRITY_PHRASES:
                self.assertIn(phrase, text, f"{f.relative_to(ROOT)} sem a frase obrigatória: {phrase}")

    def test_09b_network_failure_never_verifies(self):
        srtool._FIXTURES = json.loads((FIX / "network-fixtures.json").read_text(encoding="utf-8"))
        try:
            res = srtool.doi_check("10.5555/sr-test.0002", title="qualquer")
            self.assertEqual(res["status"], "UNVERIFIED")
            self.assertIn(srtool.MSG_UNVERIFIABLE, res["verdict"])
            res = srtool.doi_check("10.5555/nao-esta-na-fixture")
            self.assertEqual(res["status"], "UNVERIFIED")
        finally:
            srtool._FIXTURES = None

    def test_09c_formatter_refuses_unverified(self):
        with tempfile.TemporaryDirectory() as d:
            out = pathlib.Path(d) / "refs.txt"
            r = srtool_cli("format", str(FIX / "fake-reference-sources.json"), "--style", "abnt", "--out", str(out), fixture=False)
            self.assertEqual(r.returncode, 0)
            text = out.read_text(encoding="utf-8")
            self.assertNotIn("Imaginary", text.split("<!--")[0])
            self.assertIn("não formatadas por falta de verificação", text)

    def test_09d_scan_flags_unsourced_and_unknown_evidence(self):
        ledger = srtool.load_ledger_index(FIX / "ledger-good.jsonl")
        text = (FIX / "manuscript-issues.md").read_text(encoding="utf-8")
        findings = srtool.scan_manuscript(text, ledger, None)
        codes = [(f["paragraph"], f["code"]) for f in findings]
        self.assertIn(("P-001", "NUMERO-SEM-FONTE"), codes)          # 3,2% sem fonte
        self.assertIn(("P-001", "CAUSAL-INDEVIDA"), codes)           # "reduziu" com evidência associativa
        self.assertIn(("P-002", "EVIDENCIA-INEXISTENTE"), codes)     # E-0099
        self.assertIn(("P-002", "GENERALIZACAO"), codes)             # Brasil × evidência dos EUA
        self.assertNotIn(("P-003", "CAUSAL-INDEVIDA"), codes)        # frase negativa não é causal
        self.assertFalse([c for c in codes if c[0] not in ("P-001", "P-002", "P-003")], "lista de referências não deve ser varrida")

    def test_09e_ledger_validation(self):
        self.assertTrue(srtool.validate_ledger(FIX / "ledger-good.jsonl").ok)
        r = srtool.validate_ledger(FIX / "ledger-bad.jsonl", FIX / "fake-reference-sources.json")
        text = "\n".join(r.errors)
        for expected in ("duplicado", "S-9999", "derived_from", "MAYBE", "qualitativo", "JSON inválido"):
            self.assertIn(expected, text)

    def test_09f_searchlog_arithmetic_and_unexecuted_counts(self):
        r = srtool.validate_searchlog(FIX / "searchlog-bad.json")
        text = "\n".join(r.errors)
        self.assertIn("não executada", text)
        self.assertIn("identificados (10) − duplicatas (2) ≠ triados (9)", text)
        self.assertIn("≠ incluídos", text)

    def test_09g_trace_answers_where_claim_came_from(self):
        ledger = srtool.load_ledger_index(FIX / "ledger-good.jsonl")
        sources = srtool._load_sources_index(FIX / "fake-reference-sources.json")
        out = srtool.trace("P-001", ledger, sources, (FIX / "manuscript-issues.md").read_text(encoding="utf-8"))
        self.assertIn("E-0001", out)
        self.assertIn("Table 3 reports a coefficient of -0.021", out)
        self.assertIn("Synthetic test record", out)


# ---------------------------------------------------------------------------------------
# 10. Operação sem conectores opcionais
# ---------------------------------------------------------------------------------------
class TestWithoutConnectors(unittest.TestCase):
    def test_10_search_skills_document_degraded_mode(self):
        for name in ("literature-search", "citation-chasing", "grey-literature", "research-project"):
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8").lower()
            self.assertTrue(any(k in text for k in ("sem conectores", "sem ferramentas", "nenhum conector")),
                            f"{name}: modo degradado não documentado")

    def test_10b_local_tools_work_offline(self):
        with tempfile.TemporaryDirectory() as d:
            r = srtool_cli("init", d, fixture=False)
            self.assertEqual(r.returncode, 0, r.stderr)
            proj = pathlib.Path(d) / "research"
            self.assertTrue((proj / "ledger" / "evidence.jsonl").exists())
            self.assertTrue((proj / "data" / "raw" / "README.md").exists())
            r = srtool_cli("validate", "project", str(proj), fixture=False)
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_10c_network_commands_fail_gracefully(self):
        r = srtool_cli("chase", "forward", "10.5555/nao-esta-na-fixture")
        self.assertEqual(r.returncode, 3)
        self.assertIn(srtool.MSG_UNVERIFIABLE, r.stderr)

    def test_10d_examples_validate(self):
        for ex in sorted((ROOT / "examples").glob("0*/research")):
            r = srtool.validate_project(ex)
            self.assertTrue(r.ok, r.render())


# ---------------------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------------------
class TestHooks(unittest.TestCase):
    def _hook(self, script, payload):
        r = run([sys.executable, str(ROOT / "hooks" / script)], input=json.dumps(payload))
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout) if r.stdout.strip() else None

    def test_hook_raw_data_asks(self):
        out = self._hook("protect_raw_data.py", {"tool_name": "Edit", "tool_input": {"file_path": "/p/research/data/raw/base.csv"}})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")
        self.assertIsNone(self._hook("protect_raw_data.py", {"tool_name": "Write", "tool_input": {"file_path": "/p/research/data/derived/x.csv"}}))

    def test_hook_zotero_write_asks_read_passes(self):
        out = self._hook("guard_library_writes.py", {"tool_name": "mcp__zotero__zotero_add_items_by_doi"})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")
        self.assertIsNone(self._hook("guard_library_writes.py", {"tool_name": "mcp__zotero__zotero_search_items"}))
        self.assertIsNone(self._hook("guard_library_writes.py", {"tool_name": "mcp__Scite__search_literature"}))
        self.assertIsNone(self._hook("guard_library_writes.py", {"tool_name": "mcp__github__create_branch"}))
        out = self._hook("guard_library_writes.py", {"tool_name": "mcp__plugin_x_scite__create_collection"})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_hook_session_start_context(self):
        out = self._hook("session_start.py", {"hook_event_name": "SessionStart"})
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Não foi possível verificar", ctx)
        self.assertLess(len(ctx.split()), 150)

    def test_hook_tolerates_garbage_input(self):
        r = run([sys.executable, str(ROOT / "hooks" / "guard_library_writes.py")], input="not json")
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
