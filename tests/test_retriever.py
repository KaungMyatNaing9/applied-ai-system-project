from ai.retriever import LocalPetCareRetriever


def test_medication_tasks_retrieve_medication_section():
    retriever = LocalPetCareRetriever("data/pet_care_knowledge.md")

    results = retriever.retrieve(
        task_category="medical",
        task_title="Morning medication",
        conflict_warnings=[],
    )

    assert any(section.title == "Medication" for section in results)


def test_walk_tasks_retrieve_walks_section():
    retriever = LocalPetCareRetriever("data/pet_care_knowledge.md")

    results = retriever.retrieve(
        task_category="exercise",
        task_title="Evening walk",
        conflict_warnings=[],
    )

    assert any(section.title == "Walks" for section in results)
