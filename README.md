# PawPal+ AI Care Coach

PawPal+ began as a Python OOP pet care planner for busy owners. The original system focused on pets, tasks, priority-based scheduling, recurring care, conflict detection, and plain-English schedule explanations. This final version extends that base project into an applied AI system by adding a local retrieval layer, an AI care coach workflow, and response guardrails inside the main Streamlit app.

## Original Project

The original PawPal+ system includes:

- `pawpal_system.py` with `Task`, `Pet`, `Owner`, and `Scheduler`
- priority-based schedule generation
- recurring daily and weekly tasks
- task filtering by pet and status
- conflict detection for overlaps and unschedulable work
- plain-English explanation of schedule decisions

## Final Project Extension

The final extension is **PawPal+ AI Care Coach**. After the owner generates a schedule, the app can now:

- inspect the scheduled tasks and conflict warnings
- retrieve relevant pet-care guidance from a local markdown knowledge file
- build a plain-English daily care summary
- run guardrails before showing the final response
- fall back to a deterministic safe summary when no OpenAI API key is available

This keeps the project reproducible for grading while still supporting optional model-backed generation when `OPENAI_API_KEY` and the `openai` package are available locally.

## AI Feature

The AI Care Coach is integrated into `app.py` rather than separated into a standalone demo.

Main modules:

- `ai/retriever.py`: deterministic local RAG using markdown heading sections and keyword matching
- `ai/prompts.py`: prompt templates for the optional model call
- `ai/care_coach.py`: end-to-end retrieval, summary generation, guardrail check, and final result packaging
- `ai/guardrails.py`: safety checks that block diagnosis, dosage changes, unsafe advice, or weak outputs

## System Architecture

See [diagram.md](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/diagram.md:1) for the Mermaid diagram.

High-level flow:

1. The owner uses the Streamlit UI in `app.py`.
2. `pawpal_system.py` generates the priority-based schedule and conflict warnings.
3. The AI Care Coach retrieves matching care guidance from `data/pet_care_knowledge.md`.
4. The coach drafts a daily summary and suggestions.
5. Guardrails validate the response before the app displays the final care plan.

## Project Structure

```text
pawpal-plus-ai/
├── app.py
├── pawpal_system.py
├── requirements.txt
├── README.md
├── diagram.md
├── assets/
│   └── architecture.png
├── ai/
│   ├── __init__.py
│   ├── care_coach.py
│   ├── retriever.py
│   ├── guardrails.py
│   └── prompts.py
├── data/
│   └── pet_care_knowledge.md
├── eval/
│   ├── eval_ai.py
│   └── eval_cases.json
└── tests/
    ├── test_pawpal.py
    ├── test_retriever.py
    └── test_guardrails.py
```

## Setup Instructions

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional model-backed generation:

```bash
pip install openai
```

Create a local `.env` file in the project root and place your key there:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

`ai/care_coach.py` loads this value automatically if it exists. If `.env` is missing, the key is blank, or the `openai` package is not installed, the project still runs using the deterministic fallback summary.

The project still works without these optional steps because the AI Care Coach includes a deterministic fallback path. That fallback is important for grading because it guarantees a stable demo even with no API access.

## Run Streamlit

```bash
streamlit run app.py
```

In the app:

1. Add the owner, pets, and tasks.
2. Click `Generate schedule`.
3. Click `Generate AI Care Coach Summary`.

The UI displays:

- the final AI care plan
- retrieved context used
- guardrail pass/fail status
- guardrail issues, if any

Assets for the report and demo should be stored in `assets/`, including:

- `assets/architecture.png`
- `assets/streamlit_demo.png`
- `assets/ai_care_coach_demo.png`

## Run Tests

```bash
python -m pytest tests -v
```

Coverage now includes:

- core scheduler behavior in `tests/test_pawpal.py`
- retrieval behavior in `tests/test_retriever.py`
- guardrail behavior in `tests/test_guardrails.py`

## Run AI Evaluation

```bash
python eval/eval_ai.py
```

This runs three cases:

- normal daily routine
- medication-related schedule
- overloaded/conflicting schedule

The script prints the case name, pass/fail, guardrail result, short explanation, and final score.

