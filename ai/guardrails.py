"""Guardrails for AI Care Coach outputs."""

from __future__ import annotations

import re


def check_ai_response_safety(response: str) -> dict[str, object]:
    """Validate the generated response and provide a safe fallback when needed."""

    issues: list[str] = []
    normalized = response.strip()
    lowered = normalized.lower()

    if not normalized or len(normalized.split()) < 8:
        issues.append("Response is empty or too short to be useful.")

    dosage_patterns = [
        r"\bchange (the )?(medication )?dosage\b",
        r"\bincrease (the )?(medication )?dosage\b",
        r"\bdecrease (the )?(medication )?dosage\b",
        r"\bdouble (the )?dose\b",
        r"\bskip\b.*\bdose\b",
    ]
    if any(re.search(pattern, lowered) for pattern in dosage_patterns):
        issues.append("Response suggests changing medication dosage.")

    diagnosis_patterns = [
        r"\bi diagnose\b",
        r"\bthis is definitely\b",
        r"\byour pet has\b",
        r"\bthe diagnosis is\b",
    ]
    if any(re.search(pattern, lowered) for pattern in diagnosis_patterns):
        issues.append("Response gives a medical diagnosis.")

    vet_patterns = [
        r"\bignore (the )?veterinarian\b",
        r"\bignore (the )?vet\b",
        r"\bdon't call (the )?vet\b",
        r"\bdo not contact (a )?vet\b",
    ]
    if any(re.search(pattern, lowered) for pattern in vet_patterns):
        issues.append("Response tells the user to ignore a veterinarian.")

    unsafe_patterns = [
        r"\bunsafe\b",
        r"\bfeed chocolate\b",
        r"\blet .* overheat\b",
        r"\bignore symptoms\b",
        r"\bwait several days before getting help\b",
    ]
    if any(re.search(pattern, lowered) for pattern in unsafe_patterns):
        issues.append("Response contains unsafe advice.")

    fallback = (
        "PawPal+ AI Care Coach could not provide a safe final summary. "
        "Follow the scheduled routine, watch for conflicts or missed care, "
        "and contact your veterinarian for urgent medical concerns."
    )

    return {
        "passed": not issues,
        "issues": issues,
        "safe_fallback_message": fallback,
    }
