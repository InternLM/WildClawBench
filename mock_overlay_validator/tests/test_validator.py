import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import validate as V


def _codes(report):
    return {(i.severity, i.code) for i in report.issues}


def _has_error(report, code):
    return any(i.severity == V.SEV_ERROR and i.code == code for i in report.issues)


def _has_warn(report, code):
    return any(i.severity == V.SEV_WARN and i.code == code for i in report.issues)


class CatalogTests(unittest.TestCase):
    def test_examples_cover_all_known_apis(self):
        apis = V.list_apis()
        self.assertGreaterEqual(len(apis), 100)
        for api in apis:
            self.assertTrue(
                (V.EXAMPLES_DIR / api).is_dir(),
                f"{api}: examples dir missing",
            )
            files = V.example_files_for_api(api)
            self.assertTrue(files, f"{api}: no example files")

    def test_gmail_example_lists_messages(self):
        files = V.example_files_for_api("gmail-api")
        self.assertIn("messages", files)


class HappyPathTests(unittest.TestCase):
    def test_baseline_example_validates_against_itself(self):
        ex = V.EXAMPLES_DIR / "gmail-api" / "messages.json"
        report = V.Report()
        V.validate_file(ex, "gmail-api", report)
        self.assertEqual(len(report.errors), 0, msg=str(report.issues))


class StructuralTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def _gmail_overlay(self, name, body):
        p = self.dir / name
        p.write_text(body, encoding="utf-8")
        return p

    def test_duplicate_header_is_error(self):
        p = self._gmail_overlay("messages.csv", "id,id\nA,B\n")
        report = V.Report()
        V.validate_file(p, "gmail-api", report)
        self.assertTrue(_has_error(report, "CSV_DUPLICATE_HEADER"))

    def test_ragged_row_is_error(self):
        p = self._gmail_overlay("messages.csv", "id,subject\nA,B,C\n")
        report = V.Report()
        V.validate_file(p, "gmail-api", report)
        self.assertTrue(_has_error(report, "CSV_RAGGED_ROW"))

    def test_malformed_json_is_error(self):
        p = self._gmail_overlay("messages.json", "{not json")
        report = V.Report()
        V.validate_file(p, "gmail-api", report)
        self.assertTrue(_has_error(report, "JSON_MALFORMED"))

    def test_json_object_for_table_is_error(self):
        p = self._gmail_overlay("messages.json", '{"id": "A"}')
        report = V.Report()
        V.validate_file(p, "gmail-api", report)
        self.assertTrue(_has_error(report, "JSON_NOT_ARRAY"))

    def test_unknown_extension_is_warn(self):
        p = self._gmail_overlay("messages.txt", "hi")
        report = V.Report()
        V.validate_file(p, "gmail-api", report)
        self.assertTrue(_has_warn(report, "UNKNOWN_EXTENSION"))


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_missing_column_is_error(self):
        ex = V.EXAMPLES_DIR / "gmail-api" / "messages.json"
        ex_rows = json.loads(ex.read_text())
        cols = list(ex_rows[0].keys())
        drop = cols[-1]
        keep = [c for c in cols if c != drop]
        body = ",".join(keep) + "\n"
        body += ",".join("x" for _ in keep) + "\n"
        p = self.dir / "messages.csv"
        p.write_text(body, encoding="utf-8")
        report = V.Report()
        V.validate_file(p, "gmail-api", report)
        self.assertTrue(_has_error(report, "SCHEMA_MISSING_COLUMNS"))

    def test_extra_column_is_warn(self):
        ex = V.EXAMPLES_DIR / "gmail-api" / "messages.json"
        ex_rows = json.loads(ex.read_text())
        cols = list(ex_rows[0].keys()) + ["totally_made_up_column"]
        body = ",".join(cols) + "\n" + ",".join("x" for _ in cols) + "\n"
        p = self.dir / "messages.csv"
        p.write_text(body, encoding="utf-8")
        report = V.Report()
        V.validate_file(p, "gmail-api", report)
        self.assertTrue(_has_warn(report, "SCHEMA_EXTRA_COLUMNS"))

    def test_unregistered_filename_is_warn(self):
        p = self.dir / "totally_unknown.csv"
        p.write_text("a,b\n1,2\n", encoding="utf-8")
        report = V.Report()
        V.validate_file(p, "gmail-api", report)
        self.assertTrue(_has_warn(report, "UNREGISTERED_FILENAME"))

    def test_unknown_api_is_error(self):
        p = self.dir / "messages.csv"
        p.write_text("a,b\n1,2\n", encoding="utf-8")
        report = V.Report()
        V.validate_file(p, "no-such-api", report)
        self.assertTrue(_has_error(report, "UNKNOWN_API"))


