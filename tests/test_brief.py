import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent


class TestExecutiveBrief(unittest.TestCase):

    def test_critical_evidence_present(self):
        brief = (PROJECT_DIR / "brief_v2.txt").read_text(
            encoding="utf-8"
        )

        # Critical portfolio findings must be represented
        required_evidence = [
            "PAY-02",
            "21 days",
            "PAY-05",
            "45%",
            "65%",
            "R-05-01",
            "PAY-06",
            "B-06-01",
            "D-04-01",
        ]

        for evidence in required_evidence:
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, brief)
    def test_no_unknown_initiative_ids(self):
        import json
        import re

        portfolio = json.loads(
            (PROJECT_DIR / "portfolio_week_2.json").read_text(
                encoding="utf-8"
            )
        )

        valid_ids = {
            item["initiative_id"]
            for item in portfolio["initiatives"]
        }

        brief = (PROJECT_DIR / "brief_v2.txt").read_text(
            encoding="utf-8"
        )

        mentioned_ids = set(re.findall(r"\bPAY-\d+\b", brief))

        unknown_ids = mentioned_ids - valid_ids

        self.assertEqual(
            unknown_ids,
            set(),
            f"Brief contains unknown initiative IDs: {unknown_ids}",
        )
    def test_no_unknown_risk_or_blocker_ids(self):
        import json
        import re

        evidence = json.loads(
            (PROJECT_DIR / "portfolio_changes.json").read_text(
                encoding="utf-8"
            )
        )

        valid_ids = set()

        for category in ("new_risks", "changed_risks", "resolved_risks"):
            for item in evidence.get(category, []):
                valid_ids.add(item["risk_id"])

        for item in evidence.get("new_blockers", []):
            valid_ids.add(item["blocker_id"])

        brief = (PROJECT_DIR / "brief_v2.txt").read_text(
            encoding="utf-8"
        )

        mentioned_ids = set(
            re.findall(r"\b(?:R|B)-\d{2}-\d{2}\b", brief)
        )

        unknown_ids = mentioned_ids - valid_ids

        self.assertEqual(
            unknown_ids,
            set(),
            f"Brief references unsupported risk/blocker IDs: {unknown_ids}",
        )
    def test_detects_invented_initiative(self):
        import json
        import re

        portfolio = json.loads(
            (PROJECT_DIR / "portfolio_week_2.json").read_text(
                encoding="utf-8"
            )
        )

        valid_ids = {
            item["initiative_id"]
            for item in portfolio["initiatives"]
        }

        original_brief = (PROJECT_DIR / "brief_v2.txt").read_text(
            encoding="utf-8"
        )

        # Introduce an invented initiative in memory only
        modified_brief = (
            original_brief
            + "\n- PAY-99: Critical implementation failure."
        )

        mentioned_ids = set(
            re.findall(r"\bPAY-\d+\b", modified_brief)
        )

        unknown_ids = mentioned_ids - valid_ids

        # The evaluator must detect the invented ID
        self.assertIn("PAY-99", unknown_ids)
    def test_milestone_delay_matches_evidence(self):
        import json
        import re

        evidence = json.loads(
            (PROJECT_DIR / "portfolio_changes.json").read_text(
                encoding="utf-8"
            )
        )

        delay = next(
            item["change_days"]
            for item in evidence["milestone_date_changes"]
            if item["initiative_id"] == "PAY-02"
        )

        brief = (PROJECT_DIR / "brief_v2.txt").read_text(
            encoding="utf-8"
        )

        # Find the PAY-02 milestone statement
        milestone_line = next(
            line for line in brief.splitlines()
            if "PAY-02" in line and "milestone" in line.lower()
        )

        match = re.search(r"(\d+)\s+days?", milestone_line)

        self.assertIsNotNone(
            match,
            "PAY-02 milestone statement has no numeric delay."
        )

        self.assertEqual(
            int(match.group(1)),
            delay,
            "AI-reported milestone delay differs from evidence."
        )
    def test_detects_incorrect_milestone_delay(self):
        import json
        import re

        evidence = json.loads(
            (PROJECT_DIR / "portfolio_changes.json").read_text(
                encoding="utf-8"
            )
        )

        expected_delay = next(
            item["change_days"]
            for item in evidence["milestone_date_changes"]
            if item["initiative_id"] == "PAY-02"
        )

        original_brief = (PROJECT_DIR / "brief_v2.txt").read_text(
            encoding="utf-8"
        )

        # Introduce an incorrect delay in memory only
        modified_brief = original_brief.replace(
            "21 days", "30 days"
        )

        self.assertNotEqual(
            modified_brief,
            original_brief,
            "The test did not modify the brief."
        )

        milestone_line = next(
            line for line in modified_brief.splitlines()
            if "PAY-02" in line and "milestone" in line.lower()
        )

        match = re.search(r"(\d+)\s+days?", milestone_line)

        self.assertIsNotNone(match)

        # The evaluator must recognize that 30 != 21
        self.assertNotEqual(
            int(match.group(1)),
            expected_delay,
            "The incorrect milestone delay was not detected."
        )
    def test_reusable_evaluator(self):
        import json
        from evaluate_brief import evaluate_brief

        brief = (PROJECT_DIR / "brief_v2.txt").read_text(
            encoding="utf-8"
        )

        evidence = json.loads(
            (PROJECT_DIR / "portfolio_changes.json").read_text(
                encoding="utf-8"
            )
        )

        portfolio = json.loads(
            (PROJECT_DIR / "portfolio_week_2.json").read_text(
                encoding="utf-8"
            )
        )

        # Test 1: The real brief should pass
        result = evaluate_brief(brief, evidence, portfolio)

        self.assertTrue(result["passed"], result["findings"])

        # Test 2: An invented initiative should fail
        invalid_brief = brief + "\nPAY-99: Critical failure."

        result = evaluate_brief(invalid_brief, evidence, portfolio)

        self.assertFalse(result["passed"])
        self.assertTrue(
            any("PAY-99" in finding for finding in result["findings"])
        )

        # Test 3: An incorrect milestone delay should fail
        incorrect_brief = brief.replace("21 days", "30 days")

        self.assertNotEqual(incorrect_brief, brief)

        result = evaluate_brief(incorrect_brief, evidence, portfolio)

        self.assertFalse(result["passed"])
        self.assertTrue(
            any("30 days" in finding for finding in result["findings"])
        )