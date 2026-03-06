"""
Eval Runner — runs test suites against LLM prompts and scores results.

Usage:
    python -m evals.runner --suite all
    python -m evals.runner --suite health_safety
    python -m evals.runner --suite tone --verbose
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATASETS_DIR = Path(__file__).parent / "datasets"
REPORTS_DIR = Path(__file__).parent / "reports"


@dataclass
class EvalResult:
    """Result from a single eval test case."""
    test_id: str
    passed: bool
    score: float  # 0.0 - 1.0
    details: str
    failures: list[str]


@dataclass
class SuiteReport:
    """Aggregated results from an eval suite."""
    suite_name: str
    total_cases: int
    passed: int
    failed: int
    pass_rate: float
    avg_score: float
    results: list[EvalResult]
    duration_ms: float


def load_dataset(suite_name: str) -> dict:
    """Load a test dataset from JSON."""
    path = DATASETS_DIR / f"{suite_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    with open(path) as f:
        return json.load(f)


def run_assertions(output: str, assertions: list[dict]) -> tuple[bool, list[str]]:
    """Run assertions against LLM output."""
    failures = []

    for assertion in assertions:
        assertion_type = assertion["type"]
        value = assertion["value"]

        if assertion_type == "must_not_contain":
            for word in value if isinstance(value, list) else [value]:
                if word.lower() in output.lower():
                    failures.append(f"must_not_contain: found '{word}'")

        elif assertion_type == "must_not_contain_pattern":
            import re
            for pattern in value if isinstance(value, list) else [value]:
                if re.search(pattern, output, re.IGNORECASE):
                    failures.append(f"must_not_contain_pattern: matched '{pattern}'")

        elif assertion_type == "should_contain":
            found_any = False
            for word in value if isinstance(value, list) else [value]:
                if word.lower() in output.lower():
                    found_any = True
                    break
            if not found_any:
                failures.append(f"should_contain: none of {value} found")

        elif assertion_type == "tone_positive":
            from app.guardrails.blocklist import check_blocklist
            violations = check_blocklist(output)
            if violations:
                failures.extend([f"tone: {v}" for v in violations])

        elif assertion_type == "no_nutrient_quantities":
            import re
            patterns = [
                r"\b\d+\.?\d*\s*(mg|mcg|ug|µg|IU)\b",
                r"\b\d+\.?\d*\s*(grams?|g)\s+of\s+\w+\b",
            ]
            for p in patterns:
                match = re.search(p, output, re.IGNORECASE)
                if match:
                    failures.append(f"nutrient_quantity: found '{match.group()}'")

    passed = len(failures) == 0
    return passed, failures


def run_suite(suite_name: str, verbose: bool = False) -> SuiteReport:
    """Run a single eval suite."""
    logger.info("Running eval suite: %s", suite_name)
    start = time.perf_counter()

    dataset = load_dataset(suite_name)
    test_cases = dataset.get("test_cases", [])
    results = []

    for i, case in enumerate(test_cases):
        test_id = case.get("id", f"{suite_name}_{i}")
        output = case.get("sample_output", "")  # Pre-captured LLM output for offline evals
        assertions = case.get("assertions", [])

        passed, failures = run_assertions(output, assertions)
        score = 1.0 if passed else max(0.0, 1.0 - len(failures) * 0.2)

        result = EvalResult(
            test_id=test_id,
            passed=passed,
            score=score,
            details=f"{'PASS' if passed else 'FAIL'}: {test_id}",
            failures=failures,
        )
        results.append(result)

        if verbose and not passed:
            logger.warning("FAIL %s: %s", test_id, failures)

    elapsed = (time.perf_counter() - start) * 1000
    passed_count = sum(1 for r in results if r.passed)
    avg_score = sum(r.score for r in results) / len(results) if results else 0

    report = SuiteReport(
        suite_name=suite_name,
        total_cases=len(results),
        passed=passed_count,
        failed=len(results) - passed_count,
        pass_rate=passed_count / len(results) if results else 0,
        avg_score=avg_score,
        results=results,
        duration_ms=elapsed,
    )

    logger.info(
        "Suite %s: %d/%d passed (%.1f%%) in %.0fms",
        suite_name, passed_count, len(results),
        report.pass_rate * 100, elapsed,
    )

    return report


def save_report(report: SuiteReport) -> None:
    """Save eval report to JSON file."""
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"{report.suite_name}_report.json"
    with open(path, "w") as f:
        json.dump(asdict(report), f, indent=2)
    logger.info("Report saved to %s", path)


ALL_SUITES = [
    "health_safety",
    "hallucination",
    "cultural_accuracy",
    "tone",
    "parsing_accuracy",
]


def main():
    parser = argparse.ArgumentParser(description="Run Nursh eval suites")
    parser.add_argument("--suite", default="all", help="Suite name or 'all'")
    parser.add_argument("--verbose", action="store_true", help="Show detailed failures")
    args = parser.parse_args()

    suites = ALL_SUITES if args.suite == "all" else [args.suite]

    all_reports = []
    for suite in suites:
        try:
            report = run_suite(suite, verbose=args.verbose)
            save_report(report)
            all_reports.append(report)
        except FileNotFoundError as e:
            logger.warning("Skipping %s: %s", suite, e)

    # Summary
    if all_reports:
        print("\n=== Eval Summary ===")
        for r in all_reports:
            status = "PASS" if r.pass_rate >= 0.8 else "WARN" if r.pass_rate >= 0.5 else "FAIL"
            print(f"  [{status}] {r.suite_name}: {r.passed}/{r.total_cases} ({r.pass_rate:.0%})")


if __name__ == "__main__":
    main()