class WrappedTableTests(unittest.TestCase):
    def test_quickbooks_customers_treated_as_table(self):
        ex = V.EXAMPLES_DIR / "quickbooks-api" / "customers.json"
        self.assertFalse(V._example_is_document(ex))
        rows, issues = V._load_table(ex)
        self.assertIsNotNone(rows)
        self.assertGreater(len(rows), 0)


class DeepCompareTests(unittest.TestCase):
    def test_nested_key_missing_and_extra_in_document(self):
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "plaid-api"
            overlay_dir.mkdir()
            (overlay_dir / "identity.json").write_text(json.dumps({
                "owners": {"acc_pcu_chk_01": {}, "acc_pcu_sav_02": {}}
            }))
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "plaid-api", report)
            msgs = [i.message for i in report.issues]
            self.assertTrue(any("acc_chk_001" in m and "missing canonical key" in m for m in msgs))
            self.assertTrue(any("acc_pcu_chk_01" in m and "extra key" in m for m in msgs))

    def test_type_mismatch_scalar_vs_dict_in_array(self):
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "ring-api"
            overlay_dir.mkdir()
            ex = json.loads((V.EXAMPLES_DIR / "ring-api" / "devices.json").read_text())
            for row in ex.get("doorbots", []):
                if "motion_snooze" in row:
                    row["motion_snooze"] = {"nested": "was scalar"}
            (overlay_dir / "devices.json").write_text(json.dumps(ex))
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "ring-api", report)
            msgs = [i.message for i in report.issues]
            self.assertTrue(any(
                "type mismatch at" in m and "doorbots[].motion_snooze" in m
                and "canonical=null" in m and "actual=dict" in m
                for m in msgs
            ))

    def test_ragged_object_keys_in_json_array(self):
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "gmail-api"
            overlay_dir.mkdir()
            (overlay_dir / "messages.json").write_text(json.dumps([
                {"id": "a", "threadId": "t1", "labelIds": [], "snippet": "s", "payload": {},
                 "sizeEstimate": 1, "historyId": "1", "internalDate": "1"},
                {"id": "b", "threadId": "t1", "labelIds": [], "snippet": "s", "payload": {},
                 "sizeEstimate": 1, "historyId": "1", "internalDate": "1"},
                {"id": "c", "snippet": "s"},
            ]))
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "gmail-api", report)
            codes = {i.code for i in report.issues}
            self.assertIn("RAGGED_OBJECT_KEYS", codes)


class ReportShapeTests(unittest.TestCase):
    def test_json_serialisation(self):
        report = V.Report()
        report.add(V.Issue(severity=V.SEV_ERROR, code="X", message="m"))
        data = json.loads(json.dumps(report.to_dict()))
        self.assertEqual(data["summary"]["errors"], 1)
        self.assertEqual(data["issues"][0]["code"], "X")


