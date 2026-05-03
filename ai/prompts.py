"""Prompt templates for PawPal+ AI Care Coach."""

from __future__ import annotations


SYSTEM_PROMPT = """
You are PawPal+ AI Care Coach.
Write a plain-English daily pet care summary for the owner.
Summarize the day's schedule, explain priority decisions, mention conflicts or risks,
and ground suggestions in the retrieved pet-care context.
Do not diagnose medical conditions.
Do not tell the user to change medication dosage.
Do not tell the user to ignore a veterinarian.
If there is an urgent medical concern, recommend contacting a veterinarian.
Use concise, practical language.
""".strip()


def build_user_prompt(
    schedule_text: str,
    conflict_text: str,
    retrieved_context_text: str,
) -> str:
    """Build the user prompt for the optional model call."""

    return f"""
Create a daily care coach response using the schedule and retrieved context.

Schedule:
{schedule_text}

Conflicts:
{conflict_text}

Retrieved Context:
{retrieved_context_text}

Return a short response with these labels:
Summary:
Risks:
Suggestions:
Final Message:
""".strip()
