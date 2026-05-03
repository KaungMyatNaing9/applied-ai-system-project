"""Simple local retriever for PawPal+ AI Care Coach."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


@dataclass
class RetrievedSection:
    """A retrieved knowledge section and its relevance score."""

    title: str
    text: str
    score: int


class LocalPetCareRetriever:
    """Retrieve relevant markdown sections using deterministic keyword matching."""

    def __init__(self, knowledge_path: str | Path = "data/pet_care_knowledge.md") -> None:
        self.knowledge_path = Path(knowledge_path)
        self.sections = self._load_sections()

    def _load_sections(self) -> list[dict[str, str]]:
        text = self.knowledge_path.read_text(encoding="utf-8").strip()
        pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
        matches = list(pattern.finditer(text))
        sections: list[dict[str, str]] = []

        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            title = match.group(1).strip()
            body = text[start:end].strip()
            if body:
                sections.append({"title": title, "text": body})

        return sections

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[a-zA-Z]+", text.lower())

    def _expand_keywords(self, tokens: Iterable[str]) -> set[str]:
        expanded = set(tokens)
        synonym_groups = {
            "medication": {"medication", "medicine", "meds", "pill", "dose", "dosage", "insulin"},
            "feeding": {"feeding", "feed", "meal", "breakfast", "dinner", "food", "appetite"},
            "walks": {"walk", "walks", "exercise", "outside", "outdoor", "playtime"},
            "grooming": {"grooming", "brush", "brushing", "bath", "fur", "nails", "coat"},
            "vet appointments": {"vet", "veterinarian", "appointment", "clinic", "urgent", "symptom"},
            "safety warnings": {"warning", "warnings", "conflict", "overlap", "unsafe", "risk", "heat"},
        }

        for group in synonym_groups.values():
            if expanded.intersection(group):
                expanded.update(group)

        return expanded

    def retrieve(
        self,
        task_category: str = "",
        task_title: str = "",
        conflict_warnings: list[str] | None = None,
        top_k: int = 3,
    ) -> list[RetrievedSection]:
        """Return the most relevant knowledge sections for the given schedule context."""

        query_text = " ".join(
            [
                task_category,
                task_title,
                " ".join(conflict_warnings or []),
            ]
        )
        query_tokens = self._expand_keywords(self._tokenize(query_text))
        results: list[RetrievedSection] = []

        for section in self.sections:
            haystack = f"{section['title']} {section['text']}".lower()
            title_tokens = set(self._tokenize(section["title"]))
            score = 0
            for token in query_tokens:
                if token in haystack:
                    score += 3 if token in title_tokens else 1

            if score > 0:
                results.append(
                    RetrievedSection(
                        title=section["title"],
                        text=section["text"],
                        score=score,
                    )
                )

        results.sort(key=lambda item: (-item.score, item.title.lower()))
        return results[:top_k]
