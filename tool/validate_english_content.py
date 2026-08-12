from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
BAD_MARKERS = (
    "text unclear",
    "|||||",
    "go on to the next page",
    "anhle",
)


def expected_numbers(key: str) -> list[int]:
    stem = Path(key).stem
    start_text, answers = stem.split("_", 1)
    start = int(start_text)
    return list(range(start, start + len(answers)))


def validate_entry(key: str, entry: dict) -> list[str]:
    errors: list[str] = []
    documents = entry.get("documents") or []
    questions = entry.get("questions") or []
    if entry.get("status") != "reviewed":
        errors.append("status is not reviewed")
    if not documents:
        errors.append("documents are missing")
    combined = "\n".join(str(doc.get("content", "")) for doc in documents)
    if len(combined.strip()) < 180:
        errors.append("document content is suspiciously short")
    lowered = combined.lower()
    for marker in BAD_MARKERS:
        if marker in lowered:
            errors.append(f"document contains forbidden marker: {marker}")
    expected = expected_numbers(key)
    if expected[0] <= 146:
        for number in expected:
            if f"[{number}]" not in combined:
                errors.append(f"Part 6 document is missing blank [{number}]")
    actual = [int(question.get("number", -1)) for question in questions]
    if actual != expected:
        errors.append(f"question numbers {actual} != {expected}")
    for question in questions:
        number = int(question.get("number", -1))
        text = str(question.get("text", "")).strip()
        choices = question.get("choices") or {}
        if not text:
            errors.append(f"question {number} has empty text")
        if set(choices) != set("ABCD"):
            errors.append(f"question {number} does not have A/B/C/D")
            continue
        normalized_choices = [re.sub(r"\s+", " ", str(choices[letter]).strip().lower()) for letter in "ABCD"]
        if len(set(normalized_choices)) != 4:
            errors.append(f"question {number} contains duplicate choices")
        for letter, value in choices.items():
            choice = str(value).strip()
            if not choice:
                errors.append(f"question {number}{letter} is empty")
                continue
            lowered_choice = choice.lower()
            if any(marker in lowered_choice for marker in BAD_MARKERS):
                errors.append(f"question {number}{letter} contains a forbidden marker")
            other_numbers = [item for item in expected if item != number]
            if any(re.search(rf"(?<!\d){item}[.,]\s*\([A-D]\)", choice) for item in other_numbers):
                errors.append(f"question {number}{letter} contains another question")
            if len(choice) > 650:
                errors.append(f"question {number}{letter} is suspiciously long")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fragment", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.fragment.read_text(encoding="utf-8"))
    failures = {key: validate_entry(key, entry) for key, entry in payload.items()}
    failures = {key: errors for key, errors in failures.items() if errors}
    print(f"Checked {len(payload)} entries; failed {len(failures)}")
    for key, errors in failures.items():
        print(f"{key}: {'; '.join(errors)}")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