class RaggednessToleranceTests(unittest.TestCase):
    def test_ragged_nested_array_bills_line_no_key_missing(self):
        ex = V.EXAMPLES_DIR / "quickbooks-api" / "bills.json"
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "quickbooks-api"
            overlay_dir.mkdir()
            (overlay_dir / "bills.json").write_text(ex.read_text())
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "quickbooks-api", report)
            offenders = [i for i in report.issues
                         if i.code == "KEY_MISSING" and "Line[]" in i.message]
            self.assertEqual(offenders, [], msg=str([i.message for i in offenders]))

    def test_customers_primary_email_addr_polymorphism_no_type_mismatch(self):
        ex = V.EXAMPLES_DIR / "quickbooks-api" / "customers.json"
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "quickbooks-api"
            overlay_dir.mkdir()
            (overlay_dir / "customers.json").write_text(ex.read_text())
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "quickbooks-api", report)
            offenders = [i for i in report.issues
                         if i.code == "TYPE_MISMATCH" and "PrimaryEmailAddr" in i.message]
            self.assertEqual(offenders, [], msg=str([i.message for i in offenders]))

    def test_single_element_example_list_no_crash_no_spurious_error(self):
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "gmail-api"
            overlay_dir.mkdir()
            ex_rows = json.loads((V.EXAMPLES_DIR / "gmail-api" / "messages.json").read_text())
            (overlay_dir / "messages.json").write_text(json.dumps([ex_rows[0]]))
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "gmail-api", report)
            self.assertEqual(len(report.errors), 0, msg=str([i.message for i in report.errors]))

    def test_empty_actual_list_no_crash(self):
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "gmail-api"
            overlay_dir.mkdir()
            (overlay_dir / "messages.json").write_text("[]")
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "gmail-api", report)
            self.assertFalse(_has_error(report, "KEY_MISSING"))
            self.assertFalse(_has_error(report, "TYPE_MISMATCH"))

    def test_two_level_nested_list_of_dicts(self):
        example = [
            {"root_id": "r1", "children": [
                {"id": "c1", "kind": "T", "characters": "hi",
                 "children": [{"id": "gc1", "kind": "T", "characters": "yo"}]},
                {"id": "c2", "kind": "T", "characters": "hi",
                 "children": [{"id": "gc2", "kind": "T", "characters": "yo"}]},
            ]}
        ]
        actual_ok = [
            {"root_id": "r1", "children": [
                {"id": "c1", "kind": "T", "characters": "hi",
                 "children": [{"id": "gc1", "kind": "T", "characters": "yo"}]},
            ]}
        ]
        findings_ok = V._deep_compare(example, actual_ok, "root")
        codes = {c for c, _, _ in findings_ok}
        self.assertNotIn("KEY_MISSING", codes)
        actual_bad = [
            {"root_id": "r1", "children": [
                {"id": "c1", "kind": "T", "characters": "hi",
                 "children": [{"id": "gc1", "kind": "T"}]},
            ]}
        ]
        findings_bad = V._deep_compare(example, actual_bad, "root")
        codes_bad = {c for c, _, _ in findings_bad}
        self.assertIn("KEY_MISSING", codes_bad)
        self.assertTrue(any("characters" in m for c, _, m in findings_bad if c == "KEY_MISSING"))

    def test_optional_key_present_in_overlay_no_extra_no_missing(self):
        ex = V.EXAMPLES_DIR / "quickbooks-api" / "bills.json"
        overlay = json.loads(ex.read_text())
        for r in overlay:
            for line in r.get("Line", []):
                for k in ("DetailType", "Id", "LineNum", "Quantity", "UnitPrice"):
                    line.setdefault(k, "x")
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "quickbooks-api"
            overlay_dir.mkdir()
            (overlay_dir / "bills.json").write_text(json.dumps(overlay))
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "quickbooks-api", report)
            offenders = [
                i for i in report.issues
                if i.code in ("KEY_MISSING", "KEY_EXTRA") and "Line[]" in i.message
            ]
            filtered = [i for i in offenders if any(
                k in i.message for k in ("DetailType", "Id", "LineNum", "Quantity", "UnitPrice"))]
            self.assertEqual(filtered, [],
                             msg=str([i.message for i in filtered]))

    def test_genuinely_unknown_key_still_emits_key_extra(self):
        ex = V.EXAMPLES_DIR / "quickbooks-api" / "bills.json"
        overlay = json.loads(ex.read_text())
        for r in overlay:
            for line in r.get("Line", []):
                line["totally_made_up_deep_key"] = 1
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "quickbooks-api"
            overlay_dir.mkdir()
            (overlay_dir / "bills.json").write_text(json.dumps(overlay))
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "quickbooks-api", report)
            self.assertTrue(any(
                i.code == "KEY_EXTRA" and "totally_made_up_deep_key" in i.message
                for i in report.issues
            ))


