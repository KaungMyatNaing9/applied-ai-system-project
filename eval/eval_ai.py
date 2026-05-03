"""Evaluation harness for PawPal+ AI Care Coach."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.care_coach import generate_ai_care_coach_summary


def main() -> None:
    cases_path = Path(__file__).with_name("eval_cases.json")
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    passed = 0

    for case in cases:
        result = generate_ai_care_coach_summary(
            schedule_items=case["schedule_items"],
            conflict_warnings=case["conflict_warnings"],
            pet_task_data=case["schedule_items"],
        )
        case_passed = bool(result["final_message"]) and result["guardrail_passed"]
        if case_passed:
            passed += 1

        explanation = (
            "Generated a grounded summary with passing guardrails."
            if case_passed
            else "Guardrails failed or no final message was produced."
        )

        print(f"Case: {case['name']}")
        print(f"Pass/Fail: {'PASS' if case_passed else 'FAIL'}")
        print(f"Guardrail Result: {result['guardrail_passed']} | Issues: {result['guardrail_issues']}")
        print(f"Explanation: {explanation}")
        print()

    print(f"Final Score: {passed}/{len(cases)} passed")


if __name__ == "__main__":
    main()
