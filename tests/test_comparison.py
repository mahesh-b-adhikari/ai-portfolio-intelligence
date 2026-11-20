import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


PROJECT_DIR = Path(__file__).resolve().parent.parent


class TestPortfolioComparison(unittest.TestCase):

    def test_known_portfolio_changes(self):
        with TemporaryDirectory() as folder:
            temp_dir = Path(folder)

            # Copy the original weekly data into a temporary folder
            for name in ("portfolio_week_1.json", "portfolio_week_2.json"):
                data = json.loads(
                    (PROJECT_DIR / name).read_text(encoding="utf-8")
                )
                (temp_dir / name).write_text(
                    json.dumps(data), encoding="utf-8"
                )

            # Run comparison without touching the working outputs
            subprocess.run(
                [sys.executable, str(PROJECT_DIR / "compare_portfolio.py")],
                cwd=temp_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            results = json.loads(
                (temp_dir / "portfolio_changes.json").read_text(
                    encoding="utf-8"
                )
            )

            # Verify PAY-02's milestone moved by 21 days
            delays = results["milestone_date_changes"]
            self.assertTrue(
                any(
                    item["initiative_id"] == "PAY-02"
                    and item["change_days"] == 21
                    for item in delays
                )
            )

            # Verify PAY-06 deteriorated from amber to red
            deteriorations = results["status_deteriorations"]
            self.assertTrue(
                any(
                    item["initiative_id"] == "PAY-06"
                    and item["old_status"] == "amber"
                    and item["new_status"] == "red"
                    for item in deteriorations
                )
            )
    def test_new_status_deterioration(self):
        with TemporaryDirectory() as folder:
            temp_dir = Path(folder)

            for name in ("portfolio_week_1.json", "portfolio_week_2.json"):
                data = json.loads(
                    (PROJECT_DIR / name).read_text(encoding="utf-8")
                )

                # Introduce a new deterioration in Week 2
                if name == "portfolio_week_2.json":
                    for initiative in data["initiatives"]:
                        if initiative["initiative_id"] == "PAY-01":
                            initiative["status"] = "red"
                            break

                (temp_dir / name).write_text(
                    json.dumps(data), encoding="utf-8"
                )

            subprocess.run(
                [sys.executable, str(PROJECT_DIR / "compare_portfolio.py")],
                cwd=temp_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            results = json.loads(
                (temp_dir / "portfolio_changes.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertIn(
                {
                    "initiative_id": "PAY-01",
                    "old_status": "green",
                    "new_status": "red",
                },
                results["status_deteriorations"],
            )
    def test_progress_does_not_imply_on_track(self):
        with TemporaryDirectory() as folder:
            temp_dir = Path(folder)

            for name in ("portfolio_week_1.json", "portfolio_week_2.json"):
                data = json.loads(
                    (PROJECT_DIR / name).read_text(encoding="utf-8")
                )
                (temp_dir / name).write_text(
                    json.dumps(data), encoding="utf-8"
                )

            subprocess.run(
                [sys.executable, str(PROJECT_DIR / "compare_portfolio.py")],
                cwd=temp_dir,
                check=True,
                capture_output=True,
                text=True,
            )

            results = json.loads(
                (temp_dir / "portfolio_changes.json").read_text(
                    encoding="utf-8"
                )
            )

            # PAY-05 made measurable progress
            self.assertTrue(
                any(
                    item["initiative_id"] == "PAY-05"
                    and item["change"] == 20
                    for item in results["completion_changes"]
                )
            )

            # But PAY-05 has a newly identified high-severity risk
            self.assertTrue(
                any(
                    item["initiative_id"] == "PAY-05"
                    and item["severity"] == "high"
                    for item in results["new_risks"]
                )
            )

            # Progress alone must not qualify it as stable/on track
            self.assertFalse(
                any(
                    item["initiative_id"] == "PAY-05"
                    for item in results["stable_on_track"]
                )
            )