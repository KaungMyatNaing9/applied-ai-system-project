from ai.guardrails import check_ai_response_safety


def test_unsafe_medication_dosage_advice_fails():
    result = check_ai_response_safety(
        "Change the medication dosage and double the dose tonight."
    )

    assert result["passed"] is False
    assert any("dosage" in issue.lower() for issue in result["issues"])


def test_normal_safe_response_passes():
    result = check_ai_response_safety(
        "Keep meals and walks on schedule, watch for overlap risks, and contact your veterinarian if urgent symptoms appear."
    )

    assert result["passed"] is True
    assert result["issues"] == []
