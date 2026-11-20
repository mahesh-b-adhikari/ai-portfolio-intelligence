"""Ingest weekly Excel workbooks, compare portfolio changes, and synthesize a brief.

Run from the project directory: python3 run_pipeline.py
"""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import json
from evaluate_brief import evaluate_brief

PROJECT_DIR = Path(__file__).resolve().parent
EVIDENCE = PROJECT_DIR / "portfolio_changes.json"
BRIEF = PROJECT_DIR / "brief_v2.txt"


def run_step(script: str, *args: str) -> None:
    print(f"\nRunning {script}...", flush=True)
    subprocess.run(
        [sys.executable, str(PROJECT_DIR / script), *args],
        cwd=PROJECT_DIR,
        check=True,
    )


def main() -> None:
    required = (
        "ingest_portfolio.py",
        "compare_portfolio.py",
        "synthesize_brief.py",
        "portfolio_week_1.xlsx",
        "portfolio_week_2.xlsx",
    )
    for name in required:
        if not (PROJECT_DIR / name).is_file():
            raise SystemExit(f"Missing required file: {name}")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set in this VS Code terminal session.")

    # Validate both workbooks before replacing either working JSON snapshot.
    with tempfile.TemporaryDirectory(prefix="portfolio_ingest_") as temp_dir:
        staged = []
        for week in (1, 2):
            workbook = f"portfolio_week_{week}.xlsx"
            temporary_json = Path(temp_dir) / f"portfolio_week_{week}.json"
            run_step("ingest_portfolio.py", workbook, str(temporary_json))
            if not temporary_json.is_file() or not temporary_json.stat().st_size:
                raise SystemExit(f"Ingestion did not produce data for {workbook}")
            staged.append((temporary_json, PROJECT_DIR / f"portfolio_week_{week}.json"))

        for source, destination in staged:
            destination.write_bytes(source.read_bytes())

    # Avoid mistaking output from a previous run for new output.
    EVIDENCE.unlink(missing_ok=True)
    BRIEF.unlink(missing_ok=True)
    run_step("compare_portfolio.py")
    if not EVIDENCE.is_file():
        raise SystemExit("Comparison finished but portfolio_changes.json was not created.")
    run_step("synthesize_brief.py")
    if not BRIEF.is_file() or not BRIEF.read_text().strip():
        raise SystemExit("Synthesis finished but brief_v2.txt is missing or empty.")
        print("\nEvaluating executive brief...", flush=True)

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    portfolio = json.loads(
        (PROJECT_DIR / "portfolio_week_2.json").read_text(
            encoding="utf-8"
        )
    )
    brief = BRIEF.read_text(encoding="utf-8")

    result = evaluate_brief(brief, evidence, portfolio)

    if not result["passed"]:
        print("\nEvaluation FAILED:")
        for finding in result["findings"]:
            print(f"  - {finding}")
        raise SystemExit("Pipeline stopped: executive brief failed evaluation.")

    print("Evaluation PASSED: no issues detected by configured checks.")
    print("\nPipeline completed successfully. Evaluation passed.")
    print(f"Evidence: {EVIDENCE.name}")
    print(f"Executive brief: {BRIEF.name}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"Pipeline stopped: {Path(exc.cmd[1]).name} failed "
            f"(exit code {exc.returncode})."
        ) from exc