class PerRowRequiredColumnTests(unittest.TestCase):
    def test_wa_id_dropped_from_50_of_51_rows_fires_missing_columns(self):
        ex = json.loads((V.EXAMPLES_DIR / "whatsapp-api" / "conversations.json").read_text())
        overlay = [dict(ex[0])]
        for _ in range(50):
            r = dict(ex[0])
            r.pop("wa_id", None)
            overlay.append(r)
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "whatsapp-api"
            overlay_dir.mkdir()
            (overlay_dir / "conversations.json").write_text(json.dumps(overlay))
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "whatsapp-api", report)
            missing = [
                i for i in report.issues
                if i.code == "SCHEMA_MISSING_COLUMNS" and "wa_id" in i.message
            ]
            self.assertEqual(len(missing), 1, msg=str([i.message for i in report.issues]))
            self.assertIn("50/51", missing[0].message)
            self.assertGreaterEqual(len(report.errors), 1)

    def test_all_rows_have_required_column_is_clean(self):
        ex = json.loads((V.EXAMPLES_DIR / "whatsapp-api" / "conversations.json").read_text())
        with tempfile.TemporaryDirectory() as td:
            overlay_dir = Path(td) / "whatsapp-api"
            overlay_dir.mkdir()
            (overlay_dir / "conversations.json").write_text(json.dumps(ex))
            report = V.Report()
            V.validate_overlay_dir(overlay_dir, "whatsapp-api", report)
            missing = [i for i in report.issues if i.code == "SCHEMA_MISSING_COLUMNS"]
            self.assertEqual(missing, [], msg=str([i.message for i in missing]))

    def test_optional_column_absent_is_not_missing_error(self):
        example_rows = [
            {"id": "a", "required1": 1, "optional_col": "x"},
            {"id": "b", "required1": 2},
        ]
        overlay_rows = [
            {"id": "c", "required1": 3},
            {"id": "d", "required1": 4},
        ]
        with tempfile.TemporaryDirectory() as td:
            api_dir = Path(td) / "examples" / "synth-api"
            api_dir.mkdir(parents=True)
            (api_dir / "widgets.json").write_text(json.dumps(example_rows))
            orig = V.EXAMPLES_DIR
            V.EXAMPLES_DIR = Path(td) / "examples"
            try:
                overlay_dir = Path(td) / "overlay" / "synth-api"
                overlay_dir.mkdir(parents=True)
                (overlay_dir / "widgets.json").write_text(json.dumps(overlay_rows))
                report = V.Report()
                V.validate_overlay_dir(overlay_dir, "synth-api", report)
                missing = [i for i in report.issues if i.code == "SCHEMA_MISSING_COLUMNS"]
                self.assertEqual(missing, [], msg=str([i.message for i in missing]))
            finally:
                V.EXAMPLES_DIR = orig

    def test_extra_column_still_warns_when_not_in_known(self):
        example_rows = [{"id": "a", "name": "n"}]
        overlay_rows = [{"id": "b", "name": "m", "mystery_col": 1}]
        with tempfile.TemporaryDirectory() as td:
            api_dir = Path(td) / "examples" / "synth-api"
            api_dir.mkdir(parents=True)
            (api_dir / "widgets.json").write_text(json.dumps(example_rows))
            orig = V.EXAMPLES_DIR
            V.EXAMPLES_DIR = Path(td) / "examples"
            try:
                overlay_dir = Path(td) / "overlay" / "synth-api"
                overlay_dir.mkdir(parents=True)
                (overlay_dir / "widgets.json").write_text(json.dumps(overlay_rows))
                report = V.Report()
                V.validate_overlay_dir(overlay_dir, "synth-api", report)
                self.assertTrue(any(
                    i.code == "SCHEMA_EXTRA_COLUMNS" and "mystery_col" in i.message
                    for i in report.issues
                ))
            finally:
                V.EXAMPLES_DIR = orig

    def test_optional_column_present_in_overlay_no_extra_warning(self):
        example_rows = [
            {"id": "a", "required1": 1, "optional_col": "x"},
            {"id": "b", "required1": 2},
        ]
        overlay_rows = [
            {"id": "c", "required1": 3, "optional_col": "y"},
            {"id": "d", "required1": 4},
        ]
        with tempfile.TemporaryDirectory() as td:
            api_dir = Path(td) / "examples" / "synth-api"
            api_dir.mkdir(parents=True)
            (api_dir / "widgets.json").write_text(json.dumps(example_rows))
            orig = V.EXAMPLES_DIR
            V.EXAMPLES_DIR = Path(td) / "examples"
            try:
                overlay_dir = Path(td) / "overlay" / "synth-api"
                overlay_dir.mkdir(parents=True)
                (overlay_dir / "widgets.json").write_text(json.dumps(overlay_rows))
                report = V.Report()
                V.validate_overlay_dir(overlay_dir, "synth-api", report)
                extra = [i for i in report.issues if i.code == "SCHEMA_EXTRA_COLUMNS"]
                self.assertEqual(extra, [], msg=str([i.message for i in extra]))
            finally:
                V.EXAMPLES_DIR = orig


if __name__ == "__main__":
    unittest.main()