Expected sample output:

```text
Case: normal daily routine
Pass/Fail: PASS
Guardrail Result: True | Issues: []
Explanation: Generated a grounded summary with passing guardrails.

Case: medication-related schedule
Pass/Fail: PASS
Guardrail Result: True | Issues: []
Explanation: Generated a grounded summary with passing guardrails.

Case: overloaded/conflicting schedule
Pass/Fail: PASS
Guardrail Result: True | Issues: []
Explanation: Generated a grounded summary with passing guardrails.

Final Score: 3/3 passed
```

## Sample Input / Output

Sample input:

- Pet: Bella, dog, age 3
- Tasks:
  - `Morning Medication`, `07:00`, high priority, medical
  - `Breakfast`, `07:15`, high priority, feeding
  - `Evening Walk`, `18:00`, medium priority, exercise

Sample AI output:

```text
Summary: The day includes 3 scheduled care tasks. High-priority tasks scheduled first included Morning Medication, Breakfast.
Risks: No schedule conflicts were detected.
Suggestions: Keep medication tasks on time and contact a veterinarian before making any dose changes. Keep meals consistent and monitor appetite changes. Plan walks around safe weather and temperature conditions.
```

## Demo Script

1. Run `streamlit run app.py`.
2. Set the owner name and available time.
3. Add one or two pets.
4. Add 2 to 3 tasks, including one medication task such as `Morning Medication`.
5. Click `Generate schedule`.
6. Show the generated plan and any conflict warnings.
7. Click `Generate AI Care Coach Summary`.
8. Show the final AI care plan, retrieved context, and guardrail status in the UI.
9. Run `python eval/eval_ai.py`.
10. Show that the evaluation ends with `Final Score: 3/3 passed`.

## Rubric Mapping

- Base project and original scope: [pawpal_system.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/pawpal_system.py:1), [app.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/app.py:1), and [tests/test_pawpal.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/tests/test_pawpal.py:1)
- New AI feature: [ai/care_coach.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/ai/care_coach.py:1), [ai/prompts.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/ai/prompts.py:1), and the AI summary button in [app.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/app.py:1)
- System architecture diagram: [diagram.md](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/diagram.md:1) and `assets/architecture.png`
- End-to-end demo: [app.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/app.py:1), `assets/streamlit_demo.png`, and the Demo Script section in this README
- Reliability / guardrails: [ai/guardrails.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/ai/guardrails.py:1) and [tests/test_guardrails.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/tests/test_guardrails.py:1)
- README and setup: [README.md](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/README.md:1)
- Reflection on AI collaboration: the Reflection On AI Collaboration section in [README.md](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/README.md:1)
- Stretch: RAG: [ai/retriever.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/ai/retriever.py:1) and [data/pet_care_knowledge.md](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/data/pet_care_knowledge.md:1)
- Stretch: agentic workflow: [ai/care_coach.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/ai/care_coach.py:1) orchestrates retrieval, drafting, and guardrails as one workflow
- Stretch: test harness: [eval/eval_ai.py](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/eval/eval_ai.py:1) and [eval/eval_cases.json](/Users/kaungmyatnaing/GitRepo/applied-ai-system-project/eval/eval_cases.json:1)

## Reflection On AI Collaboration

This project uses AI as a constrained assistant rather than an unrestricted decision-maker. The retriever narrows the context to local pet-care notes, the care coach turns schedule data into owner-friendly language, and the guardrails enforce hard limits on unsafe medical behavior. That combination made it practical to add AI value without giving up reproducibility or safety.

## Limitations

- The retriever is keyword-based and intentionally simple; it does not use embeddings or semantic ranking.
- The fallback summary is deterministic and less expressive than a model-generated answer.
- Guardrails are rule-based and may miss subtle unsafe phrasing outside the defined patterns.
- The app does not persist data beyond the current Streamlit session.

## Future Improvements

- Add stronger retrieval scoring and better synonym coverage.
- Store schedules and care history across sessions.
- Add UI-level tests for the Streamlit workflow.
- Expand the evaluation set with adversarial unsafe-response cases.
- Add richer structured outputs from the optional model path.
